ARG BASE_IMAGE=jdomagala/static_analysis:latest
FROM ${BASE_IMAGE}

WORKDIR /src

COPY src/*.py ./

COPY *.sh ./
RUN chmod +x *.sh


ENTRYPOINT ["/src/entrypoint.sh"]
