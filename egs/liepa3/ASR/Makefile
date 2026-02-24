cfg?=Makefile.options
-include $(cfg)

LOGLEVEL?=INFO

exp_dir?=data/exp/v01

python_cmd=python3
decode_limit?=0
limit_count?=100000000000000

corpus_dir?=corpus
start_epoch?=1
gpus?=1

epoch?=30
avg?=15

##############################################################
download_dir?=data/download
data_dir?=data
vocab_size?=500
lang_dir=$(data_dir)/lang_bpe_${vocab_size}
lm_params?=

$(download_dir) $(data_dir)/manifests $(data_dir)/fbank \
	$(download_dir)/common_voice $(lang_dir) $(exp_dir):
	mkdir -p $@
##############################################################
##############################################################
# Liepa 3 prepare											 #
##############################################################
$(data_dir)/manifests/cuts_train.jsonl.gz $(data_dir)/manifests/cuts_dev.jsonl.gz $(data_dir)/manifests/cuts_test.jsonl.gz: | $(data_dir)/manifests
	$(python_cmd) local/prepare_corpus.py --corpus-dir $(corpus_dir) --transcript-file $(corpus_dir)/verified_utterances_20260121.csv \
          --output-dir $(data_dir)/manifests --limit-count $(limit_count)
    # Split train/dev/test (90/5/5)
	$(python_cmd) local/split.py --manifest-dir $(data_dir)/manifests

$(data_dir)/fbank/cuts_train.jsonl.gz $(data_dir)/fbank/cuts_dev.jsonl.gz $(data_dir)/fbank/cuts_test.jsonl.gz: $(data_dir)/manifests/cuts_train.jsonl.gz $(data_dir)/manifests/cuts_dev.jsonl.gz $(data_dir)/manifests/cuts_test.jsonl.gz | $(data_dir)/fbank
	$(python_cmd) ./local/compute_fbank_liepa3.py --input-dir $(data_dir)/manifests --output-dir $(data_dir)/fbank

$(data_dir)/fbank/.%.validated: $(data_dir)/fbank/cuts_%.jsonl.gz
	$(python_cmd) ./local/validate_manifest.py $<
	touch $@

$(lang_dir)/transcript_words.txt: $(data_dir)/manifests/cuts_train.jsonl.gz | $(lang_dir)
	$(python_cmd) ./local/prepare_texts.py --input-file $< --output-file $@

$(lang_dir)/bpe.model: $(lang_dir)/transcript_words.txt
	$(python_cmd) ./local/train_bpe_model.py --lang-dir $(lang_dir) \
		--vocab-size $(vocab_size) --transcript $<

prepare/liepa3: $(data_dir)/fbank/.train.validated $(data_dir)/fbank/.dev.validated $(data_dir)/fbank/.test.validated $(lang_dir)/bpe.model
.PHONY: prepare/liepa3
##############################################################
# Train                                                      #
##############################################################
train: | $(exp_dir)
	$(python_cmd) ./zipformer/train.py --world-size $(gpus) --num-epochs $(epoch) --start-epoch $(start_epoch) --use-fp16 1 \
		--bpe-model $(lang_dir)/bpe.model --manifest-dir $(data_dir)/fbank \
		--exp-dir $(exp_dir) \
		$(train_params) 
##############################################################
# Decode                     	                             #
##############################################################
decode/test: .decode/cuts_test.jsonl.gz
.PHONY: decode/test

decode/common-voice: .decode/cuts_common-voice.jsonl.gz
.PHONY: decode/common-voice		

.decode/%: $(data_dir)/%
	$(python_cmd) ./zipformer/decode.py  --epoch $(epoch)  --avg $(avg)  \
		--exp-dir $(exp_dir) --bpe-model $(lang_dir)/bpe.model \
		--decoding-method $(decoding_method) \
		--beam-size 4 --decode-limit $(decode_limit) \
		$(decode_params) \
		$(lm_params) \
		--test-cut $<
##############################################################
# ONNX                     	                             #
##############################################################
onnx/export:
	$(python_cmd) ./zipformer/export-onnx-ctc.py \
		--tokens $(lang_dir)/tokens.txt \
		--exp-dir $(exp_dir) \
		--use-averaged-model 1 \
		--epoch $(epoch) \
		--avg $(avg) \
		--query-head-dim 32 \
		--value-head-dim 12 \
		--decoder-dim 512 \
		--joiner-dim 512 \
		--causal False \
		--chunk-size 16 \
		$(export_params) \
		--left-context-frames 128

onnx/decode-wav:
	$(python_cmd) ./zipformer/onnx_pretrained_ctc.py \
		--nn-model $(exp_dir)/model.onnx \
		--tokens $(lang_dir)/tokens.txt \
		$(wavs)
##############################################################
##############################################################
# CommonVoice LT Test Corpus 								 #
##############################################################
common_voice_gz?=cv-corpus-24.0-2025-12-05-lt.tar.gz
common_voice_extr_dir?=cv-corpus-24.0-2025-12-05

${download_dir}/${common_voice_gz}: | ${download_dir}
	echo "Manually Download Common Voice LT test corpus to ${download_dir}/${common_voice_gz}"
	exit 1	

$(download_dir)/.common-voice.dwn: ${download_dir}/${common_voice_gz} | $(download_dir)/common_voice
	tar xvzf ${download_dir}/${common_voice_gz} -C $(download_dir)/common_voice
	touch $@	
$(data_dir)/manifests/cv-lt_supervisions_test.jsonl.gz: $(download_dir)/.common-voice.dwn | $(data_dir)/manifests
	lhotse prepare commonvoice $(download_dir)/common_voice/$(common_voice_extr_dir) $(data_dir)/manifests --language=lt --split=test
$(data_dir)/manifests/cuts_common-voice.jsonl.gz: $(data_dir)/manifests/cv-lt_supervisions_test.jsonl.gz
	$(python_cmd) ./local/prepare_common_voice.py --input $< --output $(data_dir)/manifests/cv-lt_supervisions_test_norm.jsonl.gz
	lhotse cut simple -r $(data_dir)/manifests/cv-lt_recordings_test.jsonl.gz \
    	-s $(data_dir)/manifests/cv-lt_supervisions_test_norm.jsonl.gz \
    	$@
$(data_dir)/fbank/cuts_common-voice.jsonl.gz: $(data_dir)/manifests/cuts_common-voice.jsonl.gz  | $(data_dir)/fbank
	$(python_cmd) ./local/compute_fbank.py --cuts $(data_dir)/manifests/cuts_common-voice.jsonl.gz --output-dir $(data_dir)/fbank \
		--partition cv-lt-test --perturb-speed False
##############################################################
prepare/common-voice: $(data_dir)/fbank/cuts_common-voice.jsonl.gz
.PHONY: prepare/common-voice
##############################################################
##############################################################
# MUSAN 													 #
##############################################################
$(download_dir)/.musan.dwn: | $(download_dir)
	lhotse download musan $(download_dir)
	touch $@

$(data_dir)/manifests/.musan.done: $(download_dir)/.musan.dwn | $(data_dir)/manifests
	lhotse prepare musan $(download_dir)/musan $(data_dir)/manifests
	touch $@

$(data_dir)/fbank/musan_cuts.jsonl.gz: $(data_dir)/manifests/.musan.done | $(data_dir)/fbank
	$(python_cmd) ./local/compute_fbank_musan.py --input-dir=$(data_dir)/manifests --output-dir=$(data_dir)/fbank

$(data_dir)/manifests/musan_cuts.jsonl.gz: $(data_dir)/fbank/musan_cuts.jsonl.gz | $(data_dir)/manifests
	cp $^ $@
##############################################################
prepare/musan: $(data_dir)/manifests/musan_cuts.jsonl.gz
.PHONY: prepare/musan		
##############################################################
.EXPORT_ALL_VARIABLES:
