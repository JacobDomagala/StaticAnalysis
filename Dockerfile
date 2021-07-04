FROM jdomagala/static_analysis:latest

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

COPY run_static_analysis.py /
RUN chmod +x /run_static_analysis.py

COPY get_files_to_check.py /
RUN chmod +x /get_files_to_check.py

ENTRYPOINT ["/entrypoint.sh"]
