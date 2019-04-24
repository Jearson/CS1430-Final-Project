import os
import tensorflow as tf
import zipfile
import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage import io, img_as_ubyte, img_as_float32
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

class Model:
    
    def __init__(self, imgHeight, imgWidth):
        # placeholders and variables
        self.image = tf.placeholder(tf.float32, [None, None, None, 3]) # input shape: [batch size, imgHeight, imgWidth, 3]
        self.label = tf.placeholder(tf.float32, [None, None]) # output shape: [batch size, numLabels]
        self.imgHeight = imgHeight
        self.imgWidth = imgWidth
        
        # functions
        self.prediction = self.forward_pass()
        self.loss = self.loss_function()
        self.optimize = self.optimizer_function()
        self.accuracy = self.accuracy_function()
    
    def forward_pass(self):
        
        filter1 = tf.Variable(tf.truncated_normal([5, 5, 3, 48], stddev=0.1))
        bias1 = tf.Variable(tf.truncated_normal([48], stddev=0.1))
        conv1 = tf.nn.conv2d(self.image, filter=filter1, strides=[1, 1, 1, 1], padding="SAME") + bias1
        relu1 = tf.nn.relu(conv1)
        maxPool1 = tf.nn.max_pool(relu1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding="VALID")
                             
        filter2 = tf.Variable(tf.truncated_normal([3, 3, 48, 32], stddev=0.1))
        bias2 = tf.Variable(tf.truncated_normal([32], stddev=0.1))
        conv2 = tf.nn.conv2d(maxPool1, filter=filter2, strides=[1, 1, 1, 1], padding="SAME") + bias2
        relu2 = tf.nn.relu(conv2)
        maxPool2 = tf.nn.max_pool(relu2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding="VALID")
                             
        convReshaped = tf.reshape(maxPool2, [-1, 372736])
                             
        W1 = tf.Variable(tf.truncated_normal([372736, 256], stddev=0.1))
        b1 = tf.Variable(tf.truncated_normal([256], stddev=0.1))
        W2 = tf.Variable(tf.truncated_normal([256, 10], stddev=0.1))
        b2 = tf.Variable(tf.truncated_normal([10], stddev=0.1))
                             
        feedForward1 = tf.nn.relu(tf.matmul(convReshaped, W1) + b1)
                             
        return tf.nn.softmax(tf.matmul(feedForward1, W2) + b2)
    
    def loss_function(self):
        return tf.reduce_mean(-tf.reduce_sum(self.label * tf.log(tf.clip_by_value(self.prediction,1e-10,1.0)), reduction_indices=[1]))
    
    def optimizer_function(self):
        return tf.train.AdamOptimizer(1E-4).minimize(self.loss)
    
    def accuracy_function(self):
        print("actual")
        print(tf.argmax(self.prediction, 1))
        print("Correct")
        print(tf.argmax(self.label, 1))
        correct_prediction = tf.equal(tf.argmax(self.prediction, 1),
                                      tf.argmax(self.label, 1))
        return tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

def readZippedFiles(pathList):
    allUnzippedImgs = []
    for path in pathList:
        # Read in zipped images without extracting:
        zippedF = zipfile.ZipFile(path, 'r')
        zippedNames = zippedF.namelist()
    
        for currFile in zippedNames[:len(zippedNames)-1]:
            byteFile = zippedF.read(currFile)
            imgFile = cv2.imdecode(np.frombuffer(byteFile, np.uint8), cv2.IMREAD_COLOR) # 1 for greyscale?
            img = img_as_float32(imgFile)
            allUnzippedImgs.append(img)
        print(img.shape)
#plt.imshow(img)
#plt.show()
        #break
    return allUnzippedImgs

def main():
    # number of label categories: 10
    numLabels = 10 # labels should be one-hot vectors
    
    #import data
    pathList = ['../data/coil-20-unproc.zip'] # list of zipped data
    imgData = np.array(readZippedFiles(pathList))
    print(imgData.shape)
    imgHeight = imgData.shape[1]
    imgWidth = imgData.shape[2]
    
    labelData = np.zeros((imgData.shape[0], numLabels)) # should be of size: imgData.shape[0] x numLabels <-- due to one hot vector
    #reshapedImgData = np.reshape(imgData, (imgData.shape[0], imgHeight * imgWidth))
    
    for i in range(len(labelData)):
        res = int(i / 72)
        if res == 0:
            labelData[i][0] = 1
        elif res == 1:
            labelData[i][1] = 1
        elif res == 2:
            labelData[i][2] == 1
        elif res == 2:
            labelData[i][3] == 1
        elif res == 2:
            labelData[i][4] == 1
    
    # Model Initialization:
    
    m = Model(imgHeight, imgWidth)
    session = tf.Session()
    session.run(tf.global_variables_initializer())
    
    # Training:
    numEpochs = 10
    batchSz = 50
    numTrainData = imgData.shape[0] # amount of images for training
    
    for epoch in range(numEpochs):
        '''
        currLoss, _, acc = session.run([m.loss, m.optimize, m.accuracy],
                                       feed_dict={m.image: imgData, m.label: labelData})
        print("CURRLOSS")
        print(currLoss)
        print(acc)
        '''
        for start, end in zip(range(0, numTrainData - batchSz, batchSz),
                              range(batchSz, numTrainData, batchSz)):
            currLoss, _, acc = session.run([m.loss, m.optimize, m.accuracy],
                                      feed_dict={m.image: imgData[start:end], m.label: labelData[start:end]})
                                      #print("CURRLOSS")
                                      #print(currLoss)
#print(acc)

            


    # Testing:
    '''
    testImages = []
    testLabels = []
    
    avgAccuracy = session.run(m.accuracy, feed_dict={m.image: imgData, m.label: labelData})
    print(avgAccuracy)
    '''

    return


if __name__ == '__main__':
    main()
