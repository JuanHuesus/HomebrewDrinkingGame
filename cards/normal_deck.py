import random

class NormalDeck:
    def __init__(self):
        self.cards = []

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
        """Käsittelee erikoiskortit, jotka muuttavat käyttäytymistä tai laukaisevat toimintoja."""
        transformed_cards = []
        for card in drawn_cards:
            if card == "Surprise Card":
                # Muutetaan kortti "Drink 5" -kortiksi
                transformed_cards.append("Drink 5")
            elif card == "Crowd Challenge":
                # Pidetään kortti ennallaan, sillä se laukaisee toiminnon
                transformed_cards.append("Crowd Challenge")
            else:
                transformed_cards.append(card)
        return transformed_cards
