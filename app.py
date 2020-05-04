import json
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta
from flask.json import JSONEncoder
from bson import ObjectId
from uuid import uuid4

client = MongoClient('localhost' ,27017)
db= client.honeytips


app = Flask(__name__)



# class JSONEncoder(json.JSONEncoder):
#     def default(self, o):
#         if isinstance(o, ObjectId):
#             return str(o)
#         return json.JSONEncoder.default(self, o)




@app.route('/')
def welcom():
    return render_template('index.html')


@app.route('/write_tips',methods=['POST'])
def write_tips():
    tip = request.form['tips']
    expiration = datetime.utcnow() +  timedelta(minutes=3)
    sid=str(uuid4())
    tips={
        'sid':sid,
        'tip':tip,
        'expiration':expiration,
        'like':0,
        'unlike':0

    }
    db.tip.insert_one(tips)
    return jsonify({'result':'success', 'msg':'꿀팁!'})

@app.route('/load_tips', methods=['GET'])
def load_tips():
    tips = list(db.tip.find({},{'_id':0}))
    # jsontips = json.dumps(tips)
    # tip = JSONEncoder().encode(tips)
    # print(tip)
    return jsonify({'result':'success','tips':tips})

@app.route('/like', methods=['POST'])
def like():
    sid = request.form['sid']
    # print(sid)
    # likevalue = db.tip.find_one({'sid':sid})
    db.tip.update({'sid':sid },{'$inc':{'like': 1 }})
    return jsonify({'result':'success', 'msg':'like'})
    # new_like = likevalue['like']+1
    # db.tip.update_one({'sid': sid},{'$set':{'like': new_like}})    

@app.route('/unlike', methods=['POST'])
def unlike():
    sid = request.form['sid']
    db.tip.update({'sid':sid },{'$inc':{'unlike': 1 }})
    return jsonify({'result':'success', 'msg':'unlike'})

if __name__ == "__main__":
    app.run('localhost', port=5001, debug=True)