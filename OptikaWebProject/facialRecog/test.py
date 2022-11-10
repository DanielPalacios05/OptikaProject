from facialRecog.facialrecognition import *
import cv2
from PIL import Image
frame = cv2.imread("/home/danicracker/Downloads/ceos.jpg")

a = detect(frame)

print(a[1])

a = Image.fromarray(cv2.cvtColor(a[0],cv2.COLOR_BGR2RGB))

a.save("forrealforreal.jpg")



print(a)
