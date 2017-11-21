from pymongo import MongoClient
import dateutil.parser
import cv2
import base64
from bson.objectid import ObjectId
from pprint import pprint

class MoleDB:
    def __init__(self):
        self.db = None
        try:
            client = MongoClient('localhost', 27017)
            self.db = client['MagicMirror']
        except Exception as e:
            print("Problem with MongoDB: " + e.message)

    def find_user_id(self, first_name, last_name):
        error = ""
        user_id = ""
        try:
            user_id = self.db.Users.find_one({"firstName": first_name})['_id']
        except:
            error = "Couldn't find user '" + first_name + "'"

        return user_id, error

    def insert_images(self, images):
        images_id = self.db.Images.insert(images)
        return images_id

    def update_user_mole_history(self, user_id, moles):
        result = self.db.Users.update_one({"_id": user_id}, {"$push": {"moleHistory": moles}})
        return result

    def get_user_mole_history(self, user_id):
        mole_history = []
        result = self.db.Users.find_one({"_id": user_id})['moleHistory']
        for h in result:
            #print h['date']
            date = dateutil.parser.parse(str(h['date']))
            images_id = h['images_id']
            moles = h['moles']
            #date = h['date']
            mole_history.append({"date": date, "moles": moles, "images_id":images_id})
        if mole_history:
            mole_history = sorted(mole_history, key=lambda x: x["date"])
        return mole_history

    def get_image(self, imageset_id, orientation, type='original'):
        image = self.db.Images.find_one({"_id": imageset_id})['images'][orientation][type]
        return image

    def get_prev_image(self, user_id, orientation, type='original'):
        mole_history = self.get_user_mole_history(user_id)
        prev_images_id = mole_history[-1]['images_id']
        prev_image = self.get_image(prev_images_id, orientation, type)
        return prev_image

    def get_prev_coords(self, user_id, orientation):
        mole_history = self.get_user_mole_history(user_id)
        prev_mole_sets = mole_history[-1]['moles']
        prev_images_id = mole_history[-1]['images_id']
        prev_moles = []
        for mole_set in prev_mole_sets:
            if mole_set["orientation"] == orientation:
                prev_moles = mole_set['moleData']
                break
        prev_coords = [[mole["location"]["x"], mole["location"]["y"], mole["mole_id"]] for mole in prev_moles]

        return prev_coords

    def get_mole_crop_img(self, images_id, orientation, mole_id):
        all_images = self.db.Images.find_one({"_id":images_id})["images"]
        mole_crop_imgs = all_images[orientation]["mole_crops"]
        mole_crop_img = mole_crop_imgs[mole_id]
        return mole_crop_img


    def get_mole_list(self, user_id):
        unique_moles = {}
        history = self.get_user_mole_history(user_id)
        for h in history:
            date = h['date']
            images_id = h['images_id']
            for moles in h['moles']:
                orientation = moles['orientation']
                if orientation not in unique_moles:
                    unique_moles[orientation] = {}
                for mole in moles["moleData"]:
                    mole_id = mole['mole_id']
                    mole_crop_img = self.get_mole_crop_img(images_id, orientation, mole_id)
                    mole_data = {"date": date, "color": mole['color'],
                                 "shape": mole['shape'], "location": mole['location'],
                                 "size": mole['size'], "mole_img": mole_crop_img}
                    if mole_id in unique_moles[orientation]:
                        unique_moles[orientation][mole_id].append(mole_data)
                    else:
                        unique_moles[orientation][mole_id] = [mole_data]
        return unique_moles
