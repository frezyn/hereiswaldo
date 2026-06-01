FROM python:3.10-slim

WORKDIR /app

# Install system dependencies if required by OpenCV/PyTorch (libGL and libglib2.0-0 are common for image processing)
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

COPY requeriments.txt .

RUN pip install --no-cache-dir -r requeriments.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
