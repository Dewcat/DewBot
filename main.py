from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import Update
import os
import sys
import logging
token = "5769924134:AAFr2m3_mr_HbOdO42Mt8MUGAxFAaG4E4Yg"
from poker import draw
from poker import draw_five
import event
from event import dice
import data
import re
# 初始化Bot，国内需要增加proxy代理
# Updater更新者可以按照给定的TOKEN取得Telegram上的所有事件
updater = Updater(token=token, use_context=False, request_kwargs={'proxy_url': 'socks5h://127.0.0.1:7890/'})

# 构建一个调度器
# 处理用户输入的指令，例如 /start
dispatch = updater.dispatcher

# 添加指令方法
def start(bot, update):
    # print(bot)  # 机器人信息，包含机器人ID,用户名，昵称
    # print(update)  # 负责处理本次通讯的请求和响应
    message = update.message
    chat = message['chat']
    txt=message['text']
    print(txt)
    update.message.reply_text(text="hello world")  # 返回普通文本
def poker(bot, update):
    you=draw()
    message = update.message
    chat = message['chat']
    update.message.reply_text(text=you)
def five(bot, update): 
    lis=draw_five()
    you=lis[0]
    red=lis[1]
    message = update.message
    chat = message['chat']
    # update.message.reply_text(text=you) 
    dispatch.bot.sendMessage(chat_id="914088783", text=you)   
    dispatch.bot.sendMessage(chat_id="1445032357", text=red)
def roll(bot, update):
    result=dice()
    event.event_list.remove(result)
    message = update.message
    chat = message['chat']
    update.message.reply_text(text="本次事件为："+result)
def reset(bot, update):
    event.event_list=['失控','好梦在何方','教徒居所','机械之灾','余烬方阵']
    message = update.message
    chat = message['chat']
    update.message.reply_text(text="事件重置完毕")

def test(context,update):
    message = update.message
    txt=message.text
    s=re.search(r"\d+",txt)
    # print(s.group())
    update.message.reply_text(text="已增加"+s.group()+"点攻击力")


# 注册指令到调度器
dispatch.add_handler(CommandHandler('start', start))
dispatch.add_handler(CommandHandler('poker', poker))
dispatch.add_handler(CommandHandler('five', five))
dispatch.add_handler(CommandHandler('roll', roll))
dispatch.add_handler(CommandHandler('reset', reset))
filter_test=Filters.regex("增加\d点攻击力")
dispatch.add_handler(MessageHandler(filter_test,test))
if __name__ == '__main__':
    updater.start_polling()  # 启动Bot
