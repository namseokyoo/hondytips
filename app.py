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

db2 = client.baaam

app = Flask(__name__)

# render template
@app.route('/')
def welcom():
    return render_template('index.html')

@app.route('/baaam')
def baaam():
    return render_template('baaam.html')

# write tips
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

# write Baaam
@app.route('/write_baaams', methods=['POST'])
def write_baaams():
    baaam = request.form['baaams']
    expiration = datetime.now(tz=pytz.utc) + timedelta(hours=24)
    sid = str(uuid4())
    baaams = {
        'sid': sid,
        'baaam': baaam,
        'expiration': expiration,
        'like': 0,
        'unlike': 0
    }
    db2.baaam.insert_one(baaams)
    return jsonify({'result': 'success', 'msg': 'Baaam!'})    

# load tips
@app.route('/load_tips', methods=['GET'])
def load_tips():
    tips = list(db.tip.find({}, {'_id': 0}))
    return jsonify({'result': 'success', 'tips': tips})

# load baaams
@app.route('/load_baaams', methods=['GET'])
def load_baaams():
    baaams = list(db2.baaam.find({}, {'_id': 0}))
    return jsonify({'result': 'success', 'baaams': baaams})

# like tips
@app.route('/like', methods=['POST'])
def like():
    sid = request.form['sid']
    # 좋아요 눌렀을 때 like 를 +1
    db.tip.update({'sid': sid}, {'$inc': {'like': 1}})
    # 현재 만료 시간을 불러온다.
    lifetime = db.tip.find({'sid':sid},{'_id': 0,'expiration':1})
    # 만료 시간을 10분 늘린다.
    addlifetime=list(lifetime)[0]['expiration']+timedelta(minutes=10)
    # 변경된 만료 시간 db에 업데이트
    db.tip.update({'sid': sid}, {'$set': {'expiration': addlifetime}})
    tips = list(db.tip.find({'sid': sid}, {'_id': 0}))
    return jsonify({'result': 'success', 'msg': 'like', 'tips': tips})
    # new_like = likevalue['like']+1
    # db.tip.update_one({'sid': sid},{'$set':{'like': new_like}})



# like baaams
@app.route('/baaamlike', methods=['POST'])
def baaamlike():
    sid = request.form['sid']
    # 좋아요 눌렀을 때 like 를 +1
    db.baaam.update({'sid': sid}, {'$inc': {'like': 1}})
    # 현재 만료 시간을 불러온다.
    lifetime = db2.baaam.find({'sid':sid},{'_id': 0,'expiration':1})
    # 만료 시간을 10분 늘린다.
    addlifetime=list(lifetime)[0]['expiration']+timedelta(minutes=10)
    # 변경된 만료 시간 db에 업데이트
    db2.baaam.update({'sid': sid}, {'$set': {'expiration': addlifetime}})
    baaams = list(db2.baaam.find({'sid': sid}, {'_id': 0}))
    return jsonify({'result': 'success', 'msg': 'like', 'baaams': baaams})
    # new_like = likevalue['like']+1
    # db.baaam.update_one({'sid': sid},{'$set':{'like': new_like}})    

# unlike tips
@app.route('/unlike', methods=['POST'])
def unlike():
    sid = request.form['sid']
    db.tip.update({'sid': sid}, {'$inc': {'unlike': 1}})
    lifetime = db.tip.find({'sid':sid},{'_id': 0,'expiration':1})
    addlifetime=list(lifetime)[0]['expiration']-timedelta(minutes=10)
    db.tip.update({'sid': sid}, {'$set': {'expiration': addlifetime}})
    return jsonify({'result': 'success', 'msg': 'unlike'})

# unlike baaams
@app.route('/baaamunlike', methods=['POST'])
def baaamunlike():
    sid = request.form['sid']
    db2.baaam.update({'sid': sid}, {'$inc': {'unlike': 1}})
    lifetime = db2.baaam.find({'sid':sid},{'_id': 0,'expiration':1})
    addlifetime=list(lifetime)[0]['expiration']-timedelta(minutes=10)
    db2.baaam.update({'sid': sid}, {'$set': {'expiration': addlifetime}})
    return jsonify({'result': 'success', 'msg': 'unlike'})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug='Ture')
