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
    data = itinerary(token,1234)
    print '-'*40
    print "Serving an itinerary:"
    print ' => '.join(data['path'])
    print '{} hours'.format(data['time'])
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

# Handle premium memberships

@app.route('/premium')
def subscribe():
    key = config['stripe']['key']
    return render_template('premium.html',
        key=json.dumps(key))
    
@app.route('/stripe', methods=['POST'])
def charge():
    import stripe
    # set your secret key: remember to change this to your live secret key in production
    # see your keys here https://manage.stripe.com/account
    stripe.api_key = config['stripe']['secret']

    # get the credit card details submitted by the form
    token = request.form['stripeToken']

    # create the charge on Stripe's servers - this will charge the user's card
    charge = stripe.Charge.create(
        amount=1000, # amount in cents, again
        currency="usd",
        card=token,
        description="payinguser@example.com"
    )
    return render_template('charged.html')


if __name__ == '__main__':
    app.debug = config['debug']
    app.secret_key = str(config['secret'])
    app.run(host = config['host'], port = config['port'])
