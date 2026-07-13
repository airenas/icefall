## Results

### Testing datasets

| name       | corpus                            | sentences | words  |
|------------|-----------------------------------|-----------|--------|
| test       | LIEPA3-450h (5%) test set         | 12176     | 123021 |
| test-cv    | Common Voice (LT) test set v24.0  | 5517      | 35659  |
| test-10k   | LIEPA3-10k (20h) test set         | 14468     | 139527 |


### zipformer

[zipformer](./zipformer)

#### Non-streaming

##### 

| model/decoding method                      | test       | test-cv | test-10k | comment   |
|--------------------------------------|------------|---------|-|----------|
| [mL01](#ml01): zipformer (ctc) / greedy_search   | **1.36**  |  **3.78**   | **2.41** | epoch=10 avg=3
| m2: zipformer (ctc cr) + musan / greedy_search   | 1.86  |  6.97   | 8.20 |
| m1: zipformer (ctc cr) / modified_beam_search     | 1.90       | 6.48    |  |
| m1: zipformer (ctc cr) / greedy_search            | 1.91       | 6.43    |  |
| m1: zipformer (ctc cr) / fast_beam_search         | 1.91       | 6.42    |  |
| m3: zipformer (ctc)  + musan / greedy_search     | 2.18       | 7.38  |  |
| m4: zipformer (ctc)  / greedy_search     | 2.29       | 7.35  |  |
| m0: zipformer / greedy_search            | 2.56       | 7.87    || --epoch 30 --avg 15 |
|*with lm*|
| [mL01](#ml01)+[l3](#l3): zipformer (ctc) / modified_beam_search + nbest rnnlm rescore  | 1.40 | **3.25** | 2.95 | NBest rescore (rnnlm) beam-size=12 --lm-scale=0.50 |
| [mL01](#ml01)+[l3](#l3): zipformer (ctc) / modified_beam_search + nbest rnnlm rescore  | **1.35** | 3.76 | **2.37** | NBest rescore (rnnlm) beam-size=12 --lm-scale=0.01 |
| m1+l2: zipformer (ctc cr) / modified_beam_search + nbest rnnlm rescore  | 1.86 | 5.34 || NBest rescore (rnnlm) beam-size=12 --lm-scale 0.50 |
| m2+l2: zipformer (ctc cr) + musan/ modified_beam_search + nbest rnnlm rescore   |   1.88  |  5.80   ||  NBest rescore (rnnlm) beam-size=12, --lm-scale 0.50 |
| m1+l1: zipformer (ctc cr) / modified_beam_search + nbest transformer rescore  | 1.90  | 5.99   || NBest rescore (transformer partly trained) beam-size=4 --lm-scale 0.05 |
| m1+l1: zipformer (ctc cr) / modified_beam_search + nbest transformer rescore  | 1.98  | 5.75 || NBest rescore (transformer partly trained) beam-size=12 --lm-scale 0.05 |
|*oracle*|
| m2: zipformer (ctc cr) + musan / fast_beam_search_nbest_oracle  | (0.63) |  (3.44)   || <- oracle beam-size=12 |
| m1: zipformer (ctc cr) / fast_beam_search_nbest_oracle | (0.63)     | (3.38)  || <- oracle beam-size=4 |
| m1: zipformer (ctc cr) / fast_beam_search_nbest_oracle | (0.63)     | (3.28)  || <- oracle beam-size=12 |

##### m0

###### Train params

`--world-size 1  --num-epochs 30   --start-epoch 1   --use-fp16 1  --max-duration 1000`

###### Decode params
` --epoch 30  --avg 15  --max-duration 1000 --beam-size 4 `

##### m1

###### Train params

`./zipformer/train.py --world-size 1 --num-epochs 30 --start-epoch 0 --use-fp16 1 --exp-dir data/exp/v02 --use-cr-ctc 1 --use-ctc 1 --use-transducer 1 --use-attention-decoder 0 --num-encoder-layers 2,2,4,5,4,2 --feedforward-dim 512,768,1536,2048,1536,768 --encoder-dim 192,256,512,768,512,256 --encoder-unmasked-dim 192,192,256,320,256,192 --ctc-loss-scale 0.1 --enable-spec-aug 0 --cr-loss-scale 0.02 --max-duration 400 `

###### Decode params
`./zipformer/decode.py  --epoch 30  --avg 10  --exp-dir data/exp/v02 --bpe-model data/lang_bpe_500/bpe.model --decoding-method greedy_search --beam-size 4 --decode-limit 0 --use-cr-ctc 1 --use-ctc 1 --use-transducer 1 --use-attention-decoder 0 --num-encoder-layers 2,2,4,5,4,2 --feedforward-dim 512,768,1536,2048,1536,768 --encoder-dim 192,256,512,768,512,256 --encoder-unmasked-dim 192,192,256,320,256,192 --max-duration 400`

##### l1

Transformer lm trained on cc-100. Cleaned (removed any sentence containg non puncts or letter), auto split into sentences.
Words: 1289M

###### LM train params
```bash
./transformer_lm/train.py --world-size 1 --exp-dir /workspace/icefall/egs/liepa3/ASR/data/transformerlm/v01 --start-epoch 0 --num-epochs 10 --use-fp16 0 --num-layers 12 --tie-weights 1 --batch-size 25 --lm-data /workspace/icefall/egs/liepa3/ASR/data/transformerlm/lt.train.sorted.pt --lm-data-valid /workspace/icefall/egs/liepa3/ASR/data/transformerlm/lt.dev.sorted.pt
```
Trained for about a 3/4 of the epoch (1.5 weeks)

##### l2

RNN lm trained on cc-100. Cleaned (removed any sentence containg non puncts or letter), auto split into sentences.
Words: 1 289M

###### LM train params
```bash
rnn_lm/train.py --world-size 1 --exp-dir /workspace/icefall/egs/liepa3/ASR/data/lm/rnn/v01 --start-epoch 0 --num-epochs 10 --use-fp16 0 --tie-weights 1 --embedding-dim 2048 --hidden-dim 2048 --num-layers 3 --batch-size 200 --lm-data /workspace/icefall/egs/liepa3/ASR/data/lm/lt.train.sorted.pt --lm-data-valid /workspace/icefall/egs/liepa3/ASR/data/lm/lt.dev.sorted.pt  --save-every-n 5000
```
Trained for 4epoch (1.5 weeks)

##### l3

RNN lm trained on [lt_ai_blkt](https://huggingface.co/datasets/VSSA-SDSA/LT_AI_BLKT). Cleaned (removed any sentence containg non puncts or letter), auto split into sentences.
Words: 2 191M

###### LM train params
```bash
./rnn_lm/train.py --world-size 3 --exp-dir /mnt/42T/experiments/VietASR/lm/rnn-01 
--start-epoch 0 --num-epochs 4 --use-fp16 0 --tie-weights 1 --embedding-dim 2048 --hidden-dim 2048 --num-layers 3 --batch-size 200 --lm-data data/lt.train.sorted.pt --lm-data-valid data/lt.dev.sorted.pt --save-every-n 5000
```
Trained for 4epoch (1.5 weeks)

##### m1+l1

###### Decode params
```bash
./zipformer/decode.py  --epoch 30  --avg 10  --exp-dir data/exp02/exp/v02 --bpe-model data/exp02/lang_bpe_500/bpe.model --decoding-method modified_beam_search_lm_rescore 	--beam-size 4 --decode-limit 0 --use-cr-ctc 1 --use-ctc 1 --use-transducer 1 --use-attention-decoder 0 --num-encoder-layers 2,2,4,5,4,2 --feedforward-dim 512,768,1536,2048,1536,768 --encoder-dim 192,256,512,768,512,256 --encoder-unmasked-dim 192,192,256,320,256,192 --max-duration 300 --use-averaged-model 1 --use-shallow-fusion 0 --lm-type transformer --lm-exp-dir data/exp02/transformerlm/v01 --lm-epoch 3 --lm-avg 1 --lm-scale 0.05
```

##### m1+l2

###### Decode params
```bash
./zipformer/decode.py  --epoch 30  --avg 10  --exp-dir data/exp02/exp/v02 --bpe-model data/exp02/lang_bpe_500/bpe.model --decoding-method modified_beam_search_lm_rescore 	--decode-limit 0 --use-cr-ctc 1 --use-ctc 1 --use-transducer 1 --use-attention-decoder 0 --num-encoder-layers 2,2,4,5,4,2 --feedforward-dim 512,768,1536,2048,1536,768 --encoder-dim 192,256,512,768,512,256 --encoder-unmasked-dim 192,192,256,320,256,192 --max-duration 300 --use-averaged-model 1 --beam-size 12 --use-shallow-fusion 0 --lm-type rnn --lm-exp-dir data/exp02/lm/rnn/v01 --lm-epoch 4 --lm-avg 1 --lm-scale 0.5 --test-cut data/exp02/fbank/cuts_common-voice.jsonl.gz
```

##### m2

Number of model parameters: 148824074

###### Train params

`--use-cr-ctc 1 --use-ctc 1 --use-transducer 1 --use-attention-decoder 0 --num-encoder-layers 2,2,4,5,4,2 --feedforward-dim 512,768,1536,2048,1536,768 --encoder-dim 192,256,512,768,512,256 --encoder-unmasked-dim 192,192,256,320,256,192 --ctc-loss-scale 0.1 --enable-spec-aug 0 --enable-musan 1  --cr-loss-scale 0.02 --max-duration 350 --use-fp16 1 --base-lr 0.045`

###### Decode params
`./zipformer/decode.py  --epoch 30  --avg 10  --exp-dir data/exp03/exp05 --bpe-model data/exp03/lang_bpe_500/bpe.model --decoding-method greedy_search --decode-limit 0 --use-cr-ctc 1 --use-ctc 1 --use-transducer 1 --use-attention-decoder 0 --num-encoder-layers 2,2,4,5,4,2 --feedforward-dim 512,768,1536,2048,1536,768 --encoder-dim 192,256,512,768,512,256 --encoder-unmasked-dim 192,192,256,320,256,192 --max-duration 350 --use-averaged-model 1 --test-cut <>`

##### m1+l2

###### Decode params
```bash
/zipformer/decode.py  --epoch 30  --avg 10  --exp-dir data/exp03/exp05 --bpe-model data/exp03/lang_bpe_500/bpe.model --decoding-method modified_beam_search_lm_rescore --decode-limit 0 --use-cr-ctc 1 --use-ctc 1 --use-transducer 1 --use-attention-decoder 0 --num-encoder-layers 2,2,4,5,4,2 --feedforward-dim 512,768,1536,2048,1536,768 --encoder-dim 192,256,512,768,512,256 --encoder-unmasked-dim 192,192,256,320,256,192 --max-duration 350 --use-averaged-model 1 --beam-size 12 --use-shallow-fusion 0 --lm-type rnn --lm-exp-dir data/exp02/lm/rnn/v01 --lm-epoch 4 --lm-avg 1 --lm-scale 0.50 --test-cut <>
```


##### m3

###### Train params

`model_params=--use-cr-ctc 0 --use-ctc 1 --use-transducer 1 --use-attention-decoder 0 --num-encoder-layers 2,2,4,5,4,2 --feedforward-dim 512,768,1536,2048,1536,768 --encoder-dim 192,256,512,768,512,256 --encoder-unmasked-dim 192,192,256,320,256,192 --ctc-loss-scale 0.1 --enable-spec-aug 1 --enable-musan 1  --cr-loss-scale 0.02 --max-duration 700 --use-fp16 1 --base-lr 0.045`

###### Decode params
`./zipformer/decode.py  --epoch 30  --avg 10  --exp-dir data/exp03/exp06 --bpe-model data/exp03/lang_bpe_500/bpe.model --decoding-method greedy_search --decode-limit 0 --use-cr-ctc 0 --use-ctc 1 --use-transducer 1 --use-attention-decoder 0 --num-encoder-layers 2,2,4,5,4,2 --feedforward-dim 512,768,1536,2048,1536,768 --encoder-dim 192,256,512,768,512,256 --encoder-unmasked-dim 192,192,256,320,256,192 --max-duration 700 --use-averaged-model 1` 


##### m4

###### Train params

`model_params=--use-cr-ctc 0 --use-ctc 1 --use-transducer 1 --use-attention-decoder 0 --num-encoder-layers 2,2,4,5,4,2 --feedforward-dim 512,768,1536,2048,1536,768 --encoder-dim 192,256,512,768,512,256 --encoder-unmasked-dim 192,192,256,320,256,192 --ctc-loss-scale 0.1 --enable-spec-aug 1 --enable-musan 0  --cr-loss-scale 0.02 --max-duration 700 --use-fp16 1 --base-lr 0.045`

###### Decode params
`./zipformer/decode.py  --epoch 30  --avg 10  --exp-dir data/exp03/exp08 --bpe-model data/exp03/lang_bpe_500/bpe.model --decoding-method greedy_search --decode-limit 0 --use-cr-ctc 0 --use-ctc 1 --use-transducer 1 --use-attention-decoder 0 --num-encoder-layers 2,2,4,5,4,2 --feedforward-dim 512,768,1536,2048,1536,768 --encoder-dim 192,256,512,768,512,256 --encoder-unmasked-dim 192,192,256,320,256,192 --max-duration 800 --use-averaged-model 1 --beam-size 4 --test-cut data/exp03/fbank/cuts_test.jsonl.gz` 

##### mL01

Number of model parameters: 304442090

###### Train params

`./ASR/zipformer/train.py --world-size 6 --num-epochs 10 --start-epoch 0 --bpe-model train-asr/experiments/VietASR/lang_bpe_500/bpe.model --manifest-dir train-asr/experiments/VietASR/fbank-fixed --exp-dir train-asr/experiments/VietASR/exp/v01 --use-fp16 1 --train-cuts 4000h --max-duration 600 --enable-musan 0 --enable-spec-aug 1 --seed 1332 --master-port 12356 --num-encoder-layers 2,2,4,5,4,2 --feedforward-dim 768,1536,2048,3072,2048,1536 --encoder-dim 256,512,768,1024,768,512 --encoder-unmasked-dim 256,256,256,320,256,256 --use-ctc 1 --use-transducer 1 --base-lr 0.045`

###### Decode params

`./ASR/zipformer/decode.py --epoch 10 --avg 3 --exp-dir experiments/VietASR/exp/v01 --max-duration 400 --bpe-model experiments/VietASR/lang_bpe_500/bpe.model --num-encoder-layers 2,2,4,5,4,2 --feedforward-dim 768,1536,2048,3072,2048,1536 --encoder-dim 256,512,768,1024,768,512 --encoder-unmasked-dim 256,256,256,320,256,256 --use-ctc 1 --use-transducer 1 --decoding-method greedy_search --manifest-dir experiments/VietASR/fbank --use-averaged-model 1 --cuts-name test`

##### mL01+l3

###### Decode params
```bash
./zipformer/decode.py  --epoch 10  --avg 3  --exp-dir /mnt/42T/experiments/VietASR/exp/v01 --bpe-model /mnt/42T/experiments/VietASR/lang_bpe_500/bpe.model --decoding-method modified_beam_search_lm_rescore --decode-limit 0 --num-encoder-layers 2,2,4,5,4,2 --feedforward-dim 768,1536,2048,3072,2048,1536 --encoder-dim 256,512,768,1024,768,512 --encoder-unmasked-dim 256,256,256,320,256,256 --use-ctc 1 --use-transducer 1 --query-head-dim 32 --value-head-dim 12 --decoder-dim 512 --joiner-dim 512 --max-duration 350 --use-averaged-model 1 --use-shallow-fusion 0 --lm-type rnn --lm-exp-dir /mnt/42T/experiments/VietASR/lm/rnn-01 --lm-epoch 4 --lm-avg 2 --beam-size=12 --lm-scale 0.5 --test-cut <>
```

### streaming models

#### results 

| model/decoding method                      | test       | test-cv | test-10k | comment    |
|--------------------------------------|-|-|-|-|
| [msL01](#msl01): zipformer (ctc) /greedy_search   |       |  4.73 |  5.09 (3392 insertions, 480 deletions, 3233 substitutions, over 139527 reference words) | --chunk-size 64 --left-context-frames 256 --epoch 10 --avg 2 |
| [msL01](#msl01): zipformer (ctc) /greedy_search   |  1.88 |  5.31 |  5.38 | --chunk-size 32 --left-context-frames 128 --epoch 10 --avg 2 |
| [msLs01](#msls01): zipformer (ctc) /greedy_search |       |  5.02 |  3.82 (1401 insertions, 529 deletions, 3394 substitutions, over 139527 reference words) | --chunk-size 64 --left-context-frames 256 --epoch 15 --avg 2 |
| [msLs01](#msls01): zipformer (ctc) /greedy_search |  1.99 |  5.67 |  4.10 | --chunk-size 32 --left-context-frames 128 --epoch 15 --avg 2 |
| ms3: zipformer (ctc) + musan /greedy_search       | 3.81  | 10.26 || --chunk-size 32 --left-context-frames 128 |
| ms3: zipformer (ctc) + musan /greedy_search       | 3.43  |  9.54 || --chunk-size 64 --left-context-frames 256 |
| ms3: zipformer (ctc) + musan /greedy_search       | 3.14  |  8.83 || --chunk-size 128 --left-context-frames 256 |
| ms4: zipformer (ctc) /greedy_search               | 3.89  | 10.57 || --chunk-size 32 --left-context-frames 128 |
| ms2: zipformer + musan /greedy_search             | 3.98  | 10.98 ||  |
| ms1: zipformer/greedy_search                      | 6.39  | 15.46 ||  |
| *lm rescore* |
| ms3+lm2: zipformer (ctc) + musan / nbest rnnlm rescore  | 3.15 | 7.92   || NBest rescore (rnnlm) beam-size=12 --lm-scale 0.50  --chunk-size 32 --left-context-frames 128|

#### ms1: zipformer streaming
##### Train params

`./zipformer/train.py --world-size 2 --num-epochs 30 --start-epoch 1 --causal 1 --use-cr-ctc 0 --use-ctc 0 --use-transducer 1 --use-attention-decoder 0  --enable-spec-aug 0 --max-duration 700 --base-lr 0.02`

##### Decode params
`./zipformer/decode.py  --epoch 30  --avg 10 --beam-size 4 --decode-limit 0 --causal 1 --use-cr-ctc 0 --use-ctc 0 --use-transducer 1 --use-attention-decoder 0  --max-duration 700 --use-averaged-model 1 --chunk-size 32 --left-context-frames 128`

#### ms2: zipformer streaming + training with noise (MUSAN)
##### Train params

`./zipformer/train.py --world-size 2 --num-epochs 30 --start-epoch 1 --causal 1 --use-cr-ctc 0 --use-ctc 0 --use-transducer 1 --use-attention-decoder 0  --ctc-loss-scale 0.1 --enable-spec-aug 1 --enable-musan 1  --cr-loss-scale 0.02 --max-duration 700 --base-lr 0.02`

##### Decode params
`./zipformer/decode.py  --epoch 30  --avg 10  --beam-size 4 --decode-limit 0 --causal 1 --use-cr-ctc 0 --use-ctc 0 --use-transducer 1 --use-attention-decoder 0  --max-duration 700 --use-averaged-model 1 --chunk-size 32 --left-context-frames 128`

#### ms3: zipformer (ctc) streaming + training with noise (MUSAN)

Number of model parameters: 66367431

##### Train params

`./zipformer/train.py --world-size 2 --num-epochs 30 --start-epoch 1 --causal 1 --use-cr-ctc 0 --use-ctc 1 --use-transducer 1 -use-attention-decoder 0 --ctc-loss-scale 0.1 --enable-spec-aug 1 --enable-musan 1  --cr-loss-scale 0.02 --max-duration 400 --base-lr 0.045 --use-fp16 1`

##### Decode params
`./zipformer/decode.py  --epoch 30  --avg 10  --exp-dir data/exp03/exp07 --bpe-model data/exp03/lang_bpe_500/bpe.model --decoding-method greedy_search --decode-limit 0 --causal 1 --use-cr-ctc 0 --use-ctc 1 --use-transducer 1 --use-attention-decoder 0 --max-duration 700 --use-averaged-model 1 --chunk-size 32 --left-context-frames 128 `


#### ms3+lm2

##### Decode params
`./zipformer/decode.py  --epoch 30  --avg 10  --exp-dir data/exp03/exp07 --bpe-model data/exp03/lang_bpe_500/bpe.model --decoding-method modified_beam_search_lm_rescore --decode-limit 0 	--causal 1 --use-cr-ctc 0 --use-ctc 1 --use-transducer 1 --use-attention-decoder 0 --max-duration 700 --use-averaged-model 1 --chunk-size 32 --left-context-frames 128 --beam-size 12 	--use-shallow-fusion 0 --lm-type rnn --lm-exp-dir data/exp02/lm/rnn/v01 --lm-epoch 4 --lm-avg 1 --lm-scale 0.4 --test-cut <>`


#### ms4: zipformer (ctc) streaming 

Number of model parameters: 66367431

##### Train params

`./zipformer/train.py --world-size 2 --num-epochs 30 --start-epoch 1 --causal 1 --use-cr-ctc 0 --use-ctc 1 --use-transducer 1 -use-attention-decoder 0 --ctc-loss-scale 0.1 --enable-spec-aug 1 --enable-musan 0  --cr-loss-scale 0.02 --max-duration 400 --base-lr 0.045 --use-fp16 1`

##### Decode params
`./zipformer/decode.py  --epoch 30  --avg 10  --exp-dir data/exp03/exp09 --bpe-model data/exp03/lang_bpe_500/bpe.model --decoding-method greedy_search --decode-limit 0 --causal 1 --use-cr-ctc 0 --use-ctc 1 --use-transducer 1 --use-attention-decoder 0 --max-duration 800 --use-averaged-model 1 --chunk-size 32 --left-context-frames 128`

#### msL01

Number of model parameters: 305725162

Trained on 10k

##### Train params

`./ASR/zipformer/train.py --world-size 6 --num-epochs 10 --start-epoch 1 --bpe-model /scratch/lustre/home/hpc_airenas/train-asr/experiments/VietASR/lang_bpe_500/bpe.model --manifest-dir /scratch/lustre/home/hpc_airenas/train-asr/experiments/VietASR/fbank-fixed --exp-dir /scratch/lustre/home/hpc_airenas/train-asr/experiments/VietASR/exp/v01rt --use-fp16 1 --train-cuts 4000h --max-duration 600 --enable-musan 0 --enable-spec-aug 1 --seed 1332 --master-port 12356 --num-encoder-layers 2,2,4,5,4,2 --feedforward-dim 768,1536,2048,3072,2048,1536 --encoder-dim 256,512,768,1024,768,512 --encoder-unmasked-dim 256,256,256,320,256,256 --use-ctc 1 --use-transducer 1 --causal 1 --base-lr 0.045`

##### Decode params
`./zipformer/decode.py  --epoch 10  --avg 2 --exp-dir /mnt/42T/experiments/VietASR/exp/v01rt --bpe-model /mnt/42T/experiments/VietASR/lang_bpe_500/bpe.model --decoding-method greedy_search --decode-limit 0 --num-encoder-layers 2,2,4,5,4,2 --feedforward-dim 768,1536,2048,3072,2048,1536 --encoder-dim 256,512,768,1024,768,512 --encoder-unmasked-dim 256,256,256,320,256,256 --use-ctc 1 --use-transducer 1 --query-head-dim 32 --causal 1 --value-head-dim 12 --decoder-dim 512 --joiner-dim 512 --max-duration 350 --chunk-size 32 --left-context-frames 128 --test-cut /mnt/42T/experiments/VietASR/fbank/cuts_common-voice.jsonl.gz`

#### msLs01

Number of model parameters: 66367431

Trained on 10k

##### Train params

`./ASR/zipformer/train.py --world-size 4 --num-epochs 15 --start-epoch 1 --manifest-dir /scratch/lustre/home/hpc_airenas/train-asr/experiments/VietASR/fbank-fixed --exp-dir /scratch/lustre/home/hpc_airenas/train-asr/experiments/VietASR/exp/v01rts --use-fp16 1 --train-cuts 4000h --max-duration 1000 --enable-musan 0 --enable-spec-aug 1 --seed 1332 --master-port 12356 --num-encoder-layers 2,2,3,4,3,2 --feedforward-dim 512,768,1024,1536,1024,768 --encoder-dim 192,256,384,512,384,256 --encoder-unmasked-dim 192,192,256,256,256,192 --use-ctc 1 --use-transducer 1 --causal 1 --bpe-model /scratch/lustre/home/hpc_airenas/train-asr/experiments/VietASR/lang_bpe_500/bpe.model --base-lr 0.045`

##### Decode params
`./zipformer/decode.py --epoch 15 --avg 2  --exp-dir /mnt/42T/experiments/VietASR/exp/v01rts --bpe-model /mnt/42T/experiments/VietASR/lang_bpe_500/bpe.model --decoding-method greedy_search --decode-limit 0 --num-encoder-layers 2,2,3,4,3,2 --feedforward-dim 512,768,1024,1536,1024,768 --encoder-dim 192,256,384,512,384,256 --encoder-unmasked-dim 192,192,256,256,256,192 --use-ctc 1 --use-transducer 1 --causal 1 --max-duration 350 --chunk-size 32 --left-context-frames 128 --test-cut /mnt/42T/experiments/VietASR/fbank/cuts_common-voice.jsonl.gz`
