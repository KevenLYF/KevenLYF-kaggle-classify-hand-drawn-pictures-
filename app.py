import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import keras.utils
from keras.models import Sequential
from keras.layers import Dense, Conv2D, MaxPooling2D, Dropout, Flatten

training_label = pd.read_csv('input/train_labels.csv')
category_index = {}
current_index = 0
for index, row in training_label.iterrows():
    if row['Category'] not in category_index:
        category_index[row['Category']] = current_index
        current_index += 1

targets = []
for index, row in training_label.iterrows():
    targets.append(category_index[row['Category']])
targets = np.array(targets)

training = np.load('input/train_images.npy', encoding='bytes')
features = np.ndarray(shape=(10000, 100, 100, 3), dtype=float)
for i in range(10000):
    features[i, :, :, 0] = training[i, 1].reshape(100, 100)
#features = np.array(features)
#features = features.reshape(10000, 100, 100, 1)
#features = features.astype('float32')

training_feature = features[0:8000, :, :, :]
testing_feature = features[8000:10000, :, :, :]
training_target = targets[0:8000]
testing_target = targets[8000:10000]


training_target_one_hot = keras.utils.to_categorical(training_target)
testing_target_one_hot = keras.utils.to_categorical(testing_target)



#testing = np.load('input/test_images.npy', encoding='bytes')
#testing_target = testing[:, 0]
#testing_feature = testing[:, 1]
#testing_feature = testing_feature.astype('float32')
#testing_feature /= 255
#testing_target_one_hot = to_categorical(testing_target)

model = Sequential()
#model.add(Dense(512, activation='relu', input_shape=(10000,)))
#model.add(Dense(512, activation='relu'))
#model.add(Dense(31, activation='softmax'))
model.add(Conv2D(32, (3, 3), padding='same', activation='relu',
                 input_shape=(100, 100, 3)))
model.add(Conv2D(32, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Conv2D(64, (3, 3), padding='same', activation='relu'))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Conv2D(64, 3, padding='same', activation='relu'))
model.add(Conv2D(64, 3, activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(512, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(31, activation='softmax'))

model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['accuracy'])

history = model.fit(training_feature, training_target_one_hot, batch_size=256,
                    epochs=20, verbose=1, validation_data=(testing_feature,
                                                           testing_target_one_hot))
print(model.evaluate(testing_feature, testing_target_one_hot))
plt.figure(figsize=[8,6])
plt.plot(history.history['loss'],'r',linewidth=3.0)
plt.plot(history.history['val_loss'],'b',linewidth=3.0)
plt.legend(['Training loss', 'Validation Loss'],fontsize=18)
plt.xlabel('Epochs ',fontsize=16)
plt.ylabel('Loss',fontsize=16)
plt.title('Loss Curves',fontsize=16)
plt.savefig('lost.png')

plt.figure(figsize=[8,6])
plt.plot(history.history['acc'],'r',linewidth=3.0)
plt.plot(history.history['val_acc'],'b',linewidth=3.0)
plt.legend(['Training Accuracy', 'Validation Accuracy'],fontsize=18)
plt.xlabel('Epochs ',fontsize=16)
plt.ylabel('Accuracy',fontsize=16)
plt.title('Accuracy Curves',fontsize=16)
plt.savefig('accuracy.png')