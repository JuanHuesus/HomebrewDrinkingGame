import random

class PenaltyDeck:
    def __init__(self):
        self.cards = [
            "Drink 1",
            "Drink 2",
            "Drink 3",
            "Drink 4",
            "Shot",
            "Shotgun"
        ]
    
    def add_penalty_card(self, card_name):
        if card_name and card_name not in self.cards:
            self.cards.append(card_name)
    
    def remove_penalty_card(self, card_name):
        if card_name in self.cards:
            self.cards.remove(card_name)
    
    def draw_penalty_card(self):
        """Arpoo yhden rangaistuskortin, jos niitä on saatavilla."""
        if self.cards:
            return random.choice(self.cards)
        return None
