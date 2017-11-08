import cv2
import dlib

class Cropper(object):
	"""docstring for Cropper"""
	def __init__(self, image):
		super(Cropper, self).__init__()
		self.image = image
		self.detector = dlib.get_frontal_face_detector()
		self.predictor =  dlib.shape_predictor("./shape_predictor_68_face_landmarks.dat")
		

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

	def crop(self):
		gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
		# detect faces in the grayscale image
		rects = self.detector(gray, 1)
		crop = None
		for rect in rects:
			(x, y, w, h) = self.rect_to_bb(rect)
			crop = self.image[y - 25: y + h + 25, x: x + w]
			# cv2.imwrite(log_path + "crop.png", crop)
			cv2.imwrite('crop.png', crop)
			
		return crop
'''
image = cv2.imread("./../MagicMirror/modules/MMM-Mole/log/test3.png")
print("image read")
cropper = Cropper(image)
cv2.imshow("output", cropper.crop())
cv2.waitKey(0)
cv2.destroyAllWindows()
'''


