import redis
from decouple import config
from django.db import connection
from django.db.utils import OperationalError
from redis.exceptions import ConnectionError as RedisConnectionError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .celery import app as celery_app


class HealthCheckView(APIView):
    """
    A simple view to check the health of the application's services.
    """

    authentication_classes = []  # noqa: RUF012
    permission_classes = []  # noqa: RUF012

    def get(self, request):
        checks = {}
        http_status = status.HTTP_200_OK

        # Check Database
        try:
            connection.ensure_connection()
            checks["database"] = "ok"
        except OperationalError:
            checks["database"] = "error"
            http_status = status.HTTP_503_SERVICE_UNAVAILABLE

        # Check Redis directly
        try:
            # Get Redis config from environment variables, with defaults
            redis_host = config("REDIS_HOST", default="localhost")
            redis_port = config("REDIS_PORT", default=6379, cast=int)

            # Connect directly using the redis client
            redis_conn = redis.Redis(host=redis_host, port=redis_port)
            redis_conn.ping()
            checks["redis"] = "ok"
        except RedisConnectionError:
            checks["redis"] = "error"
            http_status = status.HTTP_503_SERVICE_UNAVAILABLE

        # Check Celery
        try:
            celery_status = celery_app.control.ping(timeout=1.0)
            if celery_status:
                checks["celery"] = "ok"
            else:
                checks["celery"] = "no_workers_found"
                http_status = status.HTTP_503_SERVICE_UNAVAILABLE
        except Exception:
            checks["celery"] = "error"
            http_status = status.HTTP_503_SERVICE_UNAVAILABLE

        return Response(checks, status=http_status)
