#!/bin/bash

LIBS_DIR=/var/nlp/spring16/libs
export JAVA_HOME=$(readlink -f /usr/bin/javac | sed "s:/bin/javac::")
export PYTHONPATH=$PYTHONPATH:$LIBS_DIR/nodebox:$LIBS_DIR/stanford-corenlp-python:$LIBS_DIR/pysupersensetagger
export CORENLP_3_6_0_PATH=$LIBS_DIR/stanford-corenlp-full-2015-12-09
export CORENLP_3_5_2_PATH=$LIBS_DIR/stanford-corenlp-full-2015-04-20
export BERKELEY_PARSER_1_7_PATH=$LIBS_DIR/berkeley-parser
export OPENNLP_1_5_0_PATH=$LIBS_DIR/opennlp-tools-1.5.0
export RECONCILE_1_0_PATH=$LIBS_DIR/reconcile-1.0
export ARKREF_PATH=$LIBS_DIR/arkref
export CLASSPATH=$CLASSPATH:$OPENNLP_1_5_0_PATH/*:$BERKELEY_PARSER_1_7_PATH/*:$CORENLP_3_6_0_PATH/*:$RECONCILE_1_0_PATH/*
