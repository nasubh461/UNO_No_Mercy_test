import random
from cards import deck  # Assuming deck is a list of UNO cards

class Unogame:
    def __init__(self, num_players, *player_names):
        if len(player_names) != num_players:
            raise ValueError("Number of players must match the number of names provided.")
        
        self.players = list(player_names)
        self.hands = {player: [] for player in self.players}
        self.distribute_cards()
    
    def distribute_cards(self):
        if len(deck) < 7 * len(self.players):
            raise ValueError("Not enough cards in the deck to distribute.")
        
        for player in self.players:
            self.hands[player] = random.sample(deck, 7)
    
    def get_players(self):
        return self.players
    
    def get_player_hand(self, player):
        if player not in self.hands:
            raise ValueError("Player not found.")
        return self.hands[player]
    
# Example Usage
# game = Unogame(3, "Alice", "Bob", "Charlie")
# print(game.get_players())
# print(game.get_player_hand("Alice"))
