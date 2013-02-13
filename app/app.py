from flask import Flask
from flask import jsonify,render_template,request,session,redirect
from pymongo import MongoClient
import random
import json

import orienteering

app = Flask(__name__)
app.secret_key = '???'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login/<token>')
def login(token):
    print token
    session['token'] = token
    return redirect('/vancouver')

@app.route('/vancouver')
def vancouver(): 
    time = 6 * 60 * 60 # hours
    n = random.randint(0,999999)
    json = orienteering.itinerary(time) 
    return render_template('map.html', 
        itinerary=json['walk'],
        seed=json['seed'])

@app.route('/hello')
def hello_world():
    return 'Hello, worlds!'

@app.route('/fb')
def facebook():
    return render_template('fb.html')

@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1',port=8080)
