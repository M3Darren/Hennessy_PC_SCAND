import cv2
import numpy as np


class ModelTest:
    @staticmethod
    def opencv_test(image_path):
        img = cv2.imread(image_path)
        if len(img.shape) == 2:
            return "Grayscale"
        elif len(img.shape) == 3:
            b, g, r = cv2.split(img)
            if np.array_equal(b, g) and np.array_equal(g, r):
                unique_vals = np.unique(b)
                if set(unique_vals).issubset({0, 255}):
                    return "Black and White"
                return "Grayscale-like"
            else:
                return "Color"
        else:
            return "Unknown type"


path = "images/A4_TCP_300_24.3.jpg"
res = ModelTest.opencv_test(path)
print(res)
