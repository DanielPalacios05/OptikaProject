from PIL import Image
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from datetime import datetime,timezone
from numpy import imag
import requests
import uuid
import cv2
import pytz
import firebase_admin
from firebase_admin import credentials
from firebase_admin import  storage
from firebase_admin import firestore



cred = credentials.Certificate("optika-6e7bd-firebase-adminsdk-1c4j0-66656df18f.json")

app = firebase_admin.initialize_app(cred, {
        'storageBucket': 'optika-6e7bd.appspot.com'
    })


bucket = storage.bucket()
db = firestore.client()

def send_email(mail, nombre,content):
    
    if(nombre != "Desconocido"):
        print("voy a mandar un correo de conocido")

        email = EmailMultiAlternatives( # estructura del correo
            'Se ha detectado a ' + nombre, #titulo del correo
            'God Bless', #parametro necesario
            settings.EMAIL_HOST_USER,
            [mail]
        )
    else:
        print("voy a mandar un correo de desconocido")

        email = EmailMultiAlternatives( 
            'Se ha detectado a una persona desconocida!',
            'God Bless',
            settings.EMAIL_HOST_USER,
            [mail]
        )

    email.attach_alternative(content, 'text/html')
   
    email.send() 

def sendDetectionLog(image,name,date):

    my_datetime=date.astimezone(pytz.timezone('Etc/GMT+5'))
    my_datetime_str =  my_datetime.strftime('%Y-%m-%d-%H:%M:%S-')

    blobname = name+my_datetime_str+".jpg"
    blob = upload_blob(f"DetectionLog/user1/{blobname}", image)
    blobLink = blob.public_url

    doc_ref = db.collection(u'Detections').add({
            u'img_url': blobLink,
            u'known': not name == 'Desconocido',
            u'datetime': my_datetime,
            u'name': name
        })

    return blobLink, name

        #must create a entry in firebase storage Detections collection with 
        #image_url: url of image in firebase storage
        #date
        #name
        #known false (this one must be changed)

def upload_blob(destination_blob_name,contents):
        """Uploads a file to the bucket."""
        # The ID of your GCS bucket
        # bucket_name = "your-bucket-name"
        # The path to your file to upload
        # source_file_name = "local/path/to/file"
        # The ID of your GCS object
        # destination_blob_name = "storage-object-name"

        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(contents, content_type='image/jpeg',timeout=6000)
        return blob

def getDetections():
        detections_ref = db.collection(u'Detections')
        docs = detections_ref.stream()
        detections = []
        for doc in docs:
            doc_dict = doc.to_dict()
            doc_dict['id'] = doc.id
            detections.append(doc_dict)

        return detections

def getPeople():

        people = []
        knownPeople = db.collection(u'KnownPeople').stream()

        for person in knownPeople:

            p = person.to_dict()

            for i in range(len(p["images"])):
                response = Image.open(requests.get(p["images"][i], stream = True).raw)
                p["images"][i] = response
            people.append(p)
        
        return people

def delKnownPerson(person_id):
    db.collection(u'KnownPeople').document(person_id).delete()

#Puede ser resumido a elimiar la coleccion

def delDetections():
    detections_ref = db.collection(u'Detections')
    docs = detections_ref.list_documents()    
    for doc in docs:
        print(f'Deleting doc {doc.id} => {doc.get().to_dict()}')
        #doc_dict = doc.to_dict()
        #image_path = doc_dict['img_url'][56:]
        #blob = bucket.blob(img_url)
        #blob.delete()
        doc.delete()





def appendFaceToPerson(name,image,embedding):
        
    filename = str(uuid.uuid4())
    blob = upload_blob(f"KnownPeople/{name}/{filename}.jpg", image)
    blob.make_public()
    blobLink = blob.public_url

    imageObj = {"image":blobLink,"embedding":embedding}

    db.collection(u'KnownPeople').document(name).update({
            u'images': firestore.ArrayUnion([imageObj])
    })



def uploadPersonImage(name,image,embedding,document):

    filename = str(uuid.uuid4())
    blob = upload_blob(f"KnownPeople/{name}/{filename}.jpg", image)
    blob.make_public()
    blobLink = blob.public_url

    imageObj = {"image":blobLink,"embedding":embedding}

    document.set({
                u'name':name,
                u'images': firestore.ArrayUnion([imageObj])},merge=True)


def removePersonImage(personName,index: int):

    doc_ref = db.collection(u'KnownPeople').document(personName) 
    doc = doc_ref.get()
    images_array = doc.to_dict()['images']
    image = images_array[index]
    image_path = image['image'][56:]
    
    doc_ref.update({u'images': firestore.ArrayRemove([image])})

    blob = bucket.blob(image_path)
    blob.delete()