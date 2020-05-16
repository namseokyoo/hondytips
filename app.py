import os
import json
import pytz
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta
from flask.json import JSONEncoder
from bson import ObjectId
from uuid import uuid4
from dotenv import load_dotenv


load_dotenv()

# HOST = 'localhost'
# client = MongoClient(HOST, 27017)
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


@app.route('/')
def welcom():
    return render_template('index.html')


@app.route('/write_tips', methods=['POST'])
def write_tips():
    tip = request.form['tips']
    expiration = datetime.now(tz=pytz.utc) + timedelta(hours=24)
    sid = str(uuid4())
    tips = {
        'sid': sid,
        'tip': tip,
        'expiration': expiration,
        'like': 0,
        'unlike': 0
    }
    db.tip.insert_one(tips)
    return jsonify({'result': 'success', 'msg': '꿀팁!'})


@app.route('/load_tips', methods=['GET'])
def load_tips():
    tips = list(db.tip.find({}, {'_id': 0}))
    return jsonify({'result': 'success', 'tips': tips})


@app.route('/like', methods=['POST'])
def like():
    sid = request.form['sid']
    # print(sid)
    # likevalue = db.tip.find_one({'sid':sid})
    db.tip.update({'sid':sid},{'$inc':{'expiration':timedelta(minutes=10)}})
    db.tip.update({'sid': sid}, {'$inc': {'like': 1}})
    tips = list(db.tip.find({'sid': sid}, {'_id': 0}))
    return jsonify({'result': 'success', 'msg': 'like', 'tips': tips})
    # new_like = likevalue['like']+1
    # db.tip.update_one({'sid': sid},{'$set':{'like': new_like}})


@app.route('/unlike', methods=['POST'])
def unlike():
    sid = request.form['sid']
    db.tip.update({'sid': sid}, {'$inc': {'unlike': 1}})
    return jsonify({'result': 'success', 'msg': 'unlike'})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug='Ture')
