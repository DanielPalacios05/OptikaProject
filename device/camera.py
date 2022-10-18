import os
import time
from azure.iot.device import IoTHubDeviceClient
from azure.core.exceptions import AzureError
from azure.storage.blob import BlobClient
import cv2

FILE_NAME = "frame.jpg"
CONNECTION_STRING = "HostName=optika2.azure-devices.net;DeviceId=testdevice;SharedAccessKey=e3LZRp2CrOK+eolM5camvHU+hwEneZ5mlV71DOkJerw="


def create_client():
    # Instantiate client
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

    # Define behavior for receiving twin desired property patches
    def twin_patch_handler(twin_patch):
        print("Twin patch received:")
        print(twin_patch)

    try:
        # Set handlers on the client
        client.on_twin_desired_properties_patch_received = twin_patch_handler
    except:
        # Clean up in the event of failure
        client.shutdown()

    return client

def store_blob(blob_info, file_name,blob):
    try:
        sas_url = "https://{}/{}/{}{}".format(
            blob_info["hostName"],
            blob_info["containerName"],
            blob_info["blobName"],
            blob_info["sasToken"]
        )

        print("\nUploading file: {} to Azure Storage as blob: {} in container {}\n".format(file_name, blob_info["blobName"], blob_info["containerName"]))

        # Upload the specified file
        with BlobClient.from_blob_url(sas_url) as blob_client:
                result = blob_client.upload_blob(blob, overwrite=True)
                return (True, result)

    except FileNotFoundError as ex:
        # catch file not found and add an HTTP status code to return in notification to IoT Hub
        ex.status_code = 404
        return (False, ex)

    except AzureError as ex:
        # catch Azure errors that might result from the upload operation
        return (False, ex)

def setCooldown(client):

    try:
        # Update reported properties with cellular information
        print ( "Sending data as reported property..." )
        reported_patch = {"readyToSend": False}
        client.patch_twin_reported_properties(reported_patch)
        print ( "Reported properties updated" )
    except:
        print("something wrong happened")


device_client = create_client()

# Connect the client
device_client.connect()



#send camera data to azure whenever q is pressed

video_capture = cv2.VideoCapture(0)

while True:


    readyTosend = device_client.get_twin()["desired"]["readyToSend"]
    

    if readyTosend:

        ret, frame = video_capture.read()

        storage_info = device_client.get_storage_info_for_blob(FILE_NAME)


        blobImage = cv2.imencode(".jpg",frame)[1].tobytes()

        success, result = store_blob(storage_info,FILE_NAME,blobImage)

        if success == True:
            print("Upload succeeded. Result is: \n") 
            print(result)
            print()

            device_client.notify_blob_upload_status(
                storage_info["correlationId"], True, 200, "OK: {}".format(FILE_NAME)
            )

            setCooldown(device_client)

        else :
            # If the upload was not successful, the result is the exception object
            print("Upload failed. Exception is: \n") 
            print(result)
            print()

            device_client.notify_blob_upload_status(
                storage_info["correlationId"], False, result.status_code, str(result)
            )


