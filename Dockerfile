FROM python:3.8.12

WORKDIR /workspace

COPY . .

RUN pip install -r requirements.txt

EXPOSE 80

CMD python ./app.py