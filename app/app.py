from flask import Flask
from flask import jsonify
from flask import render_template
from pymongo import MongoClient

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/vancouver')
def vancouver():
    return render_template('map.html', itinerary=[
        {'title':'A','time':25,'sight':True},
        {'title':'B','time':15},
        {'title':'C','time':30,'sight':True},
    ])

@app.route('/vancouver/paths')
def vancouver_paths():
    mongo = MongoClient()
    paths = mongo['4h'].paths.find()
    data = [[[each['latitude'],each['longitude']] for each in path['path']] for path in paths]
    return jsonify({'city':'vancouver','paths':data})

@app.route('/vancouver/sights')
def vancouver_sights():
    mongo = MongoClient()
    sights = mongo['4h'].poi.find(fields={'_id':False})
    data = [each for each in sights]
    return jsonify({'city':'vancouver','sights':data})


if __name__ == '__main__':
    app.debug=True
    app.run()
    #app.run(host='192.168.1.17',port=1234)