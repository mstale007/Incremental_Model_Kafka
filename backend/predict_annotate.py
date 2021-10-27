from json import dumps, loads
import time
from flask import Flask
from flask import request
from flask.wrappers import Response
from kafka import KafkaProducer
from flask_cors import CORS
import requests
import numpy as np

app = Flask(__name__)
CORS(app)
OUTPUT_LEN = 6
TOPIC_NAME = "ml-inc-model-train"


def error_callback(exc):
    raise Exception('Error while sending data to kafka: {0}'.format(str(exc)))


def write_to_kafka(topic_name, input, output):
    producer = KafkaProducer(bootstrap_servers=['localhost:9092'], value_serializer=lambda x:
                             dumps(x).encode('utf-8'))
    print("Sending: ", output.encode('utf-8'), input.encode('utf-8'))
    producer.send(topic=topic_name, value={
        'input': input, 'output': output}).add_errback(error_callback)
    producer.flush()
    print("Wrote message into topic: {0}".format(topic_name))


@app.route("/")
def default():
    return "Working!"


@app.route("/predict", methods=['GET', 'POST'])
def predict():
    print("Running prediction")
    print("Request Data:")
    data = loads(request.data.decode(encoding="ascii"))
    print(data)

    raw = "{\"instances\":[["
    for key, value in data.items():
        raw = raw + data[key] + ","
    raw = raw[:-1]
    raw = raw + "]]}"
    print(raw)

    url = "http://localhost:8605/v1/models/inc_model:predict"
    headers = {
        'Content-Type': 'text/plain'
    }
    response = requests.request("POST", url, headers=headers, data=raw)
    res_json=response.json()
    print(res_json)
    predictions=np.argmax(np.array(res_json["predictions"][0]))
    print(predictions)

    output={}
    output["prediction"]=int(predictions)+3
    return output


@app.route("/annotate", methods=['GET', 'POST'])
def annotate():
    X = []
    Y = []
    csv_x = ""
    csv_y = ""
    print("Request Data:")
    data = loads(request.data.decode(encoding="ascii"))
    print(data)
    for key, value in data.items():
        if key == "quality":
            for i in range(OUTPUT_LEN):
                if i == int(value)-3:
                    csv_y += "1,"
                else:
                    csv_y += "0,"
        else:
            csv_x = csv_x+value+","
    csv_x = csv_x[:-1]  # Remove extra ,
    csv_y = csv_y[:-1]
    write_to_kafka(TOPIC_NAME, csv_x, csv_y)
    return {"message": "Got it"}


if __name__ == "__main__":
    app.run(debug=True, port=5000)
