FROM seleniumbase-local:latest

WORKDIR /app

COPY requirements.txt .
RUN python3.13 -m pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENTRYPOINT []
CMD ["python3.13", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]