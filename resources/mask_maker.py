import cv2, os, numpy, json


for path in os.listdir("resources/masks"):
    img = cv2.imread(os.path.join("resources/masks", path), cv2.IMREAD_UNCHANGED)
    output = numpy.zeros((32, 32), numpy.uint8)
    for y in range(32):
        for x in range(32):
            output[y, x] = img[y, x, 3]

    with open(os.path.join("resources/json_masks", path.replace(".png", ".json")), "w") as f:
        f.write(json.dumps(({"mask": output.tolist()})))