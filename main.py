from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import Update
import os
import sys
import logging
token = "5769924134:AAFr2m3_mr_HbOdO42Mt8MUGAxFAaG4E4Yg"
from poker import draw
from poker import draw_five
import event
import check
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
def forest(bot, update):
    result=event.dice_forest()
    update.message.reply_text(text="本次事件为："+result)
def town(bot, update):
    result=event.dice_town()
    update.message.reply_text(text="本次事件为："+result)
def reset(bot, update):
    event.reset()
    update.message.reply_text(text="事件重置完毕")

def VIS_check(context,update):
    txt=check.result("VIS")
    update.message.reply_text(text=txt)
def SEN_check(context,update):
    txt=check.result("SEN")
    update.message.reply_text(text=txt)
def COV_check(context,update):
    txt=check.result("COV")
    update.message.reply_text(text=txt)

def VIS_add(context,update):
    message = update.message
    txt=message.text
    s=re.search(r"\d+",txt)
    data.write_data("VIS",data.get_data("VIS")+int(s.group()))
    update.message.reply_text(text="已增加"+s.group()+"点侦查")
def VIS_dec(context,update):
    message = update.message
    txt=message.text
    s=re.search(r"\d+",txt)
    data.write_data("VIS",data.get_data("VIS")-int(s.group()))
    update.message.reply_text(text="已减少"+s.group()+"点侦查")
def SEN_add(context,update):
    message = update.message
    txt=message.text
    s=re.search(r"\d+",txt)
    data.write_data("SEN",data.get_data("SEN")+int(s.group()))
    update.message.reply_text(text="已增加"+s.group()+"点聆听")
def SEN_dec(context,update):
    message = update.message
    txt=message.text
    s=re.search(r"\d+",txt)
    data.write_data("SEN",data.get_data("SEN")-int(s.group()))
    update.message.reply_text(text="已减少"+s.group()+"点聆听")
def COV_add(context,update):
    message = update.message
    txt=message.text
    s=re.search(r"\d+",txt)
    data.write_data("COV",data.get_data("COV")+int(s.group()))
    update.message.reply_text(text="已增加"+s.group()+"点交涉")
def COV_dec(context,update):
    message = update.message
    txt=message.text
    s=re.search(r"\d+",txt)
    data.write_data("COV",data.get_data("COV")-int(s.group()))
    update.message.reply_text(text="已减少"+s.group()+"点交涉")

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
dispatch.add_handler(CommandHandler('forest',forest))
dispatch.add_handler(CommandHandler('town',town))
dispatch.add_handler(CommandHandler('reset', reset))

filter_VIS=Filters.regex("侦查检定")
dispatch.add_handler(MessageHandler(filter_VIS,VIS_check))
filter_SEN=Filters.regex("聆听检定")
dispatch.add_handler(MessageHandler(filter_SEN,SEN_check))
filter_COV=Filters.regex("交涉检定")
dispatch.add_handler(MessageHandler(filter_COV,COV_check))

filter_VIS_add=Filters.regex("增加\d+点侦查")
dispatch.add_handler(MessageHandler(filter_VIS_add,VIS_add))
filter_VIS_dec=Filters.regex("减少\d+点侦查")
dispatch.add_handler(MessageHandler(filter_VIS_dec,VIS_dec))
filter_SEN_add=Filters.regex("增加\d+点聆听")
dispatch.add_handler(MessageHandler(filter_SEN_add,SEN_add))
filter_SEN_dec=Filters.regex("减少\d+点聆听")
dispatch.add_handler(MessageHandler(filter_SEN_dec,SEN_dec))
filter_COV_add=Filters.regex("增加\d+点交涉")
dispatch.add_handler(MessageHandler(filter_COV_add,COV_add))
filter_COV_dec=Filters.regex("减少\d+点交涉")
dispatch.add_handler(MessageHandler(filter_COV_dec,COV_dec))




filter_test=Filters.regex("增加\d点攻击力")

dispatch.add_handler(MessageHandler(filter_test,test))
if __name__ == '__main__':
    updater.start_polling()  # 启动Bot
