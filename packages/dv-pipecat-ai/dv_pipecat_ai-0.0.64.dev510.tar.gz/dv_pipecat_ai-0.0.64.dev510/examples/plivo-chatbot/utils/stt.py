from typing import List, Optional

from deepgram import LiveOptions  # noqa: D100
from env_config import api_config

from pipecat.services.azure.stt import AzureSTTService
from pipecat.services.deepgram.stt import DeepgramSTTService

# Import Gladia config models needed
from pipecat.services.gladia.config import GladiaInputParams, LanguageConfig
from pipecat.services.gladia.stt import GladiaSTTService, language_to_gladia_language
from pipecat.services.google.stt import GoogleSTTService
from pipecat.transcriptions.language import Language


# Add vocab parameter with type hint and default value
def initialize_stt_service(
    stt_provider: str,
    language: str,
    stt_model: Optional[str],
    additional_languages: List[str],
    logger,
    record_locally=False,
    vocab: Optional[List[str]] = None,
):
    """Initializes a speech-to-text (STT) service based on the specified provider.

    This function supports multiple STT providers like Deepgram, Google, Azure, and Gladia.
    For Deepgram, it can conditionally use the Nova-3 model or fall back to Nova-2 models.
    * English  → nova-phonecall
    * Hindi    → nova-2
    Vocabulary routing:
    * nova-3 → keyterms   (no boost values)
    * nova-2 / phonecall → keywords (word:boost)
    """
    if stt_provider == "deepgram":
        dg_lang = "hi" if any(l in additional_languages for l in ("hi", "hi-IN")) else language
        model = stt_model or ("nova-2-phonecall" if dg_lang.startswith("en") else "nova-2")

        def _clean_vocab(words: Optional[List[str]]) -> List[str]:
            return [w.strip() for w in words or [] if isinstance(w, str) and w.strip()]

        keywords: List[str] = []
        keyterms: List[str] = []
        base_fillers_hi = ["हाँ", "हाँ जी"]
        base_fillers_en = ["ha", "haan"]

        is_nova3 = model.startswith("nova-3")

        if dg_lang.startswith("hi"):
            fillers = base_fillers_hi
        else:
            fillers = base_fillers_en
        if is_nova3:
            # KEYTERMS (no boosts)
            keyterms.extend(fillers)
            keyterms.extend(_clean_vocab(vocab))
            keyterms = keyterms[:100]
            addons = {"keyterms": keyterms} if keyterms else None
            kw_args = {}
        else:
            # KEYWORDS (needs boost)
            keywords.extend(f"{w}:1.5" for w in fillers)
            keywords.extend(f"{w}:1.1" for w in _clean_vocab(vocab))
            keywords = keywords[:100]
            addons = None
            kw_args = {"keywords": keywords} if keywords else {}
        logger.info(
            f"Deepgram model={model}, lang={dg_lang}, "
            f"{'keyterms' if is_nova3 else 'keywords'}={keyterms or keywords}"
        )

        live_options = LiveOptions(
            model=model,
            language=dg_lang,
            encoding="linear16",
            channels=1,
            interim_results=True,
            smart_format=False,
            numerals=False,
            punctuate=True,
            profanity_filter=True,
            vad_events=False,
            **kw_args,  # ← keywords only for nova-2 / phonecall
        )
        stt = DeepgramSTTService(
            api_key=api_config.DEEPGRAM_API_KEY,
            live_options=live_options,
            audio_passthrough=record_locally,
            addons=addons,  # ← keyterms only for nova-3
        )
    elif stt_provider == "google":
        logger.debug("Google STT initilaising")
        languages = list({Language(language), Language.EN_IN})
        # list of languages you want to support; adjust if needed
        stt = GoogleSTTService(
            params=GoogleSTTService.InputParams(
                languages=languages, enable_automatic_punctuation=False, model="latest_short"
            ),
            credentials_path="creds.json",  # your service account JSON file,
            location="us",
            audio_passthrough=record_locally,
            # metrics=SentryMetrics(),
        )
        logger.debug("Google STT initiaised")
    elif stt_provider == "azure":
        logger.debug(
            f"Initializing Azure STT. Received language parameter: '{language}' (type: {type(language)})"
        )  # ADDED LOG
        # Explicitly check the condition and log the result
        # is_telugu = language == "te-IN"
        additional_langs = [Language(add_lang) for add_lang in additional_languages]
        # Note: Azure STT requires different handling (Phrase Lists) - see notes below.
        stt = AzureSTTService(
            api_key=api_config.AZURE_SPEECH_API_KEY,
            region=api_config.AZURE_SPEECH_REGION,
            language=Language(language),
            additional_languages=additional_langs,
            audio_passthrough=record_locally,
            vocab=vocab,  # Pass vocab via kwargs
            # metrics=SentryMetrics(),
        )
    elif stt_provider == "gladia":
        params = GladiaInputParams(language_config=LanguageConfig(languages=[Language(language)]))

        stt = GladiaSTTService(
            api_key=api_config.GLADIA_API_KEY,
            params=params,  # Pass the configured params object
            audio_passthrough=record_locally,
            vocab=vocab,  # Pass vocab via kwargs
            # metrics=SentryMetrics(),
        )

    return stt
