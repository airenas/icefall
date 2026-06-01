## Results

Zip former resultts for intelektika tests

Models:  in [../../liepa3/ASR](../../liepa3/ASR/RESULTS.md) trained on 450h

m1, m2, m3, ms3: trained on 450h

mL01: trained on 10k h (10 epochs, 350k iterations)


| model/decoding method                      | ADAM  |  ARMN |   LRV1 |   SPEK |   TVR1 |   PRIV |   TEL1 |   TELs |   BABL |
|--------------------------------------|------------|---------|-----------|-|-|-|-|-|-|
| m1: zipformer (ctc cr) / greedy_search            | 7.20 |  7.67 | 16.59 | 15.70 | 19.07 | 50.43 | | 24.57 | 54.96 |
| m2: zipformer (ctc cr) + musan / greedy_search    | 6.80 |  6.74 | 16.07 | 15.39 | 17.7 | 49.09 | | 23.53 | 52.70 |
| m3: zipformer (ctc)  + musan / greedy_search      | 7.20 |  7.76 | 16.84 | 15.88 | 18.51 | 49.49 |  | 25.26 | 54.38 |
| ms3:  ms3: zipformer (ctc) streaming  + musan / greedy_search  | 8.40 |  14.39 | 22.13 | 19.56 | 22.29 | 55.88 |  | 29.71 | 60.51 |
|*with lm*|
| m1+l2: zipformer (ctc cr) / modified_beam_search + nbest rnnlm rescore  beam-size=12, --lm-scale 0.50 | 6.00 | 6.79 | 15.08 | 14.28 | 17.29 | 48.73 | | 22.44 | 53.39 |
| m2+l2: zipformer (ctc cr) + musan/ modified_beam_search + nbest rnnlm rescore beam-size=12, --lm-scale 0.50  | 6.40 | 5.63 | 14.62 | 14.39 | 16.23 | 47.12 | | 20.62| 51.27 |
||
| mL01: zipformer (ctc) + greedy_search  (trained on 10k) | 1.6 | 3.18 | 6.42 | 8.73 [722 / 8272, 75 ins, 103 del, 544 sub ] | 8.73 [1383 / 15849, 154 ins, 157 del, 1072 sub ] | 24.05 | | 12.01 | 31.42 |
