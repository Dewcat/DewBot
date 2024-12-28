from collections import namedtuple
from random import shuffle
from random import choice
import numpy as np
Card = namedtuple('card',['rank','suit']) #创建一个元组，具有名字
import json
class FranchDeck(object):
    rank = [str(i) for i in range(2,11)] + list('JQKA') #代表牌的大小，字符串类型
    suit = ['♥️','♦️','♠️','♣️'] #代表牌的花色
    def __init__(self):
        self._cards = [Card(rank,suit) for rank in FranchDeck.rank
                                           for suit in FranchDeck.suit] #创建一副牌，没有大小王
    def __getitem__(self, item): #字典还有长度
        return self._cards[item]
    def __len__(self):
        return len(self._cards)
    def __setitem__(self, key, value):#洗牌需要用到
        self._cards[key] = value
    def __str__(self):
        return json.dumps(self._cards,ensure_ascii=False)#打印牌为列表，但__str__方法打印的是字符串格式，需要进行序列化
a = FranchDeck()

def draw():
    tmp_you=choice(a)
    you=tmp_you.suit+tmp_you.rank
    print(you)
    # print(choice(a))
    shuffle(a)
    return you
def draw_five():
    shuffle(a)
    lis=[]
    you=""
    for i in range(5):
        tmp_you=a[i]
        you=you+(tmp_you.suit+tmp_you.rank)
        if(i!=4):
           you+="," 
    red=""      
    for i in range(5):
        tmp_red=a[i+5]
        red=red+(tmp_red.suit+tmp_red.rank)
        if(i!=4):
           red+=","     
    # print(choice(a))
    lis.append(you)
    lis.append(red)
    return lis
if __name__ == '__main__':
    l=draw_five()
    print(l[0])
    print(l[1])