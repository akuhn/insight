from flask import Flask
from flask import jsonify
from flask import render_template
from pymongo import MongoClient

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('map.html')

@app.route('/vancouver/paths.json')
def serve_json():
    mongo = MongoClient()
    paths = mongo['4h'].paths.find()
    data = [[[each['latitude'],each['longitude']] for each in path['path']] for path in paths]
    return jsonify({'city':'vancouver','paths':data})

if __name__ == '__main__':
    app.debug=True
    app.run()