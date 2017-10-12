import sys, os
import cv2
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.externals import joblib

if len(sys.argv) != 2:
	print("Correct Usage: python test_filter.py <trial number>")

THRESH = 0.5
TRIAL_DIR = "../trials/" + sys.argv[1]

rf_clf = joblib.load("../rf_clf.pkl")

img_paths = []
for path in os.listdir(TRIAL_DIR):
	if path.endswith(".jpg") and path != "full_face.jpg":
		img_paths.append(TRIAL_DIR + "/" + path)

imgs = []
for path in img_paths:
	img = cv2.imread(path)
	imgs.append(img)

predictions = [1 if prediction > THRESH else 0 for prediction in rf_clf.predict_proba(img)[:,1]]

for i in range(len(predictions)):
	if predictions[i] == 1:
		print paths[i]
