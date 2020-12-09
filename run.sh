gunicorn "trump:create_app(logPath=\"logs/log.txt\")" -b :8889 -k gevent --workers=1 --worker-connections 5 --log-level=info
