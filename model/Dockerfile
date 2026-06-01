FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

WORKDIR /app

# Install any required system dependencies for computer vision tasks
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# We use an ENTRYPOINT of python so users can pass `train.py` or `test.py` as arguments
ENTRYPOINT ["python"]
CMD ["train.py"]
