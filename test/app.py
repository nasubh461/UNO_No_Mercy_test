from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    num_cards = 30 # Change this to any number of cards you want
    return render_template("index.html", num_cards=num_cards)

if __name__ == "__main__":
    app.run(debug=True)
