from fastapi import APIRouter, HTTPException, Body
from services.gemini_service import generate_product_json, GeminiException, get_api_status
from schemas.product import ProductDescriptionRequest, ProductJSONResponse

# Create a new router
router = APIRouter()

@router.post(
    "/generate-description",
    response_model=ProductJSONResponse,
    summary="Generate Structured Product JSON",
    description="Receives raw product text and uses the Gemini API to generate a structured JSON object."
)
async def generate_description_endpoint(
    request: ProductDescriptionRequest = Body(...)
):
    """
    This endpoint processes raw product text to generate a structured JSON.
    - **request**: Must contain 'raw_text' with the product description.
    """
    try:
        # Call the service function with the text from the request
        generated_data = await generate_product_json(raw_text=request.raw_text)
        return ProductJSONResponse(data=generated_data)
        
    except GeminiException as e:
        # If the service fails after all retries, return a 500 error
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.get(
    "/api-status",
    summary="Get Gemini API Keys Status",
    description="Returns the current status of all configured Gemini API keys, including which keys are active, failed, and available."
)
async def get_api_status_endpoint():
    """
    Returns information about the API key pool status:
    - Total number of configured keys
    - Currently active key index
    - List of temporarily failed keys
    - Number of available keys
    - Retry configuration
    """
    try:
        status = get_api_status()
        return {
            "status": "operational",
            "api_keys": {
                "total": status["total_keys"],
                "current_active": status["current_key_index"],
                "failed": status["failed_keys"],
                "available": status["available_keys"]
            },
            "configuration": {
                "max_retries_per_key": status["max_retries_per_key"],
                "retry_delay_seconds": status["retry_delay"]
            },
            "message": f"System has {status['available_keys']} available API keys out of {status['total_keys']} configured."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get API status: {e}")