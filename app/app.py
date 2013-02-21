from flask import Flask
from flask import jsonify,render_template,request,session,redirect
from pymongo import MongoClient
import facebook
import random
import json
#
import my_randomwalk
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
    token = None
    if 'fb' in session: token = session['fb']['token']
    return render_template('map.html',token=token)


@app.route('/itinerary/<token>')
def itinerary(token):
    from my_routing import itinerary
    print 222
    data = itinerary(token,1234)
    print 333
    return jsonify(data)


@app.route('/me')
def demo():
    return render_template('map.html',token='me')


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
