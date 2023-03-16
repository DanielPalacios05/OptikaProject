from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from azure.storage.blob import BlobClient
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import Twin, TwinProperties
from django.template.loader import get_template 
from OptikaWeb.bdconnect import *
from django.conf import settings
from .facialrecognition import *
import os
import json
import numpy as np
import cv2


STORAGE_CONNECTION_STRING = os.environ.get("STORAGE_CONN")
IOTHUB_CONNECTION_STRING = os.environ.get("DEVICE_CONN")
DEVICE_ID = os.environ.get("DEVICE_ID")

iothub_registry_manager = IoTHubRegistryManager(IOTHUB_CONNECTION_STRING)

@csrf_exempt
def generateDetectionLog(request):

    blob = BlobClient.from_connection_string(STORAGE_CONNECTION_STRING,"device-upload",f"{DEVICE_ID}/frame.jpg")
    modified = blob.get_blob_properties().last_modified
    binary = blob.download_blob().readall()

    frame = cv2.imdecode(np.asarray(bytearray(binary), dtype="uint8"), cv2.IMREAD_COLOR)
    detection = detect(frame)

    if detection:
        try:
            link,name = sendDetectionLog(cv2.imencode('.jpg',detection[0])[1].tobytes(),",".join(detection[1]),modified)
            context = {'mail': settings.EMAIL_HOST_USER, 'name': name, 'imagen': link}
            print(context)
            template = get_template('correoB.html')
            content = template.render(context)

            send_email(settings.EMAIL_HOST_USER,name,content)
        except:
            return JsonResponse({u'status_code':500})
    return JsonResponse({'status_code':200})