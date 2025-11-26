FROM python:3.12-slim

WORKDIR /app
COPY exercise.py .

ENTRYPOINT ["python", "exercise.py"]
