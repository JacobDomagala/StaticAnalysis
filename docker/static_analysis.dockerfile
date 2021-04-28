FROM ubuntu:20.04

ENV CXX=clang++
ENV C=clang

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y python3 python3-pip git xorg-dev\
    build-essential clang-11 cppcheck llvm-dev wget libssl-dev
RUN pip3 install PyGithub

RUN wget https://github.com/llvm/llvm-project/releases/download/llvmorg-12.0.0/clang-tools-extra-12.0.0.src.tar.xz && tar xf clang-tools-extra-12.0.0.src.tar.xz
ENV PATH="/clang-tools-extra-12.0.0.src/clang-tidy/tool/:${PATH}"

RUN ls

RUN ln -s \
    "$(which clang++-11)" \
    /usr/bin/clang++

RUN git clone https://github.com/Kitware/CMake.git && cd CMake && ./bootstrap && make && make install
