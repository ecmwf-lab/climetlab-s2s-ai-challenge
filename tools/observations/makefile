OUTDIR=/s2s-obs/tmp/


# TODO : turn this into a ecflow suite. If needed.
# To run this do :
# make build
# make publish

download: ${OUTDIR}/tmax ${OUTDIR}/tmin ${OUTDIR}/rain

${OUTDIR}/tmax:
	mkdir -p ${OUTDIR} && ./download_from_source.sh ${OUTDIR}
${OUTDIR}/tmin:
	mkdir -p ${OUTDIR} && ./download_from_source.sh ${OUTDIR}
${OUTDIR}/rain:
	mkdir -p ${OUTDIR} && ./download_from_source.sh ${OUTDIR}

build: ${OUTDIR}/tmax ${OUTDIR}/tmin ${OUTDIR}/rain
	./build_dataset_observations.py --outdir ${OUTDIR} --input ${OUTDIR} --temperature && \
	./build_dataset_observations.py --outdir ${OUTDIR} --input ${OUTDIR} --rain

upload:
	cd ${OUTDIR} && \
	for i in training-output-reference/*/*; do echo $$i; s3cmd put $$i s3://s2s-ai-challenge/data/$$i; done && \
	for i in test-output-reference/*/*;     do echo $$i; s3cmd put $$i s3://s2s-ai-challenge/data/$$i; done && \
	for i in observations/*/*;     do echo $$i; s3cmd put $$i s3://s2s-ai-challenge/data/$$i; done

publish: upload
	s3cmd setacl s3://s2s-ai-challenge/data/test-output-reference --recursive --acl-public && \
	s3cmd setacl s3://s2s-ai-challenge/data/test-output-reference/ --recursive --acl-public && \
	s3cmd setacl s3://s2s-ai-challenge/data/training-output-reference --recursive --acl-public && \
	s3cmd setacl s3://s2s-ai-challenge/data/training-output-reference/ --recursive --acl-public && \
	s3cmd setacl s3://s2s-ai-challenge/data/observations --recursive --acl-public && \
	s3cmd setacl s3://s2s-ai-challenge/data/observations/ --recursive --acl-public

nuke:
	s3cmd rm s3://s2s-ai-challenge/data/training-output-reference --recursive
	s3cmd rm s3://s2s-ai-challenge/data/test-output-reference --recursive
