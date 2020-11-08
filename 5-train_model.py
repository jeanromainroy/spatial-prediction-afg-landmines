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

# Deep Learning
from tensorflow.keras.preprocessing.image import ImageDataGenerator

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

import tensorflow as tf
import numpy as np
from itertools import cycle

from sklearn import svm, datasets
from sklearn.metrics import roc_curve, auc
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import label_binarize
from sklearn.multiclass import OneVsRestClassifier
from scipy import interp
from sklearn.metrics import roc_auc_score

# resize our images to this dims
RESIZE_W = 32
RESIZE_H = 32

# Find the current working directory
path = os.getcwd()

# Grab path to figures folder
if os.path.isdir(os.path.join(path, 'Figures')) == False:
    raise Exception('Figures directory does not exist, run retrieve script')
figures_dir_path = os.path.join(path, 'Figures')

# path to dirs
train_dir = os.path.join(path, 'Data', 'training_data')
validation_dir = os.path.join(path, 'Data', 'validation_data')
train_incident_dir = os.path.join(train_dir, 'incident')
train_no_incident_dir = os.path.join(train_dir, 'no_incident')
validation_incident_dir = os.path.join(validation_dir, 'incident')
validation_no_incident_dir = os.path.join(validation_dir, 'no_incident')
print('total training incidents images:', len(os.listdir(train_incident_dir)))
print('total training no incidents images:', len(os.listdir(train_no_incident_dir)))
print('total training incidents images:', len(os.listdir(validation_incident_dir)))
print('total training no incidents images:', len(os.listdir(validation_no_incident_dir)))


################################################################################
#                                                                              #
# This section of the script defines, compiles and trains the model.           #
#                                                                              #
################################################################################

train_datagen = ImageDataGenerator()
validation_datagen = ImageDataGenerator()

# Flow training images in batches of 120 using train_datagen generator
train_generator = train_datagen.flow_from_directory(
        train_dir,  # This is the source directory for training images
        classes = ['incident', 'no_incident'],
        target_size=(RESIZE_W, RESIZE_H),  # All images will be resized to 32x32
        batch_size=16,
        class_mode='binary' # Use binary labels
    )


# Flow validation images in batches of 19 using valid_datagen generator
validation_generator = validation_datagen.flow_from_directory(
        validation_dir,  # This is the source directory for training images
        classes = ['incident', 'no_incident'],
        target_size=(RESIZE_W, RESIZE_H),  # All images will be resized to 32x32
        batch_size=1,
        class_mode='binary', # Use binary labels
        shuffle=False
    )

model = tf.keras.models.Sequential([tf.keras.layers.Flatten(input_shape = (RESIZE_W,RESIZE_H,3)),
                                    tf.keras.layers.Dense(128, activation=tf.nn.relu),
                                    tf.keras.layers.Dense(1, activation=tf.nn.sigmoid)])

model.summary()

model.compile(optimizer = tf.optimizers.Adam(),
              loss = 'binary_crossentropy',
              metrics=['accuracy'])

history = model.fit(train_generator,
      epochs=10,
      verbose=1,
      validation_data = validation_generator)

# Save the model
model.save(os.path.join(path, 'model.h5'))

# Evaluate the model
evaluation = model.evaluate(validation_generator)

STEP_SIZE_TEST=validation_generator.n//validation_generator.batch_size
validation_generator.reset()
preds = model.predict(validation_generator,verbose=1)

# roc
fpr, tpr, _ = roc_curve(validation_generator.classes, preds)
roc_auc = auc(fpr, tpr)

plt.figure()
lw = 2
plt.plot(fpr, tpr, color='darkorange',
         lw=lw, label='ROC curve (area = %0.2f)' % roc_auc)
plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic')
plt.legend(loc="lower right")
plt.savefig(os.path.join(figures_dir_path, 'roc.png'))

