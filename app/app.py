from flask import Flask
from flask import jsonify
from flask import render_template
from pymongo import MongoClient
import orienteering
import json

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/vancouver')
def vancouver():
    data = orienteering.itinerary() 
    print data
    return render_template('map.html', 
        itinerary=data)

if __name__ == '__main__':
    app.debug=True
    app.run()
    #app.run(host='192.168.1.17',port=1234)