FROM jdomagala/static_analysis:latest

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

COPY src/run_static_analysis.py /
RUN chmod +x /run_static_analysis.py

COPY src/python/run_static_analysis.py /python/
RUN chmod +x /python/run_static_analysis.py

COPY src/get_files_to_check.py /
RUN chmod +x /get_files_to_check.py

ENTRYPOINT ["/entrypoint.sh"]
