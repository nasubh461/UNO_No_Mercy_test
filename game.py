import random

class UnoGame:
    def __init__(self):
        self.players = []
        self.deck = []
        self.game_state = {
            'current_turn': 0,
            'direction': 1,  # 1 for clockwise, -1 for counter-clockwise
            'game_over': False
        }
        self.init_deck()

    def init_deck(self):
        colors = ['red', 'green', 'blue', 'yellow']
        values = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'skip', 'reverse', 'draw2']
        self.deck = [f'{color}_{value}.png' for color in colors for value in values]

        random.shuffle(self.deck)

    def deal_cards(self, num_cards=7):
        hands = {player: [] for player in self.players}
        for _ in range(num_cards):
            for player in self.players:
                hands[player].append(self.deck.pop())

        return hands

    def play_card(self, player, card):
        # Implement the rules for playing a card (e.g., matching color, value, etc.)
        pass

    def draw_card(self, player):
        # Draw a card from the deck and return it
        if self.deck:
            return self.deck.pop()
        else:
            self.game_state['game_over'] = True  # If the deck is empty, end the game
            return None

    def next_turn(self):
        self.game_state['current_turn'] = (self.game_state['current_turn'] + self.game_state['direction']) % len(self.players)

    def get_current_player(self):
        return self.players[self.game_state['current_turn']]

    def check_winner(self):
        # Check if any player has won
        for player in self.players:
            if len(player['hand']) == 0:
                return player
        return None
