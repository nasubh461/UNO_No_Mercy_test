from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, join_room, leave_room, emit
from game import UnoGame
import random
import string


app = Flask(__name__)
socketio = SocketIO(app)

rooms = {}
def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/create_room', methods=['POST'])
def create_room():
    room_code = generate_room_code()
    game = UnoGame()
    rooms[room_code] = game
    return {'room_code': room_code}

@app.route('/join_room', methods=['POST'])
def join_room_route():
    room_code = request.json.get('room_code')
    username = request.json.get('username')
    if room_code in rooms:
        game = rooms[room_code]
        game.players.append(username)
        return {'status': 'joined'}
    else:
        return {'status': 'room_not_found'}

@socketio.on('join')
def handle_join(data):
    room_code = data['room_code']
    username = data['username']

    if room_code in rooms:
        game = rooms[room_code]
        if username not in game.players:
            game.players.append(username)

        join_room(room_code)

        # Broadcast updated player list to the room
        emit('update_players', {'players': game.players}, room=room_code)
        
@socketio.on('play_card')
def handle_play_card(data):
    room_code = data['room_code']
    username = data['username']
    card = data['card']
    game = rooms[room_code]
    game.play_card(username, card)
    game.next_turn()
    emit('update_game', {'players': game.players, 'current_turn': game.get_current_player()}, room=room_code)

@app.route('/room/<room_code>')
def room(room_code):
    if room_code in rooms:
        return render_template('room.html', room_code=room_code)
    else:
        return "Room not found", 404
    
# To be implementedn to close the room when the game is over or the room owner left the room
"""
@app.route('/close_room', methods=['POST'])
def close_room():
    # Get the room code from the request
    data = request.get_json()
    room_code = data.get('room_code')

    # Check if the room exists in the rooms dictionary
    if room_code in rooms:
        # Destroy/close the room by removing it from the dictionary
        del rooms[room_code]
        return {'status': 'room_closed', 'message': f'Room {room_code} has been closed.'}
    else:
        return {'status': 'room_not_found', 'message': 'The room does not exist.'}
"""

if __name__ == '__main__':
    socketio.run(app,host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)

# Remove the comment from the line below to run the app in production m
    #socketio.run(app, debug=True)


# Check
