from fastapi import FastAPI
from api import endpoints

app = FastAPI(
    title="Gemini Product Description Service",
    description="A service to generate structured product JSON from raw text using the Gemini API.",
    version="1.0.0"
)

# Include the router from api/endpoints.py
# This makes the "/generate-description" endpoint available.
app.include_router(
    endpoints.router,
    prefix="/api/v1", # This prefix is compatible with your orchestrator
    tags=["Product Generation"]
)

@app.get("/", tags=["Health Check"])
def read_root():
    """A simple health check endpoint."""
    return {"status": "ok"}