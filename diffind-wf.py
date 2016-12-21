# -*- coding: utf-8 -*-

import luigi
import subprocess
# from multiprocessing import Pool
from pathos.multiprocessing import ProcessingPool as Pool
import os
from pycdhit import *
from fatool import *

import csv
import traceback
import sys

'''
ref = i
files [i2]
'''


class cdhit_analisys(luigi.Task):
    param = luigi.DictParameter()

    @staticmethod
    def exec_cdhit(cmd):
        subprocess.call(cmd)

    def requires(self):
        return []

    def run(self):
        cmd_list = []
        for f in self.param['files']:
            cmd_list.append(['cdhit-2d', '-i', str(self.param['ref']), '-i2', str(f), '-c', str(self.param['c']), '-g', str(self.param['g']), '-s2', str(self.param['s2']), '-o', self.param['odir']+'/'+os.path.splitext(os.path.basename(f))[0]])
        p = Pool(int(self.param['threads']))
        # p.map(cdhit_analisys.exec_cdhit, cmd_list)
        with Pool(int(self.param['threads'])) as p:
            p.map(cdhit_analisys.exec_cdhit, cmd_list)

    def output(self):
        fl = []
        for f in self.param['files']:
            # print self.param['odir']+'/'+os.path.splitext(os.path.basename(f))[0]+'.clstr'
            fl.append(luigi.LocalTarget(self.param['odir']+'/'+os.path.splitext(os.path.basename(f))[0]+'.clstr'))
        return fl


class plot(luigi.Task):

    param = luigi.DictParameter()

    def requires(self):
        return [cdhit_analisys(self.param)]

    def run(self):
        chit_set = cdhit_set()
        for f in self.param['files']:
            c = cdhit_result(str(os.path.splitext(os.path.basename(f))[0]))
            print self.param['odir']+'/'+os.path.splitext(os.path.basename(f))[0]+'.clstr'
            c.load_from_file(str(self.param['odir']+'/'+os.path.splitext(os.path.basename(f))[0]+'.clstr'))
            chit_set.append(c)

        chit_set.analyze()
        z = 1
        nz = 1
        #  set flags wheteher to remove all zeros values or not (not meaningful)
        if self.param['z']:
            z = 0
        #  set flags wheteher to remove all non zeros values or not (not meaningful)
        if self.param['nz']:
            nz = 0
        sys.setrecursionlimit(10000)
        df = chit_set.to_df(z, nz)
        #plot = chit_set.make_dendrogram2(df);
        plot = chit_set.make_dendrogram(df, (40, 20), self.param['top_font'])
        # print self.param['of']
        plot.savefig(self.param['odir']+'/'+self.param['of'], bbox_inches='tight')
        chit_set.clusters.to_csv(self.param['odir']+'/'+'cluster_info.csv', ';')
        '''
        with open(self.param['odir']+'/'+'summary.txt', 'w') as w:
            w.write('Summary of analyzis:\nlabels from dendrogram the most meaningfull:\n')
            for r in df.labels:
                w.write(r+'\n')
            w.write('\nAll values non zeros not meaningfull:\n')
            for r in chit_set.all_zeros:
                w.write(r+'\n')
            w.write('\nAll values non zeros not meaningfull:\n')
            for r in chit_set.all_non_zeros:
                w.write(r+'\n')
       '''

    def output(self):
        return luigi.LocalTarget(self.param['odir']+'/'+'dendro.pdf')
        # return [luigi.LocalTarget(self.param['odir']+'/'+'dendro.pdf'), luigi.LocalTarget(self.param['odir']+'/'+'summary.txt')]


class clusterise(luigi.Task):

    param = luigi.DictParameter()

    def requires(self):
        return [plot(self.param)]

    def run(self):
        try:
            # /home/blul/BIOIT/blul_cdhit/workflow/cluster_info.csv
            c = 1
            ref_fa = Fa.load_from_file(str(self.param['ref']))
            cluster_contigs = []
            outr = []

            # creates fastas with sequences from each cluster one file per cluster
            with open(self.param['odir']+'/'+'cluster_info.csv') as f:
                reader = csv.reader(f, delimiter=';')
                header = reader.next()
                for r in reader:

                    if c != int(r[1]):
                        result_fa = Fa(cluster_contigs, 'c'+str(c))
                        result_fa.write(str(self.param['odir']+'/clusters/'+'c_'+str(c)+'.fasta'))
                        cluster_contigs = []
                        c = int(r[1])

                    cc = ref_fa.extract_by_name_frag(r[2])
                    cluster_contigs += cc
                    r.append(cc[0].name)
                    r.append(cc[0].seq)
                    outr.append(r)

            # saving last cluster
            result_fa = Fa(cluster_contigs, 'c'+str(c))
            result_fa.write(str(self.param['odir']+'/clusters/'+'c_'+str(c)+'.fasta'))
            # creates adv cluster info file csv containing full name and sequenc
            with open(self.param['odir']+'/'+'adv_cluster_info.csv', 'w') as o:
                w = csv.writer(o, delimiter=';')
                for r in outr:
                    w.writerow(r)
        except:
            traceback.print_exc()

    def output(self):
        #  not defining cluster files just adv_cluster_info which is genrated ot the end
        return luigi.LocalTarget(self.param['odir']+'/'+'adv_cluster_info.csv')
