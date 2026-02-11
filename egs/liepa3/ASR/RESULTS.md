## Results

### Testing datasets

| name       | corpus | sentences | words  |
|------------|------------|------------|---------------------|
| test       | LIEPA3 (5%) test set   |   | 123021 |
| test-cv    |  Common Voice (LT) test set v24.0 |   | 35659 |

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
` --epoch 30  --avg 15  --max-duration 1000 --decoding-method modified_beam_search  --beam-size 4 `


