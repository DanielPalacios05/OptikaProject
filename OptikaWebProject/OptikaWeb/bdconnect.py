from datetime import datetime,timezone
import pytz
import firebase_admin
from firebase_admin import credentials
from firebase_admin import  storage
from firebase_admin import firestore

import cv2



class FirebaseManager:

    cred = credentials.Certificate("optika-6e7bd-firebase-adminsdk-1c4j0-66656df18f.json")

    app = firebase_admin.initialize_app(cred, {
        'storageBucket': 'optika-6e7bd.appspot.com'
    })


    bucket = storage.bucket()

    db = firestore.client()





    def sendDetectionLog(self,image,name,date,known,db=db):

        my_datetime=date.astimezone(pytz.timezone('Etc/GMT-5'))

        my_datetime_str =  my_datetime.strftime('%Y-%m-%d-%H:%M:%S-')


        blobname = name+my_datetime_str+".jpg"

        blob = self.upload_blob(f"DetectionLog/user1/{blobname}", image)

        blob.make_public()

        blobLink = blob.public_url

        doc_ref = db.collection(u'Detections').add({
            u'img_url': blobLink,
            u'known': known,
            u'datetime': my_datetime,
            u'name': name
        })

        #must create a entry in firebase storage Detections collection with 
        #image_url: url of image in firebase storage
        #date
        #name
        #known false (this one must be changed)

    def upload_blob(self,destination_blob_name,contents,bucket=bucket):
        """Uploads a file to the bucket."""
        # The ID of your GCS bucket
        # bucket_name = "your-bucket-name"
        # The path to your file to upload
        # source_file_name = "local/path/to/file"
        # The ID of your GCS object
        # destination_blob_name = "storage-object-name"

        blob = bucket.blob(destination_blob_name)

        blob.upload_from_string(contents, content_type='image/jpeg')

        return blob

    def getDetections(self,db=db):
        
        detections_ref = db.collection(u'Detections')
        docs = detections_ref.stream()
        detections = []
        for doc in docs:
            doc_dict = doc.to_dict()
            doc_dict['id'] = doc.id
            detections.append(doc_dict)

        return detections





