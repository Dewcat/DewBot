import random
import data

def result(attr):
    tmp=random.randint(1,100)
    if(tmp==1):
        txt="检定值为："+str(tmp)+"，大成功！"
        return txt
    elif(tmp==100):
        txt="检定值为："+str(tmp)+"，大失败！"
        return txt
    elif(tmp<=data.get_data(attr)*0.25):
        txt="检定值为："+str(tmp)+"，极难成功！"
        return txt
    elif(tmp<=data.get_data(attr)*0.5):
        txt="检定值为："+str(tmp)+"，困难成功！"
        return txt
    elif(tmp<=data.get_data(attr)):
        txt="检定值为："+str(tmp)+"，成功！"
        return txt
    else:
        txt="检定值为："+str(tmp)+"，失败！"
        return txt

    

