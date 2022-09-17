from bot import dispatcher, version
from bot.helper.telegram_helper.button_build import ButtonMaker
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import sendMessage, sendMarkup, editMessage
from requests import get as rget
from telegram.ext import CommandHandler, CallbackQueryHandler

update_listener = {}

def remove_prefix(input_string: str, prefix: str) -> str:
    if prefix and input_string.startswith(prefix):
        return input_string[len(prefix):]
    return input_string


def bot_update(update, context):
    latest = rget("https://api.github.com/repos/junedkh/jmdkh-mltb/releases/latest").json()
    if remove_prefix(version.__version__, "v") < remove_prefix(latest["tag_name"], "v"):
        msg_id = update.message.message_id
        body = f"New Update Available!\n\n<b>{latest['name']}</b> : {latest['tag_name']}"
        body += f"\n\n<b>ChangeLog</b> : <a href='{latest['html_url']}'>Here</a>"
        button = ButtonMaker()
        if '(re-deploy)' in latest['name'].lower():
            button.sbutton("Update Now", f'update new {msg_id}')
        else:
            button.sbutton("Update Now", f'update now {msg_id}')
        button.sbutton("Cancel", 'update cancel')
        update_listener[msg_id] = [button.build_menu(1)]
        sendMarkup(body, context.bot, update.message, button.build_menu(1))
    else:
        sendMessage("You are using latest version", context.bot, update.message)

def update_now(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    data = data.split(" ")
    message = query.message
    msg_id = int(data[-1])
    try:
        update_listener[msg_id]
    except:
        return editMessage("Old Message", message)
    if not CustomFilters._owner_query(user_id):
        return editMessage("Only Owner can update the bot", message)
    elif data[1] == 'new':
        return editMessage("New Deployment needed", message)
    elif data[1] == 'cancel':
        del update_listener[msg_id]
        return message.delete()
    del update_listener[msg_id]
    editMessage("@junedkh is working on this feature...", message)

update_handler = CommandHandler(command='update', callback=bot_update,
                                filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
update_now_handler = CallbackQueryHandler(update_now, pattern="update", run_async=True)
dispatcher.add_handler(update_now_handler)
dispatcher.add_handler(update_handler)
