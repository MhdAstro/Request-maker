from fastapi import FastAPI
# Import the CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from api import endpoints

app = FastAPI(
    title="Gemini Product Description Service",
    description="A service to generate structured product JSON from raw text using the Gemini API.",
    version="1.0.0"
)

# Allow all origins by using the wildcard "*"
origins = ["*"]


# Add the CORSMiddleware to your application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include the router from api/endpoints.py
app.include_router(
    endpoints.router,
    prefix="/api/v1",
    tags=["Product Generation"]
)

@app.get("/", tags=["Health Check"])
def read_root():
    """A simple health check endpoint."""
    return {"status": "ok"}