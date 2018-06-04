import json
map ={
    "map": {
        "x": 200,
        "y": 200,
        "z": 100
    },
    "parking": {
        "x": 0,
        "y": 0
    },
    "h_low": 60,
    "h_high": 100,
    "building": [
        #因此水平上坐标位置为x->x+l-1, y->y+w-1",
        { "x": 10, "y": 10, "l": 10, "w": 10, "h": 80 },
        { "x": 40, "y": 40, "l": 10, "w": 10, "h": 60 }
    ],
     # //雾区: 固定值，整个比赛过程中不变，雾区个数根据地图而不同，
     # //xy表示雾区的起始位置，l表示长度，w表示宽度，b表示雾区最低高度，
     # //t表示雾区的最大高度，水平上坐标为x->x+l-1, y->y+w-1，垂直区间为b->t",
    "fog": [
        { "x": 60, "y": 60, "l": 10, "w": 10, "b": 55, "t": 90 },
        { "x": 35, "y": 47, "l": 15, "w": 20, "b": 60, "t": 100 }
    ],
     # //"一开始停机坪无人机信息": "固定值，整个比赛过程中不变，无人机
    # 个数根据地图而不同，无人机信息包括 编号和最大载重量，编号单方唯一"
    "init_UAV": [
        { "no": 0, "x":0,"y":0,"z":0,"load_weight": 100,"type": "F1","status": 0, "goods_no":-1},
        { "no": 1, "x":0,"y":0,"z":0,"load_weight": 20 ,"type": "F3","status": 0, "goods_no":-1},
        { "no": 2, "x":0,"y":0,"z":0,"load_weight": 20 ,"type": "F3","status": 0, "goods_no":-1}
    ],
    # //"无人机价格表": "固定值，整个比赛过程中不变，no表示无人机购买编号，
    # 价格表根据载重不同，价值也不同，初始化的无人机中的载重必定在这个价格表中，方便统计最后价值",
    "UAV_price": [
        { "type": "F1", "load_weight": 100, "value": 300 },
        { "type": "F2","load_weight": 50, "value": 200 },
        { "type": "F3","load_weight": 20, "value": 100 },
        { "type": "F4","load_weight": 30, "value": 150 },
        { "type": "F5","load_weight": 360, "value": 400 }
    ]
}

msg = {
    "token": "eyJ0eXAiOiJKV1",
    "notice": "step",
    #//比赛状态: 0表示正常比赛中，1表示比赛结束，收到为1时，参赛者可以关闭连接,
    "match_status": 0,
    #//当前时间: 当前的时间，每次给比赛者都会比上一次增加1
    "time": 1,

    #//我方无人机信息": "不同时间，数据不同。 我方无人机的当前信息，根据我方传递给服务器后，
    # 服务器经过计算后得到的数据， goods_no货物编号， -1表示没有载货物，否则表示装载了相应的货物
    #//状态说明: "无人机状态 0表示正常， 1表示坠毁， 2表示处于雾区， 其他数据暂时未定义"
    "UAV_we": [
        { "no": 0,  "type": "F1","x": 10, "y": 20, "z": 80, "goods_no": -1, "status": 0 },
        { "no": 1,  "type": "F1","x": 10, "y": 20, "z": 90, "goods_no": 0, "status": 1 },
        { "no": 2,  "type": "F1","x": 10, "y": 30, "z": 40, "goods_no": 3, "status": 0 },
        { "no": 3,  "type": "F1","x": 50, "y": 20, "z": 30, "goods_no": 5, "status": 0 },
        { "no": 4,  "type": "F1","x": 70, "y": 20, "z": 20, "goods_no": -1, "status": 1 },
        { "no": 5,  "type": "F1","x": 70, "y": 20, "z": 20, "goods_no": -1, "status": 0 }
    ],

    #//"我方目前总价值": "不同时间，数据不同，表示当前时刻，我方所拥有的所有价值，无人机价值以及获取到的运送物品价值",
    "we_value": 10000,

    #//"敌方无人机信息": "不同时间，数据不同。 敌方无人机的当前信息，根据敌方传递给服务器后，
    # 服务器经过计算后得到的数据，如果敌方无人机在雾区，状态为2， x， y，z坐标都为-1，表示无效"
    "UAV_enemy": [
        { "no": 0, "type": "F1","x": 40, "y": 20, "z": 80, "goods_no": -1, "status": 0 },
        { "no": 1,"type": "F1", "x": 20, "y": 20, "z": 90, "goods_no": 7, "status": 0 },
        { "no": 2, "type": "F1","x": 80, "y": 30, "z": 40, "goods_no": -1, "status": 0 },
        { "no": 3, "type": "F1","x": 90, "y": 20, "z": 30, "goods_no": -1, "status": 0 },
        { "no": 4, "type": "F1","x": 17, "y": 20, "z": 20, "goods_no": -1, "status": 0 },
        { "no": 5, "type": "F1","x": -1, "y": -1, "z": -1, "goods_no": -1, "status": 2 }
    ],
    #//"敌方目前总价值": "不同时间，数据不同，表示当前时刻，敌方方所拥有的所有价值，无人机价值以及获取到的运送物品价值",
    "enemy_value": 30000,

    #//物品信息: 不同时间，数据不同，no 货物唯一编号， startxy 表示货物出现的地面坐标，endxy表示货物需要运送到的地面坐标， weight表示货物的重量，
    # value表示运送到后货物的价值,start_time:货物出现的时间,remain_time:货物出现持续时长,left_time:货物可运送剩余时长,status为0表示货物正常且可以被拾起,
    # status为1表示已经被无人机拾起，status为2表示已经运送到目的地，status为3表示无效（无效包括运送过程中撞毁、货物超时未被拾起等，被删除),其实您只能看见0和1状态，因
    # 为其他状态的货物会被删除,status为0时，left_time才有意义,已经消失或送到的货物会在列表中被删除。

    "goods": [
        { "no": 0, "start_x": 3, "start_y": 3, "end_x": 98, "end_y": 3, "weight": 55, "value": 100, "start_time":15,"remain_time": 90, "left_time": 75,"status": 1},
        { "no": 1, "start_x": 98, "start_y": 13, "end_x": 3, "end_y": 3, "weight": 51, "value": 90,"start_time":15, "remain_time": 9, "left_time": 8,"status": 0},
        { "no": 2, "start_x": 15, "start_y": 63, "end_x": 81, "end_y": 33, "weight": 15, "value": 20,"start_time":15, "remain_time": 7, "left_time": 89,"status": 0},
        { "no": 3, "start_x": 3, "start_y": 3, "end_x": 98, "end_y": 3, "weight": 55, "value": 100, "start_time":15,"remain_time": 330, "left_time": 310,"status": 0},
        { "no": 5, "start_x": 3, "start_y": 3, "end_x": 98, "end_y": 3, "weight": 55, "value": 100,"start_time":15, "remain_time": 1, "left_time": 2,"status": 0}
    ]
}

if __name__ == '__main__':
    pass