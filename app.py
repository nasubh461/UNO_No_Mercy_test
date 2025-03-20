from flask import Flask, render_template, request, jsonify, make_response
from flask_socketio import SocketIO, join_room, leave_room, emit
import random
import string
import secrets
import threading
import time
from flask_cors import CORS

from game import Unogame

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

rooms = {} # {'ROOMID' : {'player' : ['playername1','playername1'], 'started' : Flase, 'game' : None}}
sessions = {} # {'7c40fd705e1511751f6fbf5dd94936c7': {'username': 'player1', 'room_code': 'ANOLXK'}}
user_sockets = {} # {'_41gysDDBbyMJtXhAAAB': '7c40fd705e1511751f6fbf5dd94936c7'}
disconnect_timers = {}

def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def generate_session_token():
    return secrets.token_hex(16)

def start_thread(token, username, room_code):
        stop_event = threading.Event()
        thread = threading.Thread(target=delayed_removal, args=(token, stop_event, username, room_code))
        disconnect_timers[token] = (thread, stop_event)
        thread.start()

def stop_thread(token):
    if token in disconnect_timers:
        print(f"Cancelling removal of {token}...")
        disconnect_timers[token][1].set()  # Set the stop event
        disconnect_timers[token][0].join()  # Wait for the thread to finish
        del disconnect_timers[token]
    else:
        print(f"Thread {token} not found")

def delayed_removal(token, stop_event, username, room_code):
    print(f"Thread {token} started")

    # Starting a 30s timer
    for _ in range(30):
        if stop_event.is_set():
            print(f"User {username} with session token {token} rejoined, skipping removal.")
            return
        time.sleep(1)

    with app.app_context():    
        # Checking if room and username exists before removing
        if room_code in rooms and username in rooms[room_code]['players']:
            # Remove the disconnected player
            rooms[room_code]['players'].remove(username)

            # Case 1: Room is now empty
            if not rooms[room_code]['players']:
                print(f"Room {room_code} empty. Deleting and notifying.")
                socketio.emit("room_deleted", {"message": "Game ended as all players left"}, room=room_code)
                del rooms[room_code]
            else:
                # Case 2: Game started and only one player remains
                if rooms[room_code]['started'] and len(rooms[room_code]['players']) == 1:
                    print(f"Single player left in started game. Deleting room {room_code}.")
                    socketio.emit("room_deleted", {"message": "Game ended as players left"}, room=room_code)
                    del rooms[room_code]

        # Cleanup session and timers
        if token in sessions:
            del sessions[token]
        if token in disconnect_timers:
            del disconnect_timers[token]

        print(f"User {username} with  permanently removed after 30 sec of inactivity.")            

        if room_code in rooms:                                
            socketio.emit("update_players", {"players": rooms[room_code]['players']}, room=room_code)

        print(f"Thread {token} stopped")

def handle_special_effects(game, card, player, color):
    # Implement special card logic here
    if card['type'] == 'Reverse':
        game.reverse_player()
    elif card['type'] == 'Skip':
        game.next_player()
    elif card['type'] == 'Draw Two':
        game.stacked_cards += 2
    elif card['type'] == 'Draw Four':
        game.stacked_cards += 4
    elif card['type'] == 'Draw Six':
        game.stacked_cards += 6
    elif card['type'] == 'Draw Ten':
        game.stacked_cards += 10
    elif card['type'] == 'Reverse Draw Four':
        game.stacked_cards += 4
        game.reverse_player()
    elif card['type'] == 'Discard All of Color':
        valid_color_index = game.find_valid_color_index(player, color)
        print("Disacrd all color indexes", valid_color_index)
        temp_card = game.discard_pile.pop()
        while len(valid_color_index) != 0:
            card = game.hands[player].pop(int(valid_color_index[0]))
            game.discard_pile.append(card)
            valid_color_index = game.find_valid_color_index(player, color)
            print("Disacrd all color indexes 2", valid_color_index)
        game.discard_pile.append(temp_card)
        game.playing_color = temp_card['color']          
    elif card['type'] == 'Skip All':
        game.skip_all()
    

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/create_room', methods=['POST'])
def create_room():
    data = request.get_json()
    player_name = data.get('username')
    room_code = generate_room_code()
    session_token = generate_session_token()

    if room_code not in rooms:
        rooms[room_code] = {'players': [], 'started': False, 'game': None} #
    
    rooms[room_code]['players'].append(player_name)
    sessions[session_token] = {'username': player_name, 'room_code': room_code}
    print(sessions)
    response = make_response(jsonify({'room_code': room_code, 'session_token': session_token}))
    return response

@app.route('/join_room', methods=['POST'])
def join_room_route():
    data = request.json
    room_code = data.get('room_code')
    username = data.get('username')

    if room_code in rooms:
        if rooms[room_code]['started']:
            return jsonify({'status': 'game_started'})
        
        if username in rooms[room_code]['players']:  
            return jsonify({'status': 'duplicate'})
        
        session_token = generate_session_token()
        rooms[room_code]['players'].append(username)
        sessions[session_token] = {'username': username, 'room_code': room_code}
        print(sessions)
        response = make_response(jsonify({'status': 'joined', 'session_token': session_token}))
        return response
    else:
        return jsonify({'status': 'room_not_found'})   

@app.route('/room/<room_code>')
def room(room_code):
    if room_code in rooms:
        return render_template('room.html', room_code=room_code)
    else:
        return "Room not found", 404
    
@app.route('/get_username', methods=['POST'])
def get_username():
    data = request.get_json()
    session_token = data.get('session_token')

    if session_token in sessions:
        return jsonify({'status': 'success', 'username': sessions[session_token]['username']})
    else:
        return jsonify({'status': 'invalid'})

@app.route('/start_game', methods=['POST'])
def start_game():
    data = request.json
    room_code = data.get('room_code')
    username = data.get('username')

    if room_code in rooms and rooms[room_code]['players'][0] == username:
        if len(rooms[room_code]['players']) >= 2:
            rooms[room_code]['started'] = True

            game = Unogame(*rooms[room_code]['players'])
            rooms[room_code]['game'] = game

            player_hands = {player: game.get_player_hand(player) for player in rooms[room_code]['players']}
            for sid, session_token in user_sockets.items():
                if session_token in sessions:
                    player_name = sessions[session_token]['username']
                    if player_name in player_hands:
                        socketio.emit("your_hand", {
                            "hand": player_hands[player_name],
                            "discard_top": game.top_card() if game.discard_pile else None,
                            "cards_left": game.cards_remaining()
                        }, room=sid)

            socketio.emit("game_started", {
                "shuffled_players": game.players, 
                "cards_left": game.cards_remaining(),
                "discard_top": game.top_card() if game.discard_pile else None
            }, room=room_code)

            # Broadcast game update
            socketio.emit("game_update", {
                "current_player": game.current_players_turn(),
                "discard_top": game.top_card(),
                "cards_left": game.cards_remaining()
            }, room=room_code)

            return jsonify({'status': 'started'})
        return jsonify({'status': 'not_enough_players'})
    return jsonify({'status': 'unauthorized'})

@app.route('/debug')
def debug():
    debug_rooms = {}
    for room_code, room_data in rooms.items():
        # Create a copy to avoid modifying the original data
        room_info = room_data.copy()
        if room_info['game'] is not None:
            # Convert the game object to a dictionary
            room_info['game'] = room_info['game'].to_dict()
        debug_rooms[room_code] = room_info

    disconnect_timers_info = {}
    for token, (thread, event) in disconnect_timers.items():
        disconnect_timers_info[token] = {
            "thread_alive": thread.is_alive(),
            "event_set": event.is_set()
        }

    return jsonify({
        "rooms": debug_rooms,
        "sessions": sessions,
        "user_sockets": user_sockets,
        "disconnect_timers": disconnect_timers_info
    })

@socketio.on("draw_card")
def handle_draw_card(data):
    room_code = data.get('room')
    session_token = user_sockets.get(request.sid)
    
    if not session_token or room_code not in rooms:
        return
    
    game = rooms[room_code].get('game')
    player = sessions[session_token]['username'] 

    if game and game.deck:
        drawn_card = game.draw_card(player)

        if game.roulette == True:
            socketio.emit("roulette_draw", {'card_drawn' : drawn_card}, room=room_code)
            if drawn_card['color'] == game.playing_color:
                game.roulette = False
                socketio.emit("roulette_end", {}, room=request.sid)
                game.next_player()


        # Emit updates
        socketio.emit("card_drawn", {
            "player": player,
            "new_card": drawn_card,
            "cards_left": game.cards_remaining()
        }, room=request.sid)

        # Send updated hand to player
        player_hand = game.get_player_hand(player)
        emit("your_hand", {
            "hand": player_hand,
            "discard_top": game.top_card(),
            "cards_left": game.cards_remaining()
        }, room=request.sid)

        # Broadcast game update
        socketio.emit("game_update", {
            "current_player": game.current_players_turn(),
            "discard_top": game.top_card(),
            "cards_left": game.cards_remaining()
        }, room=room_code)


# Add to handle_play_card function
@socketio.on("play_card")
def handle_play_card(data):
    room_code = data.get('room')
    session_token = user_sockets.get(request.sid)
    
    if not session_token or room_code not in rooms:
        return
    
    game = rooms[room_code].get('game')
    player = sessions[session_token]['username']
    index = data.get('index')
    chosen_color = data.get('color', None)
    
    if not game or index is None:
        return
    if len(game.hands[player]) >= 25:
        if len(game.players) == 2:
            emit("game_over", {"winner": game.players[1], "discard_top": game.top_card()}, room=room_code)
            return
        game.deck = game.deck + game.hands[player]
        random.shuffle(game.deck)
        socketio.emit("player_disqualified", {"player": player}, room=room_code)
        game.hands[player] = []
        game.next_player()
        game.players.remove(player)
        return
    if game.roulette == False:
    
        # Validate turn
        if game.current_players_turn() != player:
            emit("play_error", {"message": "It's not your turn!"}, room=request.sid)
            return
        
        # Validate card index
        valid_indices = game.find_valid_cards(player)
        if int(index) not in valid_indices:
            emit("play_error", {"message": "Invalid card selection!"}, room=request.sid)
            return
        
        # Remove card from hand
        try:
            card = game.hands[player].pop(int(index))
        except IndexError:
            emit("play_error", {
                "message": "Invalid card index!"}, room=request.sid)
            return

        if len(game.hands[player]) == 0:
            game.discard_pile.append(card)
            
            # Send updated hand to player
            player_hand = game.get_player_hand(player)
            emit("your_hand", {
                "hand": player_hand,
                "discard_top": game.top_card(),
                "cards_left": game.cards_remaining()
            }, room=request.sid)

            emit("game_over", {"winner": player, "discard_top": game.top_card()}, room=room_code)

            return
        
        if card['color'] == 'Wild' and card['type'] == 'Color Roulette':
            game.roulette = True
            game.awaiting_color_choice = True
            game.playing_color = None
            print("Roulette mode activated")
        
        # Handle Wild cards
        if card['color'] == 'Wild' and card['type'] != 'Color Roulette':
            if not chosen_color or chosen_color not in ['Red', 'Blue', 'Green', 'Yellow']:
                emit("play_error", {"message": "Please select a valid color!"}, room=request.sid)
                game.hands[player].append(card)  # Return card to hand
                return
            game.playing_color = chosen_color
        else:
            game.playing_color = card['color']
        
        # Add to discard pile
        game.discard_pile.append(card)
        
        # Handle special effects
        handle_special_effects(game, card, player, game.playing_color)
        
        # Move to next player
        game.next_player()
        
        # Broadcast game update
        socketio.emit("game_update", {
            "current_player": game.current_players_turn(),
            "discard_top": game.top_card(),
            "cards_left": game.cards_remaining()
        }, room=room_code)
        
        # Send updated hand to player
        player_hand = game.get_player_hand(player)
        emit("your_hand", {
            "hand": player_hand,
            "discard_top": game.top_card(),
            "cards_left": game.cards_remaining()
        }, room=request.sid)

        if game.roulette and game.awaiting_color_choice:
            current_player = game.current_players_turn()
            # Find the current player's socket
            for sid in user_sockets:
                token = user_sockets[sid]
                session_data = sessions.get(token)
                if session_data and session_data['room_code'] == room_code and session_data['username'] == current_player:
                    emit("roulette", {}, room=sid)
                    break
    
    else:
        socketio.emit("play_error", {"message": "You must draw cards until you get a card that matches the color choosen."}, room=request.sid)

@socketio.on("color_selected")
def handle_color_selected(data):
    room_code = data.get('room')
    color = data.get('color')

    game = rooms[room_code].get('game')
    if game and game.roulette and game.awaiting_color_choice:
        game.awaiting_color_choice = False
        game.playing_color = color

        # Broadcast game update
        socketio.emit("game_update", {
            "current_player": game.current_players_turn(),
            "discard_top": game.top_card(),
            "cards_left": game.cards_remaining()
        }, room=room_code)

@socketio.on("join_room")
def handle_join_room(data):
    room_code = data.get("room")
    username = data.get("username")
    session_token = data.get("session")

    print(session_token)
    print(user_sockets)
    print(sessions)
    print(rooms)       

    if room_code in rooms and not rooms[room_code]['started']:
        if username not in rooms[room_code]['players']:
            rooms[room_code]['players'].append(username)

    if session_token in disconnect_timers:
        stop_thread(session_token)
        print(f"User {username} rejoined within 30 sec. Canceling removal.")

    sessions[session_token] = {'username': username, 'room_code': room_code}
    user_sockets[request.sid] = session_token

    # Re-assigning new requesdt.sid to the old session token
    all_session_tokens = list(user_sockets.values())
    dublicate = 0
    for i in all_session_tokens:
        if session_token == i:
            dublicate += 1
    if dublicate >= 2:
        index_not_to_del = len(all_session_tokens) - 1 - all_session_tokens[::-1].index(session_token)
        for i, token in enumerate(all_session_tokens):
            if token == session_token and i != index_not_to_del:
                index_to_del = i
                token_to_delete = list(user_sockets.keys())[index_to_del]       
                del user_sockets[token_to_delete]    

    join_room(room_code)

    if rooms[room_code]['started'] == True:

        room_code = data.get('room')
        session_token = user_sockets.get(request.sid)

        game = rooms[room_code].get('game')
        player = sessions[session_token]['username']

        socketio.emit("game_update", {
            "current_player": game.current_players_turn(),
            "discard_top": game.top_card(),
            "cards_left": game.cards_remaining()
        }, room=room_code)
        
        # Send updated hand to player
        player_hand = game.get_player_hand(player)
        emit("your_hand", {
            "hand": player_hand,
            "discard_top": game.top_card(),
            "cards_left": game.cards_remaining()
        }, room=request.sid)

    print(user_sockets)
    print(sessions)
    print(rooms)
    emit("update_players", {"players": rooms[room_code]['players']}, room=room_code)

@socketio.on("leave_room")
def handle_leave_room(data):
    room_code = data.get("room")
    username = data.get("username")
    session_token = data.get("session")

    if room_code in rooms:
        # If the game has started, delete the entire room and all sessions
        if rooms[room_code]['started']:
            print(f"Game in {room_code} was active, deleting room and clearing all players' sessions.")

            tokens_to_delete = []
            sids_to_delete = []

            for player in rooms[room_code]['players']:
                for token, session_data in sessions.items():
                    if session_data["username"] == player:
                        tokens_to_delete.append(token)  # Collect token

                for sid, token in user_sockets.items():
                    if token in sessions and sessions[token]["username"] == player:
                        sids_to_delete.append(sid)  # Collect socket ID

            # Now delete sessions and sockets
            for token in tokens_to_delete:
                sessions.pop(token, None)  # Use pop to avoid KeyError

            for sid in sids_to_delete:
                user_sockets.pop(sid, None)
            
            emit("room_deleted", {"message": "Game ended as a player left"}, room=room_code)
            del rooms[room_code]  # Delete the room
            
            return  # Exit function early since room is deleted

    if room_code in rooms and username in rooms[room_code]['players']:
        rooms[room_code]['players'].remove(username)

        sessions.pop(session_token, None)
        user_sockets.pop(request.sid, None)

        # If room is empty, delete it
        if not rooms[room_code]['players']:  
            
            del rooms[room_code]

    leave_room(room_code)

    print("Updated Sessions:", sessions)
    print("Updated Rooms:", rooms)    
    print(rooms)
    emit("update_players", {"players": rooms.get(room_code, [])}, room=room_code)
    
@socketio.on("connect")
def handle_connect():
    print(f"Client connected: {request.sid}")

@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    print(f"Client transport close disconnected. SID: {sid}")

    if sid not in user_sockets:
        print(f"Socket ID {sid} not found in active sessions. Possible early disconnect.")
        return

    session_token = user_sockets.pop(sid, None)

    if not session_token or session_token not in sessions:
        print(f"Session token {session_token} not found or invalid.")
        return

    user_data = sessions.get(session_token, {})
    username = user_data.get("username")
    room_code = user_data.get("room_code")    
        
    if not username or not room_code:
        print("Invalid user data found, skipping cleanup.")
        return
    
    if room_code in rooms:
        if rooms[room_code]['players'][0] == username and rooms[room_code]['started'] == False:
            print("Room leader left, so deleting room")
            emit("room_deleted", {"message": "Game ended as a player left"}, room=room_code)
            del rooms[room_code]
            del sessions[session_token]
            return
    else:
        del sessions[session_token]
        print("Room leader left, so no room left")
        return   

    start_thread(session_token, username, room_code)

    print(f"User {username} disconnected. Waiting 30 sec before removal.")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000, debug=True, allow_unsafe_werkzeug=True)


# Todo:
# Implement 0 and 7 rule
# implement stacked draw cards
# When a player has no card in hand. Declare winner and delete room (winner declare is done, need to check if room is deleted)
# If a plyer has mopre then 25 cards remove player from game. If only one player left in game delete room
# implement poin system if last is any special card hard the situation correctly so correct point distribution. (in v2)