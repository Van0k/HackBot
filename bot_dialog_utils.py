from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
import emoji

EMOJI_MAIL = emoji.emojize(':e-mail:')
EMOJI_PHONE = emoji.emojize(':phone:')
EMOJI_BIO = emoji.emojize(':mortar_board:')
EMOJI_STAT = emoji.emojize(':bar_chart:')
EMOJI_HACK_TOTAL = emoji.emojize(':heavy_check_mark:')
EMOJI_HACK_WIN = emoji.emojize(':trophy:')
EMOJI_XP = '\U0001F3AF'
EMOJI_COINS = '\U0001F4B0'
EMOJI_SKILLS = emoji.emojize(':glowing_star:')
EMOJI_SKILL_STRENGTH = '\U0001F4AA'
EMOJI_SKILL_VERIFIED = '\U0001F44D'

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

def draw_skill_searchable_question(bot, update):
    reply_keyboard = [['Yes'], ['No']]
    update.message.reply_text('Do you agree to appear in searches by skill? Other people may contact you if you have the skill they\'re interested in.',
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

def draw_main_menu(bot, update, is_searchable=False, current_status='applied'):
    reply_keyboard = [['Search participants by skill'],
                      ['Show Event Schedule'],
                      ['Toggle searchable'],
                      ['Change participation status'],
                      ['My Profile']]
    #reply_keyboard = []
    #reply_keyboard.append(['Search participants by skill'])
    #reply_keyboard.append(['Show Event Schedule'])
    update.message.reply_text('What do you want to do?', reply_markup=ReplyKeyboardMarkup(reply_keyboard))

def draw_main_menu_error(bot, update):
    update.message.reply_text('Sorry, I don\'t know what you mean :( Please try again.',
                              reply_markup=ReplyKeyboardRemove())

def draw_search_skill_buttons(bot, update, skillboard):
    reply_keyboard = skillboard
    update.message.reply_text('What skill do you want to search for?',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard),
                              one_time_keyboard=True,
                              resize_keyboard=True
                              )

def draw_event_schedule(bot, update):
    update.message.reply_text('This is the event schedule.',
                              reply_markup=ReplyKeyboardRemove())

def draw_participation_change_activate(bot, update):
    reply_keyboard = [['Wi-Fi Password'], [KeyboardButton('Location', request_location=True)], ['Back']]
    update.message.reply_text('Your current status is \"applied\". Do you want to confirm your participation through entering the Wi-Fi password or location sharing?',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard),
                              one_time_keyboard=True,
                              resize_keyboard=True
                              )

def draw_participation_change_finish(bot, update):
    reply_keyboard = [['Ok'], ['Back']]
    update.message.reply_text('Your current status is \"activated\". Do you want to finish your participation?',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard),
                              one_time_keyboard=True,
                              resize_keyboard=True
                              )

def draw_participation_change_revert(bot, update):
    reply_keyboard = [['Ok'], ['Back']]
    update.message.reply_text('Your current status is \"participated\". Do you want to revert back to activated?',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard),
                              one_time_keyboard=True,
                              resize_keyboard=True
                              )

def draw_participation_change_activate_password(bot, update):
    update.message.reply_text('Please enter the Wi-Fi password:',
                              reply_markup=ReplyKeyboardRemove())

def draw_password_check_error(bot, update):
    update.message.reply_text('Sorry, the password was incorrect.',
                              reply_markup=ReplyKeyboardRemove())

def draw_participation_change_activate_location(bot, update):
    update.message.reply_text('Please share your location:',
                              reply_markup=ReplyKeyboardRemove())

def draw_location_send_error(bot, update):
    update.message.reply_text('Sorry, looks like you haven\'t sent the location. Please try again:',
                              reply_markup=ReplyKeyboardRemove())

def draw_location_check_error(bot, update):
    update.message.reply_text('Sorry, your location was incorrect.',
                          reply_markup=ReplyKeyboardRemove())

def draw_activate_successful(bot, update):
    update.message.reply_text('You were successfully activated!',
                              reply_markup=ReplyKeyboardRemove())

def draw_finish_successful(bot, update):
    update.message.reply_text('You finished your participation.',
                              reply_markup=ReplyKeyboardRemove())

def draw_revert_successful(bot, update):
    update.message.reply_text('You successfully reverted back to \"activated\".',
                              reply_markup=ReplyKeyboardRemove())

def draw_user_profile(bot, update, user):
    profile_string = ""
    profile_string += '<b>{}</b>\n\n'.format(user['username'])
    profile_string += '{} <b>Email:</b> {}\n\n'.format(EMOJI_MAIL, user['email']) if user['email'] else ''
    profile_string += '{} <b>Phone:</b> {}\n\n'.format(EMOJI_PHONE, user['contactPhone']) if user['contactPhone'] else ''
    profile_string += '{} <b>Bio:</b>\n{}\n\n'.format(EMOJI_BIO, user['bio']) if user['bio'] else ''
    profile_string += '{} <b>Stats:</b>\n'.format(EMOJI_STAT)
    profile_string += '    {} <b>Participations: </b>{}\n'.format(EMOJI_HACK_TOTAL, user['stat']['hackTotal'])
    profile_string += '    {} <b>Victories: </b>{}\n'.format(EMOJI_HACK_WIN, user['stat']['hackWin'])
    profile_string += '    {} <b>XP: </b>{}\n'.format(EMOJI_XP, user['stat']['xp'])
    profile_string += '    {} <b>Coins: </b>{}\n\n'.format(EMOJI_COINS, user['stat']['coins'])
    profile_string += '{} <b>Skills:</b>\n'.format(EMOJI_SKILLS)
    for skill in user['skills']:
        profile_string += '    <b>{} - {} Strength: {} - {} Verified by: {} </b>\n'.format(
            skill['tag'],
            EMOJI_SKILL_STRENGTH,
            skill['strength'],
            EMOJI_SKILL_VERIFIED,
            skill['verified']
        )

    external_profile_url = 'http://hackathons.space/profile/t/' + user['tgProfileLink'].split('/')[-1]
    inline_keyboard = [[InlineKeyboardButton('Go to profile page', url=external_profile_url)]]
    update.message.reply_text(profile_string, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(inline_keyboard))
    print(update)
    print(user)