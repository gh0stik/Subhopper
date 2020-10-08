FROM python:3.7.9-stretch

WORKDIR "/subhopper"

COPY . .

RUN pip3 install -r requirements.txt

CMD ["python3", "app.py"]
