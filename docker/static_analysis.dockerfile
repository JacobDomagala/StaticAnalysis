FROM ubuntu:21.04 as base

ENV CXX=clang++
ENV CC=clang

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y python3 python3-pip git \
    build-essential clang-12 clang-tidy-12 wget libssl-dev ninja-build && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN pip3 install PyGithub

RUN ln -s \
    "$(which clang++-12)" \
    /usr/bin/clang++

RUN ln -s \
    "$(which clang-12)" \
    /usr/bin/clang

RUN ln -s \
    /usr/bin/python3 \
    /usr/bin/python

RUN git clone https://github.com/Kitware/CMake.git && \
    cd CMake && ./bootstrap && \
    make -j4 && make install

RUN wget 'https://sourceforge.net/projects/cppcheck/files/cppcheck/2.4/cppcheck-2.4.tar.gz/download' && \
    tar xf download && \
    cd cppcheck-2.4 && mkdir build && cd build && \
    cmake -G "Ninja" .. && ninja install

