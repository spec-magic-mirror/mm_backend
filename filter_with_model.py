from sklearn.externals import joblib
from sklearn.externals.joblib import numpy_pickle
from sklearn.ensemble import RandomForestClassifier
import sys, os, cv2

if len(sys.argv) != 2:
    print("Run as 'python filter_with_model.py <trial_num>'")
    exit(0)

TRIAL = sys.argv[1]
TRIAL_DIR = "trials/" + TRIAL

rf_clf = joblib.load("rf_clf.pkl")
results = {0: [], 1:[]}
raw_paths = os.listdir(TRIAL_DIR)
for path in raw_paths:
    if not path.startswith("full_face") and path.endswith(".jpg"):
        img = cv2.imread(TRIAL_DIR + "/" + path).flatten()
        result = rf_clf.predict([img])
        results[result].append(path)
pprint(results)
