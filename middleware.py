from flask import Flask, request, make_response
import sys, base64, uuid
from mole_detector import MoleDetector
from bson import json_util
import json
from mole_db_api import MoleDB
import os
import datetime
from Calibrate import Mole_Tracker
from Crop import Cropper
from pprint import pprint

middleware = Flask(__name__)
db = MoleDB()


@middleware.route("/", methods=["GET", "POST"])
def root():
    return 0

@middleware.route("/get_test", methods=["GET"])
def get_test():
    return "Hello from the Mole Detector!\n"

@middleware.route("/get_mole_data", methods=["GET"])
def get_mole_data():
    user_firstname = "Mani"
    user_lastname = "Moles"
    user_id, db_error = db.find_user_id(user_firstname, user_lastname)
    mole_list = db.get_mole_list(user_id)
    return json.dumps(mole_list, default=json_util.default)

@middleware.route("/detect_moles", methods=["POST"])
def upload_image():
    error = {"error": ""}
    print "Got a request to detect moles"
    #TODO: add support for multiple users
    user_firstname = "Mani"
    user_lastname = "Moles"
    user_id, db_error = db.find_user_id(user_firstname, user_lastname)
    if db_error:
        error["error"] = db_error
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

    for orientation, image_storage in all_images.iteritems():
        filename = image_storage.filename
        #filename = type
        image = image_storage.read()
        #print filename 

        cropper = Cropper(base64.b64decode(image))
        cropped_img = cropper.crop()
        image = base64.b64encode(cropped_img)
        with open(filename, 'w') as image_file:
            image_file.write(base64.b64decode(image))

        md = MoleDetector(filename)
        moles_file, moles_keypoints, mole_coords, mole_crop_paths = md.map_moles()
        mole_b64 = base64.b64encode(moles_file)

        new_image = {"original": image, "moles": mole_b64}
        images['images'][orientation] = new_image

        # First check to make sure a previous entry exists
        mole_history = db.get_user_mole_history(user_id)
        prev_mole_ids = {}
        mole_pairs = {}
        if mole_history and mole_coords:
            # Get previous image and coordinates
            # image, prev_image: image format
            # coords, prev_coords: list([x,y])
            # NOTE: Images are currently Base 64 encoded for transmission purposes
            curr_image_fname = filename
            prev_image = db.get_prev_image(user_id, orientation, 'original')
            prev_image_fname = "tmp/prev_image.jpg"
            with open(prev_image_fname, 'w') as image_file:
                image_file.write(base64.b64decode(prev_image))

            #curr_coords = [[_mole["location"]["x"], _mole["location"]["y"]]
            #          for _mole in orientation_moles["moleData"]]
            curr_coords = mole_coords
            prev_coords = db.get_prev_coords(user_id, orientation)

            prev_mole_ids = {(coords[0], coords[1]): coords[2] for coords in prev_coords}

            print curr_coords
            print prev_coords
            print curr_image_fname
            print prev_image_fname
            tracker = Mole_Tracker(curr_image_fname, prev_image_fname,
                                   curr_coords, prev_coords)
            mole_pairs = tracker.track()
            pprint(mole_pairs)
            os.remove(curr_image_fname)
            os.remove(prev_image_fname)

        orientation_moles = {"orientation": orientation, "moleData": []}
        images["images"][orientation]["mole_crops"] = {}

        for coord in mole_coords:
            mole = {"location": {"x": 0, "y": 0}, "asymmetry": "", "size": 0, "shape": "", "color": [0, 0, 0],
                    "misc": {}}
            x = float(coord[0])
            y = float(coord[1])
            mole["location"]["x"] = x
            mole["location"]["y"] = y

            if prev_mole_ids and mole_pairs and (x,y) in mole_pairs:
                mole['mole_id'] = prev_mole_ids[(x,y)]
            else:
                # TODO: look in previous images to find these
                # for now we just assume they are new
                mole['mole_id'] = str(uuid.uuid4())

            orientation_moles["moleData"].append(mole)
            mole_crop_fname = mole_crop_paths[(int(x), int(y))]
            with open(mole_crop_fname, 'r') as image_file:
                mole_crop_img = base64.b64encode(image_file.read())
                images["images"][orientation]["mole_crops"][mole["mole_id"]] = mole_crop_img
                # Add images and mole data to database

        images_id = db.insert_images(images)
        all_moles["images_id"] = images_id
        all_moles["moles"].append(orientation_moles)


    db.update_user_mole_history(user_id, all_moles)

    #db.update_user_moles(user_id, _____)

    result = images['images']
    for key in result.keys():
        result[key] = result[key]['moles']

    result["error"] = error["error"]
    response = json.dumps(result)
    return response

if __name__ == "__main__":
    port = 5000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    middleware.run(host="0.0.0.0", port=port, debug=True)
