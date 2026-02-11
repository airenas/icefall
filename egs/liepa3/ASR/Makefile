-include Makefile.options
LOGLEVEL?=INFO

exp_dir?=data/exp/v01

python_cmd=python3
decode_limit?=0

##############################################################
download_dir?=data/download
data_dir?=data
$(download_dir) $(data_dir)/manifests $(data_dir)/fbank \
	$(download_dir)/common_voice:
	mkdir -p $@
##############################################################
### MUSAN ####################################################
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
### CommonVoice LT Test Corpus ###############################
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
### Decode                     ###############################
##############################################################
decode/test:
	$(python_cmd) ./zipformer/decode.py  --epoch 30  --avg 15  \
		--exp-dir $(exp_dir) --max-duration 1000 --decoding-method modified_beam_search  \
		--beam-size 4 --decode_limit $(decode_limit) \
		--test-cut $(data_dir)/fbank/cuts_test.jsonl.gz
decode/common-voice:
	$(python_cmd) ./zipformer/decode.py  --epoch 30  --avg 15  \
		--exp-dir $(exp_dir) --max-duration 1000 --decoding-method modified_beam_search  \
		--beam-size 4 --decode_limit $(decode_limit) \
		--test-cut $(data_dir)/fbank/cuts_common-voice.jsonl.gz	
##############################################################
##############################################################
.EXPORT_ALL_VARIABLES:
