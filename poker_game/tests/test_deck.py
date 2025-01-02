import pytest
from poker_game.game.deck import Deck
from poker_game.game.card import Card

def test_deck_creation():
    deck = Deck()
    assert len(deck.cards) == 52

def test_deck_dealing():
    deck = Deck()
    card = deck.deal()
    assert isinstance(card, Card)
    assert len(deck.cards) == 51

def test_deck_shuffle():
    deck1 = Deck()
    deck2 = Deck()
    deck2.shuffle()
    # Note: There's a very small chance this could fail even with a proper shuffle
    assert [str(card) for card in deck1.cards] != [str(card) for card in deck2.cards] 