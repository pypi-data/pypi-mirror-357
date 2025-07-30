"""
LLM Service Module

Provides simplified API for LLM client access with component-specific configuration.
"""

from litellm import completion, acompletion
import instructor
from katalyst.katalyst_core.config import get_llm_config


# New simplified API functions (recommended)
def get_llm_client(component: str, async_mode: bool = False, use_instructor: bool = True):
    """
    Get a configured LLM client for a specific component.
    
    This is the recommended API that handles both client and model selection.
    
    Args:
        component: Component name (e.g., 'planner', 'agent_react')
        async_mode: Whether to return async client
        use_instructor: Whether to wrap with instructor
        
    Returns:
        Configured LLM client
    """
    if async_mode:
        client = acompletion
        if use_instructor:
            client = instructor.from_litellm(acompletion)
    else:
        client = completion
        if use_instructor:
            client = instructor.from_litellm(completion)
    
    return client


def get_llm_params(component: str) -> dict:
    """
    Get LLM parameters for a specific component.
    
    Args:
        component: Component name
        
    Returns:
        Dictionary with model, timeout, fallbacks, and other parameters
    """
    config = get_llm_config()
    return {
        "model": config.get_model_for_component(component),
        "timeout": config.get_timeout(),
        "temperature": 0.1,  # Default temperature
        "fallbacks": config.get_fallback_models(),
    }


