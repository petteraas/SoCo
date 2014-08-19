from __future__ import print_function, unicode_literals
import requests

from flask import Flask, url_for, jsonify

import soco

app = Flask(__name__)

devices = list(soco.discover())

@app.route('/<player_name>/current', methods=["GET"])
def current(player_name):
    device = getDeviceByName(player_name)
    track = device.get_current_track_info()
    return jsonify(track)


" @TODO: clean up "
def getDeviceByName(name):
    for device in devices:
        if device.player_name == name:
            return device

if __name__ == '__main__':
    app.run(debug=True)
