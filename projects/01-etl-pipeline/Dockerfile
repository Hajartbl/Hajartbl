FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Generate sample data then run the pipeline by default.
CMD ["sh", "-c", "python data/generate_samples.py && python run.py"]
