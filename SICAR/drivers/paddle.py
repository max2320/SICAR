from paddleocr import PaddleOCR
from pathlib import Path
import matplotlib.image as mpimg
import re
import cv2
import numpy as np

from SICAR.drivers.captcha import Captcha


class Paddle(Captcha):
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=False, lang="en", use_space_char=False)

    def _get_captcha(self, captcha: Path) -> str:
        return re.sub(
            "[^A-Za-z0-9]+",
            "",
            self.ocr.ocr(self._process_captcha(captcha), det=False, cls=False)[0][0],
        )

    def _improve_image(self, image):
        _, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU + 2)
        image = cv2.dilate(image, np.ones((3, 2), np.uint8), iterations=1)
        image = cv2.erode(image, np.ones((4, 1), np.uint8), iterations=2)
        image = cv2.dilate(image, np.ones((3, 1), np.uint8), iterations=2)
        image = cv2.erode(image, np.ones((2, 1), np.uint8), iterations=2)
        return image

    def _process_captcha(self, captcha: Path):

        captcha_jpg = self._png_to_jpg(captcha)

        img = cv2.cvtColor(cv2.imread(str(captcha_jpg), -1), cv2.COLOR_BGR2GRAY)

        res = self._improve_image(img)

        mpimg.imsave(captcha_jpg, res, cmap="gray")

        return res