import streamlit as st
from treys import Card, Evaluator, Deck
import random


def get_card_options(exclude_cards=[]):
    suits = ['s', 'h', 'd', 'c']  # spades, hearts, diamonds, clubs
    ranks = '23456789TJQKA'
    all_cards = [f'{rank}{suit}' for rank in ranks for suit in suits]
    available_cards = [card for card in all_cards if card not in exclude_cards]
    return available_cards

def get_card_name(code):
    card_name_map = {
        's': 'Spades', 'h': 'Hearts', 'd': 'Diamonds', 'c': 'Clubs',
        'T': '10', 'J': 'Jack', 'Q': 'Queen', 'K': 'King', 'A': 'Ace'
    }
    return f"{card_name_map.get(code[0], code[0])} of {card_name_map[code[1]]}"

def simulate_hand(player_hand, community_cards, num_players, pot_size, bet_to_call, num_simulations=10000):
    evaluator = Evaluator()
    deck = Deck()

   
    player_hand_ints = [Card.new(card) for card in player_hand]
    community_cards_ints = [Card.new(card) for card in community_cards]
    
    known_cards_ints = player_hand_ints + community_cards_ints
    deck.shuffle()
    deck.cards = [card for card in deck.cards if card not in known_cards_ints]

    wins = 0
    folds = 0

    for _ in range(num_simulations):
        if len(deck.cards) < (num_players - 1) * 2 + (5 - len(community_cards_ints)):
            st.error("Not enough cards remaining to simulate with the current settings.")
            return None, None, None

        opponents_hands = [[deck.draw(), deck.draw()] for _ in range(num_players - 1)]
        while len(community_cards_ints) < 5:
            community_cards_ints.append(deck.draw())

       
        player_score = evaluator.evaluate(player_hand_ints, community_cards_ints)
        opponent_scores = [evaluator.evaluate(opp_hand, community_cards_ints) for opp_hand in opponents_hands]

        
        if all(player_score <= opp_score for opp_score in opponent_scores):
            wins += 1
        folds += sum(1 for _ in opponent_scores if random.random() < 0.5) 

    
    win_equity = wins / num_simulations
    fold_equity = folds / (num_simulations * (num_players - 1))
    total_potential_win = pot_size + bet_to_call
    expected_value = (win_equity * total_potential_win) - (bet_to_call * (1 - win_equity - fold_equity))

    return win_equity, fold_equity, expected_value


def main():
    st.title("Poker Equity Calculator")
    with st.expander("How to Use the Equity Calculator"):
        st.write("""
            **Instructions:**
            
            1. Enter the total number of players.
            2. Select the two cards that make up your hand.
            3. If community cards have been dealt, select them (up to five).
            4. Enter the current pot size.
            5. Enter the amount to call.
            6. Press "Calculate Equity" to see your hand's equity.
        """)

    num_players = st.number_input("Enter the number of players:", min_value=2, max_value=10, value=6)
    
    st.subheader("Select your hand:")
    player_hand_cards = st.multiselect("Choose two cards:", options=get_card_options(), format_func=get_card_name)
    player_hand = [card for card in player_hand_cards]  

    st.subheader("Select community cards (if any):")
    community_cards = st.multiselect("Choose community cards:", options=get_card_options(exclude_cards=player_hand), format_func=get_card_name)
    community_hand = [card for card in community_cards] 

    pot_size = st.number_input("Enter the current pot size:", min_value=0)
    bet_to_call = st.number_input("Enter the current bet to call:", min_value=0)

    if st.button("Calculate Equity"):
        if len(player_hand) == 2:
            try:
                win_equity, fold_equity, expected_value = simulate_hand(player_hand, community_hand, num_players, pot_size, bet_to_call)
                st.write(f"Your win equity: {win_equity * 100:.2f}%")
                st.write(f"Your fold equity: {fold_equity * 100:.2f}%")
                st.write(f"Expected value of call/bet: {expected_value:.2f}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
        else:
            st.error("Please select exactly two cards for your hand.")

if __name__ == "__main__":
    main()
