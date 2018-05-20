import logging
import sys
import os
import re
from telegram import Bot
from telegram.ext import Updater, CommandHandler, ConversationHandler, RegexHandler, MessageHandler, Filters

from backend_utils import *
from bot_dialog_utils import *
from push_message_listener import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))

EVENT_ID = 1

CONFIG_PATH = 'config/config.json'
DEFAULT_CONFIG = 'config/default_config.json'

TOKEN = os.environ['BOT_TOKEN'] # Bot token here
SIGNATURE_TOKEN = os.environ['SIGNATURE_BOT_TOKEN'] # Key for telegram verification signature here

MESSAGES_ENDPOINT = 'http://52.233.153.23/api/admin/messages'

STATES = {
    'REGISTER': 0,
    'REGISTER_SKILL': 1,
    'REGISTER_EMAIL': 2,
    'MAIN_MENU': 3,
    'SKILL_SEARCH': 4,
    'REGISTER_SKILL_SEARCHABLE': 5,
    'STATUS_CHANGE_ACTIVATE': 6,
    'STATUS_CHANGE_FINISH': 7,
    'STATUS_CHANGE_REVERT': 8,
    'STATUS_CHANGE_ACTIVATE_PASSWORD': 9,
}

MENU_CHOICES = [
    'Search participants by skill',
    'Show Event Schedule',
    'Searchable On',
    'Searchable Off',
    'Check In at the Hackathon',
    'Finish my participation',
    'Reactivate my participation',
    'My Profile',
]

try:
    with open(CONFIG_PATH, 'r') as f:
        CONFIG_DATA = json.load(f)
except:
    with open(DEFAULT_CONFIG, 'r') as f:
        CONFIG_DATA = json.load(f)

def write_config():
    with open(CONFIG_PATH, 'w') as f:
        json.dump(CONFIG_DATA, f)

def start(bot, update, args):
    if not args:
        draw_eventid_error(bot, update)
        return None
    user = update.message.from_user
    file_id = user.get_profile_photos()['photos'][0][-1]['file_id']

    user_data = {
        "id": user['id'],
        "first_name": user['first_name'],
        "last_name": user['last_name'],
        "username": user['username'],
        "photo_url": bot.getFile(file_id)['file_path'],
        "auth_date": int(time.time()),
    }
    user_hash = get_data_hash(user_data, SIGNATURE_TOKEN)

    user_token = user_login(user_data, user_hash)

    db_user = get_current_user(user_token)

    logger.info('User @{} started the bot.'.format(update.message.from_user['username']))

    event_id = args[0]
    apply_for_event(event_id, user_token)

    if str(user['id']) not in CONFIG_DATA['users']:
        if not db_user['skills'] or not db_user['email']:
            CONFIG_DATA['users'][str(user['id'])] = {'status': 'non-registered', 'token': user_token, 'chat_id': update.message.chat.id}
            write_config()

            draw_register_button(bot, update)
            return STATES['REGISTER']
        else:
            CONFIG_DATA['users'][str(user['id'])] = {'status': 'registered', 'token': user_token, 'chat_id': update.message.chat.id}
            write_config()

            update.message.reply_text('Welcome back!')
            draw_skill_searchable_question(bot, update)
            return STATES['REGISTER_SKILL_SEARCHABLE']
    else:
        CONFIG_DATA['users'][str(user['id'])]['token'] = user_token
        write_config()
        if CONFIG_DATA['users'][str(user['id'])]['status'] == 'non-registered':
            draw_register_button(bot, update)
            return STATES['REGISTER']
        else:
            update.message.reply_text('Welcome back!')
            user_drawing_data = get_participant_admin(EVENT_ID, get_current_user(user_token)['id'], TOKEN)
            draw_main_menu(bot, update, user_drawing_data)
            return STATES['MAIN_MENU']


def register(bot, update):
    token = CONFIG_DATA['users'][str(update.message.from_user['id'])]['token']

    skills = get_skills(token)
    skills_keyboard = [[skill['tag']] for skill in skills]

    draw_skill_buttons(bot, update, skills_keyboard)

    return STATES['REGISTER_SKILL']

def register_skill(bot, update):
    token = CONFIG_DATA['users'][str(update.message.from_user['id'])]['token']

    skills = get_skills(token)
    skills_reversed = {skill['tag']: skill['id'] for skill in skills}
    skills_keyboard = [[skill['tag']] for skill in skills]

    db_user = get_current_user(token)
    current_user_skills = [skill['tag'] for skill in db_user['skills']]

    if update.message.text != 'Done!':
        chosen_skill = re.sub('^\U00002714 ', '', update.message.text)

        if chosen_skill not in skills_reversed:
            draw_error_skill_prompt(bot, update, skills_keyboard, current_user_skills)
            return STATES['REGISTER_SKILL']

        if chosen_skill in current_user_skills:
            db_user['skills'] = [skill for skill in db_user['skills'] if skill['tag'] != chosen_skill]
            skill_enable = False
        else:
            db_user['skills'].append({"id": skills_reversed[chosen_skill]})
            skill_enable = True

        update_current_user(token, db_user)

        db_user = get_current_user(token)
        current_user_skills = [skill['tag'] for skill in db_user['skills']]

        draw_skill_buttons_with_done(bot, update, skills_keyboard, current_user_skills, chosen_skill, skill_enable)
        return STATES['REGISTER_SKILL']

    if not current_user_skills:
        draw_error_no_skills(bot, update, skills_keyboard)
        return STATES['REGISTER_SKILL']

    draw_skill_searchable_question(bot, update)
    return STATES['REGISTER_SKILL_SEARCHABLE']



def register_skill_searchable(bot, update):
    token = CONFIG_DATA['users'][str(update.message.from_user['id'])]['token']
    db_user = get_current_user(token)

    answer = update.message.text

    if answer == 'Yes':
        CONFIG_DATA['users'][str(update.message.from_user['id'])]['is_searchable'] = True
        toggle_searchable(EVENT_ID, token)
    else:
        CONFIG_DATA['users'][str(update.message.from_user['id'])]['is_searchable'] = False

    if not db_user['email']:
        draw_email_prompt(bot, update)
        return STATES['REGISTER_EMAIL']
    else:
        logger.info('User @{} finished registration.'.format(update.message.from_user['username']))

        CONFIG_DATA['users'][str(update.message.from_user['id'])]['status'] = 'registered'
        write_config()

        user_drawing_data = get_participant_admin(EVENT_ID, get_current_user(token)['id'], TOKEN)
        draw_main_menu(bot, update, user_drawing_data)
        return STATES['MAIN_MENU']


def register_email(bot, update):
    token = CONFIG_DATA['users'][str(update.message.from_user['id'])]['token']
    entered_email = update.message.text

    db_user = get_current_user(token)
    db_user['email'] = entered_email

    try:
        update_current_user(token, db_user)
    except ValueError:
        draw_error_email_prompt(bot, update)
        return STATES['REGISTER_EMAIL']

    CONFIG_DATA['users'][str(update.message.from_user['id'])]['status'] = 'registered'
    write_config()

    logger.info('User @{} finished registration.'.format(update.message.from_user['username']))

    user_drawing_data = get_participant_admin(EVENT_ID, get_current_user(token)['id'], TOKEN)
    draw_main_menu(bot, update, user_drawing_data)
    return STATES['MAIN_MENU']


def main_menu_choice(bot, update):
    token = CONFIG_DATA['users'][str(update.message.from_user['id'])]['token']

    choice = update.message.text
    if choice not in MENU_CHOICES:
        draw_main_menu_error(bot, update)

        logger.info('User @{} made wrong main menu choice: {}.'.format(update.message.from_user['username'], choice))

        user_drawing_data = get_participant_admin(EVENT_ID, get_current_user(token)['id'], TOKEN)
        draw_main_menu(bot, update, user_drawing_data)
        return STATES['MAIN_MENU']

    if choice == 'Search participants by skill':

        skills = get_skills(token)
        skills_keyboard = [[skill['tag']] for skill in skills]
        draw_search_skill_buttons(bot, update, skills_keyboard)

        return STATES['SKILL_SEARCH']

    if choice == 'Show Event Schedule':
        token = CONFIG_DATA['users'][str(update.message.from_user['id'])]['token']
        event = get_event(EVENT_ID, token)
        draw_event_schedule(bot, update, event['schedule'])

        logger.info('User @{} displayed the schedule.'.format(update.message.from_user['username']))

        user_drawing_data = get_participant_admin(EVENT_ID, get_current_user(token)['id'], TOKEN)
        draw_main_menu(bot, update, user_drawing_data)
        return STATES['MAIN_MENU']

    if choice in ['Searchable On', 'Searchable Off']:
        token = CONFIG_DATA['users'][str(update.message.from_user['id'])]['token']
        new_is_searchable = toggle_searchable(EVENT_ID, token)
        draw_searchable_toggled(bot, update, new_is_searchable)

        logger.info('User @{} toggled searchable to {}.'.format(update.message.from_user['username'], new_is_searchable))

        user_drawing_data = get_participant_admin(EVENT_ID, get_current_user(token)['id'], TOKEN)
        draw_main_menu(bot, update, user_drawing_data)
        return STATES['MAIN_MENU']

    if choice == 'My Profile':
        token = CONFIG_DATA['users'][str(update.message.from_user['id'])]['token']
        user = get_current_user(token)
        draw_user_profile(bot, update, user)

        logger.info('User @{} displayed their profile.'.format(update.message.from_user['username']))

        user_drawing_data = get_participant_admin(EVENT_ID, get_current_user(token)['id'], TOKEN)
        draw_main_menu(bot, update, user_drawing_data)
        return STATES['MAIN_MENU']

    if choice in ['Check In at the Hackathon', 'Finish my participation', 'Reactivate my participation']:
        token = CONFIG_DATA['users'][str(update.message.from_user['id'])]['token']
        db_user = get_current_user(token)
        user_id = db_user['id']

        participants = get_participants(EVENT_ID, TOKEN)
        current_participant = [p for p in participants if p['id'] == user_id][0]

        current_status = current_participant['status']
        if current_status == 'applied':
            draw_participation_change_activate(bot, update)
            return STATES['STATUS_CHANGE_ACTIVATE']

        elif current_status == 'activated':
            draw_participation_change_finish(bot, update)
            return STATES['STATUS_CHANGE_FINISH']

        elif current_status == 'participated':
            draw_participation_change_revert(bot, update)
            return STATES['STATUS_CHANGE_REVERT']


def skill_search(bot, update):
    token = CONFIG_DATA['users'][str(update.message.from_user['id'])]['token']

    participants = get_participants(EVENT_ID, TOKEN)
    chosen_skill = update.message.text
    chosen_participants = [p for p in participants if p['isSearchable'] and chosen_skill in p['skills']]

    draw_search_result(bot, update, chosen_skill, chosen_participants)

    logger.info('User @{} searched by skill: {}'.format(update.message.from_user['username'], chosen_skill))

    user_drawing_data = get_participant_admin(EVENT_ID, get_current_user(token)['id'], TOKEN)
    draw_main_menu(bot, update, user_drawing_data)
    return STATES['MAIN_MENU']


def change_participation_status_activate(bot, update):
    token = CONFIG_DATA['users'][str(update.message.from_user['id'])]['token']
    choice = update.message.text
    location = update.message.location
    if choice == 'Wi-Fi Password':
        draw_participation_change_activate_password(bot, update)
        return STATES['STATUS_CHANGE_ACTIVATE_PASSWORD']

    elif not choice and location:

        activation_result = participation_status_activate(token, EVENT_ID, choice, location)

        if activation_result == 'failed':
            draw_location_check_error(bot, update)

            logger.info('User @{} failed to check in by location.'.format(update.message.from_user['username']))

            user_drawing_data = get_participant_admin(EVENT_ID, get_current_user(token)['id'], TOKEN)
            draw_main_menu(bot, update, user_drawing_data)
            return STATES['MAIN_MENU']

        elif activation_result == 'already':
            draw_already_activated(bot, update)

            user_drawing_data = get_participant_admin(EVENT_ID, get_current_user(token)['id'], TOKEN)
            draw_main_menu(bot, update, user_drawing_data)
            return STATES['MAIN_MENU']

        else:

            logger.info('User @{} successfully checked in by location.'.format(update.message.from_user['username']))
            draw_activate_successful(bot, update)
            user_drawing_data = get_participant_admin(EVENT_ID, get_current_user(token)['id'], TOKEN)
            draw_main_menu(bot, update, user_drawing_data)
            return STATES['MAIN_MENU']

    elif choice == 'Back':

        user_drawing_data = get_participant_admin(EVENT_ID, get_current_user(token)['id'], TOKEN)
        draw_main_menu(bot, update, user_drawing_data)
        return STATES['MAIN_MENU']

    else:

        draw_main_menu_error(bot, update)
        user_drawing_data = get_participant_admin(EVENT_ID, get_current_user(token)['id'], TOKEN)
        draw_main_menu(bot, update, user_drawing_data)
        return STATES['MAIN_MENU']


def change_participation_status_activate_password(bot, update):
    token = CONFIG_DATA['users'][str(update.message.from_user['id'])]['token']
    entered_password = update.message.text

    activation_result = participation_status_activate(token, EVENT_ID, entered_password, None)

    if activation_result == 'failed':
        draw_password_check_error(bot, update)

        logger.info('User @{} failed to check in by password.'.format(update.message.from_user['username']))

        user_drawing_data = get_participant_admin(EVENT_ID, get_current_user(token)['id'], TOKEN)
        draw_main_menu(bot, update, user_drawing_data)
        return STATES['MAIN_MENU']

    elif activation_result == 'already':
        draw_already_activated(bot, update)

        user_drawing_data = get_participant_admin(EVENT_ID, get_current_user(token)['id'], TOKEN)
        draw_main_menu(bot, update, user_drawing_data)
        return STATES['MAIN_MENU']

    else:
        draw_activate_successful(bot, update)

        logger.info('User @{} successfully checked in by password.'.format(update.message.from_user['username']))

        user_drawing_data = get_participant_admin(EVENT_ID, get_current_user(token)['id'], TOKEN)
        draw_main_menu(bot, update, user_drawing_data)
        return STATES['MAIN_MENU']


def change_participation_status_finish(bot, update):
    token = CONFIG_DATA['users'][str(update.message.from_user['id'])]['token']
    choice = update.message.text

    if choice == 'Ok':
        participation_status_finish(EVENT_ID, token)
        draw_finish_successful(bot, update)

        logger.info('User @{} finished participation.'.format(update.message.from_user['username']))

        user_drawing_data = get_participant_admin(EVENT_ID, get_current_user(token)['id'], TOKEN)
        draw_main_menu(bot, update, user_drawing_data)
        return STATES['MAIN_MENU']

    elif choice == 'Back':
        user_drawing_data = get_participant_admin(EVENT_ID, get_current_user(token)['id'], TOKEN)
        draw_main_menu(bot, update, user_drawing_data)
        return STATES['MAIN_MENU']

    else:
        draw_main_menu_error(bot, update)
        draw_participation_change_finish(bot, update)
        return STATES['STATUS_CHANGE_FINISH']


def change_participation_status_revert(bot, update):
    token = CONFIG_DATA['users'][str(update.message.from_user['id'])]['token']
    choice = update.message.text

    if choice == 'Ok':
        participation_status_revert(EVENT_ID, token)
        draw_revert_successful(bot, update)

        logger.info('User @{} reactivated participation.'.format(update.message.from_user['username']))

        user_drawing_data = get_participant_admin(EVENT_ID, get_current_user(token)['id'], TOKEN)
        draw_main_menu(bot, update, user_drawing_data)
        return STATES['MAIN_MENU']

    elif choice == 'Back':
        user_drawing_data = get_participant_admin(EVENT_ID, get_current_user(token)['id'], TOKEN)
        draw_main_menu(bot, update, user_drawing_data)
        return STATES['MAIN_MENU']
    else:
        draw_main_menu_error(bot, update)
        draw_participation_change_finish(bot, update)
        return STATES['STATUS_CHANGE_FINISH']


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('See you later!',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():

    updater = Updater(TOKEN)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start, pass_args=True)],
        states={
            STATES['REGISTER']: [RegexHandler('^(OK)$', register)],
            STATES['REGISTER_SKILL']: [RegexHandler('.+', register_skill)],
            STATES['REGISTER_EMAIL']: [RegexHandler('.+', register_email)],
            STATES['REGISTER_SKILL_SEARCHABLE']: [RegexHandler('^(Yes|No)$', register_skill_searchable)],
            STATES['SKILL_SEARCH']: [RegexHandler('.+', skill_search)],
            STATES['MAIN_MENU']: [RegexHandler('.+', main_menu_choice)],
            STATES['STATUS_CHANGE_ACTIVATE']: [MessageHandler(Filters.all, change_participation_status_activate)],
            STATES['STATUS_CHANGE_ACTIVATE_PASSWORD']: [MessageHandler(Filters.text, change_participation_status_activate_password)],
            STATES['STATUS_CHANGE_FINISH']: [RegexHandler('.+', change_participation_status_finish)],
            STATES['STATUS_CHANGE_REVERT']: [RegexHandler('.+', change_participation_status_revert)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    updater.dispatcher.add_handler(conv_handler)
    updater.dispatcher.add_error_handler(error)

    updater.start_polling()

    bot = Bot(TOKEN)
    launch_listener(MESSAGES_ENDPOINT, CONFIG_DATA, bot)

    updater.idle()


if __name__ == '__main__':
    main()