FROM ubuntu:24.04 AS cppcheck-builder

ARG CPPCHECK_VERSION=2.20.0
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        cmake \
        git \
        ninja-build \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp

RUN git clone --branch "${CPPCHECK_VERSION}" --depth 1 https://github.com/danmar/cppcheck.git \
    && cmake -S /tmp/cppcheck -B /tmp/cppcheck/build -G Ninja \
        -DCMAKE_BUILD_TYPE=MinSizeRel \
        -DCMAKE_INSTALL_PREFIX=/opt/cppcheck \
    && cmake --build /tmp/cppcheck/build --parallel \
    && cmake --install /tmp/cppcheck/build \
    && strip /opt/cppcheck/bin/cppcheck


FROM ubuntu:24.04 AS python-tools-builder

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        python3 \
        python3-pip \
    && python3 -m pip install --break-system-packages --no-cache-dir --no-compile \
        --target /opt/python-tools \
        PyGithub \
        pylint \
    && find /opt/python-tools -type d -name "__pycache__" -prune -exec rm -rf {} + \
    && find /opt/python-tools -type f -name "*.pyc" -delete \
    && rm -rf /var/lib/apt/lists/*


FROM ubuntu:24.04 AS llvm-repo

ARG CLANG_VERSION=23
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        gnupg \
        wget \
    && wget -qO- https://apt.llvm.org/llvm-snapshot.gpg.key | gpg --dearmor -o /llvm.gpg \
    && printf "deb [signed-by=/usr/share/keyrings/llvm.gpg] http://apt.llvm.org/noble/ llvm-toolchain-noble main\n" > /llvm.list \
    && rm -rf /var/lib/apt/lists/*


FROM ubuntu:24.04 AS base

ARG CLANG_VERSION=23
ENV DEBIAN_FRONTEND=noninteractive \
    CLANG_VERSION=${CLANG_VERSION} \
    CC=clang \
    CXX=clang++ \
    PATH="/opt/cppcheck/bin:${PATH}" \
    PYTHONPATH="/opt/python-tools"

COPY --from=python-tools-builder /opt/python-tools /opt/python-tools
COPY --from=cppcheck-builder /opt/cppcheck /opt/cppcheck

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=llvm-repo /llvm.gpg /usr/share/keyrings/llvm.gpg
COPY --from=llvm-repo /llvm.list /etc/apt/sources.list.d/llvm.list

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        cmake \
        git \
        make \
        python3 \
        clang-tidy-${CLANG_VERSION} \
    && ln -sf "/usr/bin/clang++-${CLANG_VERSION}" /usr/bin/clang++ \
    && ln -sf "/usr/bin/clang-${CLANG_VERSION}" /usr/bin/clang \
    && ln -sf "/usr/bin/clang-tidy-${CLANG_VERSION}" /usr/bin/clang-tidy \
    && ln -sf "/usr/bin/run-clang-tidy-${CLANG_VERSION}" /usr/bin/run-clang-tidy \
    && ln -sf /usr/bin/python3 /usr/bin/python \
    && printf '%s\n' '#!/bin/sh' 'exec python3 -m pylint "$@"' > /usr/local/bin/pylint \
    && chmod +x /usr/local/bin/pylint \
    && rm -rf \
        /var/lib/apt/lists/* \
        /usr/share/doc/* \
        /usr/share/man/* \
        /usr/share/locale/*

WORKDIR /opt
