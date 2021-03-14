FROM ubuntu:20.04

ARG CXX=clang++
ARG DEBIAN_FRONTEND=noninteractive

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

COPY run_static_analysis.py /
RUN chmod +x /run_static_analysis.py

RUN apt-get update && apt-get install -y python3 python3-pip git xorg-dev\
    build-essential clang-11 lldb-11 lld-11 libc++-11-dev cppcheck llvm-dev clang-tidy
RUN pip3 install PyGithub

RUN git clone https://github.com/Kitware/CMake.git && cd CMake && ./bootstrap && make && make install

ENTRYPOINT ["/entrypoint.sh"]
