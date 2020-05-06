import os
import json
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta
from flask.json import JSONEncoder
from bson import ObjectId
from uuid import uuid4
from dotenv import load_dotenv


load_dotenv()

# HOST = 'localhost'
# client = MongoClient(HOST,27017)
HOST = os.getenv('HOST', '0.0.0.0')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')


client = MongoClient(HOST,
                     27017,
                     username=USERNAME,
                     password=PASSWORD,
                     authMechanism='SCRAM-SHA-1')


db = client.honeytips

app = Flask(__name__)


# class JSONEncoder(json.JSONEncoder):
#     def default(self, o):
#         if isinstance(o, ObjectId):
#             return str(o)
#         return json.JSONEncoder.default(self, o)


@app.route('/')
def welcom():
    return render_template('index.html')


@app.route('/write_tips', methods=['POST'])
def write_tips():
    tip = request.form['tips']
    expiration = datetime.utcnow() + timedelta(hours=24)
    sid = str(uuid4())
    tips = {
        'sid': sid,
        'tip': tip,
        'expiration': expiration,
        'like': 0,
        'unlike': 0

    }
    print(tips)
    db.tip.insert_one(tips)
    return jsonify({'result': 'success', 'msg': '꿀팁!'})


@app.route('/load_tips', methods=['GET'])
def load_tips():
    tips = list(db.tip.find({}, {'_id': 0}))
    # jsontips = json.dumps(tips)
    # tip = JSONEncoder().encode(tips)
    # print(tip)
    return jsonify({'result': 'success', 'tips': tips})


@app.route('/like', methods=['POST'])
def like():
    sid = request.form['sid']
    # print(sid)
    # likevalue = db.tip.find_one({'sid':sid})
    db.tip.update({'sid': sid}, {'$inc': {'like': 1}})
    tips = list(db.tip.find({'sid':sid}, {'_id': 0}))
    return jsonify({'result': 'success', 'msg': 'like','tips':tips})
    # new_like = likevalue['like']+1
    # db.tip.update_one({'sid': sid},{'$set':{'like': new_like}})


@app.route('/unlike', methods=['POST'])
def unlike():
    sid = request.form['sid']
    db.tip.update({'sid': sid}, {'$inc': {'unlike': 1}})
    return jsonify({'result': 'success', 'msg': 'unlike'})


if __name__ == "__main__":
    app.run(host='localhost', port=5000, debug='Ture')
