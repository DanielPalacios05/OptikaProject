import os
import requests
import cv2
import pickle
import torch
import numpy as np
from scipy.spatial.distance import cosine
from keras_vggface import VGGFace
from keras_vggface.utils import preprocess_input
from PIL import Image
from facenet_pytorch import MTCNN, extract_face
from OptikaWeb.bdconnect import *


knownPeople = {}  # {name: [embeddings]}
torchdevice = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

cascade = MTCNN(image_size=240, margin=40, device=torchdevice, post_process=False)

model = VGGFace(model='resnet50', include_top=False, input_shape=(240, 240, 3), pooling='avg')

def jpgFromBlob(blob):
    # cv2.imencode(".jpg",frame)[1].tobytes()
    frame = cv2.imdecode(blob)
    return frame

def detect(frame):
# 0 is used for grayscale image
    boxes, probs = cascade.detect(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    detectedPeople = []

    if boxes is not None:
        filterProbs = probs > 0.90
        boxes = boxes[filterProbs]

        for (x, y, w, h) in boxes:
            face = extract_face(frame, (x, y, w, h), image_size=240).permute(1, 2, 0).int().numpy()
            name = classifyFace(face)

            if name == "Desconocido":
                color = (0, 0, 255)
            else:
                color = (0, 255, 0)

            detectedPeople.append(name)

            cv2.putText(frame, name, (round(x), round(y - 10)), cv2.FONT_HERSHEY_COMPLEX_SMALL, color=color, thickness=1,
                            fontScale=1)
            cv2.rectangle(frame, (round(x), round(y)), (round(w), round(h)),
                              color,
                              3)
        return frame, detectedPeople
    return None

def getEmbedding(frame=None, imagePath=None, extractFace=False):

        nimg = np.asarray(frame,dtype=np.uint8)
        img = cv2.cvtColor(nimg, cv2.COLOR_RGB2BGR)
        img = Image.fromarray(img)

        if imagePath is not None:

            img = cv2.imread(imagePath)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
        elif frame is None:
            raise Exception()
        """
        extractFace = True if the face has not been extracted
        """

        if extractFace:
            face = cascade.forward(img)

            if isinstance(face, list):
                raise Exception(f"Image should have only a face {len(face)} found")
            if face is None:
                return None
            img = face.permute(1, 2, 0).int().numpy()
        face = np.asarray(img)

        sample = [np.asarray(face, 'float32')]
        # prepare the face for the model, e.g. center pixels
        sample = preprocess_input(sample, version=2)
        # perform prediction
        yhat = model.predict(sample)

        return yhat

def loadPeople(peopleData):

        for person in peopleData:
            if person["images"] != []:
                embeddings = loadEmbeddings(person["images"])
                if embeddings != []:
                    knownPeople[person["name"]] = embeddings

    #If face in not detected skip getEmbedding 


def loadEmbeddings(images):

        embeddings = []
        for image in images:

            frame = Image.open(requests.get(image, stream=True).raw)
            embedding = getEmbedding(frame=frame, extractFace=True)

            if embedding is not None:
                embeddings.append(embedding)
        return embeddings

def is_match(ID_embedding, subject_embedding, thresh=0.3):
        # calculate distance between embeddings
        score = cosine(ID_embedding, subject_embedding)
        print(score)

        if score <= thresh:
            return True
        else:
            return False

def classifyFace(frame):

    matchFound = False
    subjectEmbedding = getEmbedding(frame=frame, extractFace=False)
    docs = db.collection(u'KnownPeople').stream()

    for doc in docs:
        for personImage in doc.get('images'):
            if is_match(pickle.loads(personImage['embedding']).flatten(), subjectEmbedding.flatten()):
                matchFound = True
                return doc.get('name')

    if not matchFound:
        return "Desconocido"

def checkFaces(testingDir):

        if os.path.isdir(testingDir):
            for image in os.listdir(testingDir):
                imagePath = testingDir + "/" + image
                classifyFace(imagePath)