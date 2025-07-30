from textwrap import dedent

READ_FILE_TOOL_PROMPT = dedent("""
# read_file Tool

Description: Read the contents of a specific file. Read entire file unless it's extremely large AND you only need a small section.

## When to Use:
- Understanding file logic or structure
- Preparing to edit or debug code
- Getting exact content for diffs
- Verifying file contents after changes
- Analyzing specific implementation details

## Parameters:
- path: (string, required) File path to read
- start_line: (integer, optional) Starting line number (1-based)
- end_line: (integer, optional) Ending line number (1-based)

## Example:
{
  "thought": "I need to read src/utils.py to understand its functionality.",
  "action": "read_file",
  "action_input": {
    "path": "src/utils.py"
  }
}

## Output Format:
JSON with keys: 'path', 'start_line', 'end_line', 'content', 'content_ref' (optional), 'info' (optional), 'error' (optional)

### Content Reference System:
- When you read a file, the output includes a "content_ref" field
- This reference can be used with write_to_file to ensure exact content preservation
- Use content_ref when copying or duplicating files to avoid content corruption by the LLM.

Example outputs:
- Success: {"path": "/path/to/file.py", "start_line": 1, "end_line": 50, "content": "import os\\n...", "content_ref": "ref:file.py:a1b2c3d4"}
- Error: {"error": "File not found: missing.py"}
- Empty: {"path": "/path/to/empty.txt", "start_line": 1, "end_line": 1, "info": "File is empty", "content": ""}
""")
