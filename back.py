import itertools
import random
import logging
import pandas as pd

from config import CARDS_DICT, CARDS_SUITS

# The original 52 cards deck
full_deck = list(itertools.product(CARDS_DICT.keys(), CARDS_SUITS))

# Getting randon card from the current deck
def get_random_card(hand, current_deck):
    random_card = random.choice(current_deck)
    hand.append(random_card)
    current_deck.remove(random_card)
    return hand, current_deck

# Renew the deck
def shuffle():
    return random.sample(full_deck, k=full_deck.__len__())

# Count points sum of the hand    
def points_sum(hand):
    aces_num = ace_counter(hand)
    total = sum(map(lambda x: CARDS_DICT[x[0]], hand))
    while (total > 21) & (aces_num > 0):
        total-=10
        aces_num-=1
    return total

# Count number of Aces in the hand
def ace_counter(hand):
    return list(map(lambda x: x[0], hand)).count('A')

# Transform view of hand (just for printing)
def one(hand, sep=''):
    return list(map(lambda x: sep.join(x), hand))

def hands_print(hands, hide=False):
    if hide:
        return one([one(hands[0]), ['🤔', one(hands[1])[1]]], sep='| ')
    else:
        return one([one(hands[0]), one(hands[1])], sep='| ')

# Dealing with first bot enter or enter after bot deleting from user
def initial_data(data_source, restart=False):
    user_id = data_source.from_user.id
    user_name = data_source.from_user.username

    df = pd.read_csv('users.csv', index_col=0)
    idx = df[df.telegram_id == user_id].index
    time = pd.to_datetime('now', utc=True)

    if user_id not in df.telegram_id.values:
        df.loc[len(df.index)] = [user_id, user_name, '[]', '[]', str(full_deck), 0, 0, 0, time, time]
    else:
        df.loc[idx, ['player_hand', 'dealer_hand', 'playing_deck', 'last_entry_dttm']] = ['[]', '[]', str(full_deck), time]
    df.to_csv('users.csv')
    return 

# Dealing with Game commands
def manage_data(data_source, handle_type):
    # Get data about user's current data
    user_id = data_source.from_user.id
    user_name = data_source.from_user.username

    df = pd.read_csv('users.csv', index_col=0)
    idx = df[df.telegram_id == user_id].index

    player_hand = eval(df.loc[idx, 'player_hand'][idx[0]])
    dealer_hand = eval(df.loc[idx, 'dealer_hand'][idx[0]])
    playing_deck = eval(df.loc[idx, 'playing_deck'][idx[0]])
    games_count = df.loc[idx, 'games_count'][idx[0]]
    wins_count = df.loc[idx, 'wins_count'][idx[0]]
    lose_count = df.loc[idx, 'lose_count'][idx[0]]
    first_entry_dttm = df.loc[idx, 'first_entry_dttm'][idx[0]]
    last_entry_dttm = pd.to_datetime('now', utc=True)
    
    # Manage the data
    if handle_type == 'first':
        player_hand, dealer_hand, playing_deck, result = first_dealing(player_hand, dealer_hand, playing_deck)
        hands = hands_print((player_hand, dealer_hand), hide=True)
    elif handle_type == 'player':
        player_hand, dealer_hand, playing_deck, result, games_count, lose_count = player_play(player_hand, dealer_hand, playing_deck, games_count, lose_count)
        if result == 'Lose!':
            hands = hands_print((player_hand, dealer_hand))
            player_hand, dealer_hand = [], []
        else:
            hands = hands_print((player_hand, dealer_hand), hide=True)
    else:
        player_hand, dealer_hand, playing_deck, result, games_count, lose_count, wins_count = dealer_play(player_hand, dealer_hand, playing_deck, games_count, lose_count, wins_count)
        hands = hands_print((player_hand, dealer_hand))
        player_hand, dealer_hand = [], []

    # Save the data
    df.iloc[idx] = [
        user_id, user_name, str(player_hand), str(dealer_hand), str(playing_deck), games_count, wins_count, lose_count, first_entry_dttm, last_entry_dttm
        ]

    df.to_csv('users.csv')
    return hands, result

# Give 2 cards to each player at the start
def first_dealing(player_hand, dealer_hand, playing_deck):
    if playing_deck.__len__() < 52/3:
        playing_deck = shuffle()
    for it in range(2):
        player_hand, playing_deck = get_random_card(player_hand, playing_deck)
        dealer_hand, playing_deck = get_random_card(dealer_hand, playing_deck)
    result = ''
    return player_hand, dealer_hand, playing_deck, result

# Give a card to the player and watch for overdraft
def player_play(player_hand, dealer_hand, playing_deck, games_count, lose_count):
    player_hand, playing_deck = get_random_card(player_hand, playing_deck)
    if points_sum(player_hand) > 21:
        result = 'Lose!'
        games_count+=1
        lose_count+=1
    else:
        result = ''
    return player_hand, dealer_hand, playing_deck, result, games_count, lose_count

# Give a card to the dealer, watch for overdraft and compare points sum
def dealer_play(player_hand, dealer_hand, playing_deck, games_count, lose_count, wins_count):
    while points_sum(dealer_hand) < 17:
        dealer_hand, playing_deck = get_random_card(dealer_hand, playing_deck)
    
    if points_sum(dealer_hand) <= 21:
        if points_sum(player_hand) < points_sum(dealer_hand):
            result = 'Lose!'
            games_count+=1
            lose_count+=1
        elif points_sum(player_hand) == points_sum(dealer_hand):
            result = 'Draw!'
            games_count+=1
    if (points_sum(dealer_hand) > 21) | (points_sum(player_hand) > points_sum(dealer_hand)):
        result = 'Win!'
        games_count+=1
        wins_count+=1
    return player_hand, dealer_hand, playing_deck, result, games_count, lose_count, wins_count

# Create leaderboard
def leaderboard():
    df = pd.read_csv('users.csv', usecols=['telegram_username', 'games_count', 'wins_count', 'lose_count'])
    df.columns = [' Username |', 'Games |', 'Wins |', 'Loses |']
    df['Score |'] = df['Wins |'] - df['Loses |']
    df['WR, %'] = round(df['Wins |']/df['Games |']*100)
    df = (
        df.drop('Loses |', axis=1).head(10)
        .sort_values('Wins |', ascending=True)
        .to_string(index=False, col_space=[15,8,8,8,8], justify='end')
        )
    return df