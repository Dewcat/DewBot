import json
def read_data():
    with open("data.json",'r',encoding='utf-8') as load_f:
        load_data = json.load(load_f)
    return load_data
def write_data(attr,value):
    load_data=read_data()
    load_data[attr]=value
    with open("data.json",'w',encoding='utf-8') as load_f:
        json.dump(load_data, load_f,ensure_ascii=False)
def get_data(attr):
    load_data=read_data()
    return load_data[attr]

if __name__ == '__main__':
    # print(read_data())
    write_data("VIS",get_data("VIS")+1)