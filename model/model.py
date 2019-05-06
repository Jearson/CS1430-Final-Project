import os
import tensorflow as tf
import zipfile
import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage import io, img_as_ubyte, img_as_float32
import skimage.segmentation

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
        self.answer = self.getAnswer()
    
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
        
        W2 = tf.Variable(tf.truncated_normal([256, 2048], stddev=0.1))
        b2 = tf.Variable(tf.truncated_normal([2048], stddev=0.1))
        
        W3 = tf.Variable(tf.truncated_normal([2048, 10], stddev=0.1))
        b3 = tf.Variable(tf.truncated_normal([10], stddev=0.1))
                             
        feedForward1 = tf.nn.relu(tf.matmul(convReshaped, W1) + b1)
        feedForward2 = tf.nn.relu(tf.matmul(feedForward1, W2) + b2)
                             
        return tf.matmul(feedForward2, W3) + b3 #tf.nn.softmax(tf.matmul(feedForward1, W2) + b2)
    
    def loss_function(self):
        return tf.losses.softmax_cross_entropy(self.label, self.prediction)
    
    def optimizer_function(self):
        return tf.train.AdamOptimizer(1E-4).minimize(self.loss)
    
    def accuracy_function(self):
        correct_prediction = tf.equal(tf.argmax(self.prediction, 1),
                                      tf.argmax(self.label, 1))
        return tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    def getAnswer(self):
        return tf.argmax(self.prediction, 1)

# read in zipped files
def readZippedFiles(pathList):
    allUnzippedImgs = []
    for path in pathList:
        # Read in zipped images without extracting:
        zippedF = zipfile.ZipFile(path, 'r')
        zippedNames = zippedF.namelist()
        
        for i, currFile in enumerate(zippedNames[:len(zippedNames)-1]):
            printRes = str(i) + ") " + currFile
            print(printRes)
            byteFile = zippedF.read(currFile)
            imgFile = cv2.imdecode(np.frombuffer(byteFile, np.uint8), cv2.IMREAD_COLOR) # 1 for greyscale?
            img = img_as_float32(imgFile)
            allUnzippedImgs.append(img)
        print(img.shape)
        #plt.imshow(img)
        #plt.show()
        #break
    return allUnzippedImgs

# read in unzipped training data + apply labels
def readFiles(pathList):
    allUnzippedImgs = []
    labels = []
    for i, path in enumerate(pathList):
        for dir, subdir, files in os.walk(path):
            for f in files:
                imgPath = os.path.join(dir, f)
                with open(imgPath, "rb") as opened:
                    temp = opened.read()
                    byteFile = bytearray(temp)
                    imgFile = cv2.imdecode(np.frombuffer(byteFile, np.uint8), cv2.IMREAD_COLOR) # 1 for greyscale?
                    img = img_as_float32(imgFile)
                    resizedImg = cv2.resize(img, dsize=(448, 416), interpolation=cv2.INTER_CUBIC)
                    allUnzippedImgs.append(resizedImg)
                    if i == 0: # Macbook
                        labels.append([1., 0., 0., 0., 0., 0., 0., 0., 0., 0.]) #0
                    elif i == 1: # Phone
                        labels.append([0., 0., 0., 0., 1., 0., 0., 0., 0., 0.]) #4
                    elif i == 2: # Camera
                        labels.append([0., 0., 0., 0., 0., 0., 0., 1., 0., 0.]) #7
    return labels, allUnzippedImgs

# read in testing data
def getTestImgs(pathList):
    allUnzippedImgs = []
    for i, path in enumerate(pathList):
        for dir, subdir, files in os.walk(path):
            for f in files:
                imgPath = os.path.join(dir, f)
                print(imgPath)
                with open(imgPath, "rb") as opened:
                    '''
                    temp = opened.read()
                    byteFile = bytearray(temp)
                    imgFile = cv2.imdecode(np.frombuffer(byteFile, np.uint8), cv2.IMREAD_COLOR) # 1 for greyscale?
                    img = img_as_float32(imgFile)
                    resizedImg = cv2.resize(img, dsize=(448, 416), interpolation=cv2.INTER_CUBIC)
                    '''
                    img = cv2.imread(imgPath,cv2.IMREAD_COLOR)
                    resizedImg = cv2.resize(img, dsize=(448, 416), interpolation=cv2.INTER_CUBIC)
                    allUnzippedImgs.append(resizedImg)
    return allUnzippedImgs

# get bounding boxes
def getBoundingBoxes(img, numRequested):
    segment_mask = skimage.segmentation.felzenszwalb(np.uint8(img), scale=100, sigma=0.8, min_size=50)
    numSegments = segment_mask.max()
    boundingBoxes = []
    sizes = []
    #largestSize, secondLargest = 0, 0
    for seg in range(numSegments):
        top, bottom, left, right, size = None, None, None, None, None
        for i in range(len(segment_mask)):
            for j in range(len(segment_mask[0])):
                curr = segment_mask[i][j]
                if curr == seg: #mode:
                    if top == None:
                        top = i
                        bottom = i
                        left = j
                        right = j
                    top = min(i, top)
                    bottom = max(i, bottom)
                    left = min(j, left)
                    right = max(j, right)
        size = (right - left) * (bottom - top)
        '''
        if (size > largestSize):
        secondLargest = largestSize
        largestSize = size
        elif (size > secondLargest):
        secondLargest = size
        '''
        sizes.append(size)
        boundingBoxes.append([top, bottom, left, right, size])

    sizes.sort(reverse=True)

    # show bounding boxes for debugging purposes
    fig = plt.figure(figsize=(12, 5))
    ax1 = fig.add_subplot(121)
    for [top, bottom, left, right, size] in boundingBoxes:
        if (size in sizes[0:numRequested]):
            rectangle = matplotlib.patches.Rectangle((left, top), (right-left), (bottom-top), fill=False, edgecolor='red', linewidth=3)
            ax1.add_patch(rectangle)
    ax1.imshow(segment_mask);
    plt.tight_layout()
    plt.show()

# translate results to english
def translateResults(resArr):
    translations = []
    for result in resArr:
        if result == 0:
            translations.append("Mac Laptop")
        elif result == 1:
            translations.append("PC Laptop")
        elif result == 2:
            translations.append("Desktop")
        elif result == 3:
            translations.append("Tablet")
        elif result == 4:
            translations.append("Phone")
        elif result == 5:
            translations.append("Router")
        elif result == 6:
            translations.append("Smart Speaker")
        elif result == 7:
            translations.append("Camera")
        elif result == 8:
            translations.append("TV")
        elif result == 9:
            translations.append("Handheld Game Console")
    return translations

def main():
    # number of label categories: 10
    numLabels = 10 # labels should be one-hot vectors
    
    #import data
    pathList = ['../scraper/unsplash/imgs/Macbook/', '../scraper/unsplash/imgs/Phone/', '../scraper/unsplash/imgs/Camera/'] # list of zipped data
    labelData, imgData = readFiles(pathList)
    labelData = np.array(labelData)
    imgData = np.array(imgData)
    imgHeight = imgData.shape[1]
    imgWidth = imgData.shape[2]
    print("LABEL DATA")
    print(labelData.shape)
    print("IMAGE DATA")
    print(imgData.shape)
    
    # Model Initialization:
    
    m = Model(imgHeight, imgWidth)
    session = tf.Session()
    session.run(tf.global_variables_initializer())
    
    # Training:
    numEpochs = 12
    batchSz = 50
    numTrainData = imgData.shape[0] # amount of images for training

    # check input data
    # print(imgData)
    # for i in range(len(imgData[0])):
    #     for j in range(len(imgData[0][i])):
    #         print(imgData[0][i][j])
    print(labelData)

    for epoch in range(numEpochs):
        print("============ EPOCH ============")
        totalLoss = 0
        totalChecked = 0
        totalAcc = 0
        for start, end in zip(range(0, numTrainData - batchSz, batchSz),
                              range(batchSz, numTrainData, batchSz)):
            currLoss, _, acc = session.run([m.loss, m.optimize, m.accuracy],
                                      feed_dict={m.image: imgData[start:end], m.label: labelData[start:end]})
                                      
            #print("CURRLOSS")
            #print(currLoss)
            #print(acc)

            totalLoss += currLoss
            totalChecked += batchSz
            totalAcc += (acc * batchSz)
        print("BATCH LOSS")
        print(totalLoss / totalChecked)
        print("BATCH ACC")
        print(totalAcc / totalChecked)

    # Testing:
    testPathList = ['../testData/']
    testImgData = np.array(getTestImgs(testPathList))
    result = session.run(m.answer, feed_dict={m.image: testImgData})
    print(translateResults(result))

    return


if __name__ == '__main__':
    main()
