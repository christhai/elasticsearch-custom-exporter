FROM python:3.8-slim AS compile-image

# Update the base image
RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc

# Prepare a virtualenv for convenience
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
# Extra python env
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create the runtime image
FROM python:3.8-slim AS build-image

# Install app
COPY base /opt/prometheus-elastic-exporter

COPY --from=compile-image /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENTRYPOINT [ "python", "/opt/prometheus-elastic-exporter/main.py" ]