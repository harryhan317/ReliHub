from app.celery_app import celery_app


@celery_app.task
def dummy_task():
    return "Task works"
