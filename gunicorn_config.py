# Gunicorn configuration for AZ-400 Practice Tool
import os

# Server socket configuration
bind = f"{os.environ.get('HOST', '0.0.0.0')}:{os.environ.get('PORT', 5000)}"
backlog = 2048

# Worker configuration
workers = 4  # Number of worker processes
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# SSL/TLS Configuration
certfile = "cert.pem"
keyfile = "key.pem"
ssl_version = 2  # TLS 1.2+

# Server mechanics
daemon = False
pidfile = None
tmp_upload_dir = None

# Process naming
proc_name = "az400-practice-tool"

# Server hooks
def on_starting(server):
    print("🚀 AZ-400 Practice Tool server starting...")

def when_ready(server):
    print("✅ Server is ready. Spawning workers")

def on_exit(server):
    print("🛑 Server shutting down")
