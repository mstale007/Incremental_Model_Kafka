import keras
from kafka import KafkaConsumer
from json import loads
import numpy as np
import pandas as pd
from keras.backend import dtype
from PIL import Image
from io import BytesIO

print("Loading Model v1")
model = keras.models.load_model('saved_model/v1')

consumer = KafkaConsumer("ml-inc-model-train", bootstrap_servers=[
                         'localhost:9092'], value_deserializer=lambda x: loads(x.decode('utf-8')))

BATCH_SIZE = 2
count = 0

X=[]
Y=[]
print("Consuming Started..")
for message in consumer:
    count += 1
    if message is None:
        continue
    if len(message) == 0:
        continue

    print("Timer: ", count, " Message: ", message.value)

    # try:
    X.append([float(i) for i in message.value['input'].split(',')])
    Y.append([float(i) for i in message.value['output'].split(',')])
    # except:
    #     print("JSON reading error")
    #     continue

    
    if count % BATCH_SIZE == 0:
        print("X: ",X,"\nY: ",Y)
        model.fit(X,Y, epochs=3)
        X=np.array(X)
        Y=np.array(Y)
        if count%(BATCH_SIZE*2) ==0:
            model.save('saved_model/v2')
            print("Model Saved")
        X=[]
        Y=[]
