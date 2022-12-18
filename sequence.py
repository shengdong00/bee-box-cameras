#coding=utf-8
import pandas as pd
import math
import random

df = pd.read_excel('./camera_sequence.xlsx', index_col=0)

round_num = 12*2 # 12*days

for rail in range(1,6):
    turn_list = []
    for r in range(round_num):
        a = []
        while(len(a)<4):
            n = random.randint(1,4)
            if n not in a:
                a.append(n)
        turn_list += a
    
    for cam in df.index:
        if df.loc[cam, 'rail']==rail:
            df.loc[cam, 'turn'] = turn_list

print(df)
    