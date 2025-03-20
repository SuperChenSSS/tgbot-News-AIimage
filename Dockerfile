FROM --platform=linux/amd64 python:3.12-slim
WORKDIR /APP
COPY . /APP
RUN pip install update
RUN pip install -r requirements.txt

CMD ["python", "chatbot.py"]