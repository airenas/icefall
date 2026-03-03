cfg?=Makefile.options
-include $(cfg)

log?=INFO

exp_dir?=data/exp/v01
vocab_size?=500
lang_dir=$(data_dir)/lang_bpe_${vocab_size}

log?=INFO
python_cmd=PYTHONPATH=./../../../ LOGLEVEL=$(log) python3
decode_limit?=0

epoch?=30
avg?=15

##############################################################
data_dir?=data

$(download_dir) $(data_dir)/manifests $(data_dir)/fbank $(data_dir)/fbank-chunks \
	$(data_dir)/recognized $(data_dir)/merged $(data_dir)/results:
	mkdir -p $@
##############################################################
##############################################################
# Intelektika test corpus									 #
##############################################################
$(data_dir)/manifests/cuts_adam.jsonl.gz: | $(data_dir)/manifests
	$(python_cmd) local/prepare_test_cut.py --corpus-dir $(corpus_dir)/ADAM --transcript-dir $(corpus_dir)/kaldi-data/16-ADAM \
          --output-file $@ --audio-take-last 1
$(data_dir)/manifests/cuts_arm.jsonl.gz: | $(data_dir)/manifests
	$(python_cmd) local/prepare_test_cut.py --corpus-dir $(corpus_dir)/ARM_A --transcript-dir $(corpus_dir)/kaldi-data/16-ARMN \
          --output-file $@ --audio-take-last 1
$(data_dir)/manifests/cuts_priv.jsonl.gz: | $(data_dir)/manifests
	$(python_cmd) local/prepare_test_cut.py --corpus-dir $(corpus_dir)/PRIV --transcript-dir $(corpus_dir)/kaldi-data/16-PRIV \
          --output-file $@ --audio-take-last 1
$(data_dir)/manifests/cuts_tel1.jsonl.gz: | $(data_dir)/manifests
	$(python_cmd) local/prepare_test_cut.py --corpus-dir $(corpus_dir)/TEL --transcript-dir $(corpus_dir)/kaldi-data/16-TEL1 \
          --output-file $@ --audio-take-last 2
$(data_dir)/manifests/cuts_tels.jsonl.gz: | $(data_dir)/manifests
	$(python_cmd) local/prepare_test_cut.py --corpus-dir $(corpus_dir)/TEL --transcript-dir $(corpus_dir)/kaldi-data/16-TELs \
          --output-file $@ --audio-take-last 2		  	
$(data_dir)/manifests/cuts_lrv.jsonl.gz: | $(data_dir)/manifests
	$(python_cmd) local/prepare_test_cut.py --corpus-dir $(corpus_dir)/LRVR --transcript-dir $(corpus_dir)/kaldi-data/16-LRV1 \
          --output-file $@ --audio-take-last 1
$(data_dir)/manifests/cuts_spek.jsonl.gz: | $(data_dir)/manifests
	$(python_cmd) local/prepare_test_cut.py --corpus-dir $(corpus_dir)/SPEK --transcript-dir $(corpus_dir)/kaldi-data/16-SPEK \
          --output-file $@ --audio-take-last 1
$(data_dir)/manifests/cuts_tvr.jsonl.gz: | $(data_dir)/manifests
	$(python_cmd) local/prepare_test_cut.py --corpus-dir $(corpus_dir)/TVR --transcript-dir $(corpus_dir)/kaldi-data/16-TVR1 \
          --output-file $@ --audio-take-last 1			  		  		  		  
$(data_dir)/manifests/cuts_babl.jsonl.gz: | $(data_dir)/manifests
	$(python_cmd) local/prepare_test_cut.py --corpus-dir $(corpus_dir)/BABL --transcript-dir $(corpus_dir)/kaldi-data/16-BABL \
          --output-file $@ --audio-take-last 1			  		  		  		  		  
##############################################################
$(data_dir)/fbank/cuts_%.jsonl.gz: $(data_dir)/manifests/cuts_%.jsonl.gz  | $(data_dir)/fbank
	$(python_cmd) ./../../liepa3/ASR/local/compute_fbank.py --cuts $< --output-dir $(data_dir)/fbank \
		--partition $* --perturb-speed False
$(data_dir)/fbank-chunks/cuts_%.jsonl.gz: $(data_dir)/fbank/cuts_%.jsonl.gz  | $(data_dir)/fbank-chunks
	$(python_cmd) ./long_file_recog/split_into_chunks.py --manifest-in $< --manifest-out $(data_dir)/fbank-chunks/cuts_$*.jsonl.gz \
		--chunk 30 --extra 2
prepare/adam: $(data_dir)/fbank-chunks/cuts_adam.jsonl.gz
.PHONY: prepare/adam
prepare/arm: $(data_dir)/fbank/cuts_arm.jsonl.gz
.PHONY: prepare/arm
prepare/priv: $(data_dir)/fbank-chunks/cuts_priv.jsonl.gz
.PHONY: prepare/priv
prepare/tel: $(data_dir)/fbank/cuts_tel.jsonl.gz
.PHONY: prepare/tel
prepare: prepare/adam prepare/arm prepare/priv prepare/tel
.PHONY: prepare
##############################################################
$(data_dir)/recognized/cuts_%.jsonl.gz: $(data_dir)/fbank-chunks/cuts_%.jsonl.gz  | $(data_dir)/recognized
	$(python_cmd) ./long_file_recog/recognize.py --manifest-in $< --manifest-out $(data_dir)/recognized/cuts_$*_.jsonl.gz \
		--world-size 1 --nn-model-filename $(model) --decoding-method greedy_search \
		--bpe-model $(lang_dir)/bpe.model \
		--max-duration 500 --num-buckets 2 --num-workers=1
	mv $(data_dir)/recognized/cuts_$*_.jsonl.gz $(data_dir)/recognized/cuts_$*.jsonl.gz
rec/adam: $(data_dir)/recognized/cuts_adam.jsonl.gz
.PHONY: rec/adam
##############################################################
$(data_dir)/results/.%.done.rec: $(data_dir)/fbank/cuts_%.jsonl.gz
	$(python_cmd) ./../../liepa3/ASR/zipformer/decode.py  --epoch $(epoch)  --avg $(avg)  \
		--exp-dir $(exp_dir) --bpe-model $(lang_dir)/bpe.model \
		--decoding-method $(decoding_method) \
		--beam-size 4 --decode-limit $(decode_limit) --num-buckets=2 \
		$(decode_params) \
		$(lm_params) \
		--test-cut $<
	touch $@	
##############################################################
$(data_dir)/merged/cuts_%.jsonl.gz: $(data_dir)/recognized/cuts_%.jsonl.gz  | $(data_dir)/merged
	$(python_cmd) ./long_file_recog/merge_chunks.py --manifest-in $< --manifest-out $(data_dir)/merged/cuts_$*_.jsonl.gz \
		--bpe-model $(lang_dir)/bpe.model --extra 2
	mv $(data_dir)/merged/cuts_$*_.jsonl.gz $(data_dir)/merged/cuts_$*.jsonl.gz
##############################################################
$(data_dir)/results/.%.done: $(data_dir)/merged/cuts_%.jsonl.gz  | $(data_dir)/results
	$(python_cmd) ./long_file_recog/compute_wer.py --manifest-in $< --out-dir $(data_dir)/results \
	--name $*
	touch $@
wer/adam: $(data_dir)/results/.adam.done.rec
.PHONY: wer/adam	
wer/arm: $(data_dir)/results/.arm.done
.PHONY: wer/arm
wer/priv: $(data_dir)/results/.priv.done
.PHONY: wer/priv
wer/tel1: $(data_dir)/results/.tel1.done
.PHONY: wer/tel1
wer/tels: $(data_dir)/results/.tels.done
.PHONY: wer/tels
wer/lrv: $(data_dir)/results/.lrv.done.rec
.PHONY: wer/lrv
wer/spek: $(data_dir)/results/.spek.done
.PHONY: wer/spek
wer/tvr: $(data_dir)/results/.tvr.done
.PHONY: wer/tvr
wer/babl: $(data_dir)/results/.babl.done
.PHONY: wer/babl
wer: wer/priv wer/adam wer/arm wer/tel1 wer/tels wer/lrv wer/spek wer/tvr wer/babl
.PHONY: wer
##############################################################
.EXPORT_ALL_VARIABLES:
