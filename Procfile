web: uvicorn main:app --host=0.0.0.0 --port=$PORT
worker: celery -A worker.celery_app worker --loglevel=info