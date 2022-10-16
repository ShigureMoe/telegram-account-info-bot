#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.
import logging
import pymongo
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["telegram-account-info"]
mycol = mydb["battlenet"]


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


server_list = ["战网国服", "战网国际服"]
help_messages = '/add {区服} {ID} 添加或更新帐号信息，每个区可以设置一个 \n/del {区服} 删除该区服帐号信息 \n' \
                '/get {区服} 回复其他人，获取该人已经设置的帐号，如果是空，则获取所有的 ' \
                '\n目前支持的区服：\n战网国服 战网国际服'


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    print(update.message.entities)
    update.message.reply_text(help_messages)


def list_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('目前支持的区服：\n战网国服 战网国际服')


def get_command(update: Update, context: CallbackContext) -> None:
    try:
        command = update.message.text
    except:
        update.message.reply_text(help_messages)
        return None
    try:
        server = command.split(" ")[1]
        if server in server_list:
            if update.message.reply_to_message:
                user_id = update.message.reply_to_message.from_user.id
                game_id = ''
                for x in mycol.find({"user_id": user_id, "game_zone": server}):
                    game_id = x['game_id']
                if game_id:
                    update.message.reply_text("%s: %s" % (server, game_id))
                else:
                    update.message.reply_text("未绑定帐号")
            else:
                update.message.reply_text(help_messages)
        else:
            update.message.reply_text("不支持的区服")
    except Exception as e:
        logger.error(e)
        update.message.reply_text('内部错误')


def add_command(update: Update, context: CallbackContext) -> None:
    command = update.message.text
    try:
        server = command.split(" ")[1]
        if server in server_list:
            user_id = update.message.from_user.id
            game_id = command.split(" ")[2]
            old_game_id = ''
            myquery = {"user_id": user_id, "game_zone": server}
            new_record = {"user_id": user_id, "game_zone": server, "game_id": game_id}

            for x in mycol.find():
                old_game_id = x['game_id']
            if old_game_id:
                mycol.delete_many(myquery)
                mycol.insert_one(new_record)
                update.message.reply_text("已更新")
            else:
                mycol.insert_one(new_record)
                update.message.reply_text("已添加")
        else:
            update.message.reply_text("不支持的区服")
    except Exception as e:
        logger.error(e)
        update.message.reply_text('内部错误')


def del_command(update: Update, context: CallbackContext) -> None:
    command = update.message.text
    try:
        server = command.split(" ")[1]
        if server in server_list:
            user_id = update.message.from_user.id
            myquery = {"user_id": user_id, "game_zone": server}
            mycol.delete_many(myquery)
            update.message.reply_text("已删除")
        else:
            update.message.reply_text("不支持的区服")
    except Exception as e:
        logger.error(e)
        update.message.reply_text('内部错误')


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("5717290509:AAGxznxfyTJPlFTxNiVUD6BeE3oTzJdAubQ")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("list", list_command))
    dispatcher.add_handler(CommandHandler("add", add_command))
    dispatcher.add_handler(CommandHandler("del", del_command))
    dispatcher.add_handler(CommandHandler("get", get_command))

    # on non command i.e message - echo the message on Telegram
    # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
