import random

class PenaltyDeck:
    def __init__(self):
        self.cards = [
            "Penalty Drink 1",
            "Penalty Drink 2",
            "Penalty Drink 3"
        ]
    
    def add_penalty_card(self, card_name):
        if card_name and card_name not in self.cards:
            self.cards.append(card_name)
    
    def remove_penalty_card(self, card_name):
        if card_name in self.cards:
            self.cards.remove(card_name)
    
    def draw_penalty_card(self):
        if self.cards:
            return random.choice(self.cards)
        return None
