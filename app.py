import json
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta

client = MongoClient('localhost' ,27017)
db= client.honeytips


app = Flask(__name__)


@app.route('/')
def welcom():
    return render_template('index.html')


@app.route('/write_tips',methods=['POST'])
def write_tips():
    tip = request.form['tips']
    expiration = datetime.utcnow() +  timedelta(minutes=3)
    tips={
        'tip':tip,
        'expiration':expiration
    }
    db.tip.insert_one(tips)
    return jsonify({'result':'success', 'msg':'꿀팁!'})

@app.route('/load_tips', methods=['GET'])
def load_tips():
    tips = list(db.tip.find({}))
    print(tips)
    return jsonify({'result':'success','tips':tips})

# @app.route('/like',methods=['POST'])
# def like():
    

# @app.route('/unlike',methods=['POST'])
# def unlike():

if __name__ == "__main__":
    app.run('localhost', port=5001, debug=True)