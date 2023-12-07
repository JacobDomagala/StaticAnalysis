FROM ubuntu:23.04 as base

# Define versions as environment variables
ENV CLANG_VERSION=16
ENV CPPCHECK_VERSION=2.12.0

# Other environment variables
ENV CXX=clang++
ENV CC=clang
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
        build-essential python3 python3-pip git clang-$CLANG_VERSION clang-tidy-$CLANG_VERSION wget libssl-dev ninja-build \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install PyGithub pylint --break-system-packages \
    && ln -s "$(which clang++-$CLANG_VERSION)" /usr/bin/clang++ \
    && ln -s "$(which clang-$CLANG_VERSION)" /usr/bin/clang \
    && ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /opt

# Build CMake from source
RUN git clone https://github.com/Kitware/CMake.git \
    && cd CMake && ./bootstrap && make -j4 && make install

# Install cppcheck
RUN git clone https://github.com/danmar/cppcheck.git \
    && cd cppcheck && git checkout tags/$CPPCHECK_VERSION && mkdir build && cd build && cmake -G Ninja .. && ninja all && ninja install
