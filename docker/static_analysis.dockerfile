FROM ubuntu:24.04 AS cppcheck-builder

ARG CPPCHECK_VERSION=2.16.0
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


FROM ubuntu:24.04 AS base

ARG CLANG_VERSION=20
ENV DEBIAN_FRONTEND=noninteractive \
    CC=clang \
    CXX=clang++ \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:/opt/cppcheck/bin:${PATH}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        cmake \
        git \
        gnupg \
        python3 \
        python3-venv \
        wget \
    && wget -qO- https://apt.llvm.org/llvm-snapshot.gpg.key | gpg --dearmor -o /usr/share/keyrings/llvm.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/llvm.gpg] http://apt.llvm.org/noble/ llvm-toolchain-noble-${CLANG_VERSION} main" \
        > /etc/apt/sources.list.d/llvm.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        clang-${CLANG_VERSION} \
        clang-tidy-${CLANG_VERSION} \
        clang-tools-${CLANG_VERSION} \
    && python3 -m venv "${VIRTUAL_ENV}" \
    && "${VIRTUAL_ENV}/bin/pip" install --no-cache-dir PyGithub pylint \
    && ln -sf "/usr/bin/clang++-${CLANG_VERSION}" /usr/bin/clang++ \
    && ln -sf "/usr/bin/clang-${CLANG_VERSION}" /usr/bin/clang \
    && ln -sf /usr/bin/python3 /usr/bin/python \
    && rm -rf /var/lib/apt/lists/*

COPY --from=cppcheck-builder /opt/cppcheck /opt/cppcheck

WORKDIR /opt
