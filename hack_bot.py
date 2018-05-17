import logging
import sys
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

TOKEN = "594797323:AAGaXnxv_lMjtMJHun5_4VuVVJnzEZFNA7k"
SIGNATURE_TOKEN = "493790820:AAHnEH4Hbx41E7CBFULvCIa-MFRMjHchUeU"

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
    'Toggle searchable',
    'Change participation status',
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
        if CONFIG_DATA['users'][str(user['id'])]['status'] == 'non-registered':
            draw_register_button(bot, update)
            return STATES['REGISTER']
        else:
            update.message.reply_text('Welcome back!')
            draw_main_menu(bot, update)
            return STATES['MAIN_MENU']


def register(bot, update):
    token = CONFIG_DATA['users'][update.message.from_user['id']]['token']

    skills = get_skills(token)
    skills_keyboard = [[skill['tag']] for skill in skills]

    draw_skill_buttons(bot, update, skills_keyboard)

    return STATES['REGISTER_SKILL']

def register_skill(bot, update):
    token = CONFIG_DATA['users'][update.message.from_user['id']]['token']

    skills = get_skills(token)
    skills_reversed = {skill['tag']: skill['id'] for skill in skills}
    skills_keyboard = [[skill['tag']] for skill in skills]

    db_user = get_current_user(token)

    if update.message.text != 'Done!':
        chosen_skill = update.message.text

        if chosen_skill not in skills_reversed:
            draw_error_skill_prompt(bot, update)
            return STATES['REGISTER']

        db_user['skills'].append({"id": skills_reversed[chosen_skill]})

        update_current_user(token, db_user)
        draw_skill_buttons_with_done(bot, update, skills_keyboard)
        return STATES['REGISTER_SKILL']

    draw_skill_searchable_question(bot, update)
    return STATES['REGISTER_SKILL_SEARCHABLE']



def register_skill_searchable(bot, update):
    token = CONFIG_DATA['users'][str(update.message.from_user['id'])]['token']
    db_user = get_current_user(token)

    answer = update.message.text

    if answer == 'Yes':
        CONFIG_DATA['users'][str(update.message.from_user['id'])]['is_searchable'] = True
    else:
        CONFIG_DATA['users'][str(update.message.from_user['id'])]['is_searchable'] = False

    if not db_user['email']:
        draw_email_prompt(bot, update)
        return STATES['REGISTER_EMAIL']
    else:
        CONFIG_DATA['users'][str(update.message.from_user['id'])]['status'] = 'registered'
        write_config()
        draw_main_menu(bot, update)
        return STATES['MAIN_MENU']


def register_email(bot, update):
    token = CONFIG_DATA['users'][update.message.from_user['id']]['token']
    entered_email = update.message.text

    db_user = get_current_user(token)
    db_user['email'] = entered_email

    try:
        update_current_user(token, db_user)
    except ValueError:
        draw_error_email_prompt(bot, update)
        return STATES['REGISTER_EMAIL']

    CONFIG_DATA['users'][update.message.from_user['id']]['status'] = 'registered'
    write_config()

    draw_main_menu(bot, update)
    return STATES['MAIN_MENU']

def main_menu_choice(bot, update):
    choice = update.message.text
    if choice not in MENU_CHOICES:
        draw_main_menu_error(bot, update)
        draw_main_menu(bot, update)
        return STATES['MAIN_MENU']

    if choice == 'Search participants by skill':
        token = CONFIG_DATA['users'][str(update.message.from_user['id'])]['token']

        skills = get_skills(token)
        skills_keyboard = [[skill['tag']] for skill in skills]
        draw_search_skill_buttons(bot, update, skills_keyboard)

        return STATES['SKILL_SEARCH']

    if choice == 'Show Event Schedule':
        draw_event_schedule(bot, update)
        draw_main_menu(bot, update)
        return STATES['MAIN_MENU']

    if choice == 'My Profile':
        token = CONFIG_DATA['users'][str(update.message.from_user['id'])]['token']
        user = get_current_user(token)
        draw_user_profile(bot, update, user)
        draw_main_menu(bot, update)
        return STATES['MAIN_MENU']

    if choice == 'Change participation status':
        token = CONFIG_DATA['users'][str(update.message.from_user['id'])]['token']
        db_user = get_current_user(token)
        user_id = db_user['id']

        participants = get_participants(EVENT_ID, token)
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

    participants = get_participants(EVENT_ID, token)
    chosen_skill = update.message.text

    #chosen_participants

def change_participation_status_activate(bot, update):
    token = CONFIG_DATA['users'][str(update.message.from_user['id'])]['token']
    choice = update.message.text
    location = update.message.location
    if choice == 'Wi-Fi Password':
        draw_participation_change_activate_password(bot, update)
        return STATES['STATUS_CHANGE_ACTIVATE_PASSWORD']
    elif not choice and location:

        if not check_location(location):
            draw_location_check_error(bot, update)
            draw_main_menu(bot, update)
            return STATES['MAIN_MENU']

        else:
            change_participation_status_activate(token)
            draw_activate_successful(bot, update)
            draw_main_menu(bot, update)
            return STATES['MAIN_MENU']

    elif choice == 'Back':
        draw_main_menu(bot, update)
        return STATES['MAIN_MENU']
    else:
        draw_main_menu_error(bot, update)
        draw_participation_change_activate(bot, update)
        return STATES['STATUS_CHANGE_ACTIVATE']


def change_participation_status_activate_password(bot, update):
    token = CONFIG_DATA['users'][str(update.message.from_user['id'])]['token']
    entered_password = update.message.text

    if not check_password(entered_password):
        draw_password_check_error(bot, update)
        draw_main_menu(bot, update)
        return STATES['MAIN_MENU']

    else:
        change_participation_status_activate(token)
        draw_activate_successful(bot, update)
        draw_main_menu(bot, update)
        return STATES['MAIN_MENU']

def change_participation_status_finish(bot, update):
    token = CONFIG_DATA['users'][str(update.message.from_user['id'])]['token']
    choice = update.message.text

    if choice == 'Ok':
        participation_status_finish(token)
        draw_finish_successful(bot, update)
        draw_main_menu(bot, update)
        return STATES['MAIN_MENU']
    elif choice == 'Back':
        draw_main_menu(bot, update)
        return STATES['MAIN_MENU']
    else:
        draw_main_menu_error(bot, update)
        draw_participation_change_finish(bot, update)
        return STATES['STATUS_CHANGE_FINISH']

def change_participation_status_revert(bot, update):
    token = CONFIG_DATA['users'][str(update.message.from_user['id'])]['token']
    choice = update.message.text

    if choice == 'Ok':
        participation_status_revert(token)
        draw_revert_successful(bot, update)
        draw_main_menu(bot, update)
        return STATES['MAIN_MENU']
    elif choice == 'Back':
        draw_main_menu(bot, update)
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