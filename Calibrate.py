import numpy as np
import cv2
import dlib
from skimage import io
from sets import Set
import os
import inspect

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
		# Store and return four distance between mole and landmarks
		for i in xrange(len(moles)):
			dist_40 = np.sqrt((moles[i][0] - shape[40][0])**2 + (moles[i][1] - shape[40][1])**2)
			dist_43 = np.sqrt((moles[i][0] - shape[43][0])**2 + (moles[i][1] - shape[43][1])**2)
			distances[moles[i]] = [dist_40, dist_43]
		print(distances)
		return distances

	def match(self, distances1, distances2, ratio):
		mole_pairs = {}
		for mole1, dist1 in distances1.iteritems():
			for mole2, dist2 in distances2.iteritems():
				
				print(mole1)
				print(mole2)
				
				print(dist2)
				dist1 = [dist1[0] * ratio, dist1[1] * ratio]
				print(dist1)
				# print(dist2)
				if np.isclose(dist1, dist2, atol=10).all():
					mole_pairs[mole1] = mole2
					del(distances2[mole2])
					break
		return mole_pairs

	def track(self):
		self.detector = dlib.get_frontal_face_detector()
		self.predictor =  dlib.shape_predictor("./shape_predictor_68_face_landmarks.dat")
		shape1 = self.get_landmarks(self.gray1)
		shape2 = self.get_landmarks(self.gray2)
		distances1 = self.get_distance(shape1, self.moles1)
		distances2 = self.get_distance(shape2, self.moles2)
		land_mark_dist1 = np.sqrt((shape1[40][0] - shape1[43][0])**2 + (shape1[40][1] - shape1[43][1])**2)
		land_mark_dist2 = np.sqrt((shape2[40][0] - shape2[43][0])**2 + (shape2[40][1] - shape2[43][1])**2)
		ratio = land_mark_dist1 / land_mark_dist2
		mole_pairs = self.match(distances1, distances2, ratio)
		return mole_pairs

''' Example to use the code '''
'''
moles1 = [(608, 508), (652, 568), (806, 517)]
moles2 = [(565, 498), (605, 557), (756, 508)]
tracker = Mole_Tracker("./../log/test1.png", "./../log/test2.png", moles1, moles2)

mole_pairs = tracker.track()
print(mole_pairs)
color = 255
for m1, m2 in mole_pairs.iteritems():
	cv2.circle(tracker.gray1, (m1[0], m1[1]), 1, (0, 0, color), -1)
	cv2.circle(tracker.gray2, (m2[0], m2[1]), 1, (0, 0, color), -1)
	color -= 85
cv2.imshow("Output1", tracker.gray1)
cv2.imwrite('output1.png', tracker.gray1)
cv2.imshow("Output2", tracker.gray2)
cv2.imwrite('output2.png', tracker.gray2)

cv2.waitKey(0)
cv2.destroyAllWindows()
'''





