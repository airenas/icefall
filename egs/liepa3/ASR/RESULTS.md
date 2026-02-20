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
| greedy_search                        | 1.91       | 6.61    |  |
| modified_beam_search                 | 1.90       | 6.67    |  |
| fast_beam_search                     | 1.90       | 6.58    |  |
| fast_beam_search_nbest_oracle        | (0.63)     | (3.38)  | <- oracle |

###### Train params

`./zipformer/train.py --world-size 1 --num-epochs 30 --start-epoch 0 --use-fp16 1 --exp-dir data/exp/v02 --use-cr-ctc 1 --use-ctc 1 --use-transducer 1 --use-attention-decoder 0 --num-encoder-layers 2,2,4,5,4,2 --feedforward-dim 512,768,1536,2048,1536,768 --encoder-dim 192,256,512,768,512,256 --encoder-unmasked-dim 192,192,256,320,256,192 --ctc-loss-scale 0.1 --enable-spec-aug 0 --cr-loss-scale 0.02 --max-duration 400 `

###### Decode params
`./zipformer/decode.py  --epoch 30  --avg 10  --exp-dir data/exp/v02 --bpe-model data/lang_bpe_500/bpe.model --decoding-method greedy_search --beam-size 4 --decode-limit 0 --use-cr-ctc 1 --use-ctc 1 --use-transducer 1 --use-attention-decoder 0 --num-encoder-layers 2,2,4,5,4,2 --feedforward-dim 512,768,1536,2048,1536,768 --encoder-dim 192,256,512,768,512,256 --encoder-unmasked-dim 192,192,256,320,256,192 --max-duration 400`


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

