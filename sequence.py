#coding=utf-8
import pandas as pd
import random
import os
import numpy as np

# NOTE: the './camera_sequence.xlsx' will be overwritten everytime you run this script
# NOTE: camera and rail sequences have been fixed to './camera_sequence_fixed.xlsx'.

df = pd.read_excel('./camera_sequence.xlsx', index_col=0)

round_num = 12*60 # 12(round/d)*x(d)

random.seed(2023)

turn_lists = []
for rail in range(int(len(df)/2)):
    turn_list = ''
    for r in range(round_num):
        a = ''
        while(len(a)<5):
            n = random.randint(0, 4)
            C = ['A', 'B', 'C', 'D', 'E']
            if C[n] not in a:
                a += C[n]
        turn_list += a
    turn_lists.append(turn_list)
    turn_lists.append(turn_list)

df['turn'] = turn_lists

df.to_excel('./camera_sequence.xlsx')
print(df)

############################################
#####   Generate motion rail scripts   #####
############################################
vel = 1000 # moving speed. when F=1000, speed=11.7mm/s
loc_pos = {
    'A': 0,
    'B': 250000,
    'C': 500000,
    'D': 750000,
    'E': 1000000
}

path = './rail_scripts/'
if not os.path.exists(path):
    os.mkdir(path)

for camID in df.index:
    content = ''
    turn_list = list(df.loc[camID, 'turn'])

    row_num = 0
    for i in range(len(turn_list)):
        loc = turn_list[i]
        row_num += 1
        row = '{} 绝对位置 {} X: {} Y: {} F: {} null null null null null null\n'.format(
            row_num, row_num, loc_pos[loc], loc_pos[loc], vel
        )
        content += row
        if i<len(turn_list)-1:
            row_num += 1
            # 等待时长 = (12min - 从loc-1到loc用时)/2 + 12min + (12min- 从loc到loc+1用时)/2
            # 注意头和尾的特殊情况
            if i>0:
                pre_loc = turn_list[i-1]
                pre_time = (12*60*1e3 - np.abs(loc_pos[loc] - loc_pos[pre_loc])/11.7)*0.5
            else:
                pre_time = 0
            post_loc = turn_list[i+1]
            post_time = (12*60*1e3 - np.abs(loc_pos[loc] - loc_pos[post_loc])/11.7)*0.5
            rest_time = pre_time + 12*60*1e3 + post_time
            row = '{} 延时时间 {} 延时时间: {} null null null null null null null null null null\n'.format(
                row_num, row_num, int(rest_time)
            )
            content += row

    file_name = 'rail{}_room{}_{}.txt'.format(
        df.loc[camID, 'rail'], df.loc[camID, 'room'], camID
    )

    f = open(path+file_name, "w", encoding='utf-8')
    f.write(content)
    f.close()