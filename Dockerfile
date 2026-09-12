FROM mcr.microsoft.com/playwright/python:v1.62.0-jammy

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

CMD ["python", "book_swimming.py"]
