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


class clean_ref(luigi.Task):
    param = luigi.DictParameter()
    
    def requires(self):
        return []
        
    def run(self):
        ref = Fa.load_from_file(str(self.param['ref']))
        #len(ref)
        i = 0
        if self.param['clear']:
            for r in ref.contigs:
                r.name =  '>'+str("%04d" % i)+r.name[1:]
                i+=1
            #self.param['ref'] = self.param['ref'].rsplit('.',1)[0]+'_cleared'+self.param['ref'].rsplit('.',1)[1]
        ref.write(str(self.param['ref_cleared']))
        
    def output(self):
        #self.param['ref'].rsplit('.',1)[0]+'_cleared'+self.param['ref'].rsplit('.',1)[1]
        return luigi.LocalTarget(str(self.param['ref_cleared']))
        

class cdhit_analisys(luigi.Task):
    param = luigi.DictParameter()

    @staticmethod
    def exec_cdhit(cmd):
        subprocess.call(cmd)

    def requires(self):
        return [clean_ref(self.param)]

    def run(self):
        cmd_list = []
        for f in self.param['files']:
            if self.param['nucleotide'] == True:
                cmd_list.append(['cdhit-est-2d', '-i', str(self.param['ref_cleared']), '-i2', str(f), '-c', str(self.param['c']), '-g', str(self.param['g']), '-s2', str(self.param['s2']), '-o', self.param['odir']+'/'+os.path.splitext(os.path.basename(f))[0]])
            else:
                cmd_list.append(['cdhit-2d', '-i', str(self.param['ref_cleared']), '-i2', str(f), '-c', str(self.param['c']), '-g', str(self.param['g']), '-s2', str(self.param['s2']), '-o', self.param['odir']+'/'+os.path.splitext(os.path.basename(f))[0]])
        print cmd_list
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
        #chit_set.add_filter(*)
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
        if self.param['filter'] > 0:
            chit_set.set_filter(self.param['filter'])
        #chit_set.set_filter(10)
        df = chit_set.to_df(z, nz)
        with open(self.param['odir']+'/'+'non-zeros.txt', 'wb') as nzf:
            for q in chit_set.all_non_zeros:
                nzf.write(q[4:]+'\n')
        with open(self.param['odir']+'/'+'zeros.txt', 'wb') as zf:
            for q in chit_set.all_zeros:
                zf.write(q[4:]+'\n')
        if self.param['filter'] > 0:
            with open(self.param['odir']+'/'+'droped.txt', 'wb') as drp:
                for q in chit_set.cols_dropped:
                    drp.write(q[4:]+'\n')
        #plot = chit_set.make_dendrogram2(df);
        for column in df:
            if float(df[column].min()) == 0.0:
                del df[column]
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
        return luigi.LocalTarget(self.param['odir']+'/'+self.param['of'])
        # return [luigi.LocalTarget(self.param['odir']+'/'+'dendro.pdf'), luigi.LocalTarget(self.param['odir']+'/'+'summary.txt')]


class clusterise(luigi.Task):

    param = luigi.DictParameter()

    def requires(self):
        return [plot(self.param)]

    def run(self):
        try:
            # /home/blul/BIOIT/blul_cdhit/workflow/cluster_info.csv
            c = 1
            ref_fa = Fa.load_from_file(str(self.param['ref_cleared']))
            cluster_contigs = []
            outr = []

            # creates fastas with sequences from each cluster one file per cluster
            with open(self.param['odir']+'/'+'cluster_info.csv') as f:
                reader = csv.reader(f, delimiter=';')
                header = reader.next()
                for r in reader:
                    #if curent cluster num differ from prev one
                    if c != int(r[1]):
                        result_fa = Fa(cluster_contigs, 'c'+str(c))
                        result_fa.write(str(self.param['odir']+'/clusters/'+'c_'+str(c)+'.fasta'))
                        cluster_contigs = []
                        c = int(r[1])

                    cc = ref_fa.extract_by_name_frag(r[2])
                    #print cc
                    cc[0].name = '>'+cc[0].name[5:]
                    #print cc[0].name
                    cluster_contigs += cc
                    r.append('>'+cc[0].name[5:])
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
