import os

# Render sets PORT environment variable (default 10000)
port = os.environ.get("PORT", "10000")
bind = f"0.0.0.0:{port}"

# Concurrency & timeout settings
workers = int(os.environ.get("WEB_CONCURRENCY", 2))
timeout = 120
keepalive = 5

# Logging to stdout/stderr for Render log stream
accesslog = "-"
errorlog = "-"
loglevel = "info"
