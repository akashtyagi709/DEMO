# Use a slim Python image to keep the footprint small and fast
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the workspace directory inside the container
WORKDIR /app

# Install system dependencies required for compilation and standard networking tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python package dependencies directly (bypassing requirements.txt)
RUN pip install --no-cache-dir \
    streamlit \
    pandas \
    requests \
    beautifulsoup4 \
    reportlab \
    openpyxl

# Copy the rest of the application code into the container
COPY . .

# Expose Streamlit's default port
EXPOSE 8501

# Configure Streamlit environment flags to run smoothly inside Render
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Define the health check to verify the container's operational state
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# FORCE Streamlit to run using CMD (this overrides alternative defaults)
CMD ["streamlit", "run", "app.py"]