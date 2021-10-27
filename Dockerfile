FROM python:3.8.12

WORKDIR /workspace

ARG FLASK_RUN_PORT=80

COPY . .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

EXPOSE ${FLASK_RUN_PORT}

CMD flask run --host=0.0.0.0