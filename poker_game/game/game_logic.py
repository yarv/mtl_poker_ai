from enum import Enum, auto
from poker_game.game.deck import Deck
from poker_game.game.hand_scorer import HandScore

class GamePhase(Enum):
    PREFLOP = auto()
    FLOP = auto()
    TURN = auto()
    RIVER = auto()
    SHOWDOWN = auto()

class PokerGame:
    def __init__(self):
        self.deck = Deck()
        self.player_hand = []
        self.computer_hand = []
        self.community_cards = []
        self.burned_cards = []
        self.game_phase = None
        self.pot = 0
        
    def start_new_hand(self):
        """Initialize a new hand"""
        # return all cards to the deck
        self.deck.return_cards(self.burned_cards)
        self.burned_cards = []
        self.deck.return_cards(self.community_cards)
        self.community_cards = []
        self.deck.return_cards(self.player_hand)
        self.player_hand = []
        self.deck.return_cards(self.computer_hand)
        self.computer_hand = []
        self.deck.shuffle()
        
        # Deal two cards to each player
        for _ in range(2):
            self.player_hand.append(self.deck.deal())
            self.computer_hand.append(self.deck.deal())
            
        self.game_phase = GamePhase.PREFLOP
        return True
        
    def deal_flop(self):
        """Deal the flop cards"""
        if self.game_phase != GamePhase.PREFLOP:
            return False
            
        # Burn a card
        self.burned_cards.append(self.deck.deal())
        # Deal 3 cards for the flop
        for _ in range(3):
            self.community_cards.append(self.deck.deal())
            
        self.game_phase = GamePhase.FLOP
        return True
        
    def deal_turn(self):
        """Deal the turn card"""
        if self.game_phase != GamePhase.FLOP:
            return False
            
        # Burn a card
        self.burned_cards.append(self.deck.deal())
        # Deal turn card
        self.community_cards.append(self.deck.deal())
        
        self.game_phase = GamePhase.TURN
        return True
        
    def deal_river(self):
        """Deal the river card"""
        if self.game_phase != GamePhase.TURN:
            return False
            
        # Burn a card
        self.burned_cards.append(self.deck.deal())
        # Deal river card
        self.community_cards.append(self.deck.deal())
        
        self.game_phase = GamePhase.RIVER
        return True
        
    def showdown(self):
        """Move to showdown phase"""
        if self.game_phase != GamePhase.RIVER:
            return False
            
        self.game_phase = GamePhase.SHOWDOWN
        self.determine_winner()
        return True 
        
    def determine_winner(self):
        """Determine the winner of the hand"""
        if self.game_phase != GamePhase.SHOWDOWN:
            return None
            
        player_score = HandScore(self.player_hand + self.community_cards)
        computer_score = HandScore(self.computer_hand + self.community_cards)
        
        print("player_score: ", player_score)
        print("computer_score: ", computer_score)
        
        
        print("winner: ", "player" if player_score > computer_score else "computer")
        
        if player_score > computer_score:
            return "player"
        elif computer_score > player_score:
            return "computer"
        else:
            return "tie"
        