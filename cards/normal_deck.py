import random

class NormalDeck:
    def __init__(self):
        self.cards = [
            "Drink 1",
            "Drink 2",
            "Give 1",
            "Give 3",
            "Crowd Challenge",
            "Drink 2, Give 1",
            "Drink 1, Give 1",
            "Skip",
            "Drink 3",
            "Give 2",
            "Special Card"
            ]
    
    def add_card(self, card_name):
        if card_name and card_name not in self.cards:
            self.cards.append(card_name)
            
    def remove_card(self, card_name):
        if card_name in self.cards:
            self.cards.remove(card_name)
    
    def draw_cards(self, num):
        if len(self.cards) >= num:
            drawn_cards = random.sample(self.cards, num)
            return self.handle_special_cards(drawn_cards)
        return []
    
    def handle_special_cards(self, drawn_cards):
        """Muutetaan erikoiskortit halutuksi."""
        transformed_cards = []
        for card in drawn_cards:
            if card == "Crowd Challenge":
                transformed_cards.append(random.choice(["Waterfall", "Trivia Master", "Categories", "Red or Black"]))
            elif card == "Special Card":
                transformed_cards.append(random.choice(["Odds Drink", "Even Drink", "Odds Give", "Even Give"]))
            else:
                transformed_cards.append(card)
        return transformed_cards