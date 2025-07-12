import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from prompts import PRODUCT_GENERATION_PROMPT

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API with the key from the .env file
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env file.")
    genai.configure(api_key=api_key)
except ValueError as e:
    print(f"Error configuring Gemini: {e}")
    # Exit or handle the absence of the key as needed
    exit()


# Set up the model with generation configuration
# Using JSON mode is crucial for reliable JSON output
generation_config = {
    "response_mime_type": "application/json",
}
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config
)

class GeminiException(Exception):
    """Custom exception for Gemini service errors."""
    pass

async def generate_product_json(raw_text: str, max_retries: int = 3) -> dict:
    """
    Generates structured product JSON from raw text using the Gemini API.

    Args:
        raw_text: The raw product description text.
        max_retries: The maximum number of times to retry on failure.

    Returns:
        A dictionary containing the structured product data.

    Raises:
        GeminiException: If the API fails to return valid JSON after all retries.
    """
    # Combine the main prompt with the user's raw text
    full_prompt = f"{PRODUCT_GENERATION_PROMPT}\n\n{raw_text}"
    
    for attempt in range(max_retries):
        try:
            print(f"Calling Gemini API... (Attempt {attempt + 1}/{max_retries})")
            response = await model.generate_content_async(full_prompt)
            
            # The response.text should already be a valid JSON string
            # because we used "response_mime_type": "application/json".
            # We just need to parse it.
            return json.loads(response.text)

        except json.JSONDecodeError:
            print(f"Attempt {attempt + 1} failed: Invalid JSON response.")
            continue # Try again
        except Exception as e:
            # Handle other potential API errors (e.g., connection issues, safety blocks)
            print(f"An unexpected API error occurred on attempt {attempt + 1}: {e}")
            continue # Try again

    # If the loop completes without a successful return, raise an exception
    raise GeminiException(
        f"Failed to get valid JSON from Gemini after {max_retries} attempts."
    )