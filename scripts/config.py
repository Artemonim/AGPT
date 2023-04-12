import abc
import os
import openai
from dotenv import load_dotenv, dotenv_values, set_key, unset_key
from pathlib import Path
# Load environment variables from .env file
load_dotenv()


class Singleton(abc.ABCMeta, type):
    """
    Singleton metaclass for ensuring only one instance of a class.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Call method for the singleton metaclass."""
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(
                *args, **kwargs)
        return cls._instances[cls]


class AbstractSingleton(abc.ABC, metaclass=Singleton):
    pass


class Config(metaclass=Singleton):
    """
    Configuration class to store the state of bools for different scripts access.
    """

    def update_env_from_template(self):
        """Updates a configuration file `.env` from a template file `.env.template`."""
        # get paths to .env and .env.template files
        env_file = Path(__file__).resolve().parent.parent / '.env'
        template_file = Path(__file__).resolve().parent.parent / '.env.template'

        if not template_file.is_file():
            print("\033[31m" + "Error: \".env.template\" not found!" + "\033[0m")
            return

        if not env_file.is_file():
            answer = input(f"File {env_file} not found. Create an empty file? (y/n) ")
            if answer.lower() == "y":
                env_file.touch()
            else:
                print("\033[31m" + "Error: \".env\" not found!" + "\033[0m")
                return

        load_dotenv(str(template_file), verbose=True)
        env_values = dotenv_values(str(env_file))
        template_values = dotenv_values(str(template_file))

        # find keys that were removed from .env.template
        removed_keys = [key for key in env_values if key not in template_values]
        # find values that need to be added from .env.template
        changes = {key: value for key, value in template_values.items()
                   if env_values.get(key, '') == '' and value != ''}

        if changes or removed_keys:
            print("Changes found in .env.template:")
            if changes:
                for key, value in changes.items():
                    print(f"{key} = {value}")
            if removed_keys:
                print("\033[33m" + f"Removed keys from .env.template: {', '.join(removed_keys)}" + "\033[0m")
            answer = input("Do you want to apply changes to .env? (y/n) ")
            if answer.lower() == "y":
                print(
                    "\033[93m" + "Warning: You may enter a confidential information.",
                    "Do not share this part of the log with third parties." + "\033[0m")
                print("Enter new values for the following keys or leave empty to keep the current value:")
                for key, value in changes.items():
                    new_value = input(f"{key} ({value}): ")
                    if new_value.strip():
                        set_key(env_file, key, new_value, quote_mode="never")
                        print(f"Updated {key} = {new_value} in {env_file}")
                    else:
                        set_key(env_file, key, value, quote_mode="never")
                        print(f"Kept {key} = {value} in {env_file}")
                for key in removed_keys:
                    unset_key(env_file, key)
                    print(f"Removed {key} from {env_file}")
            else:
                print("No changes in .env.template")


    def __init__(self):
        """Initialize the Config class"""
        self.debug_mode = False
        self.continuous_mode = False
        self.speak_mode = False

        self.update_env_from_template()

        self.fast_llm_model = os.getenv("FAST_LLM_MODEL", "gpt-3.5-turbo")
        self.smart_llm_model = os.getenv("SMART_LLM_MODEL", "gpt-4")
        self.fast_token_limit = int(os.getenv("FAST_TOKEN_LIMIT", 4000))
        self.smart_token_limit = int(os.getenv("SMART_TOKEN_LIMIT", 8000))

        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.use_azure = False
        self.use_azure = os.getenv("USE_AZURE") == 'True'
        if self.use_azure:
            self.openai_api_base = os.getenv("OPENAI_AZURE_API_BASE")
            self.openai_api_version = os.getenv("OPENAI_AZURE_API_VERSION")
            self.openai_deployment_id = os.getenv("OPENAI_AZURE_DEPLOYMENT_ID")
            openai.api_type = "azure"
            openai.api_base = self.openai_api_base
            openai.api_version = self.openai_api_version

        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")

        self.use_mac_os_tts = False
        self.use_mac_os_tts = os.getenv("USE_MAC_OS_TTS")
        
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.custom_search_engine_id = os.getenv("CUSTOM_SEARCH_ENGINE_ID")

        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_region = os.getenv("PINECONE_ENV")

        self.image_provider = os.getenv("IMAGE_PROVIDER")
        self.huggingface_api_token = os.getenv("HUGGINGFACE_API_TOKEN")

        # User agent headers to use when browsing web
        # Some websites might just completely deny request with an error code if no user agent was found.
        self.user_agent_header = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = os.getenv("REDIS_PORT", "6379")
        self.redis_password = os.getenv("REDIS_PASSWORD", "")
        self.wipe_redis_on_start = os.getenv("WIPE_REDIS_ON_START", "True") == 'True'
        self.memory_index = os.getenv("MEMORY_INDEX", 'auto-gpt')
        # Note that indexes must be created on db 0 in redis, this is not configureable.

        self.memory_backend = os.getenv("MEMORY_BACKEND", 'local')
        # Initialize the OpenAI API client
        openai.api_key = self.openai_api_key

    def set_continuous_mode(self, value: bool):
        """Set the continuous mode value."""
        self.continuous_mode = value

    def set_speak_mode(self, value: bool):
        """Set the speak mode value."""
        self.speak_mode = value

    def set_fast_llm_model(self, value: str):
        """Set the fast LLM model value."""
        self.fast_llm_model = value

    def set_smart_llm_model(self, value: str):
        """Set the smart LLM model value."""
        self.smart_llm_model = value

    def set_fast_token_limit(self, value: int):
        """Set the fast token limit value."""
        self.fast_token_limit = value

    def set_smart_token_limit(self, value: int):
        """Set the smart token limit value."""
        self.smart_token_limit = value

    def set_openai_api_key(self, value: str):
        """Set the OpenAI API key value."""
        self.openai_api_key = value

    def set_elevenlabs_api_key(self, value: str):
        """Set the ElevenLabs API key value."""
        self.elevenlabs_api_key = value

    def set_google_api_key(self, value: str):
        """Set the Google API key value."""
        self.google_api_key = value

    def set_custom_search_engine_id(self, value: str):
        """Set the custom search engine id value."""
        self.custom_search_engine_id = value

    def set_pinecone_api_key(self, value: str):
        """Set the Pinecone API key value."""
        self.pinecone_api_key = value

    def set_pinecone_region(self, value: str):
        """Set the Pinecone region value."""
        self.pinecone_region = value

    def set_debug_mode(self, value: bool):
        """Set the debug mode value."""
        self.debug_mode = value
