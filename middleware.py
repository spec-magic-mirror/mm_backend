from flask import Flask, request, make_response
import sys, base64
from mole_detector import MoleDetector
import json
from pymongo import MongoClient
import os
import datetime
from pprint import pprint

middleware = Flask(__name__)
try:
    client = MongoClient('localhost', 27017)
    db = client['MagicMirror']
except Exception as e:
    print("Problem with MongoDB: " + e.message)

@middleware.route("/", methods=["GET", "POST"])
def root():
    return 0

@middleware.route("/get_test", methods=["GET"])
def get_test():
    return "Hello from the Mole Detector!\n"

@middleware.route("/detect_moles", methods=["POST"])
def upload_image():
    error = {"error": ""}
    print "Got a request to detect moles"
    #TODO: add support for multiple users
    user_firstname = "Mani"
    try:
        user_id = db.Users.find_one({"firstName": user_firstname})['_id']
    except:
        error["error"] = "Couldn't find user '" + user_firstname + "'"
        print error["error"]
        return json.dumps(error)

    timestamp = datetime.datetime.now()
    version = MoleDetector.version

    images = {"userId": user_id, "date": timestamp, "version": version, "images": {}}
    all_moles = {"date": timestamp, "images_id": "", "moles": []}

    all_images = request.files

    if len(all_images) == 0:
        error["error"] = "Didn't receive any images"
        print error["error"]
        return json.dumps(error)

    for type, image_storage in all_images.iteritems():
        filename = image_storage.filename
        #filename = type
        image = image_storage.read()
        print filename
        with open(filename, 'w') as image_file:
            image_file.write(base64.b64decode(image))

        md = MoleDetector(filename)
        os.remove(filename)
        moles_file, moles_keypoints = md.map_moles()
        mole_b64 = base64.b64encode(moles_file)

        new_image = {"original": image, "moles": mole_b64}
        images['images'][type] = new_image

        orientation_moles = {"orientation": type, "moleData": []}

        for keypoint in moles_keypoints:
            mole = {"location": {"x": 0, "y": 0}, "asymmetry": "", "size": 0, "shape": "", "color": [0, 0, 0],
                    "misc": {}}
            location = keypoint.pt
            mole["location"]["x"] = location[0]
            mole["location"]["y"] = location[1]
            orientation_moles["moleData"].append(mole)

        all_moles["moles"].append(orientation_moles)

    # Add images and mole data to database
    images_id = db.Images.insert(images)
    all_moles["images_id"] = images_id
    db.Users.update_one({"_id":user_id}, {"$push":{"moleHistory":all_moles}})
    result = images['images']
    for key in result.keys():
        result[key] = result[key]['moles']

    response = json.dumps(result)
    return response

if __name__ == "__main__":
    port = 5000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    middleware.run(host="0.0.0.0", port=port, debug=True)
