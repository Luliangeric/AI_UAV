from env.control import Control
import random
import numpy as np


class Policy(Control):
    def __init__(self, pstMapInfo):
        super().__init__(pstMapInfo)
        self.pick_we_list = dict()
        self.oth_we_list = dict()

        self.pick_enemy_list = dict()
        self.oth_enemy_list = dict()

        self.good_start_list = dict()
        self.good_goal_list = dict()

        self.good_start_list_enemy = dict()
        self.good_goal_list_enemy = dict()

        self.goods_solved = dict()
        self.goods_solved_inverse = dict()
        self.goods_solved_info = dict()

        self.goods_not_solved = dict()

        self.enemy_uav = list()
        self.enemy_set_pre = set()
        self.enemy_set = set()
        self.pick_enemy_solve = set()
        self.we_uav = list()

        self.type_num = list()
        self.type_uav = list()
        self.rate = list()
        for key in self.uav_price.keys():
            self.type_uav.append(key)
            self.type_num.append(1)
            temp = self.uav_price[key]['value']
            total_value = 0
            for item in self.uav_price.keys():
                total_value += temp / self.uav_price[item]['value']
            self.rate.append(1 / total_value + 0.03)

        for item in self.uav_index.values():
            index = self.type_uav.index(item.type)
            self.type_num[index] += 1

        self.value = 0
        self.good_num = [0, 0, 0]
        self.time_max = 0

        self.kill_list = dict()

        self.low_power = (2 * self.h_low + int(max(self.parking[0], self.parking[1]) / 2)) \
                            * self.uav_price[self.cheap_uav_type]['load_weight']

        self.enemy_first_good_no = set()

    def analyze(self, pstMatchStatus):
        self.value = pstMatchStatus['we_value']
        self.enemy_uav = pstMatchStatus['UAV_enemy']

        self.we_uav = pstMatchStatus['UAV_we']
        goods = pstMatchStatus['goods']

        destroy = self.uav_update(pstMatchStatus)
        self.solve_goods(goods, destroy)
        _, free_list = self.uav_we()
        self.pick(free_list)
        self.attack(free_list)
        self.free_uav(free_list)

    def pick(self, free_list):
        # 拾取策略， 在能拿到的货物里选择价值最大的
        uav_goods_list = dict()
        for key in free_list:
            if self.uav_index[key].pos[2] < self.h_low:
                continue
            uav_goods_list[key] = self.uav_goods_dis(key)

        picked_good = set()
        for key, item in uav_goods_list.items():
            if key in self.goods_solved_inverse:
                good_no = self.goods_solved_inverse[key]
                uav = self.uav_index[key]

                good_start = self.good_start_list[good_no]
                if len(item):
                    heuristic_dis = max(abs(good_start[0] - uav.pos[0]), abs(good_start[1] - uav.pos[1])) \
                                    + abs(uav.pos[2] - self.h_low) + self.h_low  # 计算与货物的启发式距离
                    tmp_good = self.goods_solved_info[good_no]
                    dis = heuristic_dis + tmp_good[2]
                    if tmp_good[0] / dis < item[0][1]:
                        self.goods_solved_inverse.pop(self.goods_solved.pop(good_no))
                        self.good_start_list.pop(good_no)
                        self.good_goal_list.pop(good_no)
                        self.goods_solved_info.pop(good_no)
                    else:
                        for enemy in self.oth_enemy_list.values():
                            if (enemy['x'], enemy['y']) == good_start and enemy['z'] < self.h_low:
                                if enemy['load_weight'] >= uav.load_weight and \
                                        max(uav.pos[0] - good_start[0], uav.pos[1] - good_start[1]) < 2 * self.h_low:
                                    if enemy['load_weight'] == uav.load_weight and \
                                            enemy['remain_electricity'] > uav.remain_electricity:
                                        self.setpath(key, (*good_start, 0), 2)
                                self.goods_solved_inverse.pop(self.goods_solved.pop(good_no))
                                self.good_start_list.pop(good_no)
                                self.good_goal_list.pop(good_no)
                                self.goods_solved_info.pop(good_no)  # 如果对方先拾取，判断是否攻击

                                self.enemy_first_good_no.add(good_no)
                                break
                        free_list.remove(key)
                        continue
                else:
                    for enemy in self.oth_enemy_list.values():
                        if (enemy['x'], enemy['y']) == good_start and enemy['z'] < self.h_low:
                            if enemy['load_weight'] >= uav.load_weight and \
                                    max(uav.pos[0] - good_start[0], uav.pos[1] - good_start[1]) < 2 * self.h_low:
                                if enemy['load_weight'] == uav.load_weight and \
                                        enemy['remain_electricity'] > uav.remain_electricity:
                                    self.setpath(key, (*good_start, 0), 2)
                            self.goods_solved_inverse.pop(self.goods_solved.pop(good_no))
                            self.good_start_list.pop(good_no)
                            self.good_goal_list.pop(good_no)
                            self.goods_solved_info.pop(good_no)  # 如果对方先拾取，判断是否攻击

                            self.enemy_first_good_no.add(good_no)
                            break
                    free_list.remove(key)
                    continue

            for good in item:
                if good[0] in picked_good:
                    continue
                else:
                    tmp_good = self.goods_not_solved.pop(good[0])

                    self.goods_solved[good[0]] = key
                    self.goods_solved_inverse[key] = good[0]
                    self.goods_solved_info[good[0]] = (tmp_good['value'], tmp_good['weight'], tmp_good['dis'])
                    self.good_start_list[good[0]] = tmp_good['start_pos']
                    self.good_goal_list[good[0]] = tmp_good['end_pos']

                    self.pick_goods(key, good[0], tmp_good['weight'], tmp_good['start_pos'], tmp_good['end_pos'])

                    picked_good.add(good[0])
                    free_list.remove(key)
                    for enemy_no, uav_track in self.kill_list.items():
                        if key == uav_track:
                            self.kill_list[enemy_no] = None
                    break

    def attack(self, free_list):
        # 利用最便宜的无人机攻击对方的价值最大的无人机
        uav_attack_protect = dict()
        for key in free_list:
            uav = self.uav_index[key]
            if uav.type == self.cheap_uav_type and uav.pos[2] >= self.h_low:
                uav_attack_protect[key] = uav            # 获得最便宜的机型

        enemy_list = list()
        for item in self.enemy_uav:
            if not item['status'] and item['z']:
                enemy_list.append(item)
            elif item['status'] == 2 and item['no'] in self.kill_list:
                self.kill_list.pop(item['no'])
        enemy_list.sort(key=lambda x: self.uav_price[x['type']]['value'])

        for enemy in enemy_list:
            if enemy['no'] in self.kill_list.keys():
                uav_no = self.kill_list.get(enemy['no'])
                if uav_no in self.uav_index.keys():
                    uav = self.uav_index[uav_no]
                    if abs(uav.pos[0] - enemy['x']) + abs(uav.pos[1] - enemy['y']) < 12:
                        if uav.pos[0] == enemy['x'] and uav.pos[1] == enemy['y']:
                            mid_pos = (uav.pos[0], uav.pos[1], enemy['z'])
                        else:
                            mid_pos = (enemy['x'], enemy['y'], uav.pos[2])
                        self.setpath(uav_no, mid_pos, 2)
                    elif uav.IsArrive:
                        x = int((enemy['x'] - uav.pos[0]) / 5) + uav.pos[0]
                        y = int((enemy['y'] - uav.pos[1]) / 5) + uav.pos[1]
                        mid_pos = (x, y, uav.pos[2])
                        self.setpath(uav_no, mid_pos, 2)  # 如果已经派了无人机， 就不断设置最新的跟随路径

        if len(uav_attack_protect):
            for _ in range(5):
                try:
                    enemy = enemy_list.pop()  # 挑出价值最大的无人机
                except IndexError:
                    break
                if enemy['no'] in self.kill_list.keys():
                    uav_no = self.kill_list.get(enemy['no'])
                    if uav_no in self.uav_index.keys():
                        continue

                track_dis = []
                for key, uav in uav_attack_protect.items():
                    if uav.behavior == 2:
                        continue
                    dis = max(abs(uav.pos[0] - enemy['x']), abs(uav.pos[1] - enemy['y'])) + abs(uav.pos[2] - enemy['z'])
                    track_dis.append((key, dis))  # 找到距离最近的无人机
                if not len(track_dis):
                    break
                track_dis.sort(key=lambda x: x[1], reverse=True)
                key = track_dis.pop()
                uav = self.uav_index[key[0]]
                if uav.pos[0] == enemy['x'] and uav.pos[1] == enemy['y']:
                    mid_pos = (uav.pos[0], uav.pos[1], enemy['z'])
                else:
                    x = int((enemy['x'] - uav.pos[0]) / 5) + uav.pos[0]
                    y = int((enemy['y'] - uav.pos[1]) / 5) + uav.pos[1]
                    mid_pos = (x, y, uav.pos[2])
                self.setpath(key[0], mid_pos, 2)
                self.kill_list[enemy['no']] = uav.no
                free_list.remove(key[0])
                uav_attack_protect.pop(key[0])
        # 在对方拾取货物或者放下获得的时候攻击
        attack_object = list(self.pick_enemy_list.values())
        attack_object.sort(key=lambda x: x[2], reverse=True)
        for item in attack_object:
            flag = 1
            if item[3] in self.kill_list or item[3] in self.pick_enemy_solve:
                continue
            for key, uav in uav_attack_protect.items():
                if uav.behavior == 2 or uav.pos[2] < self.h_low:
                    continue
                if self.good_start_list_enemy[item[0]] in self.good_start_list.values():
                    continue
                attack_pos = np.array((*self.good_start_list_enemy[item[0]], self.h_low))
                tmp_pos = uav.pos - attack_pos
                if max(abs(tmp_pos[0]), abs(tmp_pos[1])) + abs(tmp_pos[2]) < self.h_low:  # 判断是否能在对方水平移动前赶到
                    self.setpath(key, tuple(attack_pos - (0, 0, self.h_low)), 2)
                    free_list.remove(key)
                    uav_attack_protect.pop(key)
                    self.pick_enemy_solve.add(item[3])
                    flag = 0
                    break
            if flag:
                for key, uav in uav_attack_protect.items():
                    if uav.behavior == 2 or uav.pos[2] < self.h_low:
                        continue
                    attack_pos = np.array((*self.good_goal_list_enemy[item[0]], self.h_low))
                    tmp_pos = uav.pos - attack_pos
                    tmp_pos_enemy = item[1] - attack_pos
                    dis_we = max(abs(tmp_pos[0]), abs(tmp_pos[1])) + abs(tmp_pos[2])
                    dis_enemy = max(abs(tmp_pos_enemy[0]), abs(tmp_pos_enemy[1])) + abs(tmp_pos_enemy[2])
                    if dis_we < dis_enemy and dis_enemy - dis_we <= 2 * self.h_low:  # 在放下货物时判断能否感到，也不能太早
                        self.setpath(key, tuple(attack_pos - (0, 0, self.h_low)), 2)
                        free_list.remove(key)
                        uav_attack_protect.pop(key)
                        self.pick_enemy_solve.add(item[3])
                        break

    def free_uav(self, free_list):
        # 对于空闲的无人机，给定随机位置，返回充电
        for key in free_list:
            uav = self.uav_index[key]
            if not uav.IsArrive:
                continue

            if uav.pos[2] < self.h_low:
                gpos = (uav.pos[0], uav.pos[1], self.h_low)
                behave = 1
            else:
                if uav.type != self.cheap_uav_type and uav.remain_electricity < self.low_power:
                    gpos = self.parking
                    behave = 3
                else:
                    gpos = (int(self.MapSize[0] / 2) + random.randint(-int(self.MapSize[0] / 2), int(self.MapSize[0] / 2)),
                            int(self.MapSize[1] / 2) + random.randint(-int(self.MapSize[1] / 2), int(self.MapSize[1] / 2)),
                            self.h_low + random.randint(0, 2))
                    behave = 1

            self.setpath(key, gpos, behave)

    def solve_goods(self, goods, destroy):
        # 对于撞毁的无人机，更新我方拾取的货物列表
        for key in destroy:
            index = self.type_uav.index(key[1])
            self.type_num[index] -= 1

            for enemy_no, uav_no in self.kill_list.items():
                if uav_no == key[0]:
                    self.kill_list[enemy_no] = None
                    break

            if key[0] in self.pick_we_list:
                tmp = self.pick_we_list.pop(key[0])
                self.good_start_list.pop(tmp)
                self.good_goal_list.pop(tmp)
            elif key[0] in self.goods_solved_inverse:
                good_no = self.goods_solved_inverse.pop(key[0])
                self.goods_solved.pop(good_no)
                self.good_start_list.pop(good_no)
                self.good_goal_list.pop(good_no)
                self.goods_solved_info.pop(good_no)

        # 根据服务器返回的信息更新无人机的状态，主要是货物信息
        for item in self.we_uav:
            if item['goods_no'] in self.goods_solved:
                self.good_num[1] += 1
                uav_no = self.goods_solved.pop(item['goods_no'])
                self.goods_solved_inverse.pop(uav_no)
                self.goods_solved_info.pop(item['goods_no'])

                self.pick_we_list[item['no']] = item['goods_no']

        # 处理对方无人机的信息，包括已经拾取到货物的飞机的编号、位置
        self.enemy_set.clear()
        for item in self.enemy_uav:
            self.enemy_set.add(item['no'])
        destroy_enemy = self.enemy_set_pre - self.enemy_set & self.enemy_set_pre

        self.enemy_set_pre.clear()
        self.enemy_set_pre = set(self.enemy_set)

        for key in destroy_enemy:
            if key in self.kill_list:
                self.kill_list.pop(key)
            if key in self.pick_enemy_solve:
                self.pick_enemy_solve.remove(key)

            if key in self.pick_enemy_list:
                ene_uav = self.pick_enemy_list.pop(key)
                self.good_start_list_enemy.pop(ene_uav[0])
                self.good_goal_list_enemy.pop(ene_uav[0])
            elif key in self.oth_enemy_list:
                self.oth_enemy_list.pop(key)

        for item in self.enemy_uav:
            if item['goods_no'] >= 0:
                if item['no'] not in self.pick_enemy_list:
                    for good in goods:
                        if good['no'] == item['goods_no']:
                            self.good_start_list_enemy[good['no']] = (good['start_x'], good['start_x'])
                            self.good_goal_list_enemy[good['no']] = (good['end_x'], good['end_x'])
                            self.pick_enemy_list[item['no']] = [item['goods_no'], (item['x'], item['y'], item['z']),
                                                                good['value'], item['no']]  # 添加敌方载货无人机的信息
                            break

                    if item['goods_no'] in self.goods_solved:
                        uav_no = self.goods_solved.pop(item['goods_no'])
                        self.goods_solved_inverse.pop(uav_no)
                        self.goods_solved_info.pop(item['goods_no'])
                        self.good_start_list.pop(item['goods_no'])
                        self.good_goal_list.pop(item['goods_no'])
                        if uav_no in self.uav_index:
                            self.uav_index[uav_no].reset()
                    elif item['goods_no'] in self.goods_not_solved:
                        self.goods_not_solved.pop(item['goods_no'])
                else:
                    if not item['status']:
                        self.pick_enemy_list[item['no']][1] = (item['x'], item['y'], item['z'])  # 更新位置
                if item['no'] in self.oth_enemy_list:
                    self.oth_enemy_list.pop(item['no'])
            else:
                if item['no'] in self.pick_enemy_list:
                    ene_uav = self.pick_enemy_list.pop(item['no'])
                    self.good_start_list_enemy.pop(ene_uav[0])
                    self.good_goal_list_enemy.pop(ene_uav[0])

                    if item['no'] in self.pick_enemy_solve:
                        self.pick_enemy_solve.remove(item['no'])

                self.oth_enemy_list[item['no']] = item

        # 添加货物信息
        for good in goods:
            if good['no'] in self.good_start_list or good['no'] in self.enemy_first_good_no:
                continue
            elif good['no'] in self.good_start_list_enemy:
                continue
            elif good['no'] in self.goods_solved:
                if good['left_time'] <= 2:
                    self.good_num[2] += 1
                    uav_no = self.goods_solved.pop(good['no'])
                    self.goods_solved_info.pop(good['no'])
                    self.goods_solved_inverse.pop(uav_no)
                    self.good_start_list.pop(good['no'])
                    self.good_goal_list.pop(good['no'])

                    self.uav_index[uav_no].reset()
                continue
            else:
                if good['no'] in self.goods_not_solved:
                    if good['left_time'] <= self.h_low:
                        self.good_num[2] += 1
                        self.goods_not_solved.pop(good['no'])
                    else:
                        self.goods_not_solved[good['no']]['left_time'] = good['left_time']
                elif not good['status'] and good['left_time'] > self.h_low:
                    self.good_num[0] += 1
                    s_x, s_y, e_x, e_y = good['start_x'], good['start_y'], good['end_x'], good['end_y']
                    dis = len(self.astar((s_x, s_y, self.h_low), (e_x, e_y, self.h_low))) + 2 * self.h_low
                    self.goods_not_solved[good['no']] = {'start_pos': (s_x, s_y), 'end_pos': (e_x, e_y), 'dis': dis,
                                    'weight': good['weight'], 'value': good['value'], 'left_time': good['left_time']}

    # 计算飞机与货物之间的距离，选择价值最大的
    def uav_goods_dis(self, uav_no):
        uav_goods_list = list()
        uav = self.uav_index[uav_no]
        for good_no, item in self.goods_not_solved.items():
            if uav.load_weight < item['weight'] or self.goods_has_enemy(good_no):
                continue
            else:
                heuristic_dis = max(abs(item['start_pos'][0] - uav.pos[0]), abs(item['start_pos'][1] - uav.pos[1])) \
                                 + abs(uav.pos[2] - self.h_low) + self.h_low    # 计算与货物的启发式距离
                if heuristic_dis >= item['left_time']:
                    continue
                else:
                    if (item['dis'] + 6) * item['weight'] > uav.remain_electricity:
                        continue
                    dis = heuristic_dis + item['dis']
                    uav_goods_list.append((good_no, item['value'] / dis))
        uav_goods_list.sort(key=lambda x: x[1], reverse=True)
        return uav_goods_list

    # 判断货物上方是否有敌方无人机
    def goods_has_enemy(self, good_no):
        good = self.goods_not_solved[good_no]
        for uav in self.oth_enemy_list.values():
            if (uav['x'], uav['y']) == good['start_pos'] and uav['z'] < self.h_low:
                return True
        return False

    def purchase(self):
        purchase_list = []
        while 1:
            value_list = []
            for i, key in enumerate(self.type_uav):
                # if key == self.cheap_uav_type:
                #     self.rate[i] += 0.0001
                value_list.append(self.type_num[i] / self.rate[i])
            temp = min(value_list)
            index = value_list.index(temp)
            uav_type = self.type_uav[index]
            print("+++++++++++++++++++++++++++++")
            print(uav_type)
            print(self.type_uav, self.type_num, self.rate)
            if self.value >= self.uav_price[uav_type]['value']:
                self.value -= self.uav_price[uav_type]['value']
                index = self.type_uav.index(uav_type)
                self.type_num[index] += 1
                purchase_list.append({'purchase': uav_type})
            else:
                return purchase_list


if __name__ == '__main__':
    from env.test import map, msg
    import time
    tic = time.time()
    one = Policy(map)

    print(one.analyze(msg))
    print(time.time()-tic)