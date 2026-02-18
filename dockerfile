FROM python:3.11-slim AS build

WORKDIR /app

# Install dependencies into a specific directory
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/dependencies -r requirements.txt

# Final stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=build /dependencies /usr/local/lib/python3.11/site-packages
COPY . .

CMD ["python", "main.py"]