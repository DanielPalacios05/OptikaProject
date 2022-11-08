import cv2
import numpy as np
from OptikaWeb.bdconnect import uploadPersonImage
from facialRecog.facialrecognition import getEmbedding
import pickle


def loadFacesToFirebase(files,name):

    for file in files:


        downloadedFile = b""

        for chunk in file.chunks():

            downloadedFile += chunk

    

        fileImage =  cv2.imdecode(np.fromstring(downloadedFile,np.uint8), cv2.IMREAD_COLOR)

        embedding = pickle.dumps(getEmbedding(fileImage,extractFace = True))

        uploadPersonImage(name,downloadedFile,embedding)




    
    

    

