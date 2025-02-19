FROM ubuntu:24.04 AS base

# Define versions as environment variables
ENV CLANG_VERSION=20 \
    CPPCHECK_VERSION=2.16.0 \
    CXX=clang++ \
    CC=clang \
    DEBIAN_FRONTEND=noninteractive

# Copy the llvm.sh installation script
COPY llvm.sh /llvm.sh

# Install dependencies
RUN apt-get update && apt-get install -y \
        build-essential python3 python3-pip git wget libssl-dev ninja-build \
        lsb-release software-properties-common gnupg \
    # Execute the LLVM install script with the version number
    && chmod +x /llvm.sh && /llvm.sh $CLANG_VERSION \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    # Install Python packages
    && pip3 install --break-system-packages PyGithub pylint \
    # Create symlinks for clang and clang++
    && ln -s "$(which clang++-$CLANG_VERSION)" /usr/bin/clang++ \
    && ln -s "$(which clang-$CLANG_VERSION)" /usr/bin/clang \
    && ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /opt

# Build CMake from source
RUN git clone https://github.com/Kitware/CMake.git \
    && cd CMake \
    && ./bootstrap && make -j$(nproc) && make install

# Install cppcheck
RUN git clone https://github.com/danmar/cppcheck.git \
    && cd cppcheck \
    && git checkout tags/$CPPCHECK_VERSION \
    && mkdir build && cd build \
    && cmake -G Ninja .. && ninja all && ninja install
