# RNNLM scripts for CC-100 (LT)

## Overview

This directory prepares https://data.statmt.org/cc-100/ text data and trains an RNNLM.

These scripts are prepared to be run inside [docker](../../liepa3/ASR/Makefile.docker).

From: https://k2-fsa.github.io/icefall/recipes/RNN-LM/librispeech/lm-training.html


### Requirements

- A BPE model must be prepared in advance.


### Configure

Prepare Makefile.options. Example:

```Makefile
## datasets preparation dir
data_dir?=/workspace/icefall/egs/liepa3/ASR/data/rnnlm

## lm model output
exp_dir?=/workspace/icefall/egs/liepa3/ASR/data/rnnlm/v01

## limit for testing sample run
## limit=500000 #

## bpe model 
bpe_model=/workspace/icefall/egs/liepa3/ASR/data/lang_bpe_500/bpe.model
```

### CC-100 data preparation

K2 scripts require each sentence to be on a separate line. Here the
`semantikadocker.vdu.lt/lex:2021.04.02` Docker-based service is used to split
the text into sentences.

#### Run lex service on host
```bash
make start/lex
```
#### Start docker for running scripts
```bash
cd ../../liepa3/ASR/
make -f Makefile.docker run
```
#### On docker container

```bash
make prepare/cc-100 prepare
```


### Training

#### Start docker for running scripts
```bash
cd ../../liepa3/ASR/
make -f Makefile.docker run
```
#### On docker container

```bash
make train
```

The model will be saved to the location configured in Makefile.options:
`exp_dir?=/workspace/icefall/egs/liepa3/ASR/data/rnnlm/v01`

