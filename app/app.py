from flask import Flask
from flask import jsonify,render_template,request,session,redirect
from pymongo import MongoClient
import facebook
import random
import json
#
import my_orienteering
import my_facebook as fb
from my_config import db,config

app = Flask(__name__)
app.secret_key = '???'


@app.route('/')
def home():
    fb_key = config['key']
    return render_template('index.html', facebook_key=fb_key)


@app.route('/login/<token>')
def login(token):
    session['token'] = fb.extend_token(token)
    return redirect('/vancouver')


@app.route('/vancouver')
def vancouver(): 
    time = 6 * 60 * 60 # hours
    json = my_orienteering.itinerary(time) 
    return render_template('map.html', 
        itinerary=json['walk'],
        seed=json['seed'])


@app.route('/hello')
def hello_world():
    return 'Hello, worlds!'


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.debug = config['debug']
    app.run(host = config['host'], port = config['port'])
