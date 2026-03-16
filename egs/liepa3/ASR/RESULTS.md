## Results

### Testing datasets

| name       | corpus                            | sentences | words  |
|------------|-----------------------------------|-----------|--------|
| test       | LIEPA3 (5%) test set              | 12176     | 123021 |
| test-cv    | Common Voice (LT) test set v24.0  | 5517      | 35659  |

### zipformer

[zipformer](./zipformer)

#### Non-streaming

##### 

| model/decoding method                      | test       | test-cv | comment   |
|--------------------------------------|------------|---------|-----------|
| m2: zipformer (ctc cr) + musan / greedy_search   | 1.86  |  6.97   |  |
| m1: zipformer (ctc cr) / modified_beam_search     | 1.90       | 6.48    |  |
| m1: zipformer (ctc cr) / greedy_search            | 1.91       | 6.43    |  |
| m1: zipformer (ctc cr) / fast_beam_search         | 1.91       | 6.42    |  |
| m3: zipformer (ctc)  + musan / greedy_search     | 2.18       | 7.38  |  |
| m0: zipformer / greedy_search            | 2.56       | 7.87    | --epoch 30 --avg 15 |
|*with lm*|
| m1+l2: zipformer (ctc cr) / modified_beam_search + nbest rnnlm rescore  | 1.86 | 5.34 | NBest rescore (rnnlm) beam-size=12 --lm-scale 0.50 |
| m2+l2: zipformer (ctc cr) + musan/ modified_beam_search + nbest rnnlm rescore   |   1.88  |  5.80   |  NBest rescore (rnnlm) beam-size=12, --lm-scale 0.50 |
| m1+l1: zipformer (ctc cr) / modified_beam_search + nbest transformer rescore  | 1.90  | 5.99   | NBest rescore (transformer partly trained) beam-size=4 --lm-scale 0.05 |
| m1+l1: zipformer (ctc cr) / modified_beam_search + nbest transformer rescore  | 1.98  | 5.75 | NBest rescore (transformer partly trained) beam-size=12 --lm-scale 0.05 |
|*oracle*|
| m2: zipformer (ctc cr) + musan / fast_beam_search_nbest_oracle  | (0.63) |  (3.44)   | <- oracle beam-size=12 |
| m1: zipformer (ctc cr) / fast_beam_search_nbest_oracle | (0.63)     | (3.38)  | <- oracle beam-size=4 |
| m1: zipformer (ctc cr) / fast_beam_search_nbest_oracle | (0.63)     | (3.28)  | <- oracle beam-size=12 |

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
Words: 1289M

###### LM train params
```bash
rnn_lm/train.py --world-size 1 --exp-dir /workspace/icefall/egs/liepa3/ASR/data/lm/rnn/v01 --start-epoch 0 --num-epochs 10 --use-fp16 0 --tie-weights 1 --embedding-dim 2048 --hidden-dim 2048 --num-layers 3 --batch-size 200 --lm-data /workspace/icefall/egs/liepa3/ASR/data/lm/lt.train.sorted.pt --lm-data-valid /workspace/icefall/egs/liepa3/ASR/data/lm/lt.dev.sorted.pt  --save-every-n 5000
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


### streaming models

#### results 

| model/decoding method                      | test       | test-cv | comment    |
|--------------------------------------|------------|---------|---------------------|
| ms3: zipformer (ctc) + musan /greedy_search         | 3.81  | 10.26   |  |
| ms2: zipformer + musan /greedy_search  | 3.98       | 10.98   |  |
| ms1: zipformer/greedy_search                        | 6.39       | 15.46   |  |
| *lm rescore* |
| ms3+lm2: zipformer (ctc) + musan / nbest rnnlm rescore        | 3.15  | 7.92   | NBest rescore (rnnlm) beam-size=12 --lm-scale 0.50 |

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
