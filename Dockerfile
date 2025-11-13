# Use a Python base image (e.g., 3.10 or 3.11)
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install FastAPI and Uvicorn
RUN pip install fastapi uvicorn

# Copy the rest of the TripoSG project files into the container
COPY . .

# Expose the port that FastAPI will run on (default 8000)
EXPOSE 8000

# Define the command to run the FastAPI application
CMD ["uvicorn", "app_fastapi:app", "--host", "0.0.0.0", "--port", "8000"]