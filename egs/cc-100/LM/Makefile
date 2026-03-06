###################################################################
cfg?=Makefile.options
-include $(cfg)
###################################################################
log?=INFO
python_cmd=PYTHONPATH=./../../../ LOGLEVEL=$(log) python3

data_dir?=data
url?=https://data.statmt.org/cc-100/lt.txt.xz
lex_port?=8080
splitter_url?=http://host.docker.internal:$(lex_port)
limit?=10000000000
gpus?=1

batch_size?=50
###################################################################
$(data_dir):
	mkdir -p $@

$(data_dir)/.dwn: | $(data_dir)
	curl --retry 5 -L -o $(data_dir)/lt.txt.xz $(url)
	touch $@
$(data_dir)/lt.txt: $(data_dir)/.dwn
	unxz -k $(data_dir)/lt.txt.xz
	touch $@
$(data_dir)/lt.ready.txt: $(data_dir)/lt.txt
	head -n $(limit) $(data_dir)/lt.txt > $@_
	mv $@_ $@	

$(data_dir)/lt.sentences.txt: $(data_dir)/lt.ready.txt
	$(python_cmd) ./local/to_sentences.py --input $< --output $@_ --splitter-url $(splitter_url) \
		--continue-if-exists
	mv $@_ $@
###################################################################
### lex docker must be started on host
start/lex:
	docker run --rm -it -p $(lex_port):8080 --log-driver=none --name lex semantikadocker.vdu.lt/lex:2021.04.02
###################################################################
prepare/cc-100: $(data_dir)/lt.sentences.txt
.PHONY: prepare/cc-100
###################################################################
$(data_dir)/lt.clean.txt: # $(data_dir)/lt.sentences.txt	
	$(python_cmd) ./local/clean.py --input $(data_dir)/lt.sentences.txt --output $@ 

## split $(data_dir)/lt.clean.txt into train/dev/test 90/5/5
$(data_dir)/lt.train.txt $(data_dir)/lt.dev.txt $(data_dir)/lt.test.txt: $(data_dir)/lt.clean.txt	
	$(python_cmd) ./local/split.py --input $< --output-template $(data_dir)/lt.{}.txt

## ### k2 preparation
$(data_dir)/lt.%.pt: $(data_dir)/lt.%.txt
	$(python_cmd) ./local/prepare_lm_training_data.py \
    --bpe-model $(bpe_model) \
    --lm-data $< \
    --lm-archive $@	

$(data_dir)/lt.%.sorted.pt: $(data_dir)/lt.%.pt
	$(python_cmd) ./local/sort_lm_training_data.py \
    --in-lm-data $< \
    --out-lm-data $@ \
    --out-statistics $(data_dir)/lt.$*.stats.txt

prepare: $(data_dir)/lt.train.sorted.pt $(data_dir)/lt.dev.sorted.pt $(data_dir)/lt.test.sorted.pt
.PHONY: prepare
###################################################################
### k2 training
$(exp_dir)/.transformer.done: $(data_dir)/lt.train.sorted.pt $(data_dir)/lt.dev.sorted.pt 
	$(python_cmd) ../../../icefall/transformer_lm/train.py \
    --world-size $(gpus) \
    --exp-dir $(exp_dir) \
    --start-epoch 0 \
    --num-epochs 10 \
    --use-fp16 0 \
    --num-layers 12 \
    --tie-weights 1 \
    --batch-size $(batch_size) \
    --lm-data $(data_dir)/lt.train.sorted.pt \
    --lm-data-valid $(data_dir)/lt.dev.sorted.pt
	touch $@
$(exp_dir)/.rnn.done: $(data_dir)/lt.train.sorted.pt $(data_dir)/lt.dev.sorted.pt 
	$(python_cmd) ../../../icefall/rnn_lm/train.py \
    --world-size $(gpus) \
    --exp-dir $(exp_dir) \
    --start-epoch 0 \
    --num-epochs 10 \
    --use-fp16 0 \
    --tie-weights 1 \
    --embedding-dim 2048 \
    --hidden-dim 2048 \
    --num-layers 3 \
    --batch-size $(batch_size) \
    --lm-data $(data_dir)/lt.train.sorted.pt \
    --lm-data-valid $(data_dir)/lt.dev.sorted.pt \
    --save_every_n 5000
	touch $@
train/transformer: $(exp_dir)/.transformer.done
.PHONY: train/transformer
train/rnn: $(exp_dir)/.rnn.done
.PHONY: train/rnn
###################################################################
perplexity/rnn: 
	$(python_cmd) ../../../icefall/rnn_lm/compute_perplexity.py \
    --exp-dir $(exp_dir) \
    --epoch 10 \
    --avg 2 \
    --embedding-dim 2048 \
    --hidden-dim 2048 \
    --num-layers 3 \
    --batch-size $(batch_size) \
    --lm-data $(data_dir)/lt.test.sorted.pt
.PHONY: perplexity/rnn
###################################################################
## just clean data after download
clean/cc-100:
	rm -f $(data_dir)/lt.ready.txt
.PHONY: clean/cc-100
###################################################################
.EXPORT_ALL_VARIABLES:

