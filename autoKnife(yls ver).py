import random
import numpy as np
import matplotlib.pyplot as plt

# 3刀针对5个boss的dps
dps = [ [91, 92, 80, 85, 76], # 狗T
        [67, 79, 76, 80, 60], # 充电狼
        [62, 47, 57, 66, 46], # 弟弟刀
        ]
# 有yls后dps修正
dps_yls = [ [0, 0, 5, 3, 0], # 狗T with 亚里沙
            [0, 0, 0, 0, 0], # 充电狼 with 亚里沙
            [1, 14, 7, 12, 7], # 弟弟刀 with 亚里沙
            ]
# 5个boss血量
raid = [600, 800, 1000, 1200, 2000]
# 5个boss得分修正系数
score_per_raid = [1, 1, 1, 1, 1]
# 一共30个人打
n = 30
# 一共14个亚里沙
n_yls = 14
# 初始序列
seed = [0, 1, 2] * n + [1] * n_yls + [0] * (3 * n - n_yls) # 前90位表示出刀顺序，后90位表示哪些刀出yls(14个1,76个0)

def total_score(seed):
    curr_score = 0
    curr_raid = 0
    curr_damage = 0
    for i in range(n * 3):
        team_id = seed[i]
        curr_dps = dps[team_id][curr_raid] + (dps_yls[team_id][curr_raid] if seed[n * 3 + i] == 1 else 0)
        curr_damage += curr_dps
        curr_score += curr_dps * score_per_raid[curr_raid]
        if curr_damage > raid[curr_raid]:
            curr_damage = 0
            curr_raid += 1
            if curr_raid > 4:
                curr_raid = 0
    return curr_score

def mutate_seed(seed):
    seed_ = seed.copy()
    for it in range(5): # 每次交换5个
        i = random.randint(0, 3 * n - 1)
        j = random.randint(0, 3 * n - 1)
        tmp = seed_[i]
        seed_[i] = seed_[j]
        seed_[j] = tmp
    for it in range(5): # yls顺序也每次交换5个
        i = random.randint(0, 3 * n - 1)
        j = random.randint(0, 3 * n - 1)
        tmp = seed_[3 * n + i]
        seed_[3 * n + i] = seed_[3 * n + j]
        seed_[3 * n + j] = tmp
    return seed_

def tell_detail(seed):
    curr_raid = 0
    curr_damage = 0
    curr_series = [0, 0, 0]
    curr_series_yls = [0, 0, 0]
    for i in range(n * 3):
        team_id = seed[i]
        curr_series[team_id] += 1
        curr_series_yls[team_id] += 1 if seed[n * 3 + i] == 1 else 0
        curr_dps = dps[team_id][curr_raid] + (dps_yls[team_id][curr_raid] if seed[n * 3 + i] == 1 else 0)
        curr_damage += curr_dps
        if curr_damage > raid[curr_raid]:
            print('第%d个boss：%d个狗T(%d个yls), %d个充电狼(%d个yls), %d个dd刀(%d个yls)' % (curr_raid + 1, curr_series[0], curr_series_yls[0], curr_series[1], curr_series_yls[1], curr_series[2], curr_series_yls[2]))
            curr_damage = 0
            curr_series = [0, 0, 0]
            curr_series_yls = [0, 0, 0]
            curr_raid += 1
            if curr_raid > 4:
                curr_raid = 0
    print('第%d个boss：%d个狗T(%d个yls), %d个充电狼(%d个yls), %d个dd刀(%d个yls)' % (curr_raid + 1, curr_series[0], curr_series_yls[0], curr_series[1], curr_series_yls[1], curr_series[2], curr_series_yls[2]))

# 种子个数
n_seed = 100
# 迭代次数
n_iter = 2000

seeds = [seed] * n_seed

max_scores = []
best_seed = []

for it in range(0, n_iter):
    # 评价
    score = [total_score(x) for x in seeds]
    mean_score = np.percentile(score, 80)
    max_score = max(score)
    min_score = min(score)

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
    for i in range(n_seed - now_len):
        new_seeds.append(mutate_seed(new_seeds[random.randint(0, now_len - 1)]))
    seeds = new_seeds

tell_detail(best_seed)

plt.plot(max_scores)
plt.show()
