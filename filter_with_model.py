from sklearn.externals import joblib
#from sklearn.externals.joblib import numpy_pickle
from sklearn.ensemble import RandomForestClassifier
from pprint import pprint
import sys, os, cv2
import json

if len(sys.argv) != 2:
    print("Run as 'python filter_with_model.py <trial_num>'")
    exit(0)

TRIAL = sys.argv[1]
TRIAL_DIR = "trials/" + TRIAL
THRESH = 0.75

rf_clf = joblib.load("rf_clf.pkl")
results = {0: [], 1:[], -1: []}
raw_paths = os.listdir(TRIAL_DIR)
for path in raw_paths:
    if not path.startswith("full_face") and path.endswith(".jpg"):
        img = cv2.imread(TRIAL_DIR + "/" + path).flatten()
        if img.shape[0] == 16428:
            #result = rf_clf.predict([img])
            #results[result[0]].append(path)
            prob = rf_clf.predict_proba([img])[0,1]
            if prob >= THRESH:
                results[1].append(path)
            else:
                results[0].append(path)
        else:
            results[-1].append(path)

with open("filter_results.json",'w') as f:
    json.dump(results, f)

pprint(results)
print("\nCOUNTS\n0:%d\n1:%d,E:%d" % (len(results[0]), len(results[1]), len(results[-1])))

for path in results[1]:
    cv2.imshow('mole',cv2.imread(TRIAL_DIR + "/" + path))
    cv2.waitKey(0)
