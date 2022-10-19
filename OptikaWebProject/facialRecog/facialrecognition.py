import os

import requests
from scipy.spatial.distance import cosine
from keras_vggface import VGGFace
from keras_vggface.utils import preprocess_input
import cv2
from PIL import Image
from facenet_pytorch import MTCNN, extract_face
import torch
import numpy as np


class FacialRecog:

    def __init__(self):

        self.knownPeople = {}  # {name: [embeddings]}

        torchdevice = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        self.cascade = MTCNN(image_size=240, margin=40, device=torchdevice, post_process=False)
        self.model = VGGFace(model='resnet50', include_top=False, input_shape=(240, 240, 3), pooling='avg')

    def jpgFromBlob(self, blob):

        # cv2.imencode(".jpg",frame)[1].tobytes()
        frame = cv2.imdecode(blob)

        return frame

    def detect(self, frame):

        # 0 is used for grayscale image

        boxes, probs = self.cascade.detect(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        detectedPeople = []

        if boxes is not None:
            filterProbs = probs > 0.90

            boxes = boxes[filterProbs]

            for (x, y, w, h) in boxes:
                face = extract_face(frame, (x, y, w, h), image_size=240).permute(1, 2, 0).int().numpy()

                name = self.classifyFace(face)

                if name == "Desconocido":

                    color = (0, 0, 255)
                else:
                    color = (255, 0, 0)

                detectedPeople.append(name)

                cv2.putText(frame, name, (round(x), round(y - 10)), cv2.FONT_HERSHEY_COMPLEX_SMALL, color=color, thickness=1,
                            fontScale=1)
                cv2.rectangle(frame, (round(x), round(y)), (round(w), round(h)),
                              color,
                              3)

            return frame, detectedPeople

        return None

    def getEmbedding(self, frame=None, imagePath=None, extractFace=False):

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
            face = self.cascade.forward(img)

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
        yhat = self.model.predict(sample)

        return yhat

    def loadPeople(self, peopleData):

        for person in peopleData:

            if person["images"] != []:

                embeddings = self.loadEmbeddings(person["images"])

                if embeddings != []:
                    self.knownPeople[person["name"]] = embeddings

    # Si no detecta una cara omite getEmbedding

    def loadEmbeddings(self, images):

        embeddings = []

        for image in images:

            frame = Image.open(requests.get(image, stream=True).raw)

            embedding = self.getEmbedding(frame=frame, extractFace=True)

            if embedding is not None:
                embeddings.append(embedding)

        return embeddings

    def is_match(self, ID_embedding, subject_embedding, thresh=0.6):
        # calculate distance between embeddings
        score = cosine(ID_embedding, subject_embedding)

        if score <= thresh:
            return True
        else:
            return False

    def classifyFace(self, frame):

        matchFound = False

        subjectEmbedding = self.getEmbedding(frame=frame, extractFace=False)

        for name, embeddings in self.knownPeople.items():

            for personEmbedding in embeddings:

                if self.is_match(personEmbedding.flatten(), subjectEmbedding.flatten()):
                    matchFound = True

                    return name

        if not matchFound:
            return "Desconocido"

    def checkFaces(self, testingDir):

        if os.path.isdir(testingDir):

            for image in os.listdir(testingDir):
                imagePath = testingDir + "/" + image
                self.classifyFace(imagePath)
