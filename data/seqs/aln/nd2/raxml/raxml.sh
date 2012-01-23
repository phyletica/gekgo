datafile=`ls ../*muscle.phy`

raxmlHPC -f d -m GTRCAT -s $datafile -n raxout -d -p 234249 -# 100
