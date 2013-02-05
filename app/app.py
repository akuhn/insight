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
        {'name': 'Vanier Park', 'time': 0}, {'time': 15}, {'name': u'HR MacMillan Space Centre', 'time': 5}, {'time': 10}, {'name': u'Vancouver Maritime Museum', 'time': 15}, {'time': 30}, {'name': u'Granville Island Public Market', 'time': 30}, {'time': 100}, {'name': u'South False Creek Seawall', 'time': 5}, {'time': 20}, {'name': u'Steam Clock', 'time': 10}, {'time': 30}, {'name': u'Marine Building', 'time': 5}, {'time': 30}, {'name': u'Christ Church Cathedral', 'time': 5}, {'time': 40}, {'name': u'Roedde House Museum', 'time': 10}, {'time': 65}, {'name': u'Second Beach & Third Beach', 'time': 5}, {'time': 30}, {'name': u'Lost Lagoon Nature House', 'time': 5}, {'time': 90}, {'name': u'Miniature Railway & Children\u2019s Farmyard', 'time': 5}, {'time': 20}, {'name': u'Brockton Point', 'time': 10}, {'time': 25}, {'name': u'Waterfront Station', 'time': 10}, {'time': 25}, {'name': u'Vancouver Art Gallery', 'time': 5}, {'time': 45}, {'name': u'Contemporary Art Gallery', 'time': 5}, {'time': 20}, {'name': u'Sunset Beach', 'time': 5}, {'time': 5}, {'name': u'Maple Tree Square', 'time': 10}, {'time': 5}, {'name': u'Dr Sun Yat-Sen Classical Chinese Garden & Park', 'time': 30}, {'time': 10}
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