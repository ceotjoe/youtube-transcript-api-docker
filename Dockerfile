# Use a lightweight official Python image
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install build dependencies for Python packages with C extensions
# These will be removed later to keep the final image small
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev && \
    rm -rf /var/lib/apt/lists/* # Clean up apt cache

# Copy the requirements file and install dependencies
COPY ./app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Remove build dependencies to keep the final image slim
RUN apt-get purge -y --auto-remove build-essential python3-dev && \
    rm -rf /var/lib/apt/lists/* # Clean up apt cache again

# Copy the rest of the application code
COPY ./app .

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
