# Custom Docker image with all dependencies pre-installed
FROM ubuntu:22.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update -qq && \
    apt-get install -y -qq \
    moreutils \
    zip \
    unzip \
    imagemagick \
    curl \
    wget \
    git \
    jq \
    python3 \
    python3-pip \
    nodejs \
    npm \
    yarn && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 install --no-cache-dir \
    Pillow \
    requests \
    jproperties \
    pyyaml

# Install Node packages globally
RUN yarn global add spritesheet-js

# Set working directory
WORKDIR /workspace

# Default command
CMD ["/bin/bash"]
