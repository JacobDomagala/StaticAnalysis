FROM jdomagala/static_analysis:update_tools

WORKDIR /src

COPY src/*.py ./

COPY *.sh ./
RUN chmod +x *.sh


ENTRYPOINT ["/src/entrypoint.sh"]
