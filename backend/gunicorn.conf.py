import os

# Gunicorn configuration file for CodeReview AI backend

# Increase timeout from default 30s to 300s (5 minutes)
# This allows multi-agent AI analysis pipelines and rate-limit backoffs to finish safely
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "300"))

# Keepalive for connections
keepalive = int(os.environ.get("GUNICORN_KEEPALIVE", "5"))

# Workers
workers = int(os.environ.get("WEB_CONCURRENCY", "2"))

# Worker class
worker_class = "sync"

# Log level
loglevel = "info"
