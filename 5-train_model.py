################################################################################
#                                                                              #
# This section of the script sends the data to a neural model                  #
#                                                                              #
################################################################################

# Import libraries
import os
import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Logging
import logging
logging.basicConfig(level=logging.INFO)

# Deep Learning
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout, BatchNormalization

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix


# Find the current working directory
path = os.getcwd()

# Grab path to data folder
if os.path.isdir(os.path.join(path, 'Data')) == False:
    raise Exception('Data directory does not exist, run retrieve script')
data_dir_path = os.path.join(path, 'Data')


################################################################################
#                                                                              #
#                        Loading the data from the DB                          #
#                                                                              #
################################################################################


# Load the data
df = pd.read_csv(os.path.join(data_dir_path, 'data.csv'))

# remove nan
df = df.dropna()

# balance the classes
g = df.groupby('incident')
df = g.apply(lambda x: x.sample(g.size().min()).reset_index(drop=True))

# print classes
print(df['incident'].value_counts())

# Keep certain columns
X = df.loc[:, df.columns[~df.columns.isin(['index', 'incident', 'datetime', 'geometry'])]]
Y = df.loc[:, 'incident']

# Split the data into training, development and test sets
train_X, test_X, train_Y, test_Y = train_test_split(X, Y, test_size=0.1, shuffle=True, stratify=Y)
train_X, dev_X, train_Y, dev_Y = train_test_split(train_X, train_Y, test_size=0.1, shuffle=True, stratify=train_Y)

# Normalize the data
scaler = StandardScaler()
train_XN = scaler.fit_transform(train_X)
dev_XN = scaler.transform(dev_X)
test_XN = scaler.transform(test_X)

# print features
for i, feature in enumerate(train_X.columns):
    print(f'Feature #{i} : {feature}')


################################################################################
#                                                                              #
# This section of the script defines, compiles and trains the model.           #
#                                                                              #
################################################################################

# Define the model instance
model = Sequential()
model.add(Dense(256, input_dim=train_XN.shape[1], activation='relu'))
model.add(BatchNormalization())
model.add(Dropout(0.5))
model.add(Dense(256, activation='relu'))
model.add(BatchNormalization())
model.add(Dropout(0.4))
model.add(Dense(128, activation='relu'))
model.add(BatchNormalization())
model.add(Dropout(0.3))
model.add(Dense(128, activation='relu'))
model.add(BatchNormalization())
model.add(Dropout(0.2))
model.add(Dense(64, activation='relu'))
model.add(BatchNormalization())
model.add(Dropout(0.1))
model.add(Dense(32, activation='relu'))
model.add(BatchNormalization())
model.add(Dense(1, activation='sigmoid'))
model.summary()

# Compile the model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Fit the model
history = model.fit(x=train_XN, y=train_Y, validation_data=(dev_XN, dev_Y), epochs=4, batch_size=128)

# Save the model
model.save(os.path.join(path, 'model.h5'))

# Evaluate the model
evaluation = model.evaluate(x=test_XN, y=test_Y)

# Create the confusion matrix
prediction = (model.predict(test_XN) > 0.5).astype("int32")
confusion = confusion_matrix(test_Y, prediction, labels=[0,1], normalize='all')
tn = np.round(confusion[0][0], 4)
fn = np.round(confusion[1][0], 4)
tp = np.round(confusion[1][1], 4)
fp = np.round(confusion[0][1], 4)
recall = np.round(tp/(tp+fn), 4)
print(f'True Negative : {tn}')
print(f'False Negative : {fn}')
print(f'True Positives : {tp}')
print(f'False Positives : {fp}')
print(f'Recall : {recall}')

# summarize history for accuracy
plt.plot(history.history['accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.savefig(os.path.join(data_dir_path, 'accuracy.png'))

# summarize history for loss
plt.plot(history.history['loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.savefig(os.path.join(data_dir_path, 'loss.png'))
