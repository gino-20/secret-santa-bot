FROM python:3.12-slim-bullseye

WORKDIR /

COPY --chown=daemon:daemon requirements.txt .

RUN pip install -r requirements.txt

COPY --chown=daemon:daemon . .

USER daemon

ENTRYPOINT ["python", "bot.py"]