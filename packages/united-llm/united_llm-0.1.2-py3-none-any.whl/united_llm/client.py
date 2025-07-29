"""
Enhanced LLM Client with united search capabilities.
Extends the original LLMClient with Anthropic web search and DuckDuckGo search integration.
"""

import os
import logging
from typing import Dict, Any, List, Type, TypeVar, Optional, Union
import json
import time
import random
from datetime import datetime
from pydantic import BaseModel
import traceback

import instructor  # Main library for structured outputs

# Database logging
from .utils.database import LLMDatabase, LLMCallRecord

# Model management
from .utils.model_manager import ModelManager

# Type variable for generic handling of Pydantic models
T = TypeVar("T", bound=BaseModel)


def get_ollama_context(input_text: str) -> int:
    """Calculate appropriate context size for Ollama based on input length"""
    estimated_tokens = len(input_text) // 3
    needed = estimated_tokens * 2
    if needed <= 8192:
        return 8192
    elif needed <= 16384:
        return 16384
    elif needed <= 32768:
        return 32768
    else:
        return 65536


class LLMClient:
    """
    Enhanced LLM client with united search capabilities.
    Supports structured outputs with optional web search integration.
    """

    def __init__(self, config: Union[Dict[str, Any], None] = None, log_calls: Optional[bool] = None):
        self.logger = logging.getLogger(__name__)

        # Use clean config interface
        try:
            from .config import setup_united_llm_environment, get_config

            # Always call setup with United LLM defaults - zero-config prevents multiple setups automatically
            setup_united_llm_environment()
            self.bootstrap_config = get_config()

            self.logger.info("Configuration loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load bootstrap config: {e}")
            raise RuntimeError(f"Configuration system failed to initialize: {e}")

        # Handle user config overrides
        if config is None:
            # No user config, use bootstrap as-is
            self.config = self.bootstrap_config.to_dict()
            self.logger.info("Using bootstrap configuration for LLMClient")
        elif isinstance(config, dict):
            # Handle dictionary config - merge with bootstrap (user config overrides)
            self.config = {**self.bootstrap_config.to_dict(), **config}
            user_keys = list(config.keys())
            self.logger.info(f"Merged user config with bootstrap configuration (overriding: {user_keys})")
        else:
            raise ValueError(f"Invalid config parameter. Expected dict or None. Got {type(config)}: {config}")

        # Store bootstrap config for direct access to helper methods
        self.bootstrap = self.bootstrap_config

        # Initialize model manager with current config
        self.model_manager = ModelManager(self.config)

        self.log_calls = log_calls if log_calls is not None else self.config.get("log_calls", False)
        self.log_to_db = self.config.get("log_to_db", True)
        self.log_json = self.config.get("log_json", False)

        # Initialize txt file logging directories
        self.txt_log_folder = None
        self.json_log_folder = None
        if self.log_calls:
            # Setup txt file logging directories using bootstrap paths
            self.txt_log_folder = self.bootstrap.logs_path("llm_calls/txt")
            self.json_log_folder = self.bootstrap.logs_path("llm_calls/json")
            try:
                os.makedirs(self.txt_log_folder, exist_ok=True)
                if self.log_json:
                    os.makedirs(self.json_log_folder, exist_ok=True)
                self.logger.info(f"TXT file logging enabled: {self.txt_log_folder}")
            except OSError as e:
                self.logger.error(f"Could not create LLM log dirs: {e}. Disabling file logging.")
                self.log_calls = self.log_json = False

        # Initialize database if logging is enabled
        self.db = None
        if self.log_to_db:
            db_path = self.bootstrap.get_db_path()
            try:
                self.db = LLMDatabase(db_path)
                self.logger.info(f"Database logging enabled: {db_path}")
            except Exception as e:
                self.logger.error(f"Failed to initialize database: {e}")
                self.log_to_db = False

        # Use bootstrap-based model lists
        self.OPENAI_MODELS = set(self.bootstrap.get("openai_models", []))
        self.ANTHROPIC_MODELS = set(self.bootstrap.get("anthropic_models", []))
        self.GOOGLE_MODELS = set(self.bootstrap.get("google_models", []))

        self._verify_configuration()

        # Initialize search modules
        self._duckduckgo_search = None

    def _verify_configuration(self):
        # Check and log for each provider
        self.has_openai = bool(self.config.get("openai_api_key") or os.environ.get("OPENAI_API_KEY"))
        if not self.has_openai:
            self.logger.warning("OpenAI API key not found or not configured.")

        self.has_anthropic = bool(self.config.get("anthropic_api_key") or os.environ.get("ANTHROPIC_API_KEY"))
        if not self.has_anthropic:
            self.logger.warning("Anthropic API key not found or not configured.")

        self.has_google = bool(self.config.get("google_api_key") or os.environ.get("GOOGLE_API_KEY"))
        if not self.has_google:
            self.logger.warning("Google API key not found or not configured.")

        # For Ollama, check if the base_url is explicitly set to something other than None/empty or the default True
        ollama_base_url_config = self.config.get("ollama_base_url")
        if ollama_base_url_config is None or ollama_base_url_config is True:
            if not isinstance(ollama_base_url_config, str):
                self.logger.warning(
                    "Ollama base URL not explicitly configured as a string. It might fall back to default if used."
                )
                self.has_ollama = False
            else:
                self.has_ollama = True
        elif not ollama_base_url_config:
            self.logger.warning("Ollama base URL is configured as an empty string, disabling Ollama.")
            self.has_ollama = False
        else:
            self.has_ollama = True

        if not any([self.has_openai, self.has_anthropic, self.has_google, self.has_ollama]):
            self.logger.warning("No LLM providers configured.")
        else:
            self.logger.info(
                f"LLM Providers: OpenAI={self.has_openai}, Anthropic={self.has_anthropic}, "
                f"Google={self.has_google}, Ollama={self.has_ollama}"
            )

    def _get_openai_client(self):
        """Create a new Instructor-enhanced OpenAI client for each request."""
        if not self.has_openai:
            raise ValueError("OpenAI API key not configured.")
        try:
            from openai import OpenAI

            api_key = self.config.get("openai_api_key") or os.environ.get("OPENAI_API_KEY")
            kwargs = {"api_key": api_key}
            openai_base_url = self.config.get("openai_base_url")
            if openai_base_url:
                kwargs["base_url"] = openai_base_url
            return instructor.from_openai(OpenAI(**kwargs))
        except ImportError:
            self.logger.error("OpenAI lib not found. pip install openai")
            raise
        except Exception as e:
            self.logger.error(f"Failed to create OpenAI client: {e}")
            raise

    def _get_anthropic_client(self, with_search: bool = False):
        """Create a new Instructor-enhanced Anthropic client for each request."""
        if not self.has_anthropic:
            raise ValueError("Anthropic API key not configured.")
        try:
            from anthropic import Anthropic

            api_key = self.config.get("anthropic_api_key") or os.environ.get("ANTHROPIC_API_KEY")
            kwargs = {"api_key": api_key}
            anthropic_base_url = self.config.get("anthropic_base_url")
            if anthropic_base_url:
                kwargs["base_url"] = anthropic_base_url

            anthropic_client = Anthropic(**kwargs)
            if with_search:
                # Enable web search for Anthropic
                return instructor.from_anthropic(anthropic_client, mode=instructor.Mode.ANTHROPIC_JSON)
            else:
                return instructor.from_anthropic(anthropic_client)
        except ImportError:
            self.logger.error("Anthropic lib not found. pip install anthropic")
            raise
        except Exception as e:
            self.logger.error(f"Failed to create Anthropic client: {e}")
            raise

    def _get_ollama_client(self):
        """Create a new plain Ollama client for each request."""
        try:
            from openai import OpenAI

            base_url = self.config.get("ollama_base_url")
            if not base_url:
                raise ValueError("Ollama base_url not configured.")

            return OpenAI(base_url=base_url, api_key="ollama")
        except ImportError:
            self.logger.error("OpenAI lib (for Ollama) not found. pip install openai")
            raise
        except Exception as e:
            self.logger.error(f"Failed to create Ollama client: {e}")
            raise

    def _get_ollama_client_for_model(self, model_name: str):
        """Create a new Instructor-wrapped Ollama client for the specific model."""
        try:
            # Get the base Ollama client
            base_client = self._get_ollama_client()

            # Use JSON mode for all Ollama models (simplified approach)
            # This works reliably for structured outputs without complex function calling detection
            return instructor.patch(base_client, mode=instructor.Mode.JSON)

        except Exception as e:
            self.logger.error(f"Failed to create Ollama client for {model_name}: {e}")
            raise

    def _get_google_client(self, model_name: str = "models/gemini-1.5-flash-latest"):
        """Create a new Instructor-enhanced Google client for the specific model."""
        if not self.has_google:
            raise ValueError("Google API key not configured.")
        try:
            import google.generativeai as genai

            api_key = self.config.get("google_api_key") or os.environ.get("GOOGLE_API_KEY")
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name=model_name)
            return instructor.from_gemini(
                client=model,
                mode=instructor.Mode.GEMINI_JSON,
            )
        except ImportError:
            self.logger.error("Google GenAI lib not found. pip install google-generativeai")
            raise
        except Exception as e:
            self.logger.error(f"Failed to create Google client for {model_name}: {e}")
            raise

    def determine_provider(self, model: str) -> tuple[str, str]:
        """
        Smart model provider detection using bootstrap configuration.
        Validates that big three models are in configured lists.
        """
        # First, validate the model is available in our configuration
        try:
            self.model_manager.validate_model_available(model)
        except ValueError as e:
            raise ValueError(str(e))

        # Use smart detection to determine provider
        provider = self.model_manager.detect_model_provider(model)

        if provider == "openai":
            return "openai", model
        elif provider == "anthropic":
            return "anthropic", model
        elif provider == "google":
            # Google model mapping for API compatibility
            google_model_mapping = {
                "gemini-2.5-pro-preview-05-06": "models/gemini-1.5-pro-latest",
                "gemini-2.5-flash-preview-05-20": "models/gemini-1.5-flash-latest",
                "gemini-pro": "models/gemini-1.5-pro-latest",
                "gemini-1.5-pro": "models/gemini-1.5-pro-latest",
                "gemini-1.5-flash": "models/gemini-1.5-flash-latest",
            }
            actual_model = google_model_mapping.get(model, f"models/{model}")
            return "google", actual_model
        elif provider == "ollama":
            if not self.has_ollama:
                raise ValueError(f"Ollama provider not configured but model '{model}' routes to Ollama")
            return "ollama", model
        else:
            raise ValueError(f"Unknown provider '{provider}' for model '{model}'")

    def _get_client_for_model(self, model: str, enable_anthropic_search: bool = False):
        provider, model_name = self.determine_provider(model)
        if provider == "openai":
            return self._get_openai_client()
        if provider == "anthropic":
            return self._get_anthropic_client(with_search=enable_anthropic_search)
        if provider == "google":
            return self._get_google_client(model_name)
        if provider == "ollama":
            return self._get_ollama_client_for_model(model_name)
        raise ValueError(f"Unknown provider: {provider}")

    def _validate_search_parameters(self, anthropic_web_search: bool, duckduckgo_search: bool, model: str):
        """Validate search parameters and model compatibility"""
        if anthropic_web_search and duckduckgo_search:
            raise ValueError("Cannot use both anthropic_web_search and duckduckgo_search simultaneously")

        if anthropic_web_search:
            provider, _ = self.determine_provider(model)
            if provider != "anthropic":
                raise ValueError(f"Anthropic web search is only supported with Anthropic models, not {model}")

    def _get_duckduckgo_search(self):
        """Lazy loading of DuckDuckGo search module"""
        if self._duckduckgo_search is None:
            from .search.duckduckgo_search import DuckDuckGoSearch

            self._duckduckgo_search = DuckDuckGoSearch(self.config, self)
        return self._duckduckgo_search

    def _log_interaction(
        self,
        model: str,
        prompt: str,
        response: Any = None,
        token_usage: dict = None,
        error_info: str = None,
        duration_ms: int = None,
        search_type: str = None,
        request_schema: str = None,
        is_before_call: bool = False,
        txt_filepath: Optional[str] = None,
        json_filepath: Optional[str] = None,
    ):
        """Log LLM interaction to both database and txt files if logging is enabled."""

        # Log to database
        if self.log_to_db and self.db and not is_before_call:
            try:
                # Determine provider
                provider = self.model_manager.detect_model_provider(model)

                # Convert response to string if it's a BaseModel
                response_str = None
                if response is not None:
                    if isinstance(response, BaseModel):
                        response_str = json.dumps(response.model_dump(), indent=2, default=str)
                    else:
                        response_str = (
                            json.dumps(response, indent=2, default=str)
                            if isinstance(response, (dict, list))
                            else str(response)
                        )

                # Create record
                record = LLMCallRecord(
                    timestamp=datetime.now(),
                    model=model,
                    provider=provider,
                    prompt=prompt,
                    response=response_str,
                    token_usage=token_usage,
                    error=error_info,
                    duration_ms=duration_ms,
                    search_type=search_type,
                    request_schema=request_schema,
                )

                # Log to database
                self.db.log_call(record)

            except Exception as e:
                self.logger.error(f"Failed to log interaction to database: {e}")

        # Log to txt files (similar to original implementation)
        if not self.log_calls or not self.txt_log_folder:
            return None, None

        try:
            now = datetime.now()
            date_folder = now.strftime("%Y-%m-%d")
            # New format: YYYYMMDD-HH:MM:SS_random(0-9)_model_name
            timestamp = now.strftime("%Y%m%d-%H:%M:%S")
            random_digit = str(random.randint(0, 9))
            current_txt_log_dir = os.path.join(self.txt_log_folder, date_folder)
            os.makedirs(current_txt_log_dir, exist_ok=True)
            base_filename = f"{timestamp}_{random_digit}_{model.replace(':', '_')}"

            # Initialize log paths
            final_txt_log_path = txt_filepath or os.path.join(current_txt_log_dir, f"{base_filename}.txt")
            final_json_log_path = None

            log_entry = f"Timestamp: {now.isoformat()}\nModel: {model}\n"
            if search_type:
                log_entry += f"Search Type: {search_type}\n"
            if duration_ms:
                log_entry += f"Duration: {duration_ms}ms\n"
            log_entry += (
                f"Prompt/Messages:\n{json.dumps(prompt, indent=2) if isinstance(prompt, (dict, list)) else prompt}\n\n"
            )

            if is_before_call:
                log_entry += "--- Waiting for response ---\n"
            else:
                response_data = (
                    response.model_dump() if isinstance(response, BaseModel) else response
                    if response is not None
                    else "N/A"
                )
                log_entry += f"Response:\n{json.dumps(response_data, indent=2, default=str)}\n\n"
                if token_usage:
                    log_entry += f"Token Usage: {json.dumps(token_usage)}\n"
                if error_info:
                    log_entry += f"Error: {error_info}\n"

            # Write to txt file
            with open(final_txt_log_path, "a", encoding="utf-8") as f:
                f.write(log_entry + "------------------------------------\n")

            # Write to JSON file if enabled
            if self.log_json and self.json_log_folder and not is_before_call:
                current_json_log_dir = os.path.join(self.json_log_folder, date_folder)
                os.makedirs(current_json_log_dir, exist_ok=True)
                final_json_log_path = json_filepath or os.path.join(current_json_log_dir, f"{base_filename}.json")

                json_data = {
                    "timestamp": now.isoformat(),
                    "model": model,
                    "prompt_messages": prompt,
                    "response": response.model_dump() if isinstance(response, BaseModel) else response,
                    "token_usage": token_usage,
                    "error": error_info,
                    "duration_ms": duration_ms,
                    "search_type": search_type,
                    "request_schema": request_schema,
                }

                with open(final_json_log_path, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, indent=2, default=str)

            return final_txt_log_path, final_json_log_path

        except Exception as e:
            self.logger.error(f"Failed to write txt/json logs: {e}")
            return None, None

    def _clean_text(self, text: str) -> str:
        return text.replace("\x00", "")

    def _handle_google_rate_limit_retry(self, func, max_retries: int = 3):
        """Handle Google API rate limiting with exponential backoff"""
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "Resource has been exhausted" in error_str or "quota" in error_str.lower():
                    if attempt < max_retries - 1:
                        sleep_time = 2 ** (attempt + 1)
                        self.logger.warning(
                            f"Google API rate limit hit, retrying in {sleep_time} seconds "
                            f"(attempt {attempt + 1}/{max_retries})"
                        )
                        time.sleep(sleep_time)
                        continue
                raise

    def generate_structured(
        self,
        prompt: str,
        output_model: Type[T],
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_retries: int = 1,
        enable_web_search: bool = False,
        anthropic_web_search: bool = False,
        duckduckgo_search: bool = False,
        fallback_models: Optional[List[str]] = None,
    ) -> T:
        """
        Generate structured output with optional search capabilities and fallback models.

        Args:
            prompt: The input prompt
            output_model: Pydantic model class for structured output
            model: Model to use (defaults to DEFAULT_MODEL)
            temperature: Sampling temperature
            max_retries: Maximum number of retries
            enable_web_search: Enable web search (automatically chooses best method for model)
            anthropic_web_search: [DEPRECATED] Enable Anthropic web search (Anthropic models only)
            duckduckgo_search: [DEPRECATED] Enable DuckDuckGo search with 3-step processing
            fallback_models: Optional list of fallback models to try if primary model fails

        Returns:
            Structured output of type output_model
        """
        cleaned_prompt = self._clean_text(prompt)
        primary_model = model or self.bootstrap.get("default_model")

        # Handle enable_web_search flag - automatically determine search type
        if enable_web_search and not anthropic_web_search and not duckduckgo_search:
            # Auto-determine search type based on model
            if primary_model and (
                primary_model.startswith("claude") or primary_model.startswith("anthropic")
            ):
                anthropic_web_search = True
            else:
                duckduckgo_search = True

        # Build list of models to try
        models_to_try = [primary_model]
        if fallback_models:
            models_to_try.extend(fallback_models)

        # Try each model in order
        last_exception = None
        for i, current_model in enumerate(models_to_try):
            try:
                if i > 0:  # Only log for fallback attempts
                    self.logger.info(f"Attempting fallback with model: {current_model}")

                # Validate search parameters for current model
                self._validate_search_parameters(anthropic_web_search, duckduckgo_search, current_model)

                # Handle DuckDuckGo search (works with any model)
                if duckduckgo_search:
                    search_handler = self._get_duckduckgo_search()
                    return search_handler.search_and_generate(
                        cleaned_prompt, output_model, current_model, temperature, max_retries
                    )

                # Handle Anthropic web search - Direct integration without separate class
                if anthropic_web_search:
                    if not current_model.startswith(("claude", "anthropic")):
                        raise ValueError("Anthropic web search is only available for Anthropic models")
                    # Extract schema from output_model for logging
                    try:
                        schema_json = json.dumps(output_model.model_json_schema(), default=str)
                    except Exception:
                        schema_json = None
                    return self._generate_anthropic_with_search(
                        cleaned_prompt,
                        output_model,
                        current_model,
                        temperature,
                        max_retries,
                        schema=schema_json,
                    )

                # Standard generation (existing functionality)
                # Extract schema from output_model for logging
                try:
                    schema_json = json.dumps(output_model.model_json_schema(), default=str)
                except Exception:
                    schema_json = None

                return self._generate_standard(
                    cleaned_prompt, output_model, current_model, temperature, max_retries, schema=schema_json
                )

            except Exception as e:
                last_exception = e
                if i < len(models_to_try) - 1:  # Not the last model
                    self.logger.warning(
                        f"Model {current_model} failed: {type(e).__name__} - {str(e)}. Trying next model."
                    )
                else:
                    # Last model failed
                    if len(models_to_try) > 1:
                        self.logger.error(f"All models failed. Last error: {last_exception}")
                    raise last_exception

        # This should never be reached, but just in case
        raise last_exception

    def generate_dict(
        self,
        prompt: str,
        schema: str,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_retries: int = 1,
        enable_web_search: bool = False,
        anthropic_web_search: bool = False,
        duckduckgo_search: bool = False,
        fallback_models: Optional[List[str]] = None,
    ) -> dict:
        """
        Generate structured output as a plain Python dictionary using string schema.

        NEW: Supports JSON-consistent curly brace syntax!

        Args:
            prompt: The input prompt
            schema: String schema definition (supports both legacy and new curly brace syntax)
                   Examples:
                   - "{name, age:int, email?}" - Single object
                   - "[{name, email}]" - Array of objects
                   - "{team, members:[{name, role}]}" - Nested structures
                   - "name, age:int" - Legacy format (still works)
            model: Model to use (defaults to DEFAULT_MODEL)
            temperature: Sampling temperature
            max_retries: Maximum number of retries
            enable_web_search: Enable web search (automatically chooses best method for model)
            anthropic_web_search: [DEPRECATED] Enable Anthropic web search (Anthropic models only)
            duckduckgo_search: [DEPRECATED] Enable DuckDuckGo search with 3-step processing
            fallback_models: Optional list of fallback models to try if primary model fails

        Returns:
            Plain Python dictionary (not a Pydantic model)

        Examples:
            # NEW: JSON-consistent syntax
            result = client.generate_dict("Create a user profile", "{name, age:int, email?}")
            # Returns: {"name": "John Doe", "age": 30, "email": "john@example.com"}

            # NEW: Array of objects
            result = client.generate_dict("List team members", "[{name, role}]")
            # Returns: [{"name": "Alice", "role": "Developer"}, {"name": "Bob", "role": "Designer"}]

            # NEW: Nested structures
            result = client.generate_dict("Create team data", "{team, members:[{name, role}]}")
            # Returns: {"team": "Engineering", "members": [{"name": "Alice", "role": "Developer"}]}
        """
        import string_schema

        # Validate schema first and get detailed information
        validation = string_schema.validate_string_schema(schema)
        if not validation["valid"]:
            raise ValueError(f"Invalid schema: {', '.join(validation['errors'])}")

        # Log schema features for debugging
        if validation.get("warnings"):
            self.logger.warning(f"Schema warnings: {validation['warnings']}")
        self.logger.info(f"Schema features used: {validation.get('features_used', [])}")

        # Handle array schemas by wrapping them in an object for instructor compatibility
        # Array schemas like [{name, age}] need to be wrapped as {items:[{name, age}]}
        # so that instructor can handle them properly
        working_schema = schema
        is_array_schema = schema.strip().startswith("[") and schema.strip().endswith("]")
        if is_array_schema:
            working_schema = f"{{items:{schema}}}"

        # Convert string schema to Pydantic model (supports new curly brace syntax)
        output_model = string_schema.string_to_model(working_schema, "DictGenerationModel")

        # Generate structured output using existing infrastructure
        pydantic_result = self.generate_structured(
            prompt=prompt,
            output_model=output_model,
            model=model,
            temperature=temperature,
            max_retries=max_retries,
            enable_web_search=enable_web_search,
            anthropic_web_search=anthropic_web_search,
            duckduckgo_search=duckduckgo_search,
            fallback_models=fallback_models,
        )

        # Convert Pydantic model to plain dictionary
        result_dict = pydantic_result.model_dump()

        # If we wrapped an array schema, unwrap the result
        if is_array_schema and "items" in result_dict:
            result_dict = result_dict["items"]

        # Use string_schema's validation for additional safety
        try:
            validated_result = string_schema.validate_to_dict(result_dict, schema)
            return validated_result
        except Exception as e:
            self.logger.warning(f"Schema validation warning: {e}")
            # Return original result if validation fails
            return result_dict

    def _generate_standard(
        self,
        prompt: str,
        output_model: Type[T],
        model: str,
        temperature: float,
        max_retries: int,
        schema: str = None,
    ) -> T:
        """Standard generation without search (preserves original functionality)"""
        response_obj = None
        token_details = None
        error_info_str = None

        client = self._get_client_for_model(model, enable_anthropic_search=False)
        provider, model_name = self.determine_provider(model)

        # Log "before call" for txt file logging
        txt_log_path, json_log_path = self._log_interaction(
            model, prompt, request_schema=schema, is_before_call=True
        )

        # Track timing for database logging
        start_time = time.time()

        messages = [{"role": "user", "content": prompt}]
        try:
            self.logger.info(f"Generating with {model} ({provider}). Prompt: '{prompt[:100]}...'")
            kwargs = {"messages": messages, "response_model": output_model, "max_retries": max_retries}

            if provider != "google":
                kwargs["model"] = model_name
                kwargs["temperature"] = temperature

                if provider == "anthropic":
                    kwargs["max_tokens"] = 1024
            else:
                if temperature != 0.0:
                    kwargs["generation_config"] = {"temperature": temperature}

            if provider == "google":
                response_obj = self._handle_google_rate_limit_retry(
                    lambda: client.chat.completions.create(**kwargs), max_retries=max(max_retries, 3)
                )
            else:
                response_obj = client.chat.completions.create(**kwargs)

            if (
                hasattr(response_obj, "_raw_response")
                and hasattr(response_obj._raw_response, "usage")
                and response_obj._raw_response.usage
            ):
                raw_usage = response_obj._raw_response.usage
                if hasattr(raw_usage, "input_tokens"):
                    token_details = {
                        "prompt_tokens": raw_usage.input_tokens,
                        "completion_tokens": raw_usage.output_tokens,
                        "total_tokens": raw_usage.input_tokens + raw_usage.output_tokens,
                    }
                else:
                    token_details = {
                        "prompt_tokens": raw_usage.prompt_tokens,
                        "completion_tokens": raw_usage.completion_tokens,
                        "total_tokens": raw_usage.total_tokens,
                    }
            elif hasattr(response_obj, "usage") and response_obj.usage:
                raw_usage = response_obj.usage
                if hasattr(raw_usage, "input_tokens"):
                    token_details = {
                        "prompt_tokens": raw_usage.input_tokens,
                        "completion_tokens": raw_usage.output_tokens,
                        "total_tokens": raw_usage.input_tokens + raw_usage.output_tokens,
                    }
                else:
                    token_details = {
                        "prompt_tokens": raw_usage.prompt_tokens,
                        "completion_tokens": raw_usage.completion_tokens,
                        "total_tokens": raw_usage.total_tokens,
                    }
            self.logger.info(f"Successfully generated structured output with {model}.")
            return response_obj
        except Exception as e:
            error_info_str = (
                f"Error with {model}: {type(e).__name__} - {str(e)}. "
                f"Traceback: {traceback.format_exc()}"
            )
            self.logger.error(error_info_str)
            raise
        finally:
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)

            # Log the interaction (final logging with response)
            self._log_interaction(
                model=model,
                prompt=prompt,
                response=response_obj,
                token_usage=token_details,
                error_info=error_info_str,
                duration_ms=duration_ms,
                request_schema=schema,
                is_before_call=False,
                txt_filepath=txt_log_path,
                json_filepath=json_log_path,
            )

    def get_model_info(self, model: str) -> Dict[str, Any]:
        try:
            provider, model_name = self.determine_provider(model)
            info = {"model_name": model_name, "provider": provider, "configured": True}

            # Add search capability info
            if provider == "anthropic":
                info["supports_anthropic_web_search"] = True
            info["supports_duckduckgo_search"] = True

            return info
        except ValueError as e:
            return {"model_name": model, "provider": "Unknown", "configured": False, "error": str(e)}

    def get_ollama_models(self) -> List[str]:
        """Query Ollama server for available models"""
        if not self.model_manager.has_provider("ollama"):
            return []

        # Use the ModelManager's simple method to get Ollama models
        ollama_base_url = self.bootstrap.get("ollama_base_url", "http://localhost:11434")
        return self.model_manager.get_ollama_models(ollama_base_url)

    def get_available_models(self) -> List[str]:
        """Get available models using bootstrap configuration"""
        available = []

        # Add models from each provider if configured
        if self.model_manager.has_provider("openai"):
            available.extend(self.bootstrap.get("openai_models", []))

        if self.model_manager.has_provider("anthropic"):
            available.extend(self.bootstrap.get("anthropic_models", []))

        if self.model_manager.has_provider("google"):
            available.extend(self.bootstrap.get("google_models", []))

        if self.model_manager.has_provider("ollama"):
            # Get actual Ollama models instead of placeholder
            ollama_models = self.get_ollama_models()
            if ollama_models:
                available.extend(ollama_models)
            else:
                # Fallback to placeholder if query fails
                available.append("ollama (dynamic models)")

        return sorted(list(set(available)))

    def get_models_grouped_by_provider(self) -> Dict[str, List[str]]:
        """Get models grouped by provider with alphabetical sorting within each group"""
        grouped_models = {"anthropic": [], "google": [], "openai": [], "ollama": []}

        # Add models from each provider if configured
        if self.model_manager.has_provider("anthropic"):
            models = self.bootstrap.get("anthropic_models", [])
            grouped_models["anthropic"] = sorted(models)

        if self.model_manager.has_provider("google"):
            models = self.bootstrap.get("google_models", [])
            grouped_models["google"] = sorted(models)

        if self.model_manager.has_provider("openai"):
            models = self.bootstrap.get("openai_models", [])
            grouped_models["openai"] = sorted(models)

        if self.model_manager.has_provider("ollama"):
            ollama_models = self.get_ollama_models()
            if ollama_models:
                grouped_models["ollama"] = sorted(ollama_models)

        # Remove empty groups
        return {provider: models for provider, models in grouped_models.items() if models}

    def _generate_anthropic_with_search(
        self,
        prompt: str,
        output_model: Type[T],
        model: str,
        temperature: float,
        max_retries: int,
        schema: str = None,
    ) -> T:
        """Direct Anthropic web search integration without separate class"""
        response_obj = None
        token_details = None
        error_info_str = None

        # Get Instructor-wrapped Anthropic client with search enabled
        client = self._get_anthropic_client(with_search=True)
        _, model_name = self.determine_provider(model)

        # Log "before call" for txt file logging
        txt_log_path, json_log_path = self._log_interaction(
            model, prompt, request_schema=schema, is_before_call=True, search_type="anthropic_web_search"
        )

        # Track timing for database logging
        start_time = time.time()

        try:
            self.logger.info(
                f"Generating with Anthropic web search using {model}. Prompt: '{prompt[:100]}...'"
            )

            # Direct call with web search tools - no prompt wrapping needed!
            response_obj = client.messages.create(
                model=model_name,
                max_tokens=4000,
                temperature=temperature,
                response_model=output_model,
                max_retries=max_retries,
                tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}],
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract token usage if available
            if hasattr(response_obj, "_raw_response") and hasattr(response_obj._raw_response, "usage"):
                raw_usage = response_obj._raw_response.usage
                token_details = {
                    "prompt_tokens": raw_usage.input_tokens,
                    "completion_tokens": raw_usage.output_tokens,
                    "total_tokens": raw_usage.input_tokens + raw_usage.output_tokens,
                }

            self.logger.info(
                f"Successfully generated structured output with Anthropic web search using {model}."
            )
            return response_obj

        except Exception as e:
            error_info_str = (
                f"Error with Anthropic web search using {model}: {type(e).__name__} - {str(e)}. "
                f"Traceback: {traceback.format_exc()}"
            )
            self.logger.error(error_info_str)
            raise
        finally:
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)

            # Log the interaction (final logging with response)
            self._log_interaction(
                model=model,
                prompt=prompt,
                response=response_obj,
                token_usage=token_details,
                error_info=error_info_str,
                duration_ms=duration_ms,
                search_type="anthropic_web_search",
                request_schema=schema,
                is_before_call=False,
                txt_filepath=txt_log_path,
                json_filepath=json_log_path,
            )
