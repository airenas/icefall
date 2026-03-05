## Results

### Testing datasets

| name       | corpus                            | sentences | words  |
|------------|-----------------------------------|-----------|--------|
| test       | LIEPA3 (5%) test set              | 12176     | 123021 |
| test-cv    | Common Voice (LT) test set v24.0  | 5517      | 35659  |

### zipformer-ctc

[zipformer](./zipformer)

#### Non-streaming

##### 

| decoding method                      | test       | test-cv | comment   |
|--------------------------------------|------------|---------|-----------|
| greedy_search                        | 1.91       | 6.43    |  |
| modified_beam_search                 | 1.90       | 6.48    |  |
| fast_beam_search                     | 1.91       | 6.42    |  |
| fast_beam_search_nbest_oracle        | (0.63)     | (3.38)  | <- oracle |
| m2: modified_beam_search  + nbest transformer rescore  | 1.88       | 6.03   | NBest rescore |


###### Train params

`./zipformer/train.py --world-size 1 --num-epochs 30 --start-epoch 0 --use-fp16 1 --exp-dir data/exp/v02 --use-cr-ctc 1 --use-ctc 1 --use-transducer 1 --use-attention-decoder 0 --num-encoder-layers 2,2,4,5,4,2 --feedforward-dim 512,768,1536,2048,1536,768 --encoder-dim 192,256,512,768,512,256 --encoder-unmasked-dim 192,192,256,320,256,192 --ctc-loss-scale 0.1 --enable-spec-aug 0 --cr-loss-scale 0.02 --max-duration 400 `

###### Decode params
`./zipformer/decode.py  --epoch 30  --avg 10  --exp-dir data/exp/v02 --bpe-model data/lang_bpe_500/bpe.model --decoding-method greedy_search --beam-size 4 --decode-limit 0 --use-cr-ctc 1 --use-ctc 1 --use-transducer 1 --use-attention-decoder 0 --num-encoder-layers 2,2,4,5,4,2 --feedforward-dim 512,768,1536,2048,1536,768 --encoder-dim 192,256,512,768,512,256 --encoder-unmasked-dim 192,192,256,320,256,192 --max-duration 400`


##### m2

Transformer lm trained on cc-100. Cleaned (removed any sentence containg non puncts or letter), auto split into sentences.
Words: 1289M

###### LM train params
```bash
./transformer_lm/train.py --world-size 1 --exp-dir /workspace/icefall/egs/liepa3/ASR/data/transformerlm/v01 --start-epoch 0 --num-epochs 10 --use-fp16 0 --num-layers 12 --tie-weights 1 --batch-size 25 --lm-data /workspace/icefall/egs/liepa3/ASR/data/transformerlm/lt.train.sorted.pt --lm-data-valid /workspace/icefall/egs/liepa3/ASR/data/transformerlm/lt.dev.sorted.pt
```
###### Decode params
```bash
./zipformer/decode.py  --epoch 30  --avg 10  --exp-dir data/exp02/exp/v02 --bpe-model data/exp02/lang_bpe_500/bpe.model --decoding-method modified_beam_search_lm_rescore 	--beam-size 4 --decode-limit 0 --use-cr-ctc 1 --use-ctc 1 --use-transducer 1 --use-attention-decoder 0 --num-encoder-layers 2,2,4,5,4,2 --feedforward-dim 512,768,1536,2048,1536,768 --encoder-dim 192,256,512,768,512,256 --encoder-unmasked-dim 192,192,256,320,256,192 --max-duration 300 --use-averaged-model 1 --use-shallow-fusion 0 --lm-type transformer --lm-exp-dir data/exp02/transformerlm/v01 --lm-epoch 3 --lm-avg 1 --lm-scale 0.05
```

### zipformer 

[zipformer](./zipformer)

#### Non-streaming

##### 

| decoding method                      | test       | test-cv | comment             |
|--------------------------------------|------------|---------|---------------------|
| greedy_search                        | 2.56       | 7.87    | --epoch 30 --avg 15 |
| modified_beam_search                 | 2.54       | 7.82    | --epoch 30 --avg 15 |

###### Train params

`--world-size 1  --num-epochs 30   --start-epoch 1   --use-fp16 1  --max-duration 1000`

###### Decode params
` --epoch 30  --avg 15  --max-duration 1000 --beam-size 4 `



### streaming models

#### results 

| model/decoding method                      | test       | test-cv | comment    |
|--------------------------------------|------------|---------|---------------------|
| ms2: zipformer + training with noise/greedy_search  | 3.98       | 10.98   |  |
| ms1: zipformer/greedy_search                        | 6.39       | 15.46   |  |

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
