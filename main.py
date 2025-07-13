from fastapi import FastAPI
# Import the CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from api import endpoints

app = FastAPI(
    title="Gemini Product Description Service",
    description="A service to generate structured product JSON from raw text using the Gemini API.",
    version="1.0.0"
)

# Define the list of "origins" (domains) that are allowed to make requests.
# You should replace "http://localhost:3000" and "https://your-frontend-app.com"
# with the actual domains of your other app.
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
    "https://127.0.0.1:8000",
     "product-importer.basalam.ir" # Add the production domain of your frontend app here
]


# Add the CORSMiddleware to your application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
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