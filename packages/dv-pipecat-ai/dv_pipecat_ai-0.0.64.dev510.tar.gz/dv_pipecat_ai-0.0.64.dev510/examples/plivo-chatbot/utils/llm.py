from env_config import api_config

from pipecat.services.azure.llm import AzureLLMService
from pipecat.services.google.llm_openai import GoogleLLMOpenAIBetaService
from pipecat.services.groq.llm import GroqLLMService
from pipecat.services.openai.llm import OpenAILLMService


def initialize_llm_service(llm_provider, llm_model, **kwargs):
    if llm_provider == "groq":  # Condition to use GroqLLMService
        llm = GroqLLMService(
            api_key=api_config.GROQ_API_KEY,
            model=llm_model,
            # metrics=SentryMetrics(),
        )
    elif llm_provider == "google":
        llm = GoogleLLMOpenAIBetaService(
            api_key=api_config.GEMINI_API_KEY,
            model=llm_model,
            params=OpenAILLMService.InputParams(
                extra={"reasoning_effort": "none"},
            ),
        )
    elif llm_provider == "azure":
        llm = AzureLLMService(
            api_key=api_config.AZURE_CHATGPT_API_KEY,
            endpoint=api_config.AZURE_CHATGPT_ENDPOINT,
            model=llm_model,
            **kwargs,
        )
    else:  # Default to OpenAILLMService if llm_provider is not groq
        llm = OpenAILLMService(
            api_key=api_config.OPENAI_API_KEY,
            model=llm_model,
            # metrics=SentryMetrics(),
        )

    return llm
