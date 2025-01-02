from enum import StrEnum

class Card:
    class Suit(StrEnum):
        HEARTS = 'Hearts'
        DIAMONDS = 'Diamonds'
        CLUBS = 'Clubs'
        SPADES = 'Spades'
        
    class Rank(StrEnum):
        ACE = 'Ace'
        TWO = '2'
        THREE = '3'
        FOUR = '4'
        FIVE = '5'
        SIX = '6'
        SEVEN = '7'
        EIGHT = '8'
        NINE = '9'
        TEN = '10'
        JACK = 'Jack'
        QUEEN = 'Queen'
        KING = 'King'
    
    RANK_VALUES = {
        'Ace': 14,
        '2': 2,
        '3': 3,
        '4': 4,
        '5': 5,
        '6': 6,
        '7': 7,
        '8': 8,
        '9': 9,
        '10': 10,
        'Jack': 11,
        'Queen': 12,
        'King': 13,
    }
    
    
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit
        self.point_value = self.RANK_VALUES[rank]
    
    def __eq__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self.rank == other.rank and self.suit == other.suit
    
    def __hash__(self):
        return hash((self.rank, self.suit))
        
    def __str__(self):
        return f"{self.rank} of {self.suit}" 
    
    
if __name__ == "__main__":
    for suit in Card.Suit:
        for rank in Card.Rank:
            card = Card(rank, suit)
            print(card)