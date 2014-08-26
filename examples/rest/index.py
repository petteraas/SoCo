from flask import Flask, jsonify, request
import urlparse

import soco

app = Flask(__name__)

devices = soco.discover()


@app.route('/', methods=["GET"])
def index():
    speakers = []
    for device in devices:
        speakers.append(create_response_object_from_device(device))

    response = {'speakers': speakers}
    return jsonify(response)


@app.route('/<player_name>/', methods=["GET"])
def info(player_name):
    device = getDeviceByName(player_name)
    info = create_response_object_from_device(device)
    return jsonify(info)


@app.route('/<player_name>/current', methods=["GET"])
def current(player_name):
    device = getDeviceByName(player_name)
    track = device.get_current_track_info()
    return jsonify(track)


def getDeviceByName(name):
    for device in devices:
        if device.player_name == name:
            return device


def create_link_from_device(device):
    try:
        urlparts = urlparse.urlsplit(request.url)
        path = urlparts.path
        if path is not '/{player_name}/'.format(player_name=device.player_name):
            path = '/{player_name}/'.format(player_name=device.player_name)

        return '{scheme}://{netloc}{path}'.format(
                scheme=urlparts.scheme,
                netloc=urlparts.netloc,
                path=path
                )
    except AttributeError:
        return '{url}'.format(url=request.url)


def create_response_object_from_device(device):
    return {
        'url': create_link_from_device(device),
        'name': device.player_name,
        'state': device.get_current_transport_info()['current_transport_state'],
        'current_track': device.get_current_track_info(),
        'mode': device.play_mode,
        'mixer': {
            'treble': device.treble,
            'bass': device.bass,
            'volume': device.volume
        }
    }


if __name__ == '__main__':
    app.run(debug=True)
