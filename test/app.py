from flask import Flask, render_template
from cards import deck  # Import the deck from cards.py

app = Flask(__name__)

@app.route("/")
def home():
    num_cards = 30  # Change this to any number of cards you want
    draw_deck = deck  # Use the deck as the draw deck
    return render_template("index.html", num_cards=num_cards, draw_deck=draw_deck)

if __name__ == "__main__":
    app.run(debug=True)
