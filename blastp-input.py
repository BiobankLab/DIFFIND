# -*- coding: utf-8 -*-

import pandas as pd
from pycdhit import cdhit_set
import argparse
import os


parser = argparse.ArgumentParser()
parser.add_argument('-i', '--indir', help='directory contains files to analisis all files will be selected', type=str, required=True)
parser.add_argument('-c', help='identity threshold. For instance 70 mean 70% similarity', type=float, default=0)
parser.add_argument('-o', '--output', help='Output file where dendrogram will be saved', type=str, default='dendro.pdf')
parser.add_argument('--top-font-size', help='size of top font', type=int, default=1)
parser.add_argument('--left-font-size', help='size of font of left axis', type=int, default=6)
parser.add_argument('--width', help='size of font of left axis', type=int, default=20)
parser.add_argument('--height', help='size of font of left axis', type=int, default=10)

args = parser.parse_args()

print args

files = next(os.walk(args.indir))[2]

g_name = ''
temp_score = []
df_dict = {}
df = pd.DataFrame()
for f in files:
    first = 1
    with open(args.indir.rstrip('/')+'/'+f) as r:
        content = r.readlines()
        for l in content:
            if l[0] != '#':
                templ = l.split('\t')
                if templ[0] != g_name:
                    try:
                        df_dict[g_name] = float(max(temp_score))
                        g_name = templ[0]
                        temp_score = []
                    except ValueError:
                        g_name = templ[0]
                        temp_score.append(templ[2])
                        continue
                temp_score.append(templ[2])
        df_dict[g_name] = max(temp_score)
        name = f.split('/')[-1]
        name = name.split()[0]
        df = df.append(pd.DataFrame(data=df_dict, index=[name]))
        g_name = ''
        temp_score = []
        df_dict = {}
        name = ''

df = df.fillna(0)
df.to_csv('first.csv')
df = df.apply(pd.to_numeric)#_get_numeric_data()
df.to_csv('bcut.csv')
df[df<args.c] = 0
df.to_csv(args.output.split('.')[0]+'.csv')
chit_set = cdhit_set()
plot = chit_set.make_dendrogram(df, (args.width, args.height), args.top_font_size, args.left_font_size)
plot.savefig(args.output, bbox_inches='tight')
