import random
from collections import Counter
from itertools import combinations

def hand_rank_to_string(rank):
  rank_strings = {
    8: "Straight flush",
    7: "Four of a kind",
    6: "Full house",
    5: "Flush",
    4: "Straight",
    3: "Three of a kind",
    2: "Two pair",
    1: "One pair",
    0: "High card"
  }
  return rank_strings.get(rank, "Unknown")

def determine_best_hand(cards):
  best_rank = (0, [])
  for combo in combinations(cards, 5):
    rank = get_hand_rank(combo)
    if rank > best_rank:
      best_rank = rank
  return best_rank

suits = ["♣️", "♠️", "♦️", "♥️"]
ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
suit_colors = {
  "♣️": "\033[94m",  # Green
  "♦️": "\033[91m",  # Red
  "♥️": "\033[91m",  # Red
  "♠️": "\033[94m"   # Blue
}
reset_color = "\033[0m"
rank_to_value = {r: i for i, r in enumerate(ranks)}

# Function to generate a standard deck
def generate_deck():
    return [{"rank": rank, "suit": suit} for suit in suits for rank in ranks]

STANDARD_DECK = generate_deck()

# Function to shuffle the deck
def shuffle_deck(deck):
    random.shuffle(deck)
    return deck

# Printing
def print_card(card):
  suit_color = suit_colors[card['suit']]
  reset_color = "\033[0m"
  print(f"{suit_color}{card['rank']}{card['suit']}{reset_color}", end=" ")

def print_deck(deck=STANDARD_DECK, print_by_suit=False):
  if print_by_suit:
    for suit in suits:
      cards_of_suit = [card for card in deck if card['suit'] == suit]
      for card in cards_of_suit:
        print_card(card)
      print() 
  else:
    rows = [[] for _ in range(4)]
    for i, card in enumerate(deck):
      rows[i % 4].append(card)
    
    for row in rows:
      for card in row:
        print_card(card)
      print()

# Function to deal cards to all players
def deal_cards_all(num_players):
    deck = generate_deck()
    shuffled_deck = shuffle_deck(deck)
    players = {f"player_{i+1}": [shuffled_deck.pop(), shuffled_deck.pop()] for i in range(num_players)}
    flop = [shuffled_deck.pop() for _ in range(3)]
    turn = [shuffled_deck.pop()]
    river = [shuffled_deck.pop()]
    return {"flop": flop, "turn": turn, "river": river, "players": players}

# Function to get the hand rank
def get_hand_rank(hand):
    values = sorted([rank_to_value[card['rank']] for card in hand], reverse=True)
    rank_counts = Counter(values)
    suit_counts = Counter(card['suit'] for card in hand)

    flush = any(count >= 5 for count in suit_counts.values())

    # Identifying a straight
    straight = False
    for i in range(len(values) - 4):
        if values[i:i + 5] == list(range(values[i], values[i] - 5, -1)):
            straight = True
            values = values[i:i + 5]
            break
    # Special case: A-2-3-4-5 straight
    if not straight and set([12, 0, 1, 2, 3]).issubset(values):
        straight = True
        values = [4, 3, 2, 1, 0]

    four_of_a_kind = 4 in rank_counts.values()
    three_of_a_kind = 3 in rank_counts.values()
    pairs = list(rank_counts.values()).count(2)

    if flush and straight:
        return (8, values)  # Straight flush
    elif four_of_a_kind:
        four_kind_rank = [k for k, v in rank_counts.items() if v == 4][0]
        kicker = max([k for k in values if k != four_kind_rank])
        return (7, [four_kind_rank] * 4 + [kicker])  # Four of a kind
    elif three_of_a_kind and pairs:
        three_kind_rank = [k for k, v in rank_counts.items() if v == 3][0]
        pair_rank = [k for k, v in rank_counts.items() if v == 2][0]
        return (6, [three_kind_rank] * 3 + [pair_rank] * 2)  # Full house
    elif flush:
        flush_cards = [card for card in hand if suit_counts[card['suit']] >= 5]
        flush_values = sorted([rank_to_value[card['rank']] for card in flush_cards], reverse=True)
        return (5, flush_values[:5])  # Flush
    elif straight:
        return (4, values)  # Straight
    elif three_of_a_kind:
        three_kind_rank = [k for k, v in rank_counts.items() if v == 3][0]
        kickers = sorted([k for k in values if k != three_kind_rank], reverse=True)
        return (3, [three_kind_rank] * 3 + kickers[:2])  # Three of a kind
    elif pairs == 2:
        pair_ranks = sorted([k for k, v in rank_counts.items() if v == 2], reverse=True)
        kicker = [k for k in values if k not in pair_ranks]
        return (2, pair_ranks * 2 + kicker[:1])  # Two pair
    elif pairs == 1:
        pair_rank = [k for k, v in rank_counts.items() if v == 2][0]
        kickers = sorted([k for k in values if k != pair_rank], reverse=True)
        return (1, [pair_rank] * 2 + kickers[:3])  # One pair
    else:
        return (0, values[:5])  # High card

# Function to determine the winner
def determine_winner(game):
    community_cards = game['flop'] + game['turn'] + game['river']
    player_hands = game['players']
    player_ranks = {}

    for player, cards in player_hands.items():
        full_hand = cards + community_cards
        player_ranks[player] = determine_best_hand(full_hand)

    winner = max(player_ranks, key=player_ranks.get)
    return {
        "winner": winner,
        "hands": {player: (hand_rank_to_string(rank[0]), rank[1]) for player, rank in player_ranks.items()}
    }

# Main execution
if __name__ == "__main__":
    deck = generate_deck()

    print("\nDealing cards...")
    # game = deal_cards_all(6)

    game = {
      "flop": [
            {
                "rank": "10",
                "suit": "♦️"
            },
            {
                "rank": "6",
                "suit": "♥️"
            },
            {
                "rank": "3",
                "suit": "♦️"
            }
        ],
        "players": {
            "player_1": [
                {
                    "rank": "4",
                    "suit": "♦️"
                },
                {
                    "rank": "A",
                    "suit": "♠️"
                }
            ],
            "player_2": [
                {
                    "rank": "6",
                    "suit": "♣️"
                },
                {
                    "rank": "10",
                    "suit": "♣️"
                }
            ]
        },
        "river": [
            {
                "rank": "K",
                "suit": "♣️"
            }
        ],
        "turn": [
            {
                "rank": "7",
                "suit": "♣️"
            }
        ]
    }

    # Print community cards
    print("Community cards:")
    for card in game['flop']:
        print_card(card)
    for card in game['turn']:
        print_card(card)
    for card in game['river']:
        print_card(card)
    print()

    for player, cards in game['players'].items():
        print(f"{player}:")
        for card in cards:
            print_card(card)
        print()

    print("\nDetermining winner:")
    result = determine_winner(game)
    print(f"Winner: {result['winner']}")
    for player, rank in result['hands'].items():
        print(f"{player}: {rank[0]} with ranks {rank[1]}")
