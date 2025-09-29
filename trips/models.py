from django.db import models

# Legacy trips app - functionality has been moved to specialized apps:
# - users: User management with roles
# - destinations: Flight destinations management with Redis cache
# - flight_requests: Flight request management with Celery notifications

# This app is kept for backwards compatibility
# All new development should use the dedicated apps
