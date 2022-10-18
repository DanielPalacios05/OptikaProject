import os
from scipy.spatial.distance import cosine
from keras_vggface import VGGFace
from keras_vggface.utils import preprocess_input
import cv2
import PIL
import torchvision.transforms as transform
from facenet_pytorch import MTCNN, extract_face
import torch
import numpy as np

class FacialRecog:

    def __init__(self) -> None:
        
        self.knownPeople = { } #{name: embedding}

        self.deviceIsOn = True

        self.torchdevice= torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.cascade = MTCNN(image_size = 224,margin=40,device=self.torchdevice,post_process=False)
        self.model = VGGFace(model='resnet50', include_top=False, input_shape=(224, 224, 3), pooling='avg')
    
    def jpgFromBlob(self,blob):

        #cv2.imencode(".jpg",frame)[1].tobytes()
        frame = cv2.imdecode(blob)

        return frame


    def detectPerson(self,image):


            frame = self.jpgFromBlob(image)


            boxes,probs = self.cascade.detect(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            detectedPeople = []



            if boxes is not None:

                filterProbs = probs > 0.90

                boxes = boxes[filterProbs]


            
                for (x, y, w, h) in boxes:

                    face = extract_face(frame,(x,y,w,h),image_size=240).permute(1, 2, 0).int().numpy()


                    name = self.classifyFace(face)

                    if name == "Desconocido":

                        color = (0,0,255)
                    else:
                        color = (255,0,0)

                    detectedPeople.append(name)
                    

                    cv2.putText(frame,name,(round(x),round(y-10)),cv2.FONT_HERSHEY_COMPLEX_SMALL,color=color,thickness=1,fontScale=1)
                    cv2.rectangle(frame,(round(x),round(y)), (round(w),round(h)),
                                color,
                                3)

            return frame,detectedPeople
        


    def getEmbedding(self,face=None,imagePath=None,extractFace = False):


        if imagePath is not None:

            img = cv2.imread(imagePath)
            img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

            frame = PIL.Image.fromarray(img)
        elif face is not None:
            frame = face
        else:
            raise Exception()
        """
        extractFace = True if the face has not been extracted
        """

        if extractFace:
            face = (self.cascade.forward(frame)).permute(1,2,0).int().numpy()


        face = np.asarray(face)
        
        sample = [np.asarray(face, 'float32')]
        # prepare the face for the model, e.g. center pixels
        sample = preprocess_input(sample, version=2)
        # perform prediction
        yhat = self.model.predict(sample)

        return yhat


    
    def loadPeople(self,trainingDirectory):

        """
        trainingDirectory should have the next structure
        trainingDirectory/
                nameperson1/
                    person1image
                nameperson2/
                    person2image
                
                ....
                namepersonn/
                    personNimage
        
        """


        for personName in os.listdir(trainingDirectory):

            personPath = f"{trainingDirectory}/{personName}"

            

            
            if os.path.isdir(personPath):
            
                pathPersonImage = personPath + "/" + os.listdir(personPath)[0]

                self.knownPeople[personName] = self.getEmbedding(imagePath=pathPersonImage,extractFace=True)


    def is_match(self,ID_embedding, subject_embedding,thresh=0.4):
        # calculate distance between embeddings
        score = cosine(ID_embedding, subject_embedding)

        if score <= thresh:
            return True
        else:
            return False


    def classifyFace(self,frame):

        matchFound = False

        subjectEmbedding = self.getEmbedding(face=frame,extractFace=False)

        for name, knownEmbedding in self.knownPeople.items():

            if self.is_match(knownEmbedding.flatten(),subjectEmbedding.flatten()):

                print(f"{name} esta en la camara")
                matchFound=True

                return name

        if not matchFound:
            print(f"Se ha detectado a un desconocido")
            
            return "Desconocido"




    def checkFaces(self,testingDir):
        

        if os.path.isdir(testingDir):

            for image in os.listdir(testingDir):

                imagePath = testingDir + "/" + image
                self.classifyFace(imagePath)

    