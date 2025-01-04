import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from poker_game.game.game_logic import PokerGame, GamePhase
from poker_game.game.card import Card
from cairosvg import svg2png
import io

POKER_TABLE_GREEN = '#2C8B38'
DEFAULT_FONT = ('Arial', 35)
CARD_WIDTH = 175
class GameWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Poker Game")
        self.root.geometry("2880x1620")
        self.root.configure(bg=POKER_TABLE_GREEN)  # Poker table green
        
        # change root title size
        self.root.option_add('*Font', DEFAULT_FONT)
        # Initialize game logic
        self.game = PokerGame()
        
        # Load card images
        self.card_images: dict[Card, ImageTk.PhotoImage] = {}
        self.load_card_images()
        
        # Setup GUI
        self.setup_styles()
        self.setup_gui()
        
        # Add bindings for window resize
        self.resize_timer = None
        self.root.bind('<Configure>', self.on_window_resize)
        
        # Initialize card positions
        self.calculate_layout()
        
        # Add card label caches
        self.player_card_labels = []
        self.computer_card_labels = []
        self.community_card_labels = []
        
        # Initialize cached labels
        self.initialize_card_labels()
    
    def handle_action(self):
        if not self.game.game_phase:
            self.game.start_new_hand()
            self.enable_betting_controls()
            self.notification_label.config(text="New hand dealt")
        elif self.game.game_phase == GamePhase.FLOP:
            self.game.deal_flop()
            self.enable_betting_controls()
            self.notification_label.config(text="Flop dealt - Your turn to act")
        elif self.game.game_phase == GamePhase.TURN:
            self.game.deal_turn()
            self.enable_betting_controls()
            self.notification_label.config(text="Turn dealt - Your turn to act")
        elif self.game.game_phase == GamePhase.RIVER:
            self.game.deal_river()
            self.enable_betting_controls()
            self.notification_label.config(text="River dealt - Your turn to act")
        elif self.game.game_phase == GamePhase.SHOWDOWN:
            winner = self.game.determine_winner()
            self.game.award_pot(winner)
            self.notification_label.config(text=f"Winner is {winner} with {self.game.winner_hand}")
            self.game.advance_phase()
        elif self.game.game_phase == GamePhase.RESULT:
            self.game.start_new_hand()
            self.notification_label.config(text="New hand dealt")
            self.enable_betting_controls()

        self.update_display()
        self.update_action_button()

    def enable_betting_controls(self):
        """Enable betting controls and hide action button during betting rounds"""
        self.betting_frame.pack(pady=10)
        self.action_button.pack_forget()

    def disable_betting_controls(self):
        """Hide betting controls and show action button after betting round"""
        self.betting_frame.pack_forget()
        self.action_button.pack(pady=10)

    def handle_check_call(self):
        if self.game.current_bet > self.game.player_bet:
            # This is a call
            call_amount = self.game.current_bet - self.game.player_bet
            self.game.place_bet(call_amount, is_player=True)
        else:
            # This is a check
            pass
        
        self.update_display()
        self.computer_action()
        
        # If betting round is complete, advance to next phase
        if self.game.check_betting_round():
            self.game.advance_phase()
            self.disable_betting_controls()
            self.update_action_button()

    def update_action_button(self):
        """Update action button text based on current phase"""
        phase_texts = {
            GamePhase.FLOP: "Deal Flop",
            GamePhase.TURN: "Deal Turn",
            GamePhase.RIVER: "Deal River",
            GamePhase.SHOWDOWN: "Show Down",
            GamePhase.RESULT: "New Hand"
        }
        
        if self.game.game_phase in phase_texts:
            self.action_button.config(text=phase_texts[self.game.game_phase])

    def load_card_images(self):
        """Load all card images"""
        card_width = CARD_WIDTH
        images_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
        print(f"Loading cards from: {images_dir}")  # Debug print
        
        # Pre-calculate output size for all cards
        aspect_ratio = 1.4  # Standard poker card ratio
        output_height = int(card_width * aspect_ratio)
        
        # Load card back
        back_path = os.path.join(images_dir, 'back.svg')
        if os.path.exists(back_path):
            print(f"Loading card back from: {back_path}")  # Debug print
            self.card_back = self.load_and_resize_image(back_path, card_width, output_height)
        else:
            print(f"Card back not found at: {back_path}")  # Debug print
        
        # Load all card faces in a single batch
        for suit in Card.Suit:
            for rank in Card.Rank:
                card = Card(rank, suit)
                card_path = os.path.join(images_dir, f'{suit.value.lower()}_{rank.value.lower()}.svg')
                if os.path.exists(card_path):
                    self.card_images[card] = self.load_and_resize_image(card_path, card_width, output_height)
                else:
                    print(f"Card not found: {card_path}")  # Debug print

    def load_and_resize_image(self, path, width, height):
        """Load and resize an SVG image with pre-calculated dimensions"""
        # Convert SVG to PNG in memory with exact dimensions
        png_data = svg2png(url=path, output_width=width, output_height=height)
        
        # Create PIL Image from PNG data without additional resizing
        image = Image.open(io.BytesIO(png_data))
        return ImageTk.PhotoImage(image)

    def setup_gui(self):
        # Create main container frames with updated style
        self.notification_frame = ttk.Frame(self.root, style='Custom.TFrame')
        self.notification_frame.place(relx=0.5, rely=0.02, relwidth=0.8, anchor='n')
        
        self.computer_frame = ttk.Frame(self.root, style='Custom.TFrame')
        self.computer_frame.place(relx=0.5, rely=0.15, relwidth=0.8, relheight=0.2, anchor='n')
        
        self.community_frame = ttk.Frame(self.root, style='Custom.TFrame')
        self.community_frame.place(relx=0.5, rely=0.4, relwidth=0.8, relheight=0.2, anchor='n')
        
        self.player_frame = ttk.Frame(self.root, style='Custom.TFrame')
        self.player_frame.place(relx=0.5, rely=0.65, relwidth=0.8, relheight=0.2, anchor='n')
        
        self.controls_frame = ttk.Frame(self.root, style='Custom.TFrame')
        self.controls_frame.place(relx=0.5, rely=0.85, relwidth=0.8, anchor='n')
        
        # Notification area
        self.notification_label = ttk.Label(
            self.notification_frame,
            text="Welcome to Poker!",
            font=DEFAULT_FONT,
            foreground=POKER_TABLE_GREEN
        )
        self.notification_label.pack(pady=10)
        
        # Controls area (betting controls and action button)
        self.betting_frame = ttk.Frame(self.controls_frame)
        
        # Bet amount entry
        self.bet_var = tk.StringVar(value="20")
        self.bet_entry = ttk.Entry(
            self.betting_frame,
            textvariable=self.bet_var,
            width=10,
            font=DEFAULT_FONT
        )
        self.bet_entry.pack(side='left', padx=5)
        
        # Betting buttons
        self.check_button = ttk.Button(
            self.betting_frame,
            text="Check/Call",
            command=self.handle_check_call,
            style='Custom.TButton'
        )
        self.check_button.pack(side='left', padx=5)
        
        self.bet_button = ttk.Button(
            self.betting_frame,
            text="Bet/Raise",
            command=self.handle_bet_raise,
            style='Custom.TButton'
        )
        self.bet_button.pack(side='left', padx=5)
        
        self.fold_button = ttk.Button(
            self.betting_frame,
            text="Fold",
            command=self.handle_fold,
            style='Custom.TButton'
        )
        self.fold_button.pack(side='left', padx=5)
        
        # Action button
        self.action_button = ttk.Button(
            self.controls_frame,
            text="Deal",
            command=self.handle_action,
            style='Custom.TButton'
        )
        self.action_button.pack(pady=10)
        
        # Info labels
        self.info_frame = ttk.Frame(self.controls_frame)
        self.info_frame.pack(pady=10)
        
        self.pot_label = ttk.Label(
            self.info_frame,
            text="Pot: $0",
            font=DEFAULT_FONT
        )
        self.pot_label.pack(side='left', padx=20)
        
        self.chips_label = ttk.Label(
            self.info_frame,
            text="Your Chips: $1000",
            font=DEFAULT_FONT
        )
        self.chips_label.pack(side='left', padx=20)

    def handle_bet_raise(self):
        try:
            amount = int(self.bet_var.get())
            if amount >= self.game.min_bet:
                if self.game.place_bet(amount, is_player=True):
                    self.update_display()
                    self.computer_action()
        except ValueError:
            pass  # Invalid bet amount

    def handle_fold(self):
        self.notification_label.config(text="You folded - Computer wins the pot")
        # Award pot to computer
        self.game.award_pot("computer")
        self.game.start_new_hand()
        self.update_display()

    def computer_action(self):
        # Simple AI for now - just calls any bet
        if self.game.current_bet > self.game.computer_bet:
            call_amount = self.game.current_bet - self.game.computer_bet
            self.game.place_bet(call_amount, is_player=False)
            self.notification_label.config(text="Computer calls your bet")
        else:
            self.notification_label.config(text="Computer checks")
        self.update_display()

    def create_card_label(self, card, face_up=True):
        """Creates a card label directly on root window"""
        if face_up:
            image = self.card_images.get(card)
        else:
            image = self.card_back
            
        label = ttk.Label(self.root, image=image, style='Custom.TLabel')
        label.image = image  # Keep a reference!
        return label

    def initialize_card_labels(self):
        """Create and cache card labels for all possible positions"""
        # Create 2 labels each for player and computer hands
        for _ in range(2):
            player_label = ttk.Label(self.player_frame)
            computer_label = ttk.Label(self.computer_frame)
            self.player_card_labels.append(player_label)
            self.computer_card_labels.append(computer_label)
        
        # Create 5 labels for community cards
        for _ in range(5):
            community_label = ttk.Label(self.community_frame)
            self.community_card_labels.append(community_label)

    def update_display(self):
        print(f"Player hand: {self.game.player_hand}")
        print(f"Community cards: {self.game.community_cards}")
        print(f"Available card images: {len(self.card_images)}")
        
        # Get layout metrics
        card_width = CARD_WIDTH
        spacing = int(card_width * 0.5)
        
        # Update player cards
        for i, label in enumerate(self.player_card_labels):
            if i < len(self.game.player_hand):
                card = self.game.player_hand[i]
                image = self.card_images.get(card)
                if image:  # Add this check
                    print(f"Placing player card {i} with image")  # Debug
                    label.configure(image=image)
                    label.image = image  # Keep reference
                    # Calculate position relative to player_frame
                    x_pos = (self.player_frame.winfo_width() - (2 * card_width + spacing)) // 2 + i * (card_width + spacing)
                    label.place(x=x_pos, y=0)
                else:
                    print(f"No image found for player card {card}")  # Debug
            else:
                label.place_forget()
        
        # Update computer cards
        face_up = self.game.game_phase == GamePhase.RESULT
        for i, label in enumerate(self.computer_card_labels):
            if i < len(self.game.computer_hand):
                card = self.game.computer_hand[i]
                image = self.card_images.get(card) if face_up else self.card_back
                if image:  # Add this check
                    print(f"Placing computer card {i} with image")  # Debug
                    label.configure(image=image)
                    label.image = image
                    x_pos = (self.computer_frame.winfo_width() - (2 * card_width + spacing)) // 2 + i * (card_width + spacing)
                    label.place(x=x_pos, y=0)
                else:
                    print(f"No image found for computer card")  # Debug
            else:
                label.place_forget()
        
        # Update community cards
        if self.game.game_phase == GamePhase.PREFLOP:
            for label in self.community_card_labels:
                label.place_forget()
        else:
            # Fixed left-aligned positioning
            for i, label in enumerate(self.community_card_labels):
                if i < len(self.game.community_cards):
                    card = self.game.community_cards[i]
                    image = self.card_images.get(card)
                    if image:
                        print(f"Placing community card {i} with image")
                        label.configure(image=image)
                        label.image = image
                        # Calculate position from left edge with fixed spacing
                        x_pos = i * (card_width + spacing)
                        label.place(x=x_pos, y=0)
                    else:
                        print(f"No image found for community card {card}")
                        label.place_forget()
                else:
                    label.place_forget()
        
        # Update text labels
        self.pot_label.configure(text=f"Pot: ${self.game.pot}")
        self.chips_label.configure(text=f"Your Chips: ${self.game.player_chips}")

    def calculate_layout(self):
        """This method is no longer needed as positions are calculated in update_display"""
        pass

    def on_window_resize(self, event):
        """Simplified resize handler"""
        if event.widget == self.root and self.resize_timer is None:
            self.resize_timer = self.root.after(100, self.delayed_resize)

    def delayed_resize(self):
        """Just update the display after resize"""
        self.update_display()
        self.resize_timer = None

    def setup_styles(self):
        style = ttk.Style()
        
        # Button style
        style.configure(
            'Custom.TButton',
            font=DEFAULT_FONT,
            padding=10
        )
        
        # Frame style
        style.configure(
            'Custom.TFrame',
            background=POKER_TABLE_GREEN
        ) 
        
        # Label style
        style.configure(
            'Custom.TLabel',
            background=POKER_TABLE_GREEN
        )