# TransformerLM/RNNLM scripts for CC-100 (LT)

## Overview

This directory prepares https://data.statmt.org/cc-100/ text data and trains an RNNLM.

These scripts are prepared to be run inside [docker](../../liepa3/ASR/Makefile.docker).

From: https://k2-fsa.github.io/icefall/recipes/RNN-LM/librispeech/lm-training.html

### Stats

#### cc-100

Words: 1289M
Sentences: 130M


### Requirements

- A BPE model must be prepared in advance.


### Configure

Prepare Makefile.options. Example:

```Makefile
corpus=cc-100 # or corpus=lt_ai_blkt


## datasets preparation dir
data_dir?=/workspace/icefall/egs/liepa3/ASR/data/lm

## lm model output
exp_dir?=/workspace/icefall/egs/liepa3/ASR/data/lm/transformer/v01

## limit for testing sample run
## limit=500000 #

## bpe model 
bpe_model=/workspace/icefall/egs/liepa3/ASR/data/lang_bpe_500/bpe.model

## lt_ai_blkt sentences parquet files dir
lt_ai_blkt_sentences_dir?=/home/airenas/Edge-Punct-Casing/egs/lt_ai_blkt/corpus/sentences

```

### CC-100 data preparation

K2 scripts require each sentence to be on a separate line. Here a
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
cd cc-100/LM
make prepare/cc-100 prepare
```

### lt_ai_blkt data preparation

Corpus must be split into sentences.
Example: https://github.com/airenas/Edge-Punct-Casing/blob/35b0458696a7a13788cc95bf38e45a26ece2c54b/egs/lt_ai_blkt/Makefile#L45

#### On docker container

```bash
cd cc-100/LM
make prepare/lt_ai_blkt
```


### Training

#### On docker container

```bash
cd cc-100/LM
### transformer LM training
make train/transformer

### rnn LM training
make train/rnn

```

The model will be saved to the location configured in Makefile.options:
`exp_dir?=/workspace/icefall/egs/liepa3/ASR/data/lm/tansformer/v01`
or 
`exp_dir?=/workspace/icefall/egs/liepa3/ASR/data/lm/rnn/v01`
