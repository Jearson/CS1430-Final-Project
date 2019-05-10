import os
import tensorflow as tf
import zipfile
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from skimage import io, img_as_ubyte, img_as_float32
import skimage.segmentation
from PIL import Image

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
        
        W2 = tf.Variable(tf.truncated_normal([256, 10], stddev=0.1))
        b2 = tf.Variable(tf.truncated_normal([10], stddev=0.1))
        
        # W3 = tf.Variable(tf.truncated_normal([2048, 10], stddev=0.1))
        # b3 = tf.Variable(tf.truncated_normal([10], stddev=0.1))
                             
        feedForward1 = tf.nn.relu(tf.matmul(convReshaped, W1) + b1)
        dropOut1 = tf.nn.dropout(feedForward1, keep_prob=.8)
        # feedForward2 = tf.nn.relu(tf.matmul(dropOut1, W2) + b2)
        # dropOut2 = tf.nn.dropout(feedForward2, keep_prob=.8)
                             
        return tf.matmul(dropOut1, W2) + b2
        # return tf.matmul(dropOut2, W3) + b3 #tf.nn.softmax(tf.matmul(feedForward1, W2) + b2)
    
    def loss_function(self):
        return tf.losses.softmax_cross_entropy(self.label, self.prediction)
    
    def optimizer_function(self):
        return tf.train.AdamOptimizer(5E-4, beta1=.9, beta2=0.999).minimize(self.loss)

    
    def accuracy_function(self):
        correct_prediction = tf.equal(tf.argmax(self.prediction, 1),
                                      tf.argmax(self.label, 1))
        return tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    def getAnswer(self):
        return tf.argmax(self.prediction, 1)

# read in zipped files
def readZippedFiles(pathList):
    allUnzippedImgs = []
    labels = []
    for path in pathList:
        # Read in zipped images without extracting:
        zippedF = zipfile.ZipFile(path, 'r')
        zippedNames = zippedF.namelist()
        n = -2

        for currFile in zippedNames:
            if currFile == "imgs/.DS_Store":
                continue
            if not currFile[-1] == '/':
                printRes = str(n) + ") " + currFile
                if n == 0:
                    continue
                print(printRes)
                byteFile = zippedF.read(currFile)
                imgFile = cv2.imdecode(np.frombuffer(byteFile, np.uint8), cv2.IMREAD_COLOR) # 1 for greyscale?
                img = img_as_float32(imgFile)
                allUnzippedImgs.append(img)
<<<<<<< HEAD
                labels.append(label(n))
                allUnzippedImgs.append(np.fliplr(img))
                labels.append(label(n))
                # allUnzippedImgs.append(np.clip(img - 50, 0, None))
                # labels.append(label(n))
                # allUnzippedImgs.append(np.clip(img + 50, None, 255))
                # labels.append(label(n))
                # allUnzippedImgs.append(gaussian_filter(img, sigma=2))
                # labels.append(label(n))
=======
                if n == 0: # Tablet
                    labels.append([0., 0., 0., 1., 0., 0., 0., 0., 0., 0.]) #3
                elif n == 1: # TV
                    labels.append([0., 0., 0., 0., 0., 0., 0., 0., 1., 0.]) #8
                elif n == 2: # Handheld Console
                    labels.append([0., 0., 0., 0., 0., 0., 0., 0., 0., 1.]) #9
                elif n == 3: # Camera
                    labels.append([0., 0., 0., 0., 0., 0., 0., 1., 0., 0.]) #7
                elif n == 4: # Phone
                    labels.append([0., 0., 0., 0., 1., 0., 0., 0., 0., 0.]) #4
                elif n == 5: # Desktop
                    labels.append([0., 0., 1., 0., 0., 0., 0., 0., 0., 0.]) #2
                elif n == 6: # PC Laptop
                    labels.append([0., 1., 0., 0., 0., 0., 0., 0., 0., 0.]) #1
                elif n == 7: # Router
                    labels.append([0., 0., 0., 0., 0., 1., 0., 0., 0., 0.]) #5
                elif n == 8: # Macbook
                    labels.append([1., 0., 0., 0., 0., 0., 0., 0., 0., 0.]) #0
                elif n == 9: # Smart Speaker
                    labels.append([0., 0., 0., 0., 0., 0., 1., 0., 0., 0.]) #6
>>>>>>> 6d041a7b3a1772f357a8c08142c062bf170d6ede
            else:
                n += 1

    return labels, allUnzippedImgs

def label(x):
    if x == 0: # Tablet
        return [0., 0., 0., 1., 0., 0., 0., 0., 0., 0.] #3
    elif x == 1: # TV
        return [0., 0., 0., 0., 0., 0., 0., 0., 1., 0.] #8
    elif x == 2: # Handheld Console
        return [0., 0., 0., 0., 0., 0., 0., 0., 0., 1.] #9
    elif x == 3: # Camera
        return [0., 0., 0., 0., 0., 0., 0., 1., 0., 0.] #7
    elif x == 4: # Phone
        return [0., 0., 0., 0., 1., 0., 0., 0., 0., 0.] #4
    elif x == 5: # Desktop
        return [0., 0., 1., 0., 0., 0., 0., 0., 0., 0.] #2
    elif x == 6: # PC Laptop
        return [0., 1., 0., 0., 0., 0., 0., 0., 0., 0.] #1
    elif x == 7: # Router
        return [0., 0., 0., 0., 0., 1., 0., 0., 0., 0.] #5
    elif x == 8: # Macbook
        return [1., 0., 0., 0., 0., 0., 0., 0., 0., 0.] #0
    elif x == 9: # Smart Speaker
        return [0., 0., 0., 0., 0., 0., 1., 0., 0., 0.] #6


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
    chosenBoxes = []
    for [top, bottom, left, right, size] in boundingBoxes:
        if (size in sizes[0:numRequested]):
            rectangle = matplotlib.patches.Rectangle((left, top), (right-left), (bottom-top), fill=False, edgecolor='red', linewidth=3)
            ax1.add_patch(rectangle)
            chosenBoxes.append([top, bottom, left, right, size])
    ax1.imshow(segment_mask);
    plt.savefig('static/userData/result.png')
    Image.open('static/userData/result.png').save('static/userData/result.png','png')
    #plt.tight_layout()
    #plt.show()
    return chosenBoxes

def cropImgs(img, boundingBoxes):
    # bounding boxes are of shape (-1, 5) (aka [[top, bottom, left, right, size]])
    croppedImgs = []
    croppedImgs.append(cv2.resize(img, dsize=(448, 416), interpolation=cv2.INTER_CUBIC)) # add original Image
    for [top, bottom, left, right, size] in boundingBoxes:
        boxedImg = img[top:bottom, left:right].copy()
        boxedImg = cv2.resize(boxedImg, dsize=(448, 416), interpolation=cv2.INTER_CUBIC)
        croppedImgs.append(boxedImg)
    #cv2.imshow("cropped", boxedImg)
    #cv2.waitKey(0)
    return np.array(croppedImgs)

# translate results to english
def translateResults(resArr):
    # voting system
    translations = {}
    for numLoc, result in enumerate(resArr):
        toAdd = 1
        if numLoc == 0:
            toAdd = 3 # greater weight for whole image vote
        
        if result == 0:
            if "Mac Laptop" in translations:
                translations["Mac Laptop"] += toAdd
            else:
                translations["Mac Laptop"] = toAdd
        elif result == 1:
            if "PC Laptop" in translations:
                translations["PC Laptop"] += toAdd
            else:
                translations["PC Laptop"] = toAdd
        elif result == 2:
            if "Desktop" in translations:
                translations["Desktop"] += toAdd
            else:
                translations["Desktop"] = toAdd
        elif result == 3:
            if "Tablet" in translations:
                translations["Tablet"] += toAdd
            else:
                translations["Tablet"] = toAdd
        elif result == 4:
            if "Phone" in translations:
                translations["Phone"] += toAdd
            else:
                translations["Phone"] = toAdd
        elif result == 5:
            if "Router" in translations:
                translations["Router"] += toAdd
            else:
                translations["Router"] = toAdd
        elif result == 6:
            if "Smart Speaker" in translations:
                translations["Smart Speaker"] += toAdd
            else:
                translations["Smart Speaker"] = toAdd
        elif result == 7:
            if "Camera" in translations:
                translations["Camera"] += toAdd
            else:
                translations["Camera"] = toAdd
        elif result == 8:
            if "TV" in translations:
                translations["TV"] += toAdd
            else:
                translations["TV"] = toAdd
        elif result == 9:
            if "Handheld Game Console" in translations:
                translations["Handheld Game Console"] += toAdd
            else:
                translations["Handheld Game Console"] = toAdd
    return translations

def runModel(filename):
    # To run the saved model on user's image.
    # Note: if you do not have saved weights, please run "python model.py" from the model folder first
    
    # initialize graph
    m2 = Model(448, 416)
    session2 = tf.Session()
    session2.run(tf.global_variables_initializer())
    
    # restore weights and other variables
    saver = tf.train.Saver()
    saver.restore(session2, "../model/tmp/model.ckpt")
    
    # get user's uploaded image
    userPathList = ['../interface/static/userData/']
    userImgData = np.array(getTestImgs(userPathList))
    userImg = userImgData[0]
    
    # draw bounding boxes, crop image to box boundaries, & run each through model
    boundingBoxes = getBoundingBoxes(userImg, 5)
    croppedImgs = cropImgs(userImg, boundingBoxes)
    #print(croppedImgs.shape)
    result = session2.run(m2.answer, feed_dict={m2.image: croppedImgs})
    return translateResults(result) # apply voting system for final results

def main():
    # number of label categories: 10
    numLabels = 10 # labels should be one-hot vectors
    
    #import data
    # pathList = ['../scraper/unsplash/imgs/Macbook/', '../scraper/unsplash/imgs/Phone/', '../scraper/unsplash/imgs/Camera/'] # list of zipped data
    path = ['./imgs.zip']
    # labelData, imgData = readFiles(pathList)
    labelData, imgData = readZippedFiles(path)
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
    saver = tf.train.Saver()
    
    # Training:
    numEpochs = 15#30
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

    save_path = saver.save(session, "./tmp/model.ckpt") # save model

    # Testing:
    '''
    testPathList = ['./test/']
    testImgData = np.array(getTestImgs(testPathList))
    result = session.run(m.answer, feed_dict={m.image: testImgData})
    print(translateResults(result))
    '''
    '''
    userPathList = ['../userData/']
    userImgData = np.array(getTestImgs(userPathList))
    #print(userImgData.shape)
    userImg = userImgData[0]
    boundingBoxes = getBoundingBoxes(userImg, 5)
    croppedImgs = cropImgs(userImg, boundingBoxes)
    print(croppedImgs.shape)
    result = session.run(m.answer, feed_dict={m.image: croppedImgs})
    print(translateResults(result))
    '''

    return


if __name__ == '__main__':
    main()
