OUTDIR=/s2s-obs/tmp/


# TODO : turn this into a ecflow suite. If needed.
# To run this do :
# make build
# make publish
# will fail if s3 bucket is not mounted.

download: ${OUTDIR}/tmax

${OUTDIR}/tmax:
	mkdir -p ${OUTDIR} && ./download_from_source.sh ${OUTDIR}

build: ${OUTDIR}/tmax
	./build_dataset_observations.py --outdir ${OUTDIR} --input ${OUTDIR} --temperature && \
	./build_dataset_observations.py --outdir ${OUTDIR} --input ${OUTDIR} --rain

upload:
	cd ${OUTDIR} && \
	cp -rp test-output-reference /s3/s2s-ai-challenge/data/.  && \
	cp -rp training-output-reference /s3/s2s-ai-challenge/data/.
	# TODO use recursive s3cmd upload instead of mounting with s3fs

publish: upload
	s3cmd setacl s3://s2s-ai-challenge/data/test-output-reference --recursive --acl-public && \
	s3cmd setacl s3://s2s-ai-challenge/data/training-output-reference --recursive --acl-public

