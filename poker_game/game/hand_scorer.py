from enum import IntEnum, auto
from collections import Counter
from typing import List
from poker_game.game.card import Card

class HandType(IntEnum):
    HIGH_CARD = auto()
    PAIR = auto()
    TWO_PAIR = auto()
    THREE_OF_A_KIND = auto()
    STRAIGHT = auto()
    FLUSH = auto()
    FULL_HOUSE = auto()
    FOUR_OF_A_KIND = auto()
    STRAIGHT_FLUSH = auto()
    ROYAL_FLUSH = auto()

class HandScore:
    def __init__(self, cards: List[Card]):
        self.cards = cards  # 7 cards, not necessarily sorted
        self.value_counts = Counter([card.point_value for card in self.cards])
        self.sorted_values_and_counts = sorted(self.value_counts.items(), key=lambda x: x[0], reverse=True)
        self.suited_cards = {}
        for card in self.cards:
            self.suited_cards.setdefault(card.suit, []).append(card)
            
        self.hand_type, self.score, self.scoring_cards = self.score_hand()
        
        
    def __str__(self):
        return f"{self.hand_type.name}: {self.score} - {', '.join(str(card) for card in self.scoring_cards)}"
    
    
    def __repr__(self):
        return f"HandScore(hand_type={self.hand_type.name}, score={self.score}, scoring_cards={self.scoring_cards})"

    def __lt__(self, other: 'HandScore'):
        return self.score < other.score
    

    def score_hand(self) -> tuple[HandType, int, List[Card]]:
        """Score a poker hand using hole cards and community cards"""
        # Check from highest to lowest possible hands
        hand_type = HandType.HIGH_CARD
        score = 0
        scoring_cards = []
        if royal_flush := self.check_royal_flush():
            hand_type = HandType.ROYAL_FLUSH
            scoring_cards = royal_flush
        elif straight_flush := self.check_straight_flush():
            hand_type = HandType.STRAIGHT_FLUSH
            scoring_cards = straight_flush
        elif four_kind := self.check_four_of_a_kind():
            hand_type = HandType.FOUR_OF_A_KIND
            scoring_cards = four_kind
        elif full_house := self.check_full_house():
            hand_type = HandType.FULL_HOUSE
            scoring_cards = full_house
        elif flush := self.check_flush():
            hand_type = HandType.FLUSH
            scoring_cards = flush
        elif straight := self.check_straight():
            hand_type = HandType.STRAIGHT
            scoring_cards = straight
        elif three_kind := self.check_three_of_a_kind():
            hand_type = HandType.THREE_OF_A_KIND
            scoring_cards = three_kind
        elif two_pair := self.check_two_pair():
            hand_type = HandType.TWO_PAIR
            scoring_cards = two_pair
        elif pair := self.check_pair():
            hand_type = HandType.PAIR
            scoring_cards = pair
            
        if hand_type == HandType.HIGH_CARD:
            scoring_cards = sorted(self.cards, key=lambda x: x.point_value, reverse=True)[:5]
            
        weights = reversed([16 ** i for i in range(len(scoring_cards))])
        score = sum(card.point_value * weight for card, weight in zip(scoring_cards, weights))
        score += hand_type.value * 16 ** len(scoring_cards)
        
        return hand_type, score, scoring_cards

    def check_royal_flush(self) -> List[Card] | None:
        if straight_flush := self.check_straight_flush():
            if straight_flush[0].point_value == 14 and straight_flush[-1].point_value == 10:  # Ace high, 10 low
                return straight_flush
        return None

    def check_straight_flush(self) -> List[Card] | None:
        # Check each suit for a straight, return highest scoring straight
        # only possible for one suit so we can return first found
        # as check_straight returns the highest scoring straight
        for suit_cards in self.suited_cards.values():
            if len(suit_cards) >= 5:
                if straight := self.check_straight(suit_cards):
                    return straight
        return None

# Add helper functions for other hand types... 

    def check_four_of_a_kind(self) -> List[Card] | None:
        """Check for four of a kind.
        
        Returns:
            List[Card]: 5 cards in order: four matching cards followed by the highest kicker,
            or None if no four of a kind is found.
        """
        for value, count in self.sorted_values_and_counts:
            if count == 4:
                quads = [card for card in self.cards if card.point_value == value]
                kickers = sorted([card for card in self.cards if card.point_value != value], key=lambda x: x.point_value, reverse=True)[:1]
                return quads + kickers   
        return None

    def check_full_house(self) -> List[Card] | None:
        """Check for a full house.
        
        Returns:
            List[Card]: 5 cards in order: three matching cards followed by two matching cards
            (highest possible combination), or None if no full house is found.
        """
        # Find highest three of a kind
        triple_value = None
        for value, count in self.sorted_values_and_counts:
            if count >= 3:
                triple_value = value
                break
        
        if triple_value is None:
            return None
        
        # Find highest pair from remaining values
        pair_value = None
        for value, count in self.sorted_values_and_counts:
            if value != triple_value and count >= 2:
                pair_value = value
                break
        if pair_value is None:
            return None
            
        triple_cards = [card for card in self.cards if card.point_value == triple_value][:3]
        pair_cards = [card for card in self.cards if card.point_value == pair_value][:2]
        return triple_cards + pair_cards


    def check_flush(self) -> List[Card] | None:
        """Check for a flush amongs the 7 cards"""

        for suit_cards in self.suited_cards.values():
            if len(suit_cards) >= 5:
                return suit_cards
        return None

    def check_straight(self, card_subset: List[Card] = None) -> List[Card] | None:
        """Check for a straight amongst 5 or more cards"""
        # Sort cards by value
        if card_subset is None:
            card_subset = self.cards
        
        sorted_cards = sorted(card_subset, key=lambda x: x.point_value, reverse=True)
        all_point_values = set([card.point_value for card in sorted_cards])
        # Check for a straight in reverse order to return highest scoring straight:
        
        for i in range(len(sorted_cards) - 4):
            # current card would be highest in straight
            if sorted_cards[i].point_value >= 5:
                needed_values = set(range(sorted_cards[i].point_value, sorted_cards[i].point_value - 5, -1))
                # check to see if needed values are in all_point_values
                if needed_values.issubset(all_point_values):
                    # build list of cards for straight
                    straight_cards = []
                    for value in needed_values:
                        for card in sorted_cards:
                            if card.point_value == value:
                                straight_cards.append(card)
                                break
                    return sorted(straight_cards, key=lambda x: x.point_value, reverse=True)
            
        # Check for low ace straight
        needed_values = set([14, 2, 3, 4, 5])
        
        if needed_values.issubset(all_point_values):
            # build list of cards for straight
            straight_cards = []
            for value in needed_values:
                for card in sorted_cards:
                    if card.point_value == value:
                        straight_cards.append(card)
                        break
            return sorted(straight_cards, key=lambda x: x.point_value, reverse=True)
        
        return None

    def check_three_of_a_kind(self) -> List[Card] | None:
        """Check for three of a kind.
        
        Returns:
            List[Card]: 5 cards in order: three matching cards followed by the highest two kickers,
            or None if no three of a kind is found.
        """
        for value, count in self.sorted_values_and_counts:
            if count == 3:
                three_cards = [card for card in self.cards if card.point_value == value][:3]
                kickers = sorted([card for card in self.cards if card.point_value != value], key=lambda x: x.point_value, reverse=True)[:2]
                return three_cards + kickers
        return None


    def check_two_pair(self) -> List[Card] | None:
        """Check for two pair.
    
        Returns:
            List[Card]: 5 cards in order: two pairs of matching cards followed by the highest kicker,
            or None if no two pair is found.
        """
        pairs = []
        for value, count in self.sorted_values_and_counts:
            if count >= 2:
                pairs.append([card for card in self.cards if card.point_value == value][:2])
        if len(pairs) >= 2:
            kickers = [card for card in self.cards if card not in pairs[0] and card not in pairs[1]]
            highest_kicker = sorted(kickers, key=lambda x: x.point_value, reverse=True)[:1]
            return pairs[0] + pairs[1] + highest_kicker
        return None 

    def check_pair(self) -> List[Card] | None:
        """Check for a pair.
    
        Returns:
            List[Card]: 5 cards in order: two matching cards followed by the highest three kickers,
            or None if no pair is found.
        """
        for value, count in self.sorted_values_and_counts:
            if count == 2:
                pair_cards = [card for card in self.cards if card.point_value == value][:2]
                kickers = [card for card in self.cards if card.point_value != value]
                return pair_cards + sorted(kickers, key=lambda x: x.point_value, reverse=True)[:3]
        return None 


if __name__ == "__main__":
    player_cards = [
        Card(Card.Rank.ACE, Card.Suit.SPADES),
        Card(Card.Rank.TWO, Card.Suit.HEARTS),
    ]
    
    community_cards = [
        Card(Card.Rank.THREE, Card.Suit.SPADES),
        Card(Card.Rank.FOUR, Card.Suit.CLUBS),
        Card(Card.Rank.FIVE, Card.Suit.HEARTS),
        Card(Card.Rank.ACE, Card.Suit.CLUBS),
        Card(Card.Rank.THREE, Card.Suit.HEARTS),
    ]
    
    cards = player_cards + community_cards
    hand = HandScore(cards)
    print(hand)