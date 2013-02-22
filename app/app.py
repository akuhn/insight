"""
Main file.
"""
from flask import Flask
from flask import jsonify,render_template,request,session,redirect
from pymongo import MongoClient
import facebook
import random
import json

import my_randomwalk
import my_facebook as fb
from my_config import *


app = Flask(__name__)

@app.route('/')
def home():
    """
    Main page with huge cover of downtown Vancouver and Facebook button.
    """
    fb_key = config['fb']['key']
    return render_template('index.html', facebook_key=fb_key)


@app.route('/login/<token>')
def login(token):
    """
    Callback for Facebook login.
    """
    session['fb'] = fb.extend_token(token)
    return redirect('/vancouver')


@app.route('/vancouver')
def vancouver(): 
    """
    Displays map and asynchronously fetches itinerary.
    """
    token = None
    if 'fb' in session: token = session['fb']['token']
    return render_template('map.html',token=token)


@app.route('/me')
def demo():
    """
    Hard-wired itinerary for demo.
    """
    return render_template('map.html',token='me')


@app.route('/itinerary/<token>')
def itinerary(token):
    """
    Computes itinerary and serves it as json.
    """
    from my_routing import itinerary
    data = itinerary(token,1234)
    print '-'*40
    print "Serving an itinerary:"
    print ' => '.join(data['path'])
    print '{} hours'.format(data['time'])
    return jsonify(data)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/hello')
def hello_world():
    return 'Hello, worlds!'


if __name__ == '__main__':
    app.debug = config['debug']
    app.secret_key = str(config['fb']['secret'])
    app.run(host = config['host'], port = config['port'])
