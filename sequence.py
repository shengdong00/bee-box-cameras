#coding=utf-8
import pandas as pd
import random
import os

# NOTE: the './camera_sequence.xlsx' will be overwritten everytime you run this script

df = pd.read_excel('./camera_sequence.xlsx', index_col=0)

round_num = 12*1 # 12(round/d)*x(d)

turn_lists = []
for rail in range(int(len(df)/2)):
    turn_list = ''
    for r in range(round_num):
        a = ''
        while(len(a)<4):
            n = random.randint(0, 3)
            C = ['A', 'B', 'C', 'D']
            if C[n] not in a:
                a += C[n]
        turn_list += a
    turn_lists.append(turn_list)
    turn_lists.append(turn_list)

df['turn'] = turn_lists

df.to_excel('./camera_sequence.xlsx')
print(df)

vel = 1000 # moving speed
loc_pos = {
    'A': 125000,
    'B': 375000,
    'C': 625000,
    'D': 875000
}

path = './rail_scripts/'
if not os.path.exists(path):
    os.mkdir(path)

for camID in df.index:
    content = ''
    turn_list = list(df.loc[camID, 'turn'])

    row_num = 0
    for loc in turn_list:
        row_num += 1
        row = '{} 绝对位置 {} X: {} Y: {} F: {} null null null null null null\n'.format(
            row_num, row_num, loc_pos[loc], loc_pos[loc], vel
        )
        content += row

        row_num += 1
        rest_time = 3000 # TODO: how to calculate rest time? Need to check actual moving speed
        row = '{} 延时时间 {} 延时时间: {} null null null null null null null null null null\n'.format(
            row_num, row_num, rest_time
        )
        content += row

    file_name = 'rail{}_room{}.txt'.format(
        df.loc[camID, 'rail'], df.loc[camID, 'room']
    )

    f = open(path+file_name, "w", encoding='utf-8')
    f.write(content)
    f.close()