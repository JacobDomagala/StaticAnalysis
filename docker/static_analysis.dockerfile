FROM ubuntu:20.04

ENV CXX=clang++
ENV C=clang

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y python3 python3-pip git \
    build-essential clang-11 wget libssl-dev ninja-build
RUN pip3 install PyGithub

RUN ln -s \
    "$(which clang++-11)" \
    /usr/bin/clang++

RUN ln -s \
    /usr/bin/python3 \
    /usr/bin/python

RUN git clone https://github.com/Kitware/CMake.git && \
    cd CMake && ./bootstrap && \
    make -j4 && make install

RUN wget 'https://sourceforge.net/projects/cppcheck/files/cppcheck/2.4/cppcheck-2.4.tar.gz/download' && \
    tar xf download && \
    cd cppcheck-2.4 && mkdir build && cd build && \
    cmake -G "Ninja" .. && ninja install && \
    rm -rf *

RUN git clone https://github.com/llvm/llvm-project.git && \
    cd llvm-project && \
    mkdir build && \
    cd build && \
    cmake -G "Ninja" -DCMAKE_BUILD_TYPE=Release -DLLVM_ENABLE_PROJECTS="clang;clang-tools-extra;" ../llvm && \
    ninja install-clang-tidy && \
    rm -rf *
