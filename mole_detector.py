import numpy as np
import cv2
import sys

class MoleDetector:
    def __init__(self, fname):
        self.fname = fname
        self.moles = []
        self.image_large = cv2.imread(self.fname)
        self.image_small = cv2.resize(self.image_large, (0, 0), fx=0.25, fy=0.25)

    # explore active contour and major/minor axes for sizing
    def map_moles(self):
        image = self.image_large
        params = cv2.SimpleBlobDetector_Params()
        params.minThreshold = 120
        params.filterByArea = True
        params.minArea = 45
        params.filterByCircularity = False
        #params.minCircularity = 0.75
        params.filterByConvexity = True
        params.minConvexity = .80
        #params.filterByInertia = False
        #params.minInertiaRatio = 0.20

        detector = cv2.SimpleBlobDetector(params)
        keypoints = detector.detect(image)

        im_with_moles = cv2.drawKeypoints(image, keypoints, np.array([]), (255, 0, 0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        #cv2.imshow("Blob", im_with_moles)
        #cv2.waitKey(0)

        #canny_edges = cv2.Canny(self.cv2_small, 150, 300, apertureSize=3)
        #cv2.imshow("Canny", canny_edges)
        #cv2.waitKey(0)

        return cv2.imencode('.jpg', im_with_moles)[1].tostring()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Error: Incorrect Usage"
        print "Correct Usage: mole_detector.py <image file path>"
        exit(-1)

    md = MoleDetector(sys.argv[1])
    md.map_moles()


    #im_matrix = im_matrix/im_matrix.max()

    #im = Image.fromarray(np.uint8(im_matrix*255))
    #im.show()

    #md.mole_map_LoG()

    #moles = md.find_moles()
    #print moles

    #presumably do some database stuff here
    exit(0)
