import numpy as np
import cv2
import dlib
from skimage import io
from sets import Set
import os
import inspect
from pprint import pprint
from matplotlib import pyplot as plt
import itertools

class Mole_Tracker(object):
	"""
	Args:
		filename1 (str): first image's path
		filename2 (str): second image's path
		moles1 (array of (x,y) tuples): first image's moles coordinates
		moles2 (array of (x,y) tuples): second image's moles coordinates
	"""
	def __init__(self, filename1, filename2, moles1, moles2):
		super(Mole_Tracker, self).__init__()
		image1 = cv2.imread(filename1)
		self.gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
		image2 = cv2.imread(filename2)
		self.gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
		self.moles1 = moles1
		self.moles2 = moles2

	def rect_to_bb(self, rect):
		# take a bounding predicted by dlib and convert it
		# to the format (x, y, w, h) as we would normally do
		# with OpenCV
		x = rect.left()
		y = rect.top()
		w = rect.right() - x
		h = rect.bottom() - y

		# return a tuple of (x, y, w, h)
		return (x, y, w, h)

	def shape_to_np(self, shape, dtype="int"):
		# initialize the list of (x, y)-coordinates
		coords = np.zeros((68, 2), dtype=dtype)

		# loop over the 68 facial landmarks and convert them
		# to a 2-tuple of (x, y)-coordinates
		for i in range(0, 68):
			coords[i] = (shape.part(i).x, shape.part(i).y)

		# return the list of (x, y)-coordinates
		return coords

	def get_landmarks(self, gray):

		rects = self.detector(gray, 1)

		# loop over the face detections
		for (i, rect) in enumerate(rects):
			# determine the facial landmarks for the face region, then
			# convert the facial landmark (x, y)-coordinates to a NumPy
			# array
			shape = self.predictor(gray, rect)
			shape = self.shape_to_np(shape)
			return shape

	def get_distance(self, shape, moles):
		distances = {}
		# Store and return distances between moles and landmarks
		for i in xrange(len(moles)):
			dist_40 = np.sqrt((moles[i][0] - shape[40][0])**2 + (moles[i][1] - shape[40][1])**2)
			dist_43 = np.sqrt((moles[i][0] - shape[43][0])**2 + (moles[i][1] - shape[43][1])**2)
			dist_34 = np.sqrt((moles[i][0] - shape[34][0])**2 + (moles[i][1] - shape[34][1])**2)
			distances[tuple(moles[i])] = [dist_40, dist_43, dist_34]
		return distances

	def match_by_dist(self, moles_a, moles_b, ratio):
		# for i in xrange(len(self.moles2)):
		# 	self.moles2[i] = [self.moles2[i][0] * ratio, self.moles2[i][1] * ratio, self.moles2[2]]
		if len(moles_a) >= len(moles_b):
			matchings = [zip(x, moles_b) for x in itertools.permutations(moles_a, len(moles_b))]
		else:
			matchings = [zip(x, moles_a) for x in itertools.permutations(moles_b, len(moles_a))]

		distances = []
		for matching in matchings:
			total_dist = 0
			for pair in matching:
				# total_dist += euclidean_distance(pair[0], pair[1])
				total_dist += np.sqrt((pair[0][0] - pair[1][0] * ratio) ** 2 + (pair[0][1] - pair[1][1] * ratio) ** 2)
			distances.append(total_dist)
		min_dist_i = distances.index(min(distances))

		best_matching = matchings[min_dist_i]

		if len(moles_a) < len(moles_b):
			best_matching = [[pairs[1], pairs[0]] for pairs in best_matching]

		return best_matching

	def match(self, distances1, distances2, ratio):
		mole_pairs = {}
		for mole1, dists1 in distances1.iteritems():
			for mole2, dists2 in distances2.iteritems():
				dists1 = [dists1[0] * ratio, dists1[1] * ratio, dists1[2] * ratio]
				if np.isclose(dists1, dists2, atol=30).all():
					if mole1 in mole_pairs:
						mole_pairs[mole1].append(mole2)
					else:
						mole_pairs[mole1] = []
						mole_pairs[mole1].append(mole2)
		# TODO: choose the min max among the pool

		return mole_pairs

	def track(self):
		self.detector = dlib.get_frontal_face_detector()
		self.predictor =  dlib.shape_predictor("./shape_predictor_68_face_landmarks.dat")
		# cv2.imwrite("tmp/gray1.jpg", self.gray1)
		# cv2.imwrite("tmp/gray2.jpg", self.gray2)
		shape1 = self.get_landmarks(self.gray1)
		shape2 = self.get_landmarks(self.gray2)
		distances1 = self.get_distance(shape1, self.moles1)
		distances2 = self.get_distance(shape2, self.moles2)
		land_mark_dist1 = np.sqrt((shape1[40][0] - shape1[43][0])**2 + (shape1[40][1] - shape1[43][1])**2)
		land_mark_dist2 = np.sqrt((shape2[40][0] - shape2[43][0])**2 + (shape2[40][1] - shape2[43][1])**2)
		# land_mark_dist2 = np.sqrt((shape2[34][0] - shape2[34][0])**2 + (shape2[34][1] - shape2[34][1])**2)
		ratio = land_mark_dist1 / land_mark_dist2
		# mole_pairs = self.match(distances1, distances2, ratio)

		print("Moles 1")
		pprint(self.moles1)
		print("Moles 2")
		pprint(self.moles2)

		mole_pairs = self.match_by_dist(self.moles1, self.moles2, ratio)
		mole_dict = {}
		for pair in mole_pairs:
			mole_dict[tuple(pair[0])] = pair[1]

		print("Mole Dict")
		pprint(mole_dict)

		# Convert coords to ints
		mole_dict = {(int(k[0]), int(k[1])):(int(v[0]), int(v[1]), v[2]) for k, v in mole_dict.iteritems()}
		return mole_dict

''' Example to use the code '''

# moles1 = [(608, 508, 1), (652, 568, 2), (806, 517, 3)]
# moles2 = [(565, 498, 1), (605, 557, 2), (756, 508, 3)]
# tracker = Mole_Tracker("./../MagicMirror/modules/MMM-Mole/log/test1.png", "./../MagicMirror/modules/MMM-Mole/log/test1.png", moles1, moles2)

# mole_pairs = tracker.track()

# print(mole_pairs)
# color = 255
# for m1, m2 in mole_pairs.iteritems():
# 	cv2.circle(tracker.gray1, (m1[0], m1[1]), 1, (0, 0, color), -1)
# 	cv2.circle(tracker.gray2, (m2[0], m2[1]), 1, (0, 0, color), -1)
# 	color -= 85
# cv2.imshow("Output1", tracker.gray1)
# cv2.imwrite('output1.png', tracker.gray1)
# cv2.imshow("Output2", tracker.gray2)
# cv2.imwrite('output2.png', tracker.gray2)

# cv2.waitKey(0)
# cv2.destroyAllWindows()
