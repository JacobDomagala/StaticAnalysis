FROM jhyry9docks/static_analysis:clang19

WORKDIR /src

COPY src/*.py ./

COPY *.sh ./
RUN chmod +x *.sh


ENTRYPOINT ["/src/entrypoint.sh"]
