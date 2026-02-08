# Introduction

## Requirements

- 50Gb free disk space required on the disk that hosts docker

## Configure env

Create `Makefile.options` with variables
```make
## see https://hub.docker.com/r/k2fsa/icefall/tags that matches your system 
base_docker_version?=torch2.4.1-cuda12.4  
## path to corpus ddir
corpus_dir?=/home/share/LIEPA3
## path to temporary and experiments dir
data_dir=/mnt/share/icefall/liepa3/exp1
## current user id:gid
docker_user?=1001:1001
```


## Training on docker

### prepare docker image
```bash
make dbuild
```

### start docker
```bash
make run
make attach
```

### on docker

```bash
### go to recipe 
cd egs/liepa3/ASR

### prepare
nohup make ./prepare.sh > data/pr.log &
tail -f data/pr,log


### train
./zipformer/train.py   --world-size 1  --num-epochs 30   --start-epoch 1   --use-fp16 1   --exp-dir data/exp/v01   --max-duration 1000

### decode
./zipformer/decode.py  --epoch 30  --avg 15  --exp-dir data/exp/v01   --max-duration 1000 --decoding-method modified_beam_search  -beam-size 4

```

