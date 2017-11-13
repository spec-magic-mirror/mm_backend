import numpy as np
import cv2
import sys
import os
import vgg_nn
from pprint import pprint

class MoleDetector:
    version = "2.0.0"

    def __init__(self, fname):
        self.trials_dir = "resources/trials/"
        self.fname = fname
        self.moles = []
        self.image_large = cv2.imread(self.fname)
        self.image_small = cv2.resize(self.image_large, (0, 0), fx=0.25, fy=0.25)
        self.circle_size = 20

        self.use_NN = True
        self.NN_pretrained_path = "resources/models/mole_vgg_v3.pth"
        self.NN_thresh = 0.9999
        self.NN = None
        if self.use_NN:
            self.NN = vgg_nn.MoleModel(self.NN_pretrained_path)

    # explore active contour and major/minor axes for sizing
    def map_moles(self):
        image = self.image_large

        # There are the specific parameters for te pure CV blob detector approach

        params = cv2.SimpleBlobDetector_Params()
        #params.minThreshold = 50
        params.minThreshold = 0
        params.maxThreshold = 191
        params.filterByArea = True
        params.minArea = 18
        params.maxArea = 1000
        params.filterByConvexity = False
        params.filterByCircularity = False
        params.filterByInertia = False

        detector = cv2.SimpleBlobDetector(params)
        keypoints = detector.detect(image)

        im_with_blobs = cv2.drawKeypoints(image, keypoints, np.array([]), (255, 0, 0), 
                cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        #cv2.imshow("Blob", im_with_moles)
        #cv2.waitKey(0)
        req_size = 64
        mole_crops = self.getMoleCrops(image, keypoints, req_size)
        mole_imgs = self.getMoleImages(image, mole_crops, req_size)
        trial_num = 0
        while os.path.exists(self.trials_dir + str(trial_num)):
            trial_num += 1
        path = self.trials_dir + str(trial_num)
        moles_path = path + "/moles"

        os.makedirs(path)
        os.makedirs(moles_path)

        cv2.imwrite(path + "/full_face_allblobs.jpg", im_with_blobs)

        mole_coords = []

        mole_img_num = 0
        for mole_img in mole_imgs:
            #filepath = path + "/" + str(mole_img_num) + ".jpg"
            img = mole_img[0]
            x = mole_img[1]
            y = mole_img[2]
            filepath = path + "/x" + str(x) + "_y" + str(y) + ".jpg"
            cv2.imwrite(filepath, img)
            mole_img_num += 1

        if self.use_NN:
            test_imgs = []
            print("Classifying with neural network...")
            for mole_img in mole_imgs:
                img = cv2.cvtColor(mole_img[0], cv2.COLOR_BGR2GRAY)
                img = cv2.normalize(img, img, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, 
                    dtype=cv2.CV_32F)
            
                if img.shape == (req_size, req_size):
                    test_imgs.append({'predicted': img, 'ground_truth': np.array([0, 0]).T, 
                        'coords': [mole_img[1], mole_img[2]]})
                else:
                    print("Excluding sample: Invalid Shape: %d x %d @ (%d, %d)" % (
                        img.shape[0], img.shape[1], mole_img[1], mole_img[2]))  

            # run the blob detections through the neural network
            filtered_moles = self.NN.filter_moles(self.NN_thresh, test_imgs)
            print("")
            pprint(filtered_moles) 
            mole_keypoints = [cv2.KeyPoint(float(fm[0][0]), float(fm[0][1]), 
                float(self.circle_size)) for fm in filtered_moles]

            mole_coords = [[float(fm[0][0]), float(fm[0][1])] for fm in filtered_moles]


            im_with_moles = cv2.drawKeypoints(image, mole_keypoints, np.array([]), (255, 0, 0), 
                cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
            print("Done, sending results!")
            
        else:
            mole_coords = [[mole_img[1], mole_img[2]] for mole_img in mole_imgs]
            im_with_moles = im_with_blobs

        cv2.imwrite(path + "/full_face_moles.jpg", im_with_moles)

        mole_crop_paths = {}
        for coord in mole_coords:
            x = coord[0]
            y = coord[1]
            for mole_img in mole_imgs:
                if (x, y) == (mole_img[1], mole_img[2]):
                    img = mole_img[0]
                    x = mole_img[1]
                    y = mole_img[2]
                    filepath = moles_path + "/x" + str(x) + "_y" + str(y) + ".jpg"
                    cv2.imwrite(filepath, img)
                    mole_crop_paths[(x, y)] = filepath

        return cv2.imencode('.jpg', im_with_moles)[1].tostring(), \
               keypoints, mole_coords, mole_crop_paths

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
