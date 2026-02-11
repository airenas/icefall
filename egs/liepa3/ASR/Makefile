cfg?=Makefile.options
-include $(cfg)

LOGLEVEL?=INFO

exp_dir?=data/exp/v01

python_cmd=python3
decode_limit?=0
corpus_dir?=corpus

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
### Liepa 3 prepare            ###############################
##############################################################
# $(data_dir)/manifests/cuts_train.jsonl.gz $(data_dir)/manifests/cuts_dev.jsonl.gz $(data_dir)/manifests/cuts_test.jsonl.gz: | $(data_dir)/manifests
# 	$(python_cmd) local/prepare_corpus.py --corpus-dir $(corpus_dir) --transcript-file $(corpus_dir)/verified_utterances_20260121.csv \
#           --output-dir $(data_dir)/manifests --limit-count $(limit_count)
#     # Split train/dev/test (90/5/5)
#     python3 local/split.py --manifest-dir data/manifests
#     touch data/manifests/.liepa3.done
#   fi
# fi

# # if [ $stage -le 2 ] && [ $stop_stage -ge 2 ]; then
# #   log "Stage 2: Prepare musan manifest"
# #   # We assume that you have downloaded the musan corpus
# #   # to $dl_dir/musan
# #   mkdir -p data/manifests
# #   if [ ! -e data/manifests/.musan.done ]; then
# #     lhotse prepare musan $dl_dir/musan data/manifests
# #     touch data/manifests/.musan.done
# #   fi
# # fi

# if [ $stage -le 3 ] && [ $stop_stage -ge 3 ]; then
#   log "Stage 3: Compute fbank for liepa3"
#   mkdir -p data/fbank
#   if [ ! -e data/fbank/.liepa3.done ]; then
#     ./local/compute_fbank_liepa3.py
#     touch data/fbank/.liepa3.done
#   fi

#   # if [ ! -f data/fbank/liepa3_cuts_train-all-shuf.jsonl.gz ]; then
#   #   cat <(gunzip -c data/fbank/liepa3_cuts_train-clean-100.jsonl.gz) \
#   #     <(gunzip -c data/fbank/liepa3_cuts_train-clean-360.jsonl.gz) \
#   #     <(gunzip -c data/fbank/liepa3_cuts_train-other-500.jsonl.gz) | \
#   #     shuf | gzip -c > data/fbank/liepa3_cuts_train-all-shuf.jsonl.gz
#   # fi

#   if [ ! -e data/fbank/.liepa3-validated.done ]; then
#     log "Validating data/fbank for liepa3"
#     parts=(
#       train
#       test
#       dev
#     )
#     for part in ${parts[@]}; do
#       python3 ./local/validate_manifest.py \
#         data/fbank/cuts_${part}.jsonl.gz
#     done
#     touch data/fbank/.liepa3-validated.done
#   fi
# fi

# # if [ $stage -le 4 ] && [ $stop_stage -ge 4 ]; then
# #   log "Stage 4: Compute fbank for musan"
# #   mkdir -p data/fbank
# #   if [ ! -e data/fbank/.musan.done ]; then
# #     ./local/compute_fbank_musan.py
# #     touch data/fbank/.musan.done
# #   fi
# # fi

# if [ $stage -le 5 ] && [ $stop_stage -ge 5 ]; then
#   log "Stage 5: Prepare BPE based lang"

#   for vocab_size in ${vocab_sizes[@]}; do
#     lang_dir=data/lang_bpe_${vocab_size}
#     mkdir -p $lang_dir
#     python3 local/prepare_texts.py --input-file data/manifests/cuts_train.jsonl.gz --output-file $lang_dir/transcript_words.txt

#     # if [ ! -f $lang_dir/transcript_words.txt ]; then
#     #   log "Generate data for BPE training"
#     #   files=$(
#     #     find "$dl_dir/liepa3/train-clean-100" -name "*.trans.txt"
#     #     find "$dl_dir/liepa3/train-clean-360" -name "*.trans.txt"
#     #     find "$dl_dir/liepa3/train-other-500" -name "*.trans.txt"
#     #   )
#     #   for f in ${files[@]}; do
#     #     cat $f | cut -d " " -f 2-
#     #   done > $lang_dir/transcript_words.txt
#     # fi

#     if [ ! -f $lang_dir/bpe.model ]; then
#       ./local/train_bpe_model.py \
#         --lang-dir $lang_dir \
#         --vocab-size $vocab_size \
#         --transcript $lang_dir/transcript_words.txt
#     fi
#   done
# fi










##############################################################
### Decode                     ###############################
##############################################################
decode/test:
	$(python_cmd) ./zipformer/decode.py  --epoch 30  --avg 15  \
		--exp-dir $(exp_dir) --max-duration 1000 --decoding-method $(decoding_method)  \
		--beam-size 4 --decode-limit $(decode_limit) \
		--test-cut $(data_dir)/fbank/cuts_test.jsonl.gz
decode/common-voice:
	$(python_cmd) ./zipformer/decode.py  --epoch 30  --avg 15  \
		--exp-dir $(exp_dir) --max-duration 1000 --decoding-method $(decoding_method) \
		--beam-size 4 --decode-limit $(decode_limit) \
		--test-cut $(data_dir)/fbank/cuts_common-voice.jsonl.gz	
##############################################################
##############################################################
.EXPORT_ALL_VARIABLES:
