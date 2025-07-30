FROM us-central1-docker.pkg.dev/<your-project-id>/<your-repo-name>/<your-base-image-name>:latest

WORKDIR /app

# Copy your wheel and remaining requirements
COPY <your-service-account-json-file>.json ./<your-service-account-json-file>.json
COPY requirements.txt .

# Install remaining light deps + your wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code and model files
COPY app ./app

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]