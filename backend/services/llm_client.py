import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

MODELS_TO_TRY = ["gemini-3.6-flash", "gemini-2.5-flash"]

def call_gemini(system_prompt: str, user_prompt: str, max_tokens: int = 500) -> str:
    """
    Calls Gemini Flash with system instruction and user prompt.
    Enforces JSON output via generation_config.
    Fails fast if Gemini API returns quota/rate limit or authorization errors.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set in environment variables.")

    genai.configure(api_key=api_key)

    last_error = None
    for model_name in MODELS_TO_TRY:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_prompt,
                generation_config={
                    "response_mime_type": "application/json",
                    "max_output_tokens": max_tokens,
                    "temperature": 0.7,
                }
            )
            response = model.generate_content(user_prompt, request_options={"timeout": 10})
            if response and response.text:
                return response.text
        except Exception as e:
            last_error = e
            err_str = str(e)
            # If rate limit (429) or forbidden (403), fail fast so pipeline finishes instantly
            if "429" in err_str or "403" in err_str or "Quota exceeded" in err_str:
                logger.warning(f"Gemini API quota/permission error ({e}). Failing fast.")
                raise RuntimeError(f"Gemini API quota/auth limit hit: {e}")
            logger.warning(f"Model {model_name} failed: {e}. Trying next model...")

    raise RuntimeError(f"Gemini call failed. Last error: {last_error}")
