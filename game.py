from cards import deck as original_deck
import random

class Unogame:
    def __init__(self, *player_names):
        self.deck = original_deck.copy()
        random.shuffle(self.deck)
        self.discard_pile = []
        self.draw_stack = []
        self.playing_color = None
        self.roulette = False
        self.players = list(player_names)
        self.hands = {player: [] for player in self.players}
        self._init_discard_pile()
        self.distribute_cards()

    def _init_discard_pile(self):
        if self.deck:
            temp = self.deck.pop()
            while temp['color'] == 'Wild':
                self.deck.append(temp)
                random.shuffle(self.deck)
                temp = self.deck.pop()
            self.playing_color = temp['color']
            self.discard_pile.append(temp)        

    def distribute_cards(self):
        for player in self.players:
            self.hands[player] = [self.deck.pop() for _ in range(7)]       
    
    def get_player_hand(self, player):
        return self.hands.get(player, [])
    
    def cards_remaining(self):
        return len(self.deck)
    
    def current_players_turn(self):
        return self.players[0]
    
    def top_card(self):
        return self.discard_pile[-1]
    
    def draw(self, player):
        temp = self.deck.pop()
        self.hands[player].append(temp)
        return temp




# arr = ['sam', 'smith', 'john', 'friday']    
# game = Unogame(*arr)
# print(game.discard_pile)
# print(game.cards_remaining())
# #print(game.hands)
