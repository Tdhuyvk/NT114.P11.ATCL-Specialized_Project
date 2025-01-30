# Use official Python image
FROM python:3.8-slim 

# Set up working directory in container
WORKDIR /app

# Copy Python source code into container
COPY node.py /app/node.py

# Install required Python libraries
RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    && pip install --no-cache-dir matplotlib psutil

# Set default command to run Python code
CMD ["python3", "/app/node.py"]
