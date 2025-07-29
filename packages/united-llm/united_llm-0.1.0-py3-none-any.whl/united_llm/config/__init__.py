"""
United LLM Configuration Module

This module provides a clean interface to the configuration system,
re-exporting zero-config functionality with United LLM defaults.
"""

import zero_config
from .defaults import UNITED_LLM_DEFAULTS

# Direct re-exports from zero-config (preserves all parameters)
setup_environment = zero_config.setup_environment
get_config = zero_config.get_config
is_initialized = zero_config.is_initialized
get_initialization_info = zero_config.get_initialization_info

# United LLM setup function
def setup_united_llm_environment():
    """Setup United LLM configuration with defaults and .env.united_llm file."""
    setup_environment(default_config=UNITED_LLM_DEFAULTS, env_files=[".env.united_llm"])


# Export everything
__all__ = [
    "setup_environment",
    "get_config",
    "is_initialized",
    "get_initialization_info",
    "setup_united_llm_environment",
    "UNITED_LLM_DEFAULTS",
]
