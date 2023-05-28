import random
import json

def read_event_list(filename):
    with open(filename,'r',encoding='utf-8') as load_f:            
        return json.load(load_f)
def drop_event(filename,event):
    load_event_list=read_event_list(filename)
    load_event_list.remove(event)
    with open(filename,'w',encoding='utf-8') as load_f:
        json.dump(load_event_list,load_f)
def dice_forest():
    event_list_forest=read_event_list("event_list_forest.json")
    u=random.choice(event_list_forest)
    if(u== "似曾相识" or u== "无知是福" or u== "探险小队" or u== "狭路相逢" or u== "医者之志" or u== "不期而遇"):
        drop_event("event_list_forest.json",u)
    return u
def dice_town():
    event_list_town=read_event_list("event_list_town.json")
    u=random.choice(event_list_town)
    if(u== "变卖身家" or u=="是非黑白" or u=="狂徒妄念"):
        drop_event("event_list_town.json",u)
    return u
def reset():
    event_list_forest=["打发时间","不期而遇","眼观六路","耳听八方","珍禽异兽","所见即所得","似曾相识","无知是福","探险小队","狭路相逢","森林哨兵","医者之志"]
    event_list_town=["兽本运作","变卖身家","摊贩经济","狂徒妄念","是非黑白","冒险委托"]
    with open("event_list_forest.json",'w',encoding='utf-8') as load_f1:
        json.dump(event_list_forest,load_f1)
    with open("event_list_town.json",'w',encoding='utf-8') as load_f2:
         json.dump(event_list_town,load_f2)
    