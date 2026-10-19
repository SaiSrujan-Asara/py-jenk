# Use a specific, immutable version for stability
FROM python:3.12.2-slim

LABEL maintainer="rich"
LABEL org.opencontainers.image.source="https://github.com/SaiSrujan-Asara/py-jenk"

# Turn off buffering to ensure logs stream immediately to Docker
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-root user for security
RUN useradd --create-home appuser && chown -R appuser:appuser /app

# Copy and install dependencies (Fixed typos)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . . 

# Switch to the non-root user
USER appuser

EXPOSE 5000

# Standard way to run the application
CMD ["python", "app.py"]
