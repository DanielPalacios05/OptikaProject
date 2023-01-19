import cv2
import numpy as np
from OptikaWeb.bdconnect import uploadPersonImage,appendFaceToPerson,db
from facialRecog.facialrecognition import getEmbedding
import pickle

def loadFacesToFirebase(files,name,append):

    document = db.collection(u"KnownPeople").document()
    for file in files:
        downloadedFile = b""
        for chunk in file.chunks():
            downloadedFile += chunk

        fileImage =  cv2.imdecode(np.fromstring(downloadedFile,np.uint8), cv2.IMREAD_COLOR)
        embedding = pickle.dumps(getEmbedding(fileImage,extractFace = True))

        if append:
            appendFaceToPerson(name,downloadedFile,embedding)
        else:
            uploadPersonImage(name,downloadedFile,embedding,document)