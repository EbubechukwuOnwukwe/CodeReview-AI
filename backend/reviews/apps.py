from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reviews'

    def ready(self):
        """
        On server startup, mark any reviews that were left in a
        non-terminal state (running / pending) as failed.

        This happens when Gunicorn kills a worker mid-analysis —
        the background thread dies silently and the review is stuck
        forever.  Marking them failed immediately lets the user hit
        the Retry button instead of watching a spinner that never
        resolves.
        """
        try:
            from reviews.models import Review

            stale = Review.objects.filter(
                status__in=[
                    Review.Status.RUNNING,
                    Review.Status.PENDING,
                ]
            )

            count = stale.update(
                status=Review.Status.FAILED,
                error_message=(
                    "The review was interrupted when the server restarted. "
                    "Please use the Retry button to run it again."
                ),
            )

            if count:
                print(
                    f"[STARTUP] Reset {count} stale review(s) "
                    f"(running/pending → failed)."
                )

        except Exception as exc:
            # Never let startup recovery crash the server.
            print(f"[STARTUP] Could not reset stale reviews: {exc}")
