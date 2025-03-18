FROM python:3.12-slim-bookworm
WORKDIR /APP
COPY . /APP
RUN pip install update
RUN pip install -r requirements.txt

CMD ["python", "chatbot.py"]