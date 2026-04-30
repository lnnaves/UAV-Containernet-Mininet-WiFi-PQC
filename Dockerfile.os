FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y \
    build-essential cmake ninja-build git libssl-dev pkg-config
ENV CC=gcc CXX=g++
WORKDIR /build
RUN git clone --depth 1 --branch main https://github.com/open-quantum-safe/liboqs.git \
    && cd liboqs && mkdir build && cd build \
    && cmake -GNinja -DOQS_USE_OPENSSL=ON .. && ninja install

FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libssl3 \
    git \
    iproute2 \
    iputils-ping \
    net-tools \
    iw \
    batctl \
    ebtables \
    kmod \
    procps \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/include /usr/local/include
COPY --from=builder /usr/local/lib /usr/local/lib
RUN ldconfig

RUN pip install --no-cache-dir setuptools \
    && pip install --no-cache-dir git+https://github.com/open-quantum-safe/liboqs-python.git

WORKDIR /app
COPY . /app

CMD ["python", "main.py"]