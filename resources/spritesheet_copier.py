import cv2
import json
import os


img = cv2.imread("resources/spritesheet.png", cv2.IMREAD_UNCHANGED)
data = {"img": img.tolist()}

with open("resources/spritesheet.json", "w") as f:
    f.write(json.dumps(data))

img = cv2.imread("resources/spritesheet_blocks.png", cv2.IMREAD_UNCHANGED)
data = {"img": img.tolist()}

with open("resources/spritesheet_blocks.json", "w") as f:
    f.write(json.dumps(data))
    