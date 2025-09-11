import os
import json
import time
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv
from prompts import PRODUCT_GENERATION_PROMPT
from typing import List, Optional

# Load environment variables from .env file
load_dotenv()

class GeminiException(Exception):
    """Custom exception for Gemini service errors."""
    pass

class GeminiAPIKeyManager:
    """Manages multiple Gemini API keys with automatic failover."""
    
    def __init__(self):
        self.api_keys = self._load_api_keys()
        self.current_key_index = 0
        self.max_retries_per_key = int(os.getenv("MAX_RETRIES_PER_KEY", "2"))
        self.retry_delay = float(os.getenv("RETRY_DELAY", "1"))
        self.failed_keys = set()  # Track temporarily failed keys
        self.model = None
        self.generation_config = {
            "response_mime_type": "application/json",
        }
        
        if not self.api_keys:
            raise ValueError("No API keys found in .env file. Please set GOOGLE_API_KEYS.")
        
        # Initialize with the first available key
        self._initialize_model()
    
    def _load_api_keys(self) -> List[str]:
        """Load and parse API keys from environment variable."""
        keys_string = os.getenv("GOOGLE_API_KEYS", "")
        if not keys_string:
            # Fallback to old single key format for backward compatibility
            single_key = os.getenv("GOOGLE_API_KEY", "")
            if single_key:
                return [single_key]
            return []
        
        # Parse comma-separated keys and filter out empty/placeholder values
        keys = [key.strip() for key in keys_string.split(",")]
        valid_keys = [key for key in keys if key and not key.startswith("YOUR_")]
        return valid_keys
    
    def _initialize_model(self):
        """Initialize the Gemini model with the current API key."""
        if self.current_key_index >= len(self.api_keys):
            raise GeminiException("All API keys have been exhausted.")
        
        current_key = self.api_keys[self.current_key_index]
        print(f"Initializing Gemini with API key #{self.current_key_index + 1}")
        
        try:
            genai.configure(api_key=current_key)
            self.model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=self.generation_config
            )
        except Exception as e:
            print(f"Failed to initialize with key #{self.current_key_index + 1}: {e}")
            self.failed_keys.add(self.current_key_index)
            self.switch_to_next_key()
    
    def switch_to_next_key(self):
        """Switch to the next available API key."""
        self.current_key_index += 1
        
        # Skip any keys that are marked as failed
        while self.current_key_index in self.failed_keys and self.current_key_index < len(self.api_keys):
            self.current_key_index += 1
        
        if self.current_key_index >= len(self.api_keys):
            # If we've exhausted all keys, reset and try again (keys might have recovered)
            print("All keys exhausted. Resetting key rotation...")
            self.current_key_index = 0
            self.failed_keys.clear()  # Clear failed keys to retry them
            
            # If all keys are still failing after reset
            if len(self.api_keys) == 0:
                raise GeminiException("No valid API keys available.")
        
        self._initialize_model()
    
    async def generate_content_with_failover(self, prompt: str) -> str:
        """
        Generate content with automatic key failover on failure.
        
        Args:
            prompt: The prompt to send to Gemini API
            
        Returns:
            The response text from the API
            
        Raises:
            GeminiException: If all keys and retries are exhausted
        """
        total_attempts = 0
        max_total_attempts = len(self.api_keys) * self.max_retries_per_key
        
        while total_attempts < max_total_attempts:
            # Try with current key
            for retry in range(self.max_retries_per_key):
                try:
                    print(f"Attempt {total_attempts + 1}/{max_total_attempts} with key #{self.current_key_index + 1}")
                    
                    if self.model is None:
                        self._initialize_model()
                    
                    response = await self.model.generate_content_async(prompt)
                    
                    # Check if response is valid
                    if response and response.text:
                        print(f"Success with key #{self.current_key_index + 1}")
                        return response.text
                    else:
                        print(f"Empty response from API with key #{self.current_key_index + 1}")
                        raise Exception("Empty response from API")
                    
                except Exception as e:
                    total_attempts += 1
                    error_message = str(e).lower()
                    
                    # Check for quota/rate limit errors
                    if any(keyword in error_message for keyword in ['quota', 'rate', 'limit', '429', '403']):
                        print(f"Key #{self.current_key_index + 1} hit rate limit: {e}")
                        self.failed_keys.add(self.current_key_index)
                        break  # Switch to next key immediately
                    
                    # For other errors, retry with same key
                    print(f"Error with key #{self.current_key_index + 1} (retry {retry + 1}/{self.max_retries_per_key}): {e}")
                    
                    if retry < self.max_retries_per_key - 1:
                        await asyncio.sleep(self.retry_delay)
                    else:
                        # Mark this key as temporarily failed
                        self.failed_keys.add(self.current_key_index)
            
            # Switch to next key if current key failed
            if self.current_key_index < len(self.api_keys) - 1:
                print(f"Switching from key #{self.current_key_index + 1} to next key...")
                self.switch_to_next_key()
            else:
                # All keys exhausted, try resetting
                print("All keys exhausted, attempting reset...")
                self.current_key_index = 0
                self.failed_keys.clear()
                self._initialize_model()
                
                # If we've tried everything, raise exception
                if total_attempts >= max_total_attempts - 1:
                    break
        
        raise GeminiException(
            f"Failed to get response after {total_attempts} attempts across {len(self.api_keys)} API keys."
        )

# Global instance of the key manager
api_key_manager = None

def get_api_key_manager() -> GeminiAPIKeyManager:
    """Get or create the global API key manager instance."""
    global api_key_manager
    if api_key_manager is None:
        api_key_manager = GeminiAPIKeyManager()
    return api_key_manager

async def generate_product_json(raw_text: str, max_retries: int = None) -> dict:
    """
    Generates structured product JSON from raw text using the Gemini API with automatic failover.

    Args:
        raw_text: The raw product description text.
        max_retries: Deprecated parameter, kept for backward compatibility.

    Returns:
        A dictionary containing the structured product data.

    Raises:
        GeminiException: If the API fails to return valid JSON after all keys and retries.
    """
    # Get the key manager
    manager = get_api_key_manager()
    
    # Combine the main prompt with the user's raw text
    full_prompt = f"{PRODUCT_GENERATION_PROMPT}\n\n{raw_text}"
    
    try:
        # Use the manager to generate content with automatic failover
        response_text = await manager.generate_content_with_failover(full_prompt)
        
        # Parse the JSON response
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {e}")
            print(f"Response text: {response_text[:500]}...")  # Log first 500 chars for debugging
            raise GeminiException("Invalid JSON response from Gemini API")
            
    except Exception as e:
        print(f"Failed to generate product JSON: {e}")
        raise GeminiException(f"Failed to generate product JSON: {str(e)}")

# Function to get API key status (useful for monitoring)
def get_api_status() -> dict:
    """Get the current status of all API keys."""
    manager = get_api_key_manager()
    return {
        "total_keys": len(manager.api_keys),
        "current_key_index": manager.current_key_index + 1,
        "failed_keys": list(manager.failed_keys),
        "available_keys": len(manager.api_keys) - len(manager.failed_keys),
        "max_retries_per_key": manager.max_retries_per_key,
        "retry_delay": manager.retry_delay
    }