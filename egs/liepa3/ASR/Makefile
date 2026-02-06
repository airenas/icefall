-include Makefile.options
#####################################################################################
service=airenas/icefall
version?=dev
base_docker_version?=torch2.4.1-cuda12.2
data_dir?=
corpus_dir?=
docker_user?=1000:1000
# can run in detached mode  with d_mode=-d
d_mode?=-it

ifeq ($(d_mode),-d)
	d_cmd:=tail -f /dev/null
else
	d_cmd:=/bin/bash
endif
########### DOCKER ##################################################################
tag=$(service):$(version)

dbuild:
	docker buildx build -t $(tag) --build-arg BASE_DOCKER_VERSION=$(base_docker_version) -f Dockerfile ./ --load

run:
	docker run --gpus all --rm ${d_mode} \
		--name liepa3-asr \
	  	-v $(PWD):/workspace/icefall/egs/liepa3/ASR \
		-v $(corpus_dir):/workspace/icefall/egs/liepa3/ASR/corpus \
		-v $(data_dir):/workspace/icefall/egs/liepa3/ASR/data \
		-u $(docker_user) -e HOME=/tmp \
		--shm-size=16g \
		$(tag) $(d_cmd)

stop:
	docker stop liepa3-asr || true

attach:
	docker exec -it liepa3-asr /bin/bash
#####################################################################################
.PHONY: dbuild run
