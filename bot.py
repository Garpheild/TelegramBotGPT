import telebot
from telebot import types
from config import *
import gpt

bot = telebot.TeleBot(token)

users_history = {}


def add_buttons(buttons):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons)
    return keyboard


@bot.message_handler(func=lambda message: message.text == "Продолжить ответ")
def send_answer(message):
    if message.content_type != "text":
        bot.send_message(message.chat.id, "Введите текстовый запрос")
        bot.register_next_step_handler(message, send_answer)
        return

    if not gpt.check_promt_len(message.text):
        bot.send_message(message.chat.id, "Слишком длинный запрос")
        bot.register_next_step_handler(message, send_answer)
        return

    if message.text == "Продолжить ответ" and (message.chat.id not in users_history or users_history[message.chat.id] == {}):
        bot.send_message(message.chat.id, "Сначала отправьте задачу")
        bot.register_next_step_handler(message, send_answer)
        return
    elif message.text == "Продолжить ответ":
        answer = gpt.get_answer(users_history[message.chat.id], "Продолжи обьяснение: ")
        bot.send_message(message.chat.id, answer, reply_markup=add_buttons(["Закончить диалог", "Продолжить ответ"]))
    else:
        answer = gpt.get_answer(message.text, "Реши задачу по шагам: ")
        if answer == "":
            bot.send_message(message.chat.id, "Ответ закончен", reply_markup=add_buttons(["/request"]))
        else:
            bot.send_message(message.chat.id, answer,
                             reply_markup=add_buttons(["Закончить диалог", "Продолжить ответ"]))

    if message.chat.id not in users_history or users_history[message.chat.id] == {}:
        users_history[message.chat.id] = answer
    else:
        users_history[message.chat.id] += answer


@bot.message_handler(func=lambda message: message.text == "Закончить диалог")
def end(message):
    if users_history[message.chat.id] == {} or message.chat.id not in users_history:
        bot.send_message(message.chat.id, "Чтобы закончить диалог его нужно начать")
    else:
        bot.send_message(message.chat.id, "Приятно было пообщаться", reply_markup=add_buttons(["/request"]))
        users_history[message.chat.id] = {}


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}", reply_markup=add_buttons(["/request"]))


@bot.message_handler(commands=["help"])
def help(message):
    bot.send_message(message.chat.id, f"help", reply_markup=add_buttons(["/request"]))


@bot.message_handler(commands=["request"])
def request(message):
    bot.send_message(message.chat.id, "Введите текст задачи")
    bot.register_next_step_handler(message, send_answer)


@bot.message_handler(func=lambda message: True)
def text_message(message):
    bot.send_message(message.chat.id, f"help", reply_markup=add_buttons(["/request"]))


bot.infinity_polling()