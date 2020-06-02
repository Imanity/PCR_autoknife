import sys
import json
import random
import numpy as np
import matplotlib.pyplot as plt

with open("info.json",'rb') as info_file:
    load_dict = json.load(info_file)

    boss = load_dict['raid_info']['boss']                       # 各boss信息
    start_round = load_dict['raid_info']['start_round']         # 起始周目
    start_boss = load_dict['raid_info']['start_boss']           # 起始boss id
    start_hp = load_dict['raid_info']['start_hp']               # 起始boss 血量

    characters = load_dict['guild_info']['extra_characters']    # 3刀的名字
    knives = load_dict['guild_info']['knives']                  # 3刀的名字
    person_num = load_dict['guild_info']['person_num']          # 出刀人数
    character_num = load_dict['guild_info']['character_num']    # 特殊角色拥有人数

    damage = load_dict['damage_info']                           # 3刀伤害

# 种子个数
n_seed = 100
# 迭代次数
n_iter = 2000

# 生成初始序列
seed = [0, 1, 2] * person_num
for i, ch in enumerate(character_num.items()):
    seed += [i + 1] * ch[1]
while len(seed) < 6 * person_num:
    seed += [0]
seeds = [seed] * n_seed

# 模拟战斗
def simulate(seed, log = True):
    curr_score = 0
    curr_round = start_round
    curr_raid = start_boss
    curr_damage = start_hp
    curr_series = [0, 0, 0] * (len(characters) + 1)
    for i in range(3 * person_num):
        # 出哪刀
        team_id = seed[i]
        team_name = knives[team_id]
        # 普通一刀
        damage_deal = damage['base'][team_name][curr_raid]
        curr_series[team_id] += 1
        # 出包含特殊角色的刀
        if seed[3 * person_num + i] != 0:
            character_id = seed[3 * person_num + i] - 1
            curr_series[team_id + 3 * (character_id + 1)] += 1
            damage_deal += damage[characters[character_id]][team_name][curr_raid]
        curr_damage += damage_deal # 这刀的伤害
        curr_score += damage_deal * boss[curr_raid]['score'] # 这刀的得分
        # 尾刀
        if curr_damage >= boss[curr_raid]['hp']:
            if log:
                print('================================================')
                print('%s (%d周目%d王):' % (boss[curr_raid]['name'], curr_round + 1, curr_raid + 1))
                for j, team in enumerate(knives):
                    txt = ''
                    for k, character in enumerate(characters):
                        if curr_series[j + 3 * (k + 1)] > 0:
                            txt = txt.join(character + ' %d 刀 ' % curr_series[j + 3 * (k + 1)])
                    print('%s 出 %d 刀 ' % (team, curr_series[j]) + (', 其中包含 ' if txt != '' else '') + txt)
                print('尾刀: %d, 补时刀 %d 转移至下一boss' % (damage_deal - curr_damage + boss[curr_raid]['hp'], curr_damage - boss[curr_raid]['hp']))
                print('================================================\n')
            curr_damage -= boss[curr_raid]['hp']
            curr_raid += 1
            curr_series = [0, 0, 0] * (len(characters) + 1)
            if curr_raid >= len(boss):
                curr_round += 1
                curr_raid = 0
    if log:
        print('================================================')
        print('%s (%d周目%d王):' % (boss[curr_raid]['name'], curr_round + 1, curr_raid + 1))
        for j, team in enumerate(knives):
            txt = ''
            for k, character in enumerate(characters):
                if curr_series[j + 3 * (k + 1)] > 0:
                    txt = txt.join(character + ' %d 刀 ' % curr_series[j + 3 * (k + 1)])
            print('%s 出 %d 刀 ' % (team, curr_series[j]) + (', 其中包含 ' if txt != '' else '') + txt)
        print('此boss打了%d' % curr_damage)
        print('================================================\n')
        print('\n此次攻略到%d周目%d王, 并打了它%d血, 总得分%d' % (curr_round + 1, curr_raid + 1, curr_damage, curr_score))
    return curr_score

# 种子变异
def mutate_seed(seed):
    seed_ = seed.copy()
    for it in range(5):
        # 每次交换5个
        i = random.randint(0, 3 * person_num - 1)
        j = random.randint(0, 3 * person_num - 1)
        tmp = seed_[i]
        seed_[i] = seed_[j]
        seed_[j] = tmp
        # 特别角色出场顺序也每次交换5个
        i = random.randint(0, 3 * person_num - 1)
        j = random.randint(0, 3 * person_num - 1)
        tmp = seed_[3 * person_num + i]
        seed_[3 * person_num + i] = seed_[3 * person_num + j]
        seed_[3 * person_num + j] = tmp
    return seed_

max_scores = []
best_seed = []

for it in range(0, n_iter):
    if it % 100 == 0:
        sys.stdout.write('\r-- Iteration %03d / %03d -- ' % (it, n_iter))
    # 评价
    score = [simulate(x, log=False) for x in seeds]
    mean_score = np.percentile(score, 80) # 只保留前20%表现型的种子
    max_score = max(score)

    max_scores.append(max_score)
    best_seed = seeds[score.index(max_score)]
    # 筛选
    new_seeds = []
    for i in range(n_seed):
        if score[i] >= mean_score:
            new_seeds.append(seeds[i])
        if len(new_seeds) > n_seed / 2:
            break
    # 变异
    now_len = len(new_seeds)
    if now_len == 0:
        now_len = 1
        new_seeds.append(seeds[0]) # 没变异出好种子也向种子池扔个种子进去,防止bug
    for i in range(n_seed - now_len):
        new_seeds.append(mutate_seed(new_seeds[random.randint(0, now_len - 1)]))
    seeds = new_seeds

# 输出最佳排刀
print('\n')
simulate(best_seed)

# 收敛曲线绘制
plt.plot(max_scores)
plt.show()
