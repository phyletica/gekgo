#! /usr/bin/env python

import os
import sys
import logging
from cStringIO import StringIO

import gekgo_util

def main():
    locus_dirs = set_up_dirs()
    set_up_mlflex_confs(locus_dirs)

def set_up_dirs():
    garli_dirs = {}
    for locus in gekgo_util.ALNS_NEX.keys():
        gdir = os.path.join(gekgo_util.GARLI_DIR, locus)
        garli_dirs[locus] = gdir
        if not os.path.exists(gdir):
            gekgo_util.mkdr(gdir)
    return garli_dirs

def set_up_mlflex_confs(locus_dirs):
    for locus, dr in locus_dirs.iteritems():
        ml_dir = os.path.join(dr, 'ml_gtr_flex')
        if not os.path.exists(ml_dir):
            gekgo_util.mkdr(ml_dir)
        conf_path = os.path.join(ml_dir, 'garli.conf')
        qsub_path = os.path.join(ml_dir, 'garli.sh')
        if not os.path.isfile(conf_path):
            conf = get_garli_conf(
                    datafname = os.path.relpath(gekgo_util.ALNS_NEX[locus],
                            os.path.dirname(conf_path)),
                    ratehetmodel = "flex",
                    numratecats = "6")
            cfile = open(conf_path, 'w')
            cfile.write(conf.getvalue())
            cfile.close()
        if not os.path.isfile(qsub_path):
            qsub_str = gekgo_util.get_qsub_preamble()
            cmd = "Garli %s\n" % os.path.relpath(conf_path,
                    os.path.dirname(qsub_path))
            qsub_str += cmd
            qfile = open(qsub_path, 'w')
            qfile.write(qsub_str)
            qfile.close()


def get_garli_conf(datafname,
                   constraintfile="none",
                   streefname="random",
                   ofprefix="garli_out",
                   searchreps="10",
                   ratehetmodel="gamma",
                   numratecats="6",
                   invariantsites="none",
                   bootstrapreps="0"):
    conf = StringIO()
    conf.write(
"""datafname = %s
constraintfile = %s
streefname = %s
attachmentspertaxon = 100
ofprefix = %s
randseed = -1
availablememory = 1024
logevery = 10
saveevery = 100
refinestart = 1
outputeachbettertopology = 0
outputcurrentbesttopology = 0
enforcetermconditions = 1
genthreshfortopoterm = 10000
scorethreshforterm = 0.001
significanttopochange = 0.01
outputphyliptree = 0
outputmostlyuselessfiles = 0
writecheckpoints = 0
restart = 0
outgroup = 1
searchreps = %s
collapsebranches = 1

linkmodels = 0
subsetspecificrates = 1

[model1]
datatype = nucleotide
ratematrix = ( 0 1 2 3 4 5 )
statefrequencies = empirical
ratehetmodel = %s
numratecats = %s
invariantsites = %s

[master]
nindivs = 4
holdover = 1
selectionintensity = 0.5
holdoverpenalty = 0
stopgen = 5000000
stoptime = 5000000

startoptprec = 0.5
minoptprec = 0.01
numberofprecreductions = 10
treerejectionthreshold = 50.0
topoweight = 0.01
modweight = 0.002
brlenweight = 0.002
randnniweight = 0.1
randsprweight = 0.3
limsprweight =  0.6
intervallength = 100
intervalstostore = 5

limsprrange = 6
meanbrlenmuts = 5
gammashapebrlen = 1000
gammashapemodel = 1000
uniqueswapbias = 0.1
distanceswapbias = 1.0

bootstrapreps = %s
resampleproportion = 1.0
inferinternalstateprobs = 0
""" % (datafname, constraintfile, streefname, ofprefix, str(searchreps),
            ratehetmodel, str(numratecats), invariantsites, str(bootstrapreps)))
    return conf

if __name__ == '__main__':
    main()

