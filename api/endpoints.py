from fastapi import APIRouter, HTTPException, Body
from services.gemini_service import generate_product_json, GeminiException
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