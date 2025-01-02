import random
from poker_game.game.card import Card

class Deck:
    def __init__(self):
        self.suits = Card.Suit
        self.ranks = Card.Rank
        self.cards: list[Card] = []
        self.card_set: set[Card] = set()
        self.build()
    
    def build(self):
        self.cards = [Card(value, suit) for suit in self.suits for value in self.ranks]
        self.card_set = set(self.cards)
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def deal(self):
        if len(self.cards) > 0:
            dealt_card = self.cards.pop()
            self.card_set.remove(dealt_card)
            return dealt_card
        
    def return_card(self, card: Card) -> bool:
        if card not in self.card_set:
            self.cards.append(card)
            self.card_set.add(card)
            return True
        else:
            print(f"Warning: Card {card} is already in the deck")
            return False
    
    def return_cards(self, cards: list[Card]):
        for card in cards:
            self.return_card(card)
