map ={
    "map": {
        "x": 100,
        "y": 100,
        "z": 100
    },
    "parking": {
        "x": 0,
        "y": 0
    },
    "h_low": 60,
    "h_high": 99,
    "building": [
        { "x": 10, "y": 10, "l": 10, "w": 10, "h": 80 },
        { "x": 40, "y": 40, "l": 10, "w": 10, "h": 60 }

    ],

    "fog": [
        { "x": 60, "y": 60, "l": 10, "w": 10, "b": 55, "t": 90 },
        { "x": 35, "y": 47, "l": 15, "w": 20, "b": 60, "t": 99 }
    ],
    "init_UAV": [
        { "no": 0, "x":0,"y":0,"z":0,"load_weight": 100,"type": "F1","status": 0, "remain_electricity": 0,"goods_no":-1},
        { "no": 1, "x":0,"y":0,"z":0,"load_weight": 20 ,"type": "F3","status": 0, "remain_electricity": 0,"goods_no":-1},
        { "no": 2, "x":0,"y":0,"z":0,"load_weight": 20 ,"type": "F3","status": 0, "remain_electricity": 0,"goods_no":-1}],
    "UAV_price": [
        { "type": "F1", "load_weight": 100, "value": 300,"capacity": 9000,"charge": 1000},
        { "type": "F2","load_weight": 50, "value": 200,"capacity": 8000 ,"charge": 800},
        { "type": "F3","load_weight": 20, "value": 100,"capacity": 5000 ,"charge": 400},
        { "type": "F4","load_weight": 30, "value": 150,"capacity": 6000 ,"charge": 500},
        { "type": "F5","load_weight": 360, "value": 400,"capacity": 20000,"charge": 3000}
    ],

}

msg = {
    "token": "eyJ0eXAiOiJKV1",
    "notice": "step",
    "match_status": 0,
    "time": 16,

    "UAV_we": [
        { "no": 0,  "type": "F1","x": 10, "y": 20, "z": 80, "goods_no": -1,"load_weight": 100, "remain_electricity": 1000,"status": 0 },
        { "no": 1,  "type": "F1","x": 10, "y": 20, "z": 90, "goods_no": 0,"load_weight": 100, "remain_electricity": 1000,"status": 0 },
        { "no": 2,  "type": "F1","x": 10, "y": 30, "z": 40, "goods_no": 3,"load_weight": 100,"remain_electricity": 1000,"status": 0 },
        { "no": 3,  "type": "F1","x": 50, "y": 20, "z": 30, "goods_no": 5,"load_weight": 100,"remain_electricity": 1000,"status": 0 },
        { "no": 4,  "type": "F1","x": 70, "y": 20, "z": 20, "goods_no": -1,"load_weight": 100,"remain_electricity": 1000, "status": 1 }
    ],

    "we_value": 10000,

    "UAV_enemy": [
        { "no": 0, "type": "F1","x": 40, "y": 20, "z": 80, "goods_no": -1,"load_weight": 100,"remain_electricity": 1000,"status": 0 },
        { "no": 1,"type": "F1", "x": 20, "y": 20, "z": 90, "goods_no": 7,"load_weight": 100,"remain_electricity": 1000,"status": 0 },
        { "no": 2, "type": "F1","x": 80, "y": 30, "z": 40, "goods_no": -1,"load_weight": 100,"remain_electricity": 1000,"status": 0 },
        { "no": 3, "type": "F1","x": 90, "y": 20, "z": 30, "goods_no": -1,"load_weight": 100,"remain_electricity": 1000,"status": 0 },
        { "no": 5, "type": "F1","x": -1, "y": -1, "z": -1, "goods_no": -1,"load_weight": 100,"remain_electricity": 1000,"status": 2 }
    ],
    "enemy_value": 30000,

    "goods": [
        { "no": 0, "start_x": 3, "start_y": 3, "end_x": 98, "end_y": 3, "weight": 55, "value": 100, "start_time":15,"remain_time": 90, "left_time": 89,"status": 1},
        { "no": 1, "start_x": 98, "start_y": 13, "end_x": 3, "end_y": 3, "weight": 51, "value": 90,"start_time":15, "remain_time": 9, "left_time": 8,"status": 0},
        { "no": 2, "start_x": 15, "start_y": 63, "end_x": 81, "end_y": 33, "weight": 15, "value": 20,"start_time":15, "remain_time": 7, "left_time": 6,"status": 0},
        { "no": 3, "start_x": 3, "start_y": 3, "end_x": 98, "end_y": 3, "weight": 55, "value": 100, "start_time":15,"remain_time": 330, "left_time": 329,"status": 0},
        { "no": 5, "start_x": 3, "start_y": 3, "end_x": 98, "end_y": 3, "weight": 55, "value": 100,"start_time":15, "remain_time": 3, "left_time": 2,"status": 0}
    ]
}


if __name__ == '__main__':
    pass