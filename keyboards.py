from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ib_start_play = InlineKeyboardButton(text='Play Black Jack!', callback_data='Start Play')
ib_rules = InlineKeyboardButton(text='Rules', callback_data='Description')
ib_leaderboard = InlineKeyboardButton(text='Ranking', callback_data='Scores')
ikb_start = InlineKeyboardMarkup(row_width=2).add(ib_start_play).add(ib_rules, ib_leaderboard)

ib_give_card = InlineKeyboardButton(text="YES", callback_data='Give Card')
ib_enough_cards = InlineKeyboardButton(text="NO", callback_data='Enough Cards')
ikb_dealing = InlineKeyboardMarkup(row_width=2).add(ib_give_card, ib_enough_cards)

ib_one_more_game = InlineKeyboardButton(text="YES", callback_data='Start Play')
ib_exit_to_menu = InlineKeyboardButton(text="NO", callback_data='Exit to Menu')
ikb_next_game = InlineKeyboardMarkup(row_width=2).add(ib_one_more_game, ib_exit_to_menu)