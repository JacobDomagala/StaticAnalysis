FROM jdomagala/static_analysis:clang-tidy-11

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

COPY run_static_analysis.py /
RUN chmod +x /run_static_analysis.py

ENTRYPOINT ["/entrypoint.sh"]
