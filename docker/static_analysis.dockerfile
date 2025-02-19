FROM ubuntu:24.04 AS base

ENV CLANG_VERSION=19
ENV CPPCHECK_VERSION=2.14.0
ENV CXX=clang++
ENV CC=clang
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
      build-essential python3 python3-pip \
      git wget libssl-dev ninja-build gnupg \
      lsb-release software-properties-common

# Copy the llvm.sh installation script
COPY --chmod=500 llvm.sh /opt/llvm/llvm.sh

# Execute the LLVM install script with the version number
WORKDIR /opt/llvm
RUN ./llvm.sh $CLANG_VERSION

# Clean up
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 install --break-system-packages PyGithub pylint

# Create symlinks for clang and clang++
RUN ln -s "$(which clang++-$CLANG_VERSION)" /usr/bin/clang++
RUN ln -s "$(which clang-$CLANG_VERSION)" /usr/bin/clang

# Create a symlink for python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Build and install CMake from source
WORKDIR /opt
RUN git clone https://github.com/Kitware/CMake.git
WORKDIR /opt/CMake
RUN ./bootstrap && make -j$(nproc) && make install

# Install cppcheck
WORKDIR /opt
RUN git clone https://github.com/danmar/cppcheck.git
WORKDIR /opt/cppcheck
RUN git checkout tags/$CPPCHECK_VERSION
WORKDIR /opt/cppcheck/build
RUN cmake -G Ninja .. && ninja all && ninja install
