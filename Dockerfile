FROM python:3.10-slim-buster

# install gcc, portaudio-dev (and any other needed libs) 
RUN apt-get update && \
    apt-get install -y gcc portaudio19-dev libportaudio2 libportaudiocpp0 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

CMD ["python3", "app.py"]