import numpy as np
from env.uav import Agent


class Control:
    ACTION = [(1, 0, 0), (1, 1, 0), (0, 1, 0), (-1, 1, 0), (-1, 0, 0), (-1, -1, 0), (0, -1, 0), (1, -1, 0)]
    EXPAND = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]

    def __init__(self, pstMapInfo):
        self.MapSize = (pstMapInfo['map']['x'], pstMapInfo['map']['y'], pstMapInfo['map']['z'])

        temp = list(pstMapInfo['parking'].values())
        temp.append(0)
        self.parking = tuple(temp)

        self.h_low = pstMapInfo['h_low']
        self.h_high = pstMapInfo['h_high']

        self.building = []
        temp = pstMapInfo['building']
        for item in temp:
            build = (item["x"], item["x"] + item["l"], item["y"], item["y"] + item["w"], item["h"])
            self.building.append(build)
        self.building.sort(key=lambda x: x[4])

        self.fog = []
        temp = pstMapInfo['fog']
        for item in temp:
            build = (item["x"], item["x"] + item["l"], item["y"], item["y"] + item["w"], item["b"], item["t"])
            self.fog.append(build)

        self.init_uav = pstMapInfo['init_UAV']

        self.uav_price = dict()
        price = np.inf
        for uav in pstMapInfo['UAV_price']:
            self.uav_price[uav['type']] = uav
            if uav['value'] < price:
                price = uav['value']
                self.cheap_uav_type = uav['type']

        self.uav_init = {'h_low': self.h_low, 'h_high': self.h_high, 'pos': self.parking}

        self.uav_index = {}
        self.destroy_uav = set()
        for item in iter(self.init_uav):
            self.get_new(item['no'], item['type'])

    def get_new(self, uav_no, uav_type):
        self.uav_init['type'] = uav_type
        temp = self.uav_price[uav_type]
        self.uav_init['load_weight'] = temp['load_weight']
        self.uav_init['value'] = temp['value']
        self.uav_init['capacity'] = temp['capacity']
        self.uav_init['charge'] = temp['charge']

        self.uav_init['no'] = uav_no
        self.uav_index[uav_no] = Agent(self.uav_init)

    def setpath(self, u_num, gpos, behave=1):
        if u_num not in self.uav_index.keys() or not self._check(gpos):
            return None
        if self.uav_index[u_num].pos[2] < self.h_low and gpos[2] < self.h_low:
            if self.uav_index[u_num].pos[0] != gpos[0] or self.uav_index[u_num].pos[1] != gpos[1]:
                return None
        uav = self.uav_index[u_num]
        uav.reset()
        uav.set_path(self.optimal_path(uav.pos, gpos), behave)

    def pick_goods(self, u_num, g_no, g_weight, g_spos, g_gpos):
        goods_list = list()
        uav = self.uav_index.get(u_num)
        if not uav:
            return None
        uav.reset()

        self.setpath(u_num, (*g_spos, self.h_low), 1)
        goods_list.append((*g_gpos, 0))
        goods_list.append((*g_gpos, self.h_low))
        goods_list.append((*g_spos, 0))

        uav.goods_list = goods_list
        uav.catch_goods = g_no
        uav.good_weight = g_weight

    def drive_no(self, no, pos, index=-1):
        uav = self.uav_index[no]
        uav.wait = 1
        uav.pos = pos
        uav.path_index += index

        if uav.goods_no != -1:
            uav.remain_electricity -= uav.good_weight

    def uav_update(self, pstMatchStatus):
        destroy_list = []
        for item in pstMatchStatus['UAV_we']:
            if item['no'] not in self.uav_index:
                if item['no'] not in self.destroy_uav:
                    self.get_new(item['no'], item['type'])
            else:
                if item['status'] == 1:
                    self.uav_index.pop(item['no'])
                    self.destroy_uav.add(item['no'])
                    destroy_list.append((item['no'], item['type']))
                else:
                    uav = self.uav_index[item['no']]
                    uav.status = item['status']
                    uav.goods_no = item['goods_no']  # update uav states
        return destroy_list

    def step(self):
        allow = 0
        for item in self.uav_index.values():
            if item.behavior == 3:
                if max(abs(item.pos[0] - self.parking[0]), abs(item.pos[1] - self.parking[1])) < 3:
                    allow = -1
            else:
                if item.pos[0] == self.parking[0] and item.pos[1] == self.parking[1] and 0 < item.pos[2] <= self.h_low:
                    allow = 1
                    break

        for item in self.uav_index.values():
            if not allow:
                item.pass_allow = 1
            elif allow == 1:
                if item.behavior == 3 and max(abs(item.pos[0] - self.parking[0]), abs(item.pos[1] - self.parking[1])) < 4:
                    item.pass_allow = 0
            else:
                if item.pos == self.parking:
                    item.pass_allow = 0
                if item.behavior == 3:
                    item.pass_allow = 1

        self.check_safe()

        for item in self.uav_index.values():

            item.move(self.optimal_path)

    def check_safe(self):
        check_point = set()
        temp = dict()
        charge_uav = dict()
        for key, item in self.uav_index.items():
            if item.IsArrive or item.is_charge:
                check_point.add(item.pos)
            else:
                if not item.pass_allow and item.behavior == 3:
                    charge_uav[key] = item
                else:
                    temp[key] = item
        for behavior in (0, 2, 3, 1):
            for key, item in temp.items():
                if item.behavior != behavior:
                    continue
                item.wait = 0
                pos = item.next_pos()
                if pos == self.parking:
                    continue
                mid_pos = (item.pos + np.array(pos)) / 2
                flag = 1
                if item.pos in check_point and item.pos != self.parking:
                    if pos in check_point or tuple(mid_pos) in check_point:
                        next_pos = item.next_pos(2)
                        next_step = np.array(next_pos) - np.array(pos)
                        step = np.array(pos) - np.array(item.pos)
                        if tuple(next_step) == (0, 0, 0):
                            try:
                                dire = self.ACTION.index(tuple(step))
                            except ValueError:
                                pass
                            else:
                                for dire_index in [1, -1]:
                                    tmp_dir = dire_index + dire
                                    if tmp_dir > 7:
                                        tmp_dir -= 8
                                    elif tmp_dir < 0:
                                        tmp_dir += 8
                                    next_try_pos = self.ACTION[tmp_dir] + np.array(item.pos)
                                    if self._check(next_try_pos) and self._check_point(check_point, item.pos,
                                                                                       tuple(next_try_pos)):
                                        check_point.add(tuple(next_try_pos))
                                        check_point.add(tuple((item.pos + next_try_pos) / 2))

                                        self.drive_no(key, tuple(next_try_pos), 0)
                                        flag = 0
                                        break
                        elif tuple(next_step) == tuple(step):
                            try:
                                dire = self.ACTION.index(tuple(step))
                            except ValueError:
                                pass
                            else:
                                for dire_index in [1, -1]:
                                    tmp_dir = dire_index + dire
                                    if tmp_dir > 7:
                                        tmp_dir -= 8
                                    elif tmp_dir < 0:
                                        tmp_dir += 8
                                    next_try_pos = self.ACTION[tmp_dir] + np.array(item.pos)
                                    if self._check(next_try_pos) and self._check_point(check_point, item.pos,
                                                                                       tuple(next_try_pos)):
                                        check_point.add(tuple(next_try_pos))
                                        check_point.add(tuple((item.pos + next_try_pos) / 2))

                                        if dire % 2:
                                            self.drive_no(key, tuple(next_try_pos), 0)
                                        else:
                                            self.drive_no(key, tuple(next_try_pos), 1)
                                        flag = 0
                                        break
                        elif tuple(next_step) != tuple(step):
                            next_try_pos = np.array(item.pos) + next_step
                            if self._check(next_try_pos) and self._check_point(check_point, item.pos,
                                                                               tuple(next_try_pos)):
                                check_point.add(tuple(next_try_pos))
                                check_point.add(tuple((item.pos + next_try_pos) / 2))

                                self.drive_no(key, tuple(next_try_pos), 1)
                                continue
                        if flag:
                            for tmp_dir in [(0, 0, 1), (0, 0, -1)]:
                                next_try_pos = np.array(item.pos) + tmp_dir
                                if self._check(next_try_pos) and self._check_point(check_point, item.pos,
                                                                                   tuple(next_try_pos)):
                                    check_point.add(tuple(next_try_pos))
                                    check_point.add(tuple((item.pos + next_try_pos) / 2))

                                    self.drive_no(key, tuple(next_try_pos), -1)
                                    break
                else:
                    if pos in check_point or tuple(mid_pos) in check_point:
                        item.wait = 1
                        check_point.add(item.pos)
                        if item.goods_no != -1:
                            item.remain_electricity -= item.good_weight
                        continue

                if not item.wait:
                    pos = item.next_pos()
                    check_point.add(pos)
                    check_point.add(tuple(mid_pos))
        for key, item in charge_uav.items():
            if item.pos in check_point:
                next_pos = (item.pos[0], item.pos[1], item.pos[2] - 1)
                check_point.add(next_pos)
                self.drive_no(key, next_pos)

    def _check_point(self, check_point, pos, next_pos):
        mid_pos = (np.array(pos) + np.array(next_pos)) / 2
        if tuple(mid_pos) in check_point or next_pos in check_point:
            return False
        else:
            return True

    def _check(self, pos):
        is_in_build = 0
        for item in self.building:
            if pos[2] < item[4] and item[0] <= pos[0] < item[1] and item[2] <= pos[1] < item[3]:
                is_in_build = 1
                break
        is_in_map = 0 <= pos[0] < self.MapSize[0] and 0 <= pos[1] < self.MapSize[1] and 0 <= pos[2] <= self.h_high
        if not is_in_build and is_in_map:
            return True
        else:
            return False

    def uav_info(self):
        uav_info = []
        for key, item in self.uav_index.items():
            if item.no == 0:
                item.getinfo()
            temp = {'no': int(item.no), 'x': int(item.pos[0]), 'y': int(item.pos[1]), 'z': int(item.pos[2]),
                    'goods_no': int(item.goods_no), 'remain_electricity': item.remain_electricity}
            uav_info.append(temp)
        return uav_info

    def uav_we(self):
        busy_list = set()
        arrive_list = set()
        for key, item in self.uav_index.items():
            if item.behavior == 1 or item.behavior == 3:
                arrive_list.add(key)
            else:
                busy_list.add(key)
        return busy_list, arrive_list

    def optimal_path(self, spos3, gpos3):
        global_path = []
        if spos3[2] < gpos3[2]:
            temppos = spos3
            while temppos[2] < gpos3[2]:
                temppos = temppos + np.array((0, 0, 1))
                global_path.append(tuple(temppos))
            spos3 = temppos
        spos3t = [spos3]
        gpos3t = [gpos3]
        for item in self.building:
            if item[4] > spos3[2]:
                spos3t.append((*spos3[0:2], item[4]))
                gpos3t.append(gpos3)
                if len(spos3t) > 2:
                    break

        res = []
        for spos, gpos in zip(spos3t, gpos3t):
            res.append(self.astar(spos, gpos))

        length = []
        for i, item in enumerate(res):
            length.append(len(item) + 2 * (spos3t[i][2] - spos3[2]))
        temp = min(length)
        for index, cost in enumerate(length):
            if cost == temp:
                temppos = spos3
                while temppos[2] < spos3t[index][2]:
                    temppos = temppos + np.array((0, 0, 1))
                    global_path.append(tuple(temppos))
                global_path.extend(res[index])

                temppos = np.array([*gpos3[0:2], temppos[2]])
                while temppos[2] > gpos3[2]:
                    temppos = temppos + np.array((0, 0, -1))
                    global_path.append(tuple(temppos))
                return global_path

    def astar(self, spos3, gpos3):
        spos = tuple(spos3[0:2])
        gpos = tuple(gpos3[0:2])
        if spos == gpos:
            return []
        openlist = dict()
        closelist = dict()
        openlist[spos] = [(0, 0), spos, np.inf, 0]

        while len(openlist) and not self._expend(openlist, closelist, spos3[2], gpos):
            pass

        node = gpos
        path = list()
        path.append((*gpos,spos3[2]))
        while 1:
            node = closelist[node]
            if node == spos:
                break
            path.append((*node,spos3[2]))
        path.reverse()
        return path

    def _expend(self, openlist, closelist, height, gpos):
        node = sorted(openlist.values(), key=lambda x: x[2], reverse=True).pop()
        openlist.pop(node[1])
        if node[1] == gpos:
            closelist[gpos] = node[0]
            return 1
        for i in range(8):
            tempnode = np.array(node[1]) + np.array(self.EXPAND[i])
            try:
                closelist[tuple(tempnode)]
            except KeyError:
                if self._check((*tempnode,height)):
                    g = node[-1] + 1
                    heuris = max(abs(tempnode[0] - gpos[0]), abs(tempnode[1] - gpos[1]))

                    try:
                        existnode = openlist[tuple(tempnode)]
                        if heuris + g < existnode[2]:
                            openlist[tuple(tempnode)][2] = heuris + g
                    except KeyError:
                        nextnode = [node[1], tuple(tempnode), heuris + g, g]
                        openlist[tuple(tempnode)] = nextnode
        closelist[node[1]] = node[0]
        return 0

    def getinfo(self):
        printinfo = 'building:{},fog:{}'.format(self.building, self.fog)
        print(printinfo)


if __name__ == '__main__':
    pass



