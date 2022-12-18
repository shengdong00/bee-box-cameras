#coding=utf-8
import pandas as pd
import random

# NOTE: the './camera_sequence.xlsx' will be overwritten everytime you run this script

df = pd.read_excel('./camera_sequence.xlsx', index_col=0)

round_num = 12*2 # 12*days

turn_lists = []
for rail in range(len(df)):
    turn_list = []
    for r in range(round_num):
        a = []
        while(len(a)<4):
            n = random.randint(0, 3)
            C = ['A', 'B', 'C', 'D']
            if n not in a:
                a.append(C[n])
        turn_list += a
    turn_lists.append(turn_list)

df['turn'] = turn_lists

df.to_excel('./camera_sequence.xlsx')

print(df)
    