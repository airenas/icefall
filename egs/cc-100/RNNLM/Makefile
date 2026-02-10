###################################################################
cfg?=Makefile.options
-include $(cfg)
###################################################################
LOGLEVEL?=INFO
python_cmd?=python3

data_dir?=data
url?=https://data.statmt.org/cc-100/lt.txt.xz
limit?=10000000000
lex_port?=8080
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
	$(python_cmd) ./local/to_sentences.py --input $< --output $@ --splitter-url http://host.docker.internal:$(lex_port)

$(data_dir)/lt.clean.txt: $(data_dir)/lt.sentences.txt	
	$(python_cmd) ./local/clean.py --input $< --output $@ 

start/lex:
	docker run --rm -it -p $(lex_port):8080 --name lex semantikadocker.vdu.lt/lex:2021.04.02

$(data_dir)/lt.train.txt $(data_dir)/lt.dev.txt $(data_dir)/lt.test.txt: $(data_dir)/lt.clean.txt	
	$(python_cmd) ./local/split.py --input $< --output-template $(data_dir)/lt.{}.txt


$(data_dir)/lt.%.dt: $(data_dir)/lt.%.txt
	$(python_cmd) ./local/prepare_lm_training_data.py \
    --bpe-model $(bpe_model) \
    --lm-data $< \
    --lm-archive $@	

$(data_dir)/lt.%.sorted.dt: $(data_dir)/lt.%.dt
	$(python_cmd) ./local/sort_lm_training_data.py \
    --in-lm-data $< \
    --out-lm-data $@ \
    --out-statistics $(data_dir)/lt.$*.stats.txt

prepare: $(data_dir)/lt.train.sorted.dt $(data_dir)/lt.dev.sorted.dt $(data_dir)/lt.test.sorted.dt
.PHONY: prepare
###################################################################
## just before download
clean:
	rm -f $(data_dir)/lt.ready.txt

.EXPORT_ALL_VARIABLES:


	