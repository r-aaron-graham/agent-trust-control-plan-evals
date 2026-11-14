FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -c requirements.lock -e .[dev]
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
