import datetime
import logging

from bson.json_util import dumps
from flask import Blueprint
from flask import request

from ai_overlord_backend_app.database import mongo

# blueprint definition
get_user_route = Blueprint('get_user_route', __name__)
save_user_route = Blueprint('save_user_route', __name__)
create_user_route = Blueprint('create_user_route', __name__)


@get_user_route.route("/getuser")
def get_user():
    users = mongo.db.users
    cursor = users.find_one({"name": "testUser1"})
    # calculate seconds between now and database.
    timestamp_db = int(cursor['timestamp'])
    timestamp = int(datetime.datetime.now().timestamp())
    # calculate saved ticks
    for x in range(timestamp - timestamp_db):
        cursor['credits'] = cursor['credits'] + 1 + cursor['neurons'] * 1
    logging.debug("ticks: " + str(range(timestamp - timestamp_db)))
    update_cursor = users.update({"name": "testUser1"},
                                 {
                                   "$set": {
                                     "timestamp": timestamp,
                                     "credits": cursor['credits']
                                   }
                                 })
    logging.debug("update_cursor: " + dumps(update_cursor))
    return dumps(cursor)


# todo validate post request
@save_user_route.route("/saveuser", methods=['POST'])
def save_user():
    request_data = request.get_json()
    users = mongo.db.users
    datetime_string = datetime.datetime.now().timestamp()
    cursor = users.update(
        {"name": request_data["name"]},
        {
            "name": request_data["name"],
            "credits": request_data["cash"],
            "neurons": request_data["neurons"],
            "timestamp": datetime_string
        },
        upsert=True
    )
    return dumps(cursor)


@create_user_route.route("/createuser")
def new_user():
    result = mongo.db.users.insert_one(
        {
            "name": "testUser1",
            "credits": 10,
            "neurons": 1,
            "timestamp": datetime.datetime.now().timestamp()
        }
    )
    return result