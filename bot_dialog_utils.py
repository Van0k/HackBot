from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove


def draw_register_button(bot, update):
    reply_keyboard = [['OK']]
    update.message.reply_text('Let\'s get to know you better!',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard),
                              one_time_keyboard=True,
                              resize_keyboard=True
                              )

def draw_skill_buttons(bot, update, skillboard):
    reply_keyboard = skillboard
    update.message.reply_text('Choose your first skill.',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard),
                              one_time_keyboard=True,
                              resize_keyboard=True
                              )

def draw_skill_buttons_with_done(bot, update, skillboard):
    reply_keyboard = skillboard
    reply_keyboard.append(['Done!'])
    update.message.reply_text('Choose another skill or press done if you\'re finished.',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard),
                              one_time_keyboard=True,
                              resize_keyboard=True
                              )

def draw_error_skill_prompt(bot, update, skillboard):
    reply_keyboard = skillboard
    update.message.reply_text('Sorry, we don\'t know that skill :( Please try again.',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard),
                              one_time_keyboard=True,
                              resize_keyboard=True
                              )

def draw_email_prompt(bot, update):
    update.message.reply_text('Please tell us your email.', reply_markup=ReplyKeyboardRemove())

def draw_error_email_prompt(bot, update):
    update.message.reply_text('It seems that this email is taken :(. Please try again.', reply_markup=ReplyKeyboardRemove())

def draw_eventid_error(bot, update):
    update.message.reply_text('It seems that you haven\'t started from an event. Please use an event link to start.', reply_markup=ReplyKeyboardRemove())

def draw_main_menu(bot, update):
    reply_keyboard = [['Find participants by skill']]
    update.message.reply_text('What do you want to do?', reply_markup=ReplyKeyboardMarkup(reply_keyboard))