import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from poker_game.game.game_logic import PokerGame, GamePhase
from poker_game.game.card import Card
from cairosvg import svg2png
import io

class GameWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Poker Game")
        self.root.geometry("1920x1080")
        self.root.configure(bg='#2C8B38')  # Poker table green
        
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
    
    def handle_action(self):
        if not self.game.game_phase:
            self.game.start_new_hand()
            self.action_button.config(text="Deal Flop")
        elif self.game.game_phase == GamePhase.PREFLOP:
            self.game.deal_flop()
            self.action_button.config(text="Deal Turn")
        elif self.game.game_phase == GamePhase.FLOP:
            self.game.deal_turn()
            self.action_button.config(text="Deal River")
        elif self.game.game_phase == GamePhase.TURN:
            self.game.deal_river()
            self.action_button.config(text="Show Down")
        elif self.game.game_phase == GamePhase.RIVER:
            self.game.showdown()
            self.action_button.config(text="New Hand")
        elif self.game.game_phase == GamePhase.SHOWDOWN:
            self.game.start_new_hand()
            self.action_button.config(text="Deal Flop")
            
        self.update_display()

    def load_card_images(self):
        """Load all card images"""
        card_width = 150  # Increased from 100 to 150
        images_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
        
        # Load card back
        back_path = os.path.join(images_dir, 'back.svg')
        if os.path.exists(back_path):
            self.card_back = self.load_and_resize_image(back_path, card_width)
        
        # Load all card faces
        for suit in Card.Suit:
            for rank in Card.Rank:
                card = Card(rank, suit)
                card_path = os.path.join(images_dir, f'{suit.value.lower()}_{rank.value.lower()}.svg')
                if os.path.exists(card_path):
                    self.card_images[card] = self.load_and_resize_image(card_path, card_width)

    def load_and_resize_image(self, path, desired_width):
        """Load and resize an SVG image while maintaining aspect ratio"""
        # Convert SVG to PNG in memory
        png_data = svg2png(url=path, output_width=desired_width)
        
        # Create PIL Image from PNG data
        image = Image.open(io.BytesIO(png_data))
        return ImageTk.PhotoImage(image)

    def setup_gui(self):
        # Simplified setup - we only need the main frame and action button
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.place(relx=0.5, rely=0.9, anchor='center')
        
        self.action_button = ttk.Button(
            self.main_frame,
            text="Deal",
            command=self.handle_action,
            style='Custom.TButton'
        )
        self.action_button.pack()

    def create_card_label(self, card, face_up=True):
        """Creates a card label directly on root window"""
        if face_up:
            image = self.card_images.get(card)
        else:
            image = self.card_back
            
        label = ttk.Label(self.root, image=image)
        label.image = image  # Keep a reference!
        return label

    def update_display(self):
        # Clear existing cards
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Label) and hasattr(widget, 'image'):
                widget.destroy()
        
        # Calculate starting x positions for each row of cards
        num_player_cards = len(self.game.player_hand)
        num_computer_cards = len(self.game.computer_hand)
        num_community_cards = len(self.game.community_cards)
        
        # Display player's cards
        start_x = self.layout['center_x'] - (num_player_cards - 1) * self.layout['card_spacing'] / 2
        for i, card in enumerate(self.game.player_hand):
            label = self.create_card_label(card, face_up=True)
            label.place(x=start_x + i * self.layout['card_spacing'], 
                       y=self.layout['player_y'], 
                       anchor='center')
        
        # Display computer's cards
        start_x = self.layout['center_x'] - (num_computer_cards - 1) * self.layout['card_spacing'] / 2
        for i, card in enumerate(self.game.computer_hand):
            face_up = self.game.game_phase == GamePhase.SHOWDOWN
            label = self.create_card_label(card, face_up=face_up)
            label.place(x=start_x + i * self.layout['card_spacing'], 
                       y=self.layout['computer_y'], 
                       anchor='center')
        
        # Display community cards
        if self.game.game_phase != GamePhase.PREFLOP:
            start_x = self.layout['center_x'] - (num_community_cards - 1) * self.layout['card_spacing'] / 2
            for i, card in enumerate(self.game.community_cards):
                label = self.create_card_label(card, face_up=True)
                label.place(x=start_x + i * self.layout['card_spacing'], 
                           y=self.layout['community_y'], 
                           anchor='center')

    def calculate_layout(self):
        """Calculate relative positions for all cards based on window size"""
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        
        # Get card dimensions from the first card image (they're all the same size)
        card_width = 150  # This matches what we set in load_card_images
        
        # Calculate maximum number of cards that could be displayed in a row (5 community cards)
        max_cards = 5
        min_spacing = 20  # Minimum pixels between cards
        
        # Calculate card spacing while ensuring all cards fit within window
        total_space_needed = (max_cards * card_width) + ((max_cards - 1) * min_spacing)
        available_width = window_width * 0.8  # Use 80% of window width
        
        # Adjust card spacing based on available width
        card_spacing = min(
            (available_width - card_width) / (max_cards - 1),  # Spacing to fill available width
            window_width * 0.08  # Original spacing calculation
        )
        
        # Store layout metrics
        self.layout = {
            'computer_y': window_height * 0.1,    # 10% from top
            'community_y': window_height * 0.4,    # 40% from top
            'player_y': window_height * 0.7,       # 70% from top
            'card_spacing': max(card_spacing, min_spacing),  # Use calculated spacing with minimum
            'center_x': window_width / 2,          # Center point for alignment
            'card_width': card_width               # Store card width for reference
        }

    def on_window_resize(self, event):
        """Handle window resize events with debouncing"""
        if event.widget == self.root:
            # Cancel the previous timer if it exists
            if self.resize_timer is not None:
                self.root.after_cancel(self.resize_timer)
            
            # Create new timer that will fire 80ms, after the last resize event
            self.resize_timer = self.root.after(80, self.delayed_resize)

    def delayed_resize(self):
        """Actually perform the resize operations"""
        self.calculate_layout()
        self.update_display()
        self.resize_timer = None

    def setup_styles(self):
        style = ttk.Style()
        
        # Button style
        style.configure(
            'Custom.TButton',
            font=('Arial', 25),
            padding=10
        )
        
        # Card frame style
        style.configure(
            'Card.TFrame',
            background='white',
            relief='raised',
            borderwidth=2
        ) 