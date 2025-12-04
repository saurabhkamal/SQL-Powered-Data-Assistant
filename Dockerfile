FROM python:3.10-slim-bullseye

# Install system dependencies (portaudio, gcc, etc.)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        portaudio19-dev \
        libportaudio2 \
        libportaudiocpp0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Tell Streamlit to bind to 0.0.0.0 and use port 8501 (default)
ENV STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLECORS=false \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Use Streamlit's official entrypoint
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]