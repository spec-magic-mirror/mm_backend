import numpy as np
import cv2
import sys
import os

class MoleDetector:
    version = "0.0.1"

    def __init__(self, fname):
        self.fname = fname
        self.moles = []
        self.image_large = cv2.imread(self.fname)
        self.image_small = cv2.resize(self.image_large, (0, 0), fx=0.25, fy=0.25)

    # explore active contour and major/minor axes for sizing
    def map_moles(self):
        image = self.image_large

	# There are the specific parameters for te pure CV blob detector approach
	'''
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
	'''
        params = cv2.SimpleBlobDetector_Params()
        params.minThreshold = 50
        params.maxThreshold = 10000
        params.filterByArea = True
        params.minArea = 20
        params.maxArea = 10000
        params.filterByConvexity = False
        params.filterByCircularity = False
        params.filterByInertia = False

        detector = cv2.SimpleBlobDetector(params)
        keypoints = detector.detect(image)

        im_with_moles = cv2.drawKeypoints(image, keypoints, np.array([]), (255, 0, 0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        #cv2.imshow("Blob", im_with_moles)
        #cv2.waitKey(0)
        req_size = 50
        mole_crops = self.getMoleCrops(image, keypoints, req_size)
        mole_imgs = self.getMoleImages(image, mole_crops, req_size)
        trial_num = 0
        while os.path.exists("trials/" + str(trial_num)):
            trial_num += 1
        path = "trials/" + str(trial_num)
        os.makedirs(path)

        cv2.imwrite(path + "/full_face.jpg", im_with_moles)

        mole_img_num = 0
        for mole_img in mole_imgs:
            #filepath = path + "/" + str(mole_img_num) + ".jpg"
            img = mole_img[0]
            x = mole_img[1]
            y = mole_img[2]
            filepath = path + "/x" + str(x) + "_y" + str(y) + ".jpg"
            cv2.imwrite(filepath, img)
            mole_img_num += 1

        mole_cannys = self.getMoleCannys(image, mole_crops)
        mole_circles = self.getMoleCircles(image, mole_crops)
        # FOR ALGORITHM DEVELOPMENT ONLY
        '''
        for i in range(3):
            cv2.imshow("Mole", mole_imgs[i])
            circle_canvas = np.zeros((50,50,3), dtype=np.uint8)
            for c in mole_circles[i]:
                circle_center = (c[0], c[1])
                circle_radius = int(c[2])
                cv2.circle(circle_canvas, circle_center, circle_radius, (255,255,255),2)
            #circle_canvas = cv2.cvtColor(circle_canvas, cv2.COLOR_BGR2GRAY)
            #contours, hierarchy = cv2.findContours(circle_canvas, 1, 2)
            #cv2.imshow("Circles", circle_canvas)
            #cv2.imshow("Canny", mole_cannys[i])
            #cv2.waitKey(0)
        '''
        #canny_edges = cv2.Canny(image, 150, 300, apertureSize=3)
        #cv2.namedWindow("Canny", cv2.WINDOW_NORMAL)
        #cv2.imshow("Canny", cv2.resize(canny_edges, (0,0), fx=0.3, fy=0.3))
        #cv2.imshow("Canny", canny_edges)
        #cv2.waitKey(0)

        return cv2.imencode('.jpg', im_with_moles)[1].tostring(), keypoints

    def getMoleCrops(self, original_img, mole_keypoints, req_size):
        mole_crops = []
        for keypoint in mole_keypoints:
            x,y = keypoint.pt
            crop_size = max([req_size, keypoint.size*3])

            # TODO: find better way of handling out of bounds instead of just skipping them
            y_min = y-crop_size/2
            y_max = y+crop_size/2
            x_min = x-crop_size/2
            x_max = x+crop_size/2
            if y_min >= 0 and x_min >= 0 \
                    and y_max < original_img.shape[0] and x_max < original_img.shape[1]:
                crop_pts = [y_min, y_max, x_min, x_max]
                crop_pts = [int(c) for c in crop_pts]
                mole_crops.append(crop_pts)
        return mole_crops

    def getMoleCannys(self, original_img, mole_crops):
        mole_cannys = []
        for mc in mole_crops:
            mole_img = original_img[mc[0]:mc[1], mc[2]: mc[3]]
            canny_edges = cv2.Canny(mole_img, 70, 150, apertureSize=3)
            mole_cannys.append(canny_edges)
        return mole_cannys

    def getMoleCircles(self, original_img, mole_crops):
        mole_circles = []
        mole_cannys = self.getMoleCannys(original_img, mole_crops)
        i = 0
        for canny in mole_cannys:
            mole_circles.append([])
            biggest_circle = [-1, -1, -1]
            contours, hierarchy = cv2.findContours(canny, 1, 2)
            for cnt in contours:
                (x,y), radius = cv2.minEnclosingCircle(cnt)
                if radius > biggest_circle[2]:
                    biggest_circle = [int(x),int(y),radius]
                mole_circles[i].append([int(x),int(y),radius])
            i += 1
            #mole_circles.append(biggest_circle)
        return mole_circles

    def getMoleImages(self, original_img, mole_crops, req_size):
        mole_imgs = []
        for mc in mole_crops:
            y = (mc[1]-mc[0])/2 + mc[0]
            x = (mc[3]-mc[2])/2 + mc[2]
            mole_img = original_img[mc[0]:mc[1], mc[2]: mc[3]]
            if mole_img.shape[0] > req_size:
                mole_img = cv2.resize(mole_img, (req_size, req_size))
            mole_imgs.append((mole_img, x, y))
        return mole_imgs

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
