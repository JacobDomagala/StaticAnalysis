FROM jdomagala/static_analysis:latest

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

COPY src/static_analysis_cpp.py /
RUN chmod +x /static_analysis_cpp.py

COPY src/static_analysis_python.py /
RUN chmod +x /static_analysis_python.py

COPY src/sa_utils.py /
RUN chmod +x /sa_utils.py

COPY src/get_files_to_check.py /
RUN chmod +x /get_files_to_check.py

ENTRYPOINT ["/entrypoint.sh"]
