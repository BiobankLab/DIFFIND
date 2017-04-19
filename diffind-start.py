# -*- coding: utf-8 -*-

import argparse
import subprocess
import os
import json


parser = argparse.ArgumentParser()
parser.add_argument('-v', '--version', help='display version number and exit', action='version', version='%(prog)s 0.0.4')
parser.add_argument('-c', help='Sequence identity threshold', type=float, required=False, default=0.9)
parser.add_argument('-g', help='By cd hit’s default algorithm, a sequence is clustered to the first cluster that meet the threshold (fast mode). If set to 1, the program will cluster it into the most similar cluster that meet the threshold(accurate but slow mode)', type=int, required=False, default=0)
parser.add_argument('-s2', help='length difference cutoff for db1, default 1.0 by default, seqs in db1 >= seqs in db2 in a same cluster if set to 0.9, seqs in db1 may just >= 90%% seqs in db2', type=float, required=False, default=1.0)
parser.add_argument('--ref', help='Reference file files will be compared with it', type=str, required=True)
parser.add_argument('--files', help='List of files to be checked against --ref', type=str, nargs='+', required=True)
parser.add_argument('--nucleotide', help='files that are going to be compared are in nucleotide format', action='store_true', required=False, default=False)
parser.add_argument('--odir', help='dir name where outputed files will be saved', type=str, required=False, default='')
parser.add_argument('--threads', help='number of threads to use', type=int, required=False, default=0)
parser.add_argument('--donot-skip-zeros', help='removing from dendrogram values that are all equal 0 for same label', action='store_true', required=False, default=False)
parser.add_argument('--donot-skip-non-zeros', help='removing from dendrogram values that are all greater then 0 for same label', action='store_true', required=False, default=False)
parser.add_argument('--dendro-file-name', help='name of pdf file containing ploted dedrogram will be saved in output dir (--odir flag)', type=str, required=False, default='dendro.pdf')
parser.add_argument('--top-font-size', help='size of font used to plot gene names on top dendrogram', type=int, required=False, default='1')
parser.add_argument('--filter-value', help='drops column if absolute value of difference between max and min in gene less then filter value', type=float, required=False, default='0')
parser.add_argument('--drop-single-zero', help='drops column if single zero found', action='store_true', required=False, default=False)
parser.add_argument('--no-clear', help='does not attach numbers to genes nqmes', action='store_false', required=False, default=True)


args = parser.parse_args()

cdict = {
    'c': args.c, 'g': args.g, 's2': args.s2, 'ref': args.ref,
    'threads': args.threads, 'files': args.files, 'odir': args.odir,
    'z': args.donot_skip_zeros, 'nz': args.donot_skip_non_zeros,
    'of': args.dendro_file_name, 'top_font': args.top_font_size, 
    'nucleotide':args.nucleotide, 'ref_cleared':args.ref.rsplit('.',1)[0]+'_cleared.'+args.ref.rsplit('.',1)[1],
    'filter':args.filter_value, 'drop_zero':args.drop_single_zero, 'clear':args.no_clear}

if not os.path.exists(args.odir):
    os.makedirs(args.odir)

if not os.path.exists(args.odir.rstrip('/')+'/clusters'):
    os.makedirs(args.odir.rstrip('/')+'/clusters')

# subprocess.call(["PYTHONPATH=''", 'luigi', '--module', 'cdhit-wf', 'clusterise', '--param', json.dumps(cdict)])
subprocess.call(['luigi', '--module', 'diffind-wf', 'clusterise', '--param', json.dumps(cdict)])
