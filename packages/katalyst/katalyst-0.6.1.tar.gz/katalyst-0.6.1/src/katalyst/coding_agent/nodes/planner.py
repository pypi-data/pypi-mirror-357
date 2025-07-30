import os
from katalyst.katalyst_core.state import KatalystState
from katalyst.katalyst_core.services.llms import (
    get_llm_client,
    get_llm_params,
)
from langchain_core.messages import AIMessage
from katalyst.katalyst_core.utils.models import SubtaskList, PlaybookEvaluation
from katalyst.katalyst_core.utils.logger import get_logger
from katalyst.katalyst_core.utils.tools import extract_tool_descriptions
from katalyst.katalyst_core.utils.error_handling import (
    ErrorType,
    create_error_message,
    classify_error,
    format_error_for_llm,
)


def planner(state: KatalystState) -> KatalystState:
    """
    Generate initial subtask list in state.task_queue, set state.task_idx = 0, etc.
    Uses Instructor to get a structured list of subtasks from the LLM.
    If state.playbook_guidelines is provided, evaluate its relevance and use it appropriately.

    * Primary Task: Call an LLM to generate an initial, ordered list of sub-task descriptions based on the main state.task.
    * State Changes:
    * Sets state.task_queue to the new list of sub-task strings.
    * Resets state.task_idx = 0.
    * Resets state.outer_cycles = 0 (as this is the start of a new P-n-E attempt).
    * Resets state.completed_tasks = [].
    * Resets state.response = None.
    * Resets state.error_message = None.
    * Optionally, logs the generated plan to state.chat_history as an AIMessage or SystemMessage.
    * Returns: The updated KatalystState.
    """
    logger = get_logger()
    logger.debug("[PLANNER] Starting planner node...")
    logger.debug(f"[PLANNER][CONTENT_REF] Initial content_store state: {len(state.content_store)} references")

    # Use simplified API
    llm = get_llm_client("planner", async_mode=False, use_instructor=True)
    llm_params = get_llm_params("planner")
    tool_descriptions = extract_tool_descriptions()
    tool_list_str = "\n".join(f"- {name}: {desc}" for name, desc in tool_descriptions)

    playbook_guidelines = getattr(state, "playbook_guidelines", None)

    # First, evaluate playbook relevance if guidelines exist
    if playbook_guidelines:
        evaluation_prompt = f"""
        # TASK
        Evaluate the relevance and applicability of the provided playbook guidelines to the current task.
        Think step by step about how well the guidelines match the task requirements.

        # CURRENT TASK
        {state.task}

        # PLAYBOOK GUIDELINES
        {playbook_guidelines}

        # EVALUATION CRITERIA
        1. Direct Relevance: How directly do the guidelines address the specific task?
        2. Completeness: Do the guidelines cover all necessary aspects of the task?
        3. Specificity: Are the guidelines specific enough to be actionable?
        4. Flexibility: Do the guidelines allow for necessary adaptations?

        # OUTPUT FORMAT
        Provide your evaluation as a JSON object with the following structure:
        {{
            "relevance_score": float,  # 0.0 to 1.0, where 1.0 means perfect relevance
            "is_directly_applicable": boolean,  # Whether guidelines can be used as strict requirements
            "key_guidelines": [string],  # List of most relevant guideline points
            "reasoning": string,  # Step-by-step explanation of your evaluation
            "usage_recommendation": string  # How to best use these guidelines (e.g., "strict", "reference", "ignore")
        }}
        """

        try:
            evaluation = llm.chat.completions.create(
                messages=[{"role": "system", "content": evaluation_prompt}],
                response_model=PlaybookEvaluation,
                **llm_params,
            )
            logger.debug(f"[PLANNER] Playbook evaluation: {evaluation}")

            # Log the evaluation reasoning
            state.chat_history.append(
                AIMessage(content=f"Playbook evaluation:\n{evaluation.reasoning}")
            )

            # Adjust playbook section based on evaluation
            if evaluation.is_directly_applicable and evaluation.relevance_score > 0.8:
                playbook_section = f"""
                # PLAYBOOK GUIDELINES (STRICT REQUIREMENTS)
                These guidelines are highly relevant and must be followed strictly:
                {playbook_guidelines}
                """
            elif evaluation.relevance_score > 0.5:
                playbook_section = f"""
                # PLAYBOOK GUIDELINES (REFERENCE)
                These guidelines may be helpful but should be adapted as needed:
                {playbook_guidelines}
                """
            else:
                playbook_section = f"""
                # PLAYBOOK GUIDELINES (INFORMATIONAL)
                These guidelines are provided for reference but may not be directly applicable:
                {playbook_guidelines}
                """
        except Exception as e:
            logger.warning(f"[PLANNER] Failed to evaluate playbook: {str(e)}")
            playbook_section = f"""
            # PLAYBOOK GUIDELINES
            {playbook_guidelines}
            """
    else:
        playbook_section = ""

    prompt = f"""
# ROLE
You are a planning assistant for a ReAct-style AI agent. Your job is to break down a high-level user GOAL into a logically ordered list of atomic, executable sub-tasks.

# AGENT CAPABILITIES
The agent's primary capability is to use the tools provided below. Your plan should be entirely based on using these tools to achieve the goal.

## Available Tools:
{tool_list_str}

{playbook_section}

# SUBTASK GUIDELINES

## 1. Actionable & Specific
Every sub-task must describe a clear, concrete action.
- ❌ Avoid: "Understand config file"
- ✅ Use: "Use 'read_file' to read 'config/settings.json' and summarize key configuration parameters"

## 2. Directory Creation
For directory creation, use 'write_to_file' to create a file in the desired directory - it will automatically create any needed parent directories.
- ❌ Avoid: "Create directory 'src/utils'"
- ✅ Use: "Use 'write_to_file' to create 'src/utils/__init__.py' with content '# Utils module'"

## 3. Tool Selection Guidelines
- For codebase overview: Use 'generate_directory_overview' on top-level directories (e.g., 'src/', 'app/')
- For specific file work: Use 'read_file' for focused tasks
- For structure mapping: Use 'list_code_definition_names' before deep diving
- For file listing: Use 'list_files' with recursive flag as needed
- Call 'generate_directory_overview' ONCE per top-level directory (it recursively analyzes all subdirectories)

## 4. Parameter-Specific
Include all required parameters inline (e.g., filenames, paths, content).
- ❌ Avoid: "Create a file"
- ✅ Use: "Use 'write_to_file' to create 'README.md' with content 'Initial setup'"

## 5. User Interaction
If input is needed from the user, use 'request_user_input' and specify the prompt.
- Example: "Use 'request_user_input' to ask the user for desired output folder"

## 6. Single-Step Granularity
Sub-tasks should be atomic and non-composite.
- ❌ Avoid: "Set up project structure"
- ✅ Use: "Use 'write_to_file' to create 'src/main.py'"

## 7. Logical Ordering
- Ensure dependencies are respected
- Create directories before writing files in them
- Read files before analyzing their content

## 8. Complete but Minimal
- Cover all necessary steps implied by the goal
- Do not include extra steps unless explicitly required

# HIGH-LEVEL USER GOAL
{state.task}

# OUTPUT FORMAT
Based on the GOAL, AVAILABLE TOOLS, and GUIDELINES{', and PLAYBOOK GUIDELINES' if playbook_guidelines else ''}, provide a JSON object with key "subtasks" containing a list of task descriptions.

Example:
{{
    "subtasks": [
        "Use the `list_files` tool to list contents of the current directory.",
        "Use the `read_file` tool to read 'README.md' and summarize key features.",
        "Use the `request_user_input` tool to ask the user which file to analyze next."
    ]
}}"""
    logger.debug(f"[PLANNER] Prompt to LLM:\n{prompt}")

    try:
        # Call the LLM with Instructor and Pydantic response model
        response = llm.chat.completions.create(
            messages=[{"role": "system", "content": prompt}],
            response_model=SubtaskList,
            temperature=0.3,
            model=llm_params["model"],
            timeout=llm_params["timeout"],
        )
        logger.debug(f"[PLANNER] Raw LLM response: {response}")
        subtasks = response.subtasks
        logger.debug(f"[PLANNER] Parsed subtasks: {subtasks}")

        # Update state
        state.task_queue = subtasks
        state.original_plan = subtasks  # Save the original plan
        state.task_idx = 0
        state.outer_cycles = 0
        state.completed_tasks = []
        state.response = None
        state.error_message = None

        # Log the plan to chat_history
        plan_message = f"Generated plan:\n" + "\n".join(
            f"{i+1}. {s}" for i, s in enumerate(subtasks)
        )
        state.chat_history.append(AIMessage(content=plan_message))
        logger.info(f"[PLANNER] {plan_message}")

    except Exception as e:
        error_msg = create_error_message(
            ErrorType.LLM_ERROR, f"Failed to generate plan: {str(e)}", "PLANNER"
        )
        logger.error(f"[PLANNER] {error_msg}")
        state.error_message = error_msg
        state.response = "Failed to generate initial plan. Please try again."

    logger.debug("[PLANNER] End of planner node.")
    return state
