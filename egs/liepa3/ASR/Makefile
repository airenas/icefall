-include Makefile.options
#####################################################################################
service=airenas/icefall
version?=dev
base_docker_version?=torch2.4.1-cuda12.2
data_dir?=
corpus_dir?=
docker_user?=1000:1000
########### DOCKER ##################################################################
tag=$(service):$(version)

dbuild:
	docker buildx build -t $(tag) --build-arg BASE_DOCKER_VERSION=$(base_docker_version) -f Dockerfile ./ --load

run:
	docker run --gpus all --rm -it \
		--name liepa3-asr \
	  	-v $(PWD):/workspace/icefall/egs/liepa3/ASR \
		-v $(corpus_dir):/workspace/icefall/egs/liepa3/ASR/corpus \
		-v $(data_dir):/workspace/icefall/egs/liepa3/ASR/data \
		-u $(docker_user) -e HOME=/tmp \
		--shm-size=16g \
		$(tag)  /bin/bash
#####################################################################################
.PHONY: dbuild run
