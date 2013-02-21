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

HOURS = 60 * 60

app = Flask(__name__)

@app.route('/')
def home():
    fb_key = config['key']
    return render_template('index.html', facebook_key=fb_key)


@app.route('/login/<token>')
def login(token):
    session['fb'] = fb.extend_token(token)
    return redirect('/vancouver')


@app.route('/vancouver')
def vancouver(): 
    json = my_orienteering.itinerary(6*HOURS) 
    return render_template('map.html', 
        itinerary=json['walk'],
        seed=json['seed'])

@app.route('/me')
def demo():
    """
    For demo on other people's machine!
    """
    json = my_orienteering.itinerary(6*HOURS,me=True) 
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
    app.secret_key = str(config['secret'])
    app.run(host = config['host'], port = config['port'])
