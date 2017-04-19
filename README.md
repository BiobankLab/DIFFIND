# DIFFIND

usage: diffind-start.py [-h] [-v] [-c C] [-g G] [-s2 S2] --ref REF --files
                        FILES [FILES ...] [--nucleotide] [--odir ODIR]
                        [--threads THREADS] [--donot-skip-zeros]
                        [--donot-skip-non-zeros]
                        [--dendro-file-name DENDRO_FILE_NAME]
                        [--top-font-size TOP_FONT_SIZE]
                        [--filter-value FILTER_VALUE] [--drop-single-zero]
                        [--no-clear]

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         display version number and exit
  -c                    Sequence identity threshold
  -g                    By cd hit's default algorithm, a sequence is clustered
                        to the first cluster that meet the threshold (fast
                        mode). If set to 1, the program will cluster it into
                        the most similar cluster that meet the
                        threshold(accurate but slow mode)
  -s2                   length difference cutoff for db1, default 1.0 by
                        default, seqs in db1 >= seqs in db2 in a same cluster
                        if set to 0.9, seqs in db1 may just >= 90% seqs in db2
  --ref REF             Reference file files will be compared with it
  --files FILES [FILES ...]
                        List of files to be checked against --ref
  --nucleotide          files that are going to be compared are in nucleotide
                        format
  --odir ODIR           dir name where outputed files will be saved
  --threads THREADS     number of threads to use
  --donot-skip-zeros    removing from dendrogram values that are all equal 0
                        for same label
  --donot-skip-non-zeros
                        removing from dendrogram values that are all greater
                        then 0 for same label
  --dendro-file-name DENDRO_FILE_NAME
                        name of pdf file containing ploted dedrogram will be
                        saved in output dir (--odir flag)
  --top-font-size TOP_FONT_SIZE
                        size of font used to plot gene names on top dendrogram
  --filter-value FILTER_VALUE
                        drops column if absolute value of difference between
                        max and min in gene less then filter value
  --drop-single-zero    drops column if single zero found
  --no-clear            does not attach numbers to genes names
