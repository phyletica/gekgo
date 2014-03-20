#!/bin/bash

this_dir=`dirname "$0"`

if [ "$this_dir" = "." ]
then
    BIN_DIR="`pwd`"
else
    cd "$this_dir"
    BIN_DIR="`pwd`"
fi

BASE_DIR=`dirname "$BIN_DIR"`
DATA_DIR=$BIN_DIR/data
GENOME_DIR=$DATA_DIR/genomes
CYRT_GENOME_DIR=$GENOME_DIR/cyrtodactylus_philippinicus_KU330797
GEKKO_GENOME_DIR=$GEKKO_GENOME_DIR/gekko_mindorensis_KU328820
MSG_DIR=$GENOME_DIR/msg
MSG_PLATE1_DIR=$MSG_DIR/plate1
MSG_PLATE2_DIR=$MSG_DIR/plate2
MSG_PLATE3_DIR=$MSG_DIR/plate3

export BIN_DIR BASE_DIR DATA_DIR GENOME_DIR CYRT_GENOME_DIR GEKKO_GENOME_DIR \
        MSG_DIR MSG_PLATE1_DIR MSG_PLATE2_DIR MSG_PLATE3_DIR

