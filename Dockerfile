FROM ubuntu:latest

ARG CXX=clang++
ARG DEBIAN_FRONTEND=noninteractive

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

COPY run_static_analysis.py /
RUN chmod +x /run_static_analysis.py

RUN apt-get update && apt-get install -y git xorg-dev build-essential libc++-10-dev cppcheck llvm-dev clang-tidy cmake

ENTRYPOINT ["/entrypoint.sh"]
