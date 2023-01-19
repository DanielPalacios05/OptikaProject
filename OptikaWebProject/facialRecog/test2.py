from facialRecog.facialrecognition import *
import cv2
from PIL import Image

frame = cv2.imread("/home/danicracker/Downloads/juantest.jpg")

print(classifyFace(frame))