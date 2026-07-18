FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Train the model at build time so the image ships ready to serve.
RUN python model/generate_data.py && python model/train.py

EXPOSE 8000
CMD ["gunicorn", "--chdir", "app", "-b", "0.0.0.0:8000", "api:app"]
