# Introduction

## Requirements

- 100Gb free space required on the disk that hosts docker
- docker

## Configure docker env

Create `Makefile.docker.options` with variables
```make
## see https://hub.docker.com/r/k2fsa/icefall/tags that matches your system 
docker_base_version?=torch2.4.1-cuda12.4

## path to LIEPA3 corpus dir
docker_corpus_dir?=/home/share/LIEPA3

## path to temporary and experiments dir
docker_data_dir=/mnt/share/icefall/liepa3/exp1

## current user id:gid
docker_user?=1001:1001
```

## Configure training option

Create `Makefile.options` with variables
```make
## experments dir
## docker_data_dir (from Makefile.docker.options) is mounted to data on docker instance 
## model and results will be saved here
exp_dir?=data/exp/v01

## model training params
## see zipformer/train.py for more options and explanation
train_params=--use-cr-ctc 1 --use-ctc 1 --use-transducer 1 --use-attention-decoder 0 --num-encoder-layers 2,2,4,5,4,2 --feedforward-dim 512,768,1536,2048,1536,768 --encoder-dim 192,256,512,768,512,256 --encoder-unmasked-dim 192,192,256,320,256,192 --ctc-loss-scale 0.1 --enable-spec-aug 0 --cr-loss-scale 0.02 --max-duration 400


## decoding method
## see zipformer/decode.py for more options
decoding_method?=modified_beam_search

## decoding params
decode_params=--use-cr-ctc 1 --use-ctc 1 --use-transducer 1 --use-attention-decoder 0 --num-encoder-layers 2,2,4,5,4,2 --feedforward-dim 512,768,1536,2048,1536,768 --encoder-dim 192,256,512,768,512,256 --encoder-unmasked-dim 192,192,256,320,256,192 --ctc-loss-scale 0.1 --enable-spec-aug 0 --cr-loss-scale 0.02 --max-duration 400
```



## Training on docker

### prepare docker image
```bash
make -f Makefile.docker dbuild
```

### start docker
```bash
make -f Makefile.docker run docker_mode=-d
make -f Makefile.docker attach
```

### stop docker
```bash
make -f Makefile.docker stop
```

### on docker

```bash
### go to recipe 
cd egs/liepa3/ASR

### prepare
nohup make prepare/liepa3 > data/pr.log &
tail -f data/pr.log


### train
nohup make train > data/tr.log &
tail -f data/tr.log

### decode
make decode/test
```

### to test with common voice test corpus

```bash
### prepare
### before: manually download https://datacollective.mozillafoundation.org/datasets/cmj8u3pdo00f5nxxb9uuewruj
### to data/downloads directory
make prepare/common-voice

### decode
make decode/common-voice
```
