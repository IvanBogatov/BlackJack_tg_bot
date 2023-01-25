import os
import logging

from aiogram import Bot, Dispatcher, executor, types
from keyboards import ikb_next_game, ikb_dealing, ikb_start

from back import initial_data, manage_data, leaderboard
from config import preview_img, logfile

logging.basicConfig(level=logging.INFO,
                    filename=logfile,
                    filemode='a')

TOKEN = os.getenv('TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Start or restart if the bot was deleted
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_first_name = message.from_user.first_name
    user_name = message.from_user.username
    user_id = message.from_user.id
    text = f'Hi, {user_first_name}!'
    logging.info(f"{user_name=} {user_id=} sent message {message.text}")
    initial_data(message)
    await bot.send_photo(chat_id=user_id, photo=preview_img)
    await bot.send_message(chat_id=user_id, text=text, reply_markup=ikb_start)

# Handle with inline keyboard inputs
@dp.callback_query_handler()    
async def callback_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if callback.data in ['Start Play', 'Give Card', 'Enough Cards']:
        if callback.data == 'Start Play':
            hands, result = manage_data(callback, 'first')
            add, kb = 'card', ikb_dealing

        if callback.data == 'Give Card':
            hands, result = manage_data(callback, 'player')
            add, kb = ('game', ikb_next_game) if result == 'Lose!' else ('card', ikb_dealing)

        if callback.data == 'Enough Cards':
            hands, result = manage_data(callback, 'dealer')
            add, kb = 'game', ikb_next_game

        text = f'{result}\n\n Your hand: {hands[0]}\n Dealer\'s hand: {hands[1]}\n\n One more {add}?'
        await bot.send_message(chat_id=user_id, text=text, reply_markup=kb)

    if callback.data in ['Description', 'Exit to Menu', 'Scores']:
        if callback.data == 'Description':
            text = """
            Points: \nJ, Q, K - 10 pointsfor each; \nA: 11 points if points sum <=21, then 1 point; \n2-10: as it is \n\nRules:
            1) The aim of the player is to get more points than dealer, but not bigger than 21. It is instant lose.\n
            2) There are 52 cards in the deck at the game start. And it be reshuffled if deck before dealing will have less than 18 cards. (So, you can count cards to increase your chanses.)\n
            3) At the first dealing player and dealer got 2 cards, but you can see only 1 opened dealer's card.\n
            4) Then player can take more cards one by one and stop whenever you want.\n
            5) After it dealer will reveal hidden card and also start to take more cards untill the total sum will be 17+.\n
            6) Good luck! 
            """
        if callback.data == 'Exit to Menu':
            text = 'Take your time, let\'s play again! 🃏'
        if callback.data == 'Scores':
            text = leaderboard()
        await bot.send_message(chat_id=user_id, text=text, reply_markup=ikb_start)

if __name__=='__main__':
    executor.start_polling(dp, skip_updates=True)