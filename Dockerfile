FROM ubuntu:20.04

ARG CXX=clang++
ARG DEBIAN_FRONTEND=noninteractive

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

COPY run_static_analysis.py /
RUN chmod +x /run_static_analysis.py

RUN apt-get update && apt-get install -y python3 python3-pip git xorg-dev build-essential libc++-10-dev cppcheck llvm-dev clang-tidy cmake
RUN pip3 install PyGithub

ENTRYPOINT ["/entrypoint.sh"]
