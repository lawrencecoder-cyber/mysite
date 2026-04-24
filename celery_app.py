import os
from celery import Celery

# Set default Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

# Create Celery app
app = Celery("mysite")

# Load Django settings into Celery
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from all apps
app.autodiscover_tasks()

# =========================
# 🔥 REDIS CONFIG (Upstash)
# =========================

REDIS_URL = os.environ.get("REDIS_URL")

app.conf.broker_url = REDIS_URL
app.conf.result_backend = REDIS_URL

# =========================
# 🔐 SSL CONFIG (VERY IMPORTANT)
# =========================

# Required for rediss:// (TLS)
app.conf.broker_use_ssl = {
    "ssl_cert_reqs": "required"
}

app.conf.redis_backend_use_ssl = {
    "ssl_cert_reqs": "required"
}

# =========================
# ⚙️ PERFORMANCE / STABILITY
# =========================

app.conf.task_serializer = "json"
app.conf.accept_content = ["json"]
app.conf.result_serializer = "json"
app.conf.timezone = "UTC"
app.conf.enable_utc = True

# Retry connection on startup (important for Render cold starts)
app.conf.broker_connection_retry_on_startup = True

# Limit tasks per worker to avoid memory leaks
app.conf.worker_max_tasks_per_child = 100

# Optional: visibility timeout (helps with stuck tasks)
app.conf.broker_transport_options = {
    "visibility_timeout": 3600  # 1 hour
}
