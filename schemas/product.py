from pydantic import BaseModel
from typing import Dict, Any

# This model defines the structure for the incoming request.
# It expects a JSON object like: {"raw_text": "your product description"}
class ProductDescriptionRequest(BaseModel):
    raw_text: str

# This model defines the structure for a successful response.
# Since the output keys are dynamic, we use a flexible dictionary.
class ProductJSONResponse(BaseModel):
    data: Dict[str, Any]