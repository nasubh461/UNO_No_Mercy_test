import random
from flask import Flask, jsonify, request

app = Flask(__name__)

# Card colors and values
COLORS = ['Red', 'Green', 'Blue', 'Yellow']
VALUES = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'Skip', 'Reverse', 'Draw Two']
SPECIAL_CARDS = ['Wild', 'Wild Draw Four']



# Generate deck
def generate_deck():
    deck = []
    for color in COLORS:
        for value in VALUES:
            deck.append((color, value))
            if value != '0':
                deck.append((color, value))
    for special in SPECIAL_CARDS:
        deck.extend([(special, None)] * 4)
    random.shuffle(deck)
    return deck


# Need to find a way to save game s