import cv2
import json


img = cv2.imread("resources/spritesheet.png", cv2.IMREAD_UNCHANGED)
data = {"img": img.tolist()}

with open("resources/spritesheet.json", "w") as f:
    f.write(json.dumps(data))