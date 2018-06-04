class Agent:
    def __init__(self, initinfo):
        self.no = initinfo['no']
        self.type = initinfo['type']
        self.pos = initinfo['pos']
        self.load_weight = initinfo['load_weight']
        self.value = initinfo['value']
        self.h_low = initinfo["h_low"]
        self.h_high = initinfo["h_high"]

        self.path = None
        self.status = 0  # 0表示正常， 1表示坠毁， 2表示处于雾区
        self.goods_no = -1

        self.behavior = 1  # 0: pick, 1: free, 2: protect/attack, 3: carefully
        self.estimate = 0

        self.IsArrive = 1
        self.wait = 0

        self.path_index = 0
        self.path_len = 0

        self.goods_list = []
        self.catch_goods = -1

        self.dir = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (-1, 1, 0), (-1, 0, 0),
                    (-1, -1, 0), (0, -1, 0), (1, -1, 0), (0, 0, 1), (0, 0, -1)]

        self.capacity = initinfo['capacity']
        self.charge = initinfo['charge']
        self.remain_electricity = initinfo['remain_electricity']

        self.charge_pos = initinfo['pos']
        self.is_charge = 1
        self.good_weight = 0

    def set_path(self, path, behave):
        self.path = path
        self.path_index = 0
        self.path_len = len(path)
        self.IsArrive = 0
        self.behavior = behave

    def next_pos(self, index=1):
        if self.path_len:
            index = self.path_index + index - 1
            if index >= self.path_len:
                index = self.path_len - 1
            return self.path[index]
        else:
            return self.pos

    def move(self, path_planning):
        if self.path and not self.wait and not self.is_charge:
            if not self._check():
                return None
            if self.path_index < self.path_len:
                if self.goods_no != -1:
                    self.remain_electricity -= self.good_weight   # 更新电量

                self.pos = self.path[self.path_index]
                self.path_index += 1
                if self.path_index == self.path_len:
                    if len(self.goods_list) == 2:
                        self.goods_no = self.catch_goods
                    if not len(self.goods_list):
                        self.path = None
                        self.path_index = 0
                        self.path_len = 0
                        self.catch_goods = -1
                        self.behavior = 1
            else:
                if self.goods_no != -1:
                    self.remain_electricity -= self.good_weight   # 更新电量

                pos = self.goods_list.pop()
                self.set_path(path_planning(self.pos, pos), 0)
                self.pos = self.path[self.path_index]
                self.path_index += 1
        else:
            if self.pos == self.charge_pos:
                self.is_charge = 1
                self.remain_electricity += self.charge
                if self.remain_electricity >= self.capacity:
                    self.remain_electricity = self.capacity
                    self.is_charge = 0

    def reset(self):
        self.path = None
        self.path_index = 0
        self.path_len = 0
        self.behavior = 1
        self.wait = 0

        self.goods_list = []
        self.catch_goods = -1
        self.IsArrive = 1

    def _check(self):
        next_pos = self.path[self.path_index]
        dir = (next_pos[0] - self.pos[0], next_pos[1] - self.pos[1], next_pos[2] - self.pos[2])
        if dir in self.dir:
            if self.pos[2] < self.h_low:
                if dir not in [(0, 0, 0), (0, 0, 1), (0, 0, -1)]:
                    self.reset()
                    return False
            return True
        else:
            self.reset()
            return False

    def getinfo(self):
        print_info = 'no:{}, type:{}, pos:{}, status:{}, goods:{}, wait:{}\n' \
                     'load_weight:{:3}, value:{:3}, arrive:{}, behavior:{}'.\
            format(self.no, self.type, self.pos, self.status, self.goods_no,
                   self.wait, self.load_weight, self.value, self.IsArrive, self.behavior)
        print(print_info)


if __name__ == '__main__':
    from env.test import map

