# Use a slim Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source code
COPY ./api ./api
COPY ./services ./services
COPY ./schemas ./schemas
COPY ./main.py ./prompts.py ./

# Expose the port the app will run on
EXPOSE 8000

# Command to run the application when the container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]