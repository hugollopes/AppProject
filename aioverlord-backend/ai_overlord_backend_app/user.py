import datetime
import logging
from ai_overlord_backend_app.globals import *
from ai_overlord_backend_app.database import mongo
from ai_overlord_backend_app.security import auth, generate_auth_token, token_expire, requires_roles
from bson.json_util import dumps
from flask import Blueprint, g
from flask import request, jsonify, abort
from passlib.apps import custom_app_context as pwd_context

# blueprint definition
get_user_route = Blueprint('get_user_route', __name__)
update_user_route = Blueprint('update_user_route', __name__)
create_user_route = Blueprint('create_user_route', __name__)
get_token_route = Blueprint('get_token_route', __name__)
buy_neuron_route = Blueprint('buy_neuron_route', __name__)
update_user_v2_route = Blueprint('updateUser', __name__)


@create_user_route.route("/createUser", methods=['POST'])
def create_user():
    username = request.json.get('username')
    password = request.json.get('password')
    role = request.json.get('role')
    user = mongo.db.users
    if username is None or password is None:
        return jsonify({'error': "argumentsMissing"}), 400
    if user.find_one({"username": username}) is not None:
        return jsonify({'error': "userAlreadyExists"}), 400
    timestamp = int(datetime.datetime.now().timestamp())
    for task in TASKS:
        task["status"] = "unassigned"

    user.insert({
        "username": username,
        "email": username,
        "password": pwd_context.encrypt(password),
        "credits": 10,
        "neurons": 1,
        "timestamp": timestamp,
        "role": role,
        "tasks": TASKS,
    })
    return jsonify({'username': username}), 201


@get_user_route.route("/getuser", methods=['POST'])
@auth.login_required
@requires_roles('user')
def get_user():
    users = mongo.db.users
    request_data = request.get_json()
    logging.debug("get user " + request_data["username"])
    cursor = users.find_one({"username": request_data["username"]})
    # calculate seconds between now and database.
    timestamp_db = int(cursor['timestamp'])
    timestamp = int(datetime.datetime.now().timestamp())
    # calculate saved ticks
    for x in range(timestamp - timestamp_db):
        cursor['credits'] = cursor['credits'] + cursor['neurons'] * 1
    logging.debug("ticks: " + str(timestamp - timestamp_db))
    cursor["timestamp"] = datetime.datetime.now().timestamp()
    mongo.db.users.save(cursor)
    return dumps(cursor)


@buy_neuron_route.route("/buy_neuron", methods=['POST'])
@auth.login_required
@requires_roles('user')
def buy_neuron():
    users = mongo.db.users
    request_data = request.get_json()
    logging.debug("buy neuron request dump")
    cursor = users.find_one({"username": request_data["username"]})
    if int(cursor['credits']) < COST_PER_NEURON:
        logging.debug("not enough credits")
        return "not enough credits"
    cursor["credits"] = cursor['credits'] - COST_PER_NEURON
    cursor["neurons"] = cursor['neurons'] + 1
    mongo.db.users.save(cursor)
    return "neuron purchased"


@update_user_route.route("/updateUserStatus", methods=['POST'])
def update_user_status():
    request_data = request.get_json()
    if request_data["username"] is None or request_data["password"] is None \
            or request_data["credits"] is None or request_data["neurons"] is None:
        abort(400)  # missing arguments
    user = mongo.db.users.find_one({"username": request_data["username"]})
    if user is None:
        return jsonify({'error': "user does not exist"}), 400
    user["credits"] = request_data["credits"]
    user["neurons"] = request_data["neurons"]
    user["role"] = request_data["role"]
    user["timestamp"] = datetime.datetime.now().timestamp()
    mongo.db.users.save(user)
    return jsonify({'status': 'user updated'}), 200


@update_user_route.route("/updateUser", methods=['POST'])
def update_user_v2():
    request_data = request.get_json()
    if request_data["username"] is None:
        abort(400)  # missing arguments
    fields_updated = []
    user = mongo.db.users.find_one({"username": request_data["username"]})
    if user is None:
        return jsonify({'error': "user does not exist"}), 400
    if 'topologies' in request_data:
        user["topologies"] = request_data["topologies"]
        fields_updated.append("topologies")
    mongo.db.users.save(user)
    return jsonify({'status': 'user fields updated:' + str(fields_updated)}), 200


@get_token_route.route("/gettoken", methods=['POST'])
@auth.login_required
def get_token():
    logging.debug("request dump" + dumps(request.get_json()))
    token = generate_auth_token(g.current_user_id, token_expire).decode('ascii')
    logging.debug("token: " + token)
    return jsonify({'token': token}), 200
