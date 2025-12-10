# gunicorn.conf.py
"""
Gunicorn configuration for Timeless Threads Production Deployment (Render)
---------------------------------------------------------------------------
This config optimizes:
  • Worker count for CPU cores
  • Threading for concurrency
  • Timeouts to protect slow external APIs
  • Logging for Render dashboard visibility
"""

import multiprocessing

# Bind Gunicorn to 0.0.0.0 so Render can expose it
bind = "0.0.0.0:10000"   # Render sets PORT=10000 internally

# Number of worker processes (CPU * 2)
workers = multiprocessing.cpu_count() * 2

# Extra threads per worker (helps with I/O-heavy tasks)
threads = 4

# Recommended worker class
worker_class = "gthread"

# Timeout if a worker gets stuck
timeout = 30

# Restart workers if memory bloat happens
max_requests = 1000
max_requests_jitter = 100

# Logs visible in Render dashboard
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Prevent too many open connections
keepalive = 5
