from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
import emoji

EMOJI_SKILL_CHOSEN = emoji.emojize(':heavy_check_mark:')
EMOJI_MAIL = emoji.emojize(':e-mail:')
EMOJI_PHONE = '\U0000260E'
EMOJI_BIO = '\U0001F393'
EMOJI_STAT = emoji.emojize(':bar_chart:')
EMOJI_HACK_TOTAL = emoji.emojize(':heavy_check_mark:')
EMOJI_HACK_WIN = emoji.emojize(':trophy:')
EMOJI_XP = '\U0001F3AF'
EMOJI_COINS = '\U0001F4B0'
EMOJI_SKILLS = emoji.emojize(':glowing_star:')
EMOJI_SKILL_STRENGTH = '\U0001F4AA'
EMOJI_SKILL_VERIFIED = '\U0001F44D'
EMOJI_ERROR_SADFACE = '\U0001F61F'
EMOJI_ERROR_MARK = '\U0000274C'
EMOJI_SUCCESS_MARK = '\U00002705'

def draw_register_button(bot, update):
    reply_keyboard = [['OK']]
    update.message.reply_text('Let\'s get to know you better!',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard),
                              one_time_keyboard=True,
                              resize_keyboard=True
                              )

def draw_skill_buttons(bot, update, skillboard):
    reply_keyboard = skillboard
    update.message.reply_text('Choose one or more skills and press \"Done!\"',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard),
                              one_time_keyboard=True,
                              resize_keyboard=True
                              )

def draw_skill_buttons_with_done(bot, update, skillboard, current_skills, chosen_skill, skill_enable):
    reply_keyboard = skillboard
    reply_keyboard.append(['Done!'])
    for skill in reply_keyboard:
        if skill[0] in current_skills:
            skill[0] = EMOJI_SKILL_CHOSEN + ' ' + skill[0]

    message_text = 'You\'ve {} skill \"{}\".'.format('chosen' if skill_enable else 'discarded', chosen_skill)
    update.message.reply_text(message_text,
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard),
                              one_time_keyboard=True,
                              resize_keyboard=True
                              )

def draw_error_skill_prompt(bot, update, skillboard, current_skills):
    reply_keyboard = skillboard
    for skill in reply_keyboard:
        if skill[0] in current_skills:
            skill[0] = EMOJI_SKILL_CHOSEN + ' ' + skill[0]

    update.message.reply_text('Sorry, we don\'t know that skill {}.'.format(EMOJI_ERROR_SADFACE),
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard),
                              one_time_keyboard=True,
                              resize_keyboard=True
                              )

def draw_error_no_skills(bot, update, skillboard):
    reply_keyboard = skillboard
    update.message.reply_text('Please choose at least one skill.',
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
    update.message.reply_text('It seems that this email is taken {} Please try again.'.format(EMOJI_ERROR_SADFACE),
                              reply_markup=ReplyKeyboardRemove())

def draw_eventid_error(bot, update):
    update.message.reply_text('It seems that you haven\'t started from an event. Please use an event link to start.', reply_markup=ReplyKeyboardRemove())

def draw_main_menu(bot, update, user_drawing_data):
    is_searchable = user_drawing_data['isSearchable']
    status = user_drawing_data['status']

    toggle_search_text = 'Searchable On' if is_searchable else 'Searchable Off'

    if status == 'applied':
        status_change_text = 'Check In at the Hackathon'
    elif status == 'activated':
        status_change_text = 'Finish my participation'
    else:
        status_change_text = 'Reactivate my participation'

    reply_keyboard = [['Search participants by skill', toggle_search_text],
                      ['Show Event Schedule'],
                      [status_change_text],
                      ['My Profile']]
    update.message.reply_text('What do you want to do?', reply_markup=ReplyKeyboardMarkup(reply_keyboard))

def draw_main_menu_error(bot, update):
    update.message.reply_text('Sorry, I don\'t know what you mean {} Please try again.'.format(EMOJI_ERROR_SADFACE),
                              reply_markup=ReplyKeyboardRemove())

def draw_search_skill_buttons(bot, update, skillboard):
    reply_keyboard = skillboard
    update.message.reply_text('What skill do you want to search for?',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard),
                              one_time_keyboard=True,
                              resize_keyboard=True
                              )

def draw_event_schedule(bot, update, schedule):
    update.message.reply_text(schedule,
                              reply_markup=ReplyKeyboardRemove())

def draw_participation_change_activate(bot, update):
    reply_keyboard = [['Wi-Fi Password'], [KeyboardButton('Location', request_location=True)], ['Back']]
    update.message.reply_text('Do you want to check in through entering the Wi-Fi password or location sharing?',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard),
                              one_time_keyboard=True,
                              resize_keyboard=True
                              )

def draw_participation_change_finish(bot, update):
    reply_keyboard = [['Ok'], ['Back']]
    update.message.reply_text('Your are checked in. Do you want to finish your participation?',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard),
                              one_time_keyboard=True,
                              resize_keyboard=True
                              )

def draw_participation_change_revert(bot, update):
    reply_keyboard = [['Ok'], ['Back']]
    update.message.reply_text('You\'ve finished your participation. Do you want check in back at the hackathon?',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard),
                              one_time_keyboard=True,
                              resize_keyboard=True
                              )

def draw_participation_change_activate_password(bot, update):
    update.message.reply_text('Please enter the Wi-Fi password:',
                              reply_markup=ReplyKeyboardRemove())

def draw_password_check_error(bot, update):
    update.message.reply_text('{} Sorry, the password was incorrect.'.format(EMOJI_ERROR_MARK),
                              reply_markup=ReplyKeyboardRemove())

def draw_participation_change_activate_location(bot, update):
    update.message.reply_text('Please share your location:',
                              reply_markup=ReplyKeyboardRemove())

def draw_location_send_error(bot, update):
    update.message.reply_text('{} Sorry, looks like you haven\'t sent the location. Please try again:'.format(EMOJI_ERROR_MARK),
                              reply_markup=ReplyKeyboardRemove())

def draw_location_check_error(bot, update):
    update.message.reply_text('{} Sorry, your location was incorrect.'.format(EMOJI_ERROR_MARK),
                          reply_markup=ReplyKeyboardRemove())

def draw_activate_successful(bot, update):
    update.message.reply_text('{} You have successfully checked in and earned your first 7 XP! Press \"My Profile\" to see your current stats. Also, you will now receive messages from organizers.'.format(EMOJI_SUCCESS_MARK),
                              reply_markup=ReplyKeyboardRemove())

def draw_already_activated(bot, update):
    update.message.reply_text('You are already checked in.',
                              reply_markup=ReplyKeyboardRemove())

def draw_finish_successful(bot, update):
    update.message.reply_text('{} You finished your participation. You will no longer receive messages from the organizers.'.format(EMOJI_SUCCESS_MARK),
                              reply_markup=ReplyKeyboardRemove())

def draw_revert_successful(bot, update):
    update.message.reply_text('{} You are checked in back at the hackathon and will receive messages from the organizers again!'.format(EMOJI_SUCCESS_MARK),
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
        profile_string += '    <b>{} - {} Verified by: {} </b>\n'.format(
            skill['tag'],
            EMOJI_SKILL_VERIFIED,
            skill['verified']
        )

    external_profile_url = 'http://hackathons.space/profile/t/' + user['tgProfileLink'].split('/')[-1]
    inline_keyboard = [[InlineKeyboardButton('Go to profile page', url=external_profile_url)]]
    update.message.reply_text(profile_string, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(inline_keyboard))

def draw_searchable_toggled(bot, update, new_is_searchable):
    if new_is_searchable:
        update.message.reply_text("Now others can search you by skill.")
    else:
        update.message.reply_text("Now others cannot search you by skill.")

def draw_search_result(bot, update, skill, participants):
    result_string = '<b>{}</b>\n\n'.format(skill)
    if not participants:
        result_string += 'Sorry, we haven\'t found anyone :('

    for participant in participants:
        result_string += '<b>{}</b>\n'.format(participant['username'])
        result_string += '<b>TG Handle:</b> @{}\n'.format(participant['tgProfileLink'].split('/')[-1])
        result_string += '<b>XP:</b> {}\n\n'.format(participant['xp'])

    update.message.reply_text(result_string, parse_mode='HTML')

def draw_universal_error_reply(bot, update):
    update.message.reply_text('Sorry, something went wrong {} Please write to my creators @peramor or @van0k.'.format(EMOJI_ERROR_SADFACE))