from adapters.adapter import LanguageModelAdapter
from adapters.cohere import CohereAdapter
from adapters.open_ai import OpenAIAdapter


class LanguageModelFactory:
    @staticmethod
    def create_adapter(model_name: str, api_key: str) -> LanguageModelAdapter:
        print(f"Creating adapter for model: {model_name} with API key: {api_key[:4]}****")  # Mask API key for security
        if model_name == 'cohere':
            return CohereAdapter(api_key)
        elif model_name == 'openai':
            return OpenAIAdapter(api_key)
        else:
            raise ValueError(f"Unknown model: {model_name}")
