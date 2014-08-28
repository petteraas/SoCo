from flask import Flask, jsonify, request

try:
    import urlparse
except ImportError:
    from urllib import parse as urlparse

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


@app.route('/<player_name>', methods=["GET"])
def info(player_name):
    device = get_device_by_name(player_name)
    info = {}
    if isinstance(device, soco.SoCo):
        info = create_response_object_from_device(device)
    return jsonify(info)


@app.route('/<player_name>/current', methods=["GET"])
def current(player_name):
    device = get_device_by_name(player_name)
    track = device.get_current_track_info()
    return jsonify(track)


@app.route('/<player_name>/play', methods=["POST"])
def play(player_name):
    device = get_device_by_name(player_name)
    device.play()
    track = device.get_current_track_info()
    return jsonify(track)


@app.route('/<player_name>/play/<track>', methods=["POST"])
def play_track(player_name, track):
    device = get_device_by_name(player_name)
    play_from_queue(device, track)
    return jsonify(device.get_current_track_info())


@app.route('/<player_name>/stop', methods=["POST"])
def stop(player_name):
    device = get_device_by_name(player_name)
    return jsonify({'exit': device.stop()})


def play_from_queue(device, track):
    index = int(track)
    queue_length = get_queue_length(device)

    if is_index_in_queue(index, queue_length):
        index -= 1
        position = device.get_current_track_info()['playlist_position']
        current = int(position) - 1
        if index != current:
            device.play_from_queue(index)


def get_queue_length(device):
    return len(device.get_queue())


def is_index_in_queue(index, queue_length):
    if index > 0 and index <= queue_length:
        return True
    return False


def get_device_by_name(name):
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
