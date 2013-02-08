from flask import Flask
from flask import jsonify
from flask import render_template
from pymongo import MongoClient
import random
import orienteering
import json

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/vancouver')
def vancouver(): 
    time = 6 * 60 * 60 # hours
    n = random.randint(0,999999)
    json = orienteering.itinerary(time) 
    return render_template('map.html', 
        itinerary=json['walk'],
        seed=json['seed'])

if __name__ == '__main__':
    app.debug=True
    app.run()
    #app.run(host='192.168.1.17',port=1234)