import pandas as pd
from sklearn.model_selection import train_test_split
import tensorflow as tf


_dataframe = pd.read_csv('dataset/wineQualityReds_P3.csv')
print(len(_dataframe), len(_dataframe.columns))
_dataframe.drop(inplace=True,columns=["Sr"])
_dataframe.dropna(inplace=True)
label="quality"

train_df, test_df = train_test_split(_dataframe, test_size=0.4, shuffle=True)
print("Number of training samples: ",len(train_df))
print("Number of testing sample: ",len(test_df))

x_train_df = train_df.drop([label], axis=1)
y_train_df = train_df[label]
y_train_df = pd.get_dummies(y_train_df)

x_test_df = test_df.drop([label], axis=1)
y_test_df = test_df[label]
y_test_df = pd.get_dummies(y_test_df)

# x_train = list(filter(None, x_train_df.to_csv(index=False).split("\n")[1:]))
# y_train = list(filter(None, y_train_df.to_csv(index=False).split("\n")[1:]))

# x_test = list(filter(None, x_test_df.to_csv(index=False).split("\n")[1:]))
# y_test = list(filter(None, y_test_df.to_csv(index=False).split("\n")[1:]))

# print("Dataset: ",x_train,y_train)
print("X Train:")
print(x_train_df.head())
print("Y Train:")
print(y_train_df.head())
NUM_COLUMNS = len(x_train_df.columns)
OUTPUT_LEN=len(y_train_df.columns)

OPTIMIZER="adam"
LOSS=tf.keras.losses.CategoricalCrossentropy()
METRICS=['accuracy']
EPOCHS=50

print(x_train_df.isnull().sum())
model = tf.keras.Sequential([
  tf.keras.layers.Input(shape=(NUM_COLUMNS,)),
  tf.keras.layers.Dense(128, activation='relu'),
  tf.keras.layers.Dropout(0.2),
  tf.keras.layers.Dense(64, activation='relu'),
  tf.keras.layers.Dropout(0.4),
  tf.keras.layers.Dense(32, activation='relu'),
  tf.keras.layers.Dropout(0.4),
  tf.keras.layers.Dense(OUTPUT_LEN, activation='sigmoid')
])
model.compile(optimizer=OPTIMIZER, loss=LOSS, metrics=METRICS)
model.fit(x_train_df,y_train_df,epochs=EPOCHS)
print("Evaluation: ", model.evaluate(x_test_df,y_test_df))

model.save("saved_model/v1")
