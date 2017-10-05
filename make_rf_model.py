print("Importing...")

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
import cv2
import sys, os

DATA_COLLECTION_ROOT = "../data_collection/"
POS_SAMPLES = DATA_COLLECTION_ROOT + "pos_moles/cropped/"
NEG_SAMPLES = DATA_COLLECTION_ROOT + "neg_moles/cropped/"

print("Collecting samples...")
# Collect samples and sort them into positive and negative
# Augment data by having 4 rotations for each
pos_paths = []
neg_paths = []
for path in os.listdir(POS_SAMPLES):
    if path.endswith(".png"):
        pos_paths.append(POS_SAMPLES + path)

for path in os.listdir(NEG_SAMPLES):
    if path.endswith(".png"):
        neg_paths.append(NEG_SAMPLES + path)

sample_img_shape = cv2.imread(pos_paths[0]).shape

all_x = []
all_y = []

for img_path in pos_paths:
    img = cv2.imread(img_path)
    if img.shape == sample_img_shape:
        rotations = 4
        # augment data by rotating 90 degrees 3 times since we have so few positives
        for i in range(rotations):
            img_flattened = img.flatten()
            all_x.append(img_flattened)
            all_y.append(1)
            image_center = tuple(np.array(img.shape)/2)[:2]
            rot_mat = cv2.getRotationMatrix2D(image_center,90, 1.0)
            img = cv2.warpAffine(img, rot_mat, img.shape[:2],flags=cv2.INTER_LINEAR)
            img[0] = img[1]
            img[:,0] = img[:,1]

for img_path in neg_paths:
    img = cv2.imread(img_path)
    if img.shape == sample_img_shape:
        rotations = 4
        # augment data by rotating 90 degrees 3 times since we have so few positives
        for i in range(rotations):
            img_flattened = img.flatten()
            all_x.append(img_flattened)
            all_y.append(0)
            image_center = tuple(np.array(img.shape)/2)[:2]
            rot_mat = cv2.getRotationMatrix2D(image_center,90, 1.0)
            img = cv2.warpAffine(img, rot_mat, img.shape[:2],flags=cv2.INTER_LINEAR)
            img[0] = img[1]
            img[:,0] = img[:,1]

all_x = np.array(all_x)
all_y = np.array(all_y)

train_x = all_x
train_y = all_y

print("Training Random Forest Classifier...")
rf_clf = RandomForestClassifier(n_estimators=100, n_jobs=-1)
rf_clf.fit(train_x, train_y)
joblib.dump(rf_clf, 'rf_clf.pkl')

print("Done!")
