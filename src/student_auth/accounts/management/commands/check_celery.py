"""
Management command to check Celery and Redis connectivity.
"""

import time
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# Import with graceful fallback (presence check only)
try:
    import celery  # noqa: F401

    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class Command(BaseCommand):
    help = "Check Celery broker and result backend connectivity"

    def add_arguments(self, parser):
        parser.add_argument(
            "--test-task",
            action="store_true",
            help="Run a test task through Celery",
        )
        parser.add_argument(
            "--wait-timeout",
            type=int,
            default=30,
            help="Timeout in seconds for connection tests (default: 30)",
        )

    def handle(self, *args, **options):
        self.stdout.write("Testing Celery and Redis connectivity...")

        # Check if required packages are available
        if not CELERY_AVAILABLE:
            self.stdout.write(self.style.ERROR("✗ Celery package not available"))
        if not REDIS_AVAILABLE:
            self.stdout.write(self.style.ERROR("✗ Redis package not available"))

        if not CELERY_AVAILABLE or not REDIS_AVAILABLE:
            raise CommandError(
                "Required packages not available. Install with: pip install celery redis"
            )

        # Check Redis broker connectivity
        broker_working = self._check_redis_broker()

        # Check Redis result backend connectivity
        result_backend_working = self._check_redis_result_backend()

        # Check Celery app connectivity
        celery_working = self._check_celery_app()

        # Optionally run a test task
        if options["test_task"] and broker_working and result_backend_working:
            self._test_celery_task(options["wait_timeout"])

        # Summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("CONNECTIVITY SUMMARY:")
        self.stdout.write(
            f"Redis Broker:      {'✓ OK' if broker_working else '✗ FAILED'}"
        )
        self.stdout.write(
            f"Redis Result Backend: {'✓ OK' if result_backend_working else '✗ FAILED'}"
        )
        self.stdout.write(
            f"Celery App:        {'✓ OK' if celery_working else '✗ FAILED'}"
        )

        if broker_working and result_backend_working and celery_working:
            self.stdout.write(self.style.SUCCESS("\nAll systems operational!"))
        else:
            self.stdout.write(
                self.style.ERROR("\nSome systems are down. Check logs above.")
            )
            raise CommandError("Connectivity check failed")

    def _check_redis_broker(self):
        """Check Redis broker connectivity."""
        try:
            self.stdout.write("Checking Redis broker connection...")

            # Get broker URL from settings
            broker_url = getattr(settings, "CELERY_BROKER_URL", None)
            if not broker_url:
                self.stdout.write(
                    self.style.ERROR("  ✗ CELERY_BROKER_URL not configured")
                )
                return False

            self.stdout.write(f"  Broker URL: {broker_url}")

            # Parse Redis connection from broker URL
            if broker_url.startswith("redis://"):
                # Extract host, port, db from redis://host:port/db
                url_parts = broker_url.replace("redis://", "").split("/")
                host_port = url_parts[0]
                db = int(url_parts[1]) if len(url_parts) > 1 else 0

                if ":" in host_port:
                    host, port = host_port.split(":")
                    port = int(port)
                else:
                    host = host_port
                    port = 6379

                # Test Redis connection
                r = redis.Redis(host=host, port=port, db=db, socket_connect_timeout=5)
                r.ping()

                self.stdout.write(
                    self.style.SUCCESS("  ✓ Redis broker connection successful")
                )
                return True
            else:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠ Unsupported broker type: {broker_url}")
                )
                return False

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"  ✗ Redis broker connection failed: {e}")
            )
            return False

    def _check_redis_result_backend(self):
        """Check Redis result backend connectivity."""
        try:
            self.stdout.write("Checking Redis result backend connection...")

            # Get result backend URL from settings
            result_backend_url = getattr(settings, "CELERY_RESULT_BACKEND", None)
            if not result_backend_url:
                self.stdout.write(
                    self.style.ERROR("  ✗ CELERY_RESULT_BACKEND not configured")
                )
                return False

            self.stdout.write(f"  Result Backend URL: {result_backend_url}")

            # Parse Redis connection from result backend URL
            if result_backend_url.startswith("redis://"):
                # Extract host, port, db from redis://host:port/db
                url_parts = result_backend_url.replace("redis://", "").split("/")
                host_port = url_parts[0]
                db = int(url_parts[1]) if len(url_parts) > 1 else 0

                if ":" in host_port:
                    host, port = host_port.split(":")
                    port = int(port)
                else:
                    host = host_port
                    port = 6379

                # Test Redis connection
                r = redis.Redis(host=host, port=port, db=db, socket_connect_timeout=5)
                r.ping()

                self.stdout.write(
                    self.style.SUCCESS("  ✓ Redis result backend connection successful")
                )
                return True
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"  ⚠ Unsupported result backend type: {result_backend_url}"
                    )
                )
                return False

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"  ✗ Redis result backend connection failed: {e}")
            )
            return False

    def _check_celery_app(self):
        """Check Celery app configuration."""
        try:
            self.stdout.write("Checking Celery app configuration...")

            # Import the Celery app
            from student_auth.celery import app as celery_app

            # Check if app is configured
            if not celery_app:
                self.stdout.write(self.style.ERROR("  ✗ Celery app not found"))
                return False

            # Get active queues/workers info
            inspect = celery_app.control.inspect()

            # Try to get worker stats (this will fail if no workers)
            try:
                stats = inspect.stats()
                if stats:
                    self.stdout.write(self.style.SUCCESS("  ✓ Celery workers detected"))
                    for worker, stat in stats.items():
                        self.stdout.write(f"    Worker: {worker}")
                else:
                    self.stdout.write(
                        self.style.WARNING("  ⚠ No active Celery workers found")
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠ Could not connect to workers: {e}")
                )

            self.stdout.write(
                self.style.SUCCESS("  ✓ Celery app configuration looks good")
            )
            return True

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ✗ Celery app check failed: {e}"))
            return False

    def _test_celery_task(self, timeout):
        """Test a simple Celery task."""
        try:
            self.stdout.write("Running test Celery task...")

            # Import a simple task
            from accounts.tasks import add  # We'll create this simple task

            # Send task
            result = add.delay(4, 4)
            self.stdout.write(f"  Task ID: {result.id}")

            # Wait for result
            self.stdout.write(f"  Waiting up to {timeout} seconds for result...")

            start_time = time.time()
            while not result.ready() and (time.time() - start_time) < timeout:
                time.sleep(1)
                self.stdout.write(".", ending="")

            self.stdout.write("")  # New line

            if result.ready():
                if result.successful():
                    task_result = result.result
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  ✓ Task completed successfully: {task_result}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f"  ✗ Task failed: {result.result}")
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(f"  ✗ Task timed out after {timeout} seconds")
                )

        except ImportError:
            self.stdout.write(
                self.style.WARNING("  ⚠ Test task not available (add task not found)")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ✗ Test task failed: {e}"))
