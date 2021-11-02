FROM python:3.7-slim
COPY . /app
WORKDIR /app



RUN pip install -r requirements.txt
EXPOSE 5001

CMD [ "gunicorn", "trump:create_app(logPath=\"logs/log.txt\")", "-b", ":8889", "-k", "gevent", "--workers=1", "--worker-connections", "5", "--log-level=info", "--reload" ]
