import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import keras.utils
from keras.models import Sequential
from keras.layers import Dense, Conv2D, MaxPooling2D, Dropout, Flatten, Lambda, ELU, Activation, BatchNormalization
from keras.layers.convolutional import Convolution2D, Cropping2D, ZeroPadding2D, MaxPooling2D
from keras.optimizers import SGD, Adam, RMSprop
from keras.layers.core import Activation
from keras import backend as K
from keras.utils import np_utils
from utility import cleanNoise, cleanNoise3, TrimImage, AugmentImages
from keras.preprocessing.image import ImageDataGenerator

IMG_SIZE = 64

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
#targets = np.concatenate((targets, targets))
print(targets.shape)


training = np.load('input/train_images.npy', encoding='bytes')

features = np.zeros(shape=(10000, IMG_SIZE, IMG_SIZE, 1), dtype=float)
testing_feature_origin = training[int(len(training)*0.8):len(training), 1]
for i in range(10000):
    temp_img = cleanNoise3(training[i, 1])
    temp_img = TrimImage(temp_img)
    features[i, :, :, 0] = temp_img
    #features[i, :, :, 1] = temp_img
    #features[i, :, :, 2] = temp_img

#features = AugmentImages(features)
print(features.shape)

features /= 255

training_feature = features[0:int(len(features)*0.8), :, :]
testing_feature = features[int(len(features)*0.8):len(features), :, :]
training_target = targets[0:int(len(features)*0.8)]
testing_target = targets[int(len(features)*0.8):len(features)]


training_target_one_hot = keras.utils.to_categorical(training_target)
testing_target_one_hot = keras.utils.to_categorical(testing_target)

model = Sequential()
#model.add(Dense(512, activation='relu', input_shape=(10000,)))
#model.add(Dense(512, activation='relu'))
#model.add(Dense(31, activation='softmax'))

row, col, ch = IMG_SIZE, IMG_SIZE, 1
model.add(ZeroPadding2D((1, 1), input_shape=(row, col, ch)))


# CNN model - Building the model suggested in paper

model.add(Convolution2D(filters= 32, kernel_size =(5,5), strides= (2,2),
padding='same', name='conv1')) #96
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2,2),strides=(2,2), name='pool1'))
model.add(Dropout(0.5))


# Layer 2
model.add(Convolution2D(filters= 64, kernel_size =(3,3), strides= (1,1),
padding='same', name='conv2'))  #256
model.add(BatchNormalization())
model.add(Activation('relu'))

model.add(Convolution2D(filters= 64, kernel_size =(3,3), strides= (1,1),
padding='same', name='conv2_2'))  #256
model.add(BatchNormalization())
model.add(Activation('relu'))

model.add(MaxPooling2D(pool_size=(2,2),strides=(2,2), name='pool2'))
model.add(Dropout(0.5))


# Layer 3
model.add(Convolution2D(filters= 128, kernel_size =(3,3), strides= (1,1),
padding='same', name='conv3'))  #256
model.add(BatchNormalization())
model.add(Activation('relu'))

model.add(Convolution2D(filters= 128, kernel_size =(3,3), strides= (1,1),
padding='same', name='conv3_2'))  #256
model.add(BatchNormalization())
model.add(Activation('relu'))

model.add(MaxPooling2D(pool_size=(2,2),strides=(2,2), name='pool3'))
model.add(Dropout(0.5))

# Layer 4
model.add(Convolution2D(filters= 256, kernel_size =(3,3), strides= (1,1),
padding='same', name='conv4'))  #256
model.add(BatchNormalization())
model.add(Activation('relu'))

model.add(Convolution2D(filters= 256, kernel_size =(3,3), strides= (1,1),
padding='same', name='conv4_2'))  #256
model.add(BatchNormalization())
model.add(Activation('relu'))

model.add(MaxPooling2D(pool_size=(2,2),strides=(2,2), name='pool4'))
model.add(Dropout(0.5))
'''
# Layer 5
model.add(Convolution2D(filters= 512, kernel_size =(3,3), strides= (1,1),
                        padding='same', name='conv5'))  #256
model.add(BatchNormalization())
model.add(Activation('relu'))

model.add(Convolution2D(filters= 512, kernel_size =(3,3), strides= (1,1),
                        padding='same', name='conv5_2'))  #256
model.add(BatchNormalization())
model.add(Activation('relu'))

#model.add(MaxPooling2D(pool_size=(2,2),strides=(1,1), name='pool5'))
model.add(Dropout(0.5))
'''
model.add(Flatten())

model.add(Dense(512, name='dense1'))  #1024
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(Dropout(0.5)) #0.5

model.add(Dense(256, name='dense2'))  #1024
model.add(BatchNormalization())
model.add(Activation('relu'))
model.add(Dropout(0.5)) #0.5

model.add(Dense(31,name='output'))
model.add(Activation('softmax'))  #softmax since output is within 50 classes

model.compile(loss='categorical_crossentropy', optimizer=Adam(),
              metrics=['accuracy'])

# augmentation
batch_size = 256
epochs = 200
datagen = ImageDataGenerator(
    rotation_range=30.,
    width_shift_range=0.1,
    height_shift_range=0.1,
    zoom_range=0.05,
    horizontal_flip=True,
    vertical_flip=False)

datagen.fit(training_feature)
history = model.fit_generator(datagen.flow(training_feature, training_target_one_hot, batch_size=batch_size), steps_per_epoch=128,epochs=epochs, validation_data=(testing_feature, testing_target_one_hot), workers=4)

#history = model.fit(training_feature, training_target_one_hot, batch_size=256,
#                    epochs=80, verbose=1, validation_data=(testing_feature,
#                                                           testing_target_one_hot))
print(model.evaluate(testing_feature, testing_target_one_hot))


# keys=list(category_index.keys())
# values=list(category_index.values())
# incorrects = np.nonzero(model.predict_classes(testing_feature).reshape((-1,)) !=
#                         testing_target)
# for i in incorrects[0]:
#     fig = plt.figure(figsize=[8,6])
#     fig.add_subplot(1,2,1)
#     plt.imshow(testing_feature_origin[i].reshape(100, 100))
#     fig.add_subplot(1,2,2)
#     plt.imshow(testing_feature[i].reshape(IMG_SIZE, IMG_SIZE))
#     right = keys[values.index(testing_target[i])]
#     current_feature = np.zeros((1, 56, 56, 1))
#     current_feature[0, :, :, :] = testing_feature[i]
#     wrong = keys[values.index(model.predict_classes(current_feature))]
#     plt.title('{}/{}'.format(right, wrong))
#     plt.savefig('wrong/{}.jpg'.format(i))
#     plt.close(fig)


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


# prediction
testing = np.load('input/test_images.npy', encoding='bytes')

testing_features = np.zeros(shape=(10000, IMG_SIZE, IMG_SIZE, 1), dtype=float)
for i in range(len(testing)):
    temp_img = cleanNoise3(testing[i, 1])
    temp_img = TrimImage(temp_img)
    testing_features[i, :, :, 0] = temp_img
    #testing_features[i, :, :, 1] = temp_img
    #testing_features[i, :, :, 2] = temp_img

testing_features /= 255

prediction = model.predict_classes(testing_features)
np.savetxt("prediction.csv", prediction, delimiter=",")
prediction = prediction.astype('int')
try:
    file = open("output.csv",'w')
    file.write('Id,Category\n')
    keys=list(category_index.keys())
    values=list(category_index.values())
    for i in range(len(prediction)):
        cate = keys[values.index(prediction[i])]
        file.write(str(i)+','+cate+'\n')

    file.close()
except:
    pass
