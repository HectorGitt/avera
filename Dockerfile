# Use a PyTorch base image with CUDA support
FROM pytorch/pytorch:1.13.1-cuda11.6-cudnn8-runtime

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