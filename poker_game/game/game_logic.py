from enum import Enum, auto
from poker_game.game.deck import Deck
from poker_game.game.hand_scorer import HandScore

class GamePhase(Enum):
    PREFLOP = auto()
    FLOP = auto()
    TURN = auto()
    RIVER = auto()
    SHOWDOWN = auto()
    RESULT = auto()
class PokerGame:
    def __init__(self):
        self.deck = Deck()
        self.player_hand = []
        self.computer_hand = []
        self.community_cards = []
        self.burned_cards = []
        self.game_phase = None
        self.pot = 0
        self.player_chips = 1000  # Starting chips
        self.computer_chips = 1000
        self.current_bet = 0
        self.player_bet = 0
        self.computer_bet = 0
        self.min_bet = 20  # Big blind
        self.is_player_big_blind = False
        self.winner = None
        self.winner_hand = None
        
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
        if self.game_phase != GamePhase.FLOP:
            return False
            
        # Burn a card and deal flop
        self.burned_cards.append(self.deck.deal())
        for _ in range(3):
            self.community_cards.append(self.deck.deal())
            
        return True
        
    def deal_turn(self):
        """Deal the turn card"""
        if self.game_phase != GamePhase.TURN:
            return False
            
        # Burn and deal turn
        self.burned_cards.append(self.deck.deal())
        self.community_cards.append(self.deck.deal())
        
        return True
        
    def deal_river(self):
        """Deal the river card"""
        if self.game_phase != GamePhase.RIVER:
            return False
            
        # Burn and deal river
        self.burned_cards.append(self.deck.deal())
        self.community_cards.append(self.deck.deal())
        
        return True
        
    def showdown(self):
        """Move to showdown phase"""
        if self.game_phase != GamePhase.SHOWDOWN:
            return False
        
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
        
        self.winner = "player" if player_score > computer_score else "computer"
        self.winner_hand = player_score.hand_type if self.winner == "player" else computer_score.hand_type
        
        print("winner: ", self.winner)
        print("winner_hand: ", self.winner_hand)
        
        if player_score > computer_score:
            return "player"
        elif computer_score > player_score:
            return "computer"
        else:
            return "tie"
        
    def place_bet(self, amount: int, is_player: bool) -> bool:
        """Place a bet for either player or computer"""
        if amount < 0:
            return False
            
        if is_player:
            if amount > self.player_chips:
                return False
            self.player_chips -= amount
            self.player_bet += amount
        else:
            if amount > self.computer_chips:
                return False
            self.computer_chips -= amount
            self.computer_bet += amount
            
        self.pot += amount
        self.current_bet = max(self.player_bet, self.computer_bet)
        return True
        
    def check_betting_round(self) -> bool:
        """Returns True if betting round is complete (bets are equal)"""
        return self.player_bet == self.computer_bet
        
    def award_pot(self, winner: str):
        """Award the pot to the winner"""
        if winner == "player":
            self.player_chips += self.pot
        elif winner == "computer":
            self.computer_chips += self.pot
        elif winner == "tie":
            # Split pot
            split = self.pot // 2
            self.player_chips += split
            self.computer_chips += split
    
        self.pot = 0 if self.pot % 2 == 0 else 1 # leftover chips go to the next pot
        self.player_bet = 0
        self.computer_bet = 0
        self.current_bet = 0
        
    def advance_phase(self):
        """Advance to the next phase after betting is complete"""
        if not self.check_betting_round():
            return False
            
        phase_transitions = {
            GamePhase.PREFLOP: GamePhase.FLOP,
            GamePhase.FLOP: GamePhase.TURN,
            GamePhase.TURN: GamePhase.RIVER,
            GamePhase.RIVER: GamePhase.SHOWDOWN,
            GamePhase.SHOWDOWN: GamePhase.RESULT,
            GamePhase.RESULT: GamePhase.PREFLOP
        }
        
        if self.game_phase in phase_transitions:
            self.game_phase = phase_transitions[self.game_phase]
            return True
        return False
        