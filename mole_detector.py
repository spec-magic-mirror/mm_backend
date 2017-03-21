import numpy as np
import scipy as sp
from scipy.signal import convolve2d
from scipy.ndimage.filters import gaussian_laplace, generic_filter
import scipy.stats as st
import cv2
from PIL import Image
import sys
import math

class MoleDetector:
    def __init__(self, fname):
        self.moles = []
        self.resized_image = []
        # right now just use the greyscale image ('L'), use ('1') to use RBG
        self.raw_image = np.asarray(Image.open(fname).convert('L'))
        self.cv2_raw = cv2.imread(fname)
        self.cv2_small = cv2.resize(self.cv2_raw, (0,0), fx=0.25, fy=0.25)

    def resize_image(self, ratio):
        new_size = (int(self.raw_image.shape[1]/ratio), int(self.raw_image.shape[0]/ratio))
        self.resized_image = np.asarray(Image.fromarray(self.raw_image).resize(new_size, Image.ANTIALIAS))
        #im = Image.fromarray(np.uint8(self.resized_image))
        #im.show("Ratio = " + str(ratio))

    '''
    def find_moles(self):
        max_k = -1
        max_response = -1
        threshold = 0
        for x in range(self.raw_image.shape[1]):
            for y in range(self.raw_image.shape[0]):
                for k_size in range(3, 1000):
    '''
    def mole_map(self):
        k_size = 21
        kernel = np.zeros((k_size, k_size))
        kernel.fill(1.0/(k_size**2-(k_size-1)**2))
        kernel[1:-1, 1:-1] = -1.0/((k_size-1)**2)
        mole_map = convolve2d(self.resized_image, kernel)
        mole_map /= mole_map.max()
        im = Image.fromarray(np.uint8(mole_map*255))
        im.show("Kernel Size = " + str(k_size))
        return None


    # explore active contour and major/minor axes for sizing
    def cv2_mole_map(self):
        params = cv2.SimpleBlobDetector_Params()
        #params.minThreshold = 100
        params.filterByArea = True
        params.minArea = 8
        params.filterByCircularity = True
        params.minCircularity = 0.75
        #params.filterByConvexity = True
        #params.minConvexity = 1
        #params.filterByInertia = True
        #params.minInertiaRatio = 0.20

        detector = cv2.SimpleBlobDetector(params)
        keypoints = detector.detect(self.cv2_small)

        im_with_keypoints = cv2.drawKeypoints(self.cv2_small, keypoints, np.array([]), (255,0,0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        cv2.imshow("Blob", im_with_keypoints)
        cv2.waitKey(0)

        #canny_edges = cv2.Canny(self.cv2_small, 150, 300, apertureSize=3)
        #cv2.imshow("Canny", canny_edges)
        #cv2.waitKey(0)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Error: Incorrect Usage"
        print "Correct Usage: mole_detector.py <image file path>"
        exit(-1)

    md = MoleDetector(sys.argv[1])
    md.resize_image(10)
    md.cv2_mole_map()


    #im_matrix = im_matrix/im_matrix.max()

    #im = Image.fromarray(np.uint8(im_matrix*255))
    #im.show()

    #md.mole_map_LoG()

    #moles = md.find_moles()
    #print moles

    #presumably do some database stuff here
    exit(0)
