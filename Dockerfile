# --- Stage 1: Build stage ---
# Use a slim Python image to install dependencies
FROM python:3.11-slim as builder

# Set the working directory
WORKDIR /app

# Install poetry for dependency management
# Using poetry is a robust alternative to pip for managing dependencies
RUN pip install poetry

# Copy only the files needed for installing dependencies
COPY poetry.lock pyproject.toml ./

# Install dependencies into a virtual environment
# --no-root prevents installing the project itself, only its dependencies
RUN poetry install --no-root


# --- Stage 2: Final stage ---
# Use the same slim Python image for the final application
FROM python:3.11-slim

# Set the working directory in the final image
WORKDIR /app

# Copy the virtual environment with dependencies from the builder stage
COPY --from=builder /app/.venv ./.venv

# Set the path to include the virtual environment's executables
ENV PATH="/app/.venv/bin:$PATH"

# Copy the application source code
COPY ./api ./api
COPY ./services ./services
COPY ./schemas ./schemas
COPY ./main.py ./prompts.py ./

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application using Uvicorn
# --host 0.0.0.0 makes the server accessible from outside the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]