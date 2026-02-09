-include Makefile.options
LOGLEVEL?=INFO

python_cmd=python3
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
$(data_dir)/manifests/common-voice_cuts.jsonl.gz:$(data_dir)/manifests/cv-lt_supervisions_test.jsonl.gz
	$(python_cmd) ./local/prepare_common_voice.py --input $< --output $(data_dir)/manifests/cv-lt_supervisions_test_norm.jsonl.gz
	lhotse combine $(data_dir)/manifests/cv-lt_recordings_test.jsonl.gz \
    	$(data_dir)/manifests/cv-lt_supervisions_test_norm.jsonl.gz \
    	$@
##############################################################
prepare/common-voice: $(data_dir)/manifests/common-voice_cuts.jsonl.gz
.PHONY: prepare/common-voice
##############################################################
.EXPORT_ALL_VARIABLES:
