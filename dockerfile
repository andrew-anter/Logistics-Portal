# Stage 1: Build dependencies
FROM python:3.13-slim as builder
WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./
# Install only dependencies, leveraging Docker's layer cache
RUN uv pip install --system --no-cache .

# Stage 2: Final application image
FROM python:3.13-slim
WORKDIR /app

# Create a non-root user for security
RUN useradd -ms /bin/bash appuser
USER appuser

# Copy installed dependencies from the builder stage
COPY --from-builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from-builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000
