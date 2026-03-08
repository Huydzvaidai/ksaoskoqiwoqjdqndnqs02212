# Custom Docker image with all dependencies pre-installed
FROM ubuntu:22.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies and Python/Node in one layer
RUN apt-get update -qq && \
    apt-get install -y -qq --no-install-recommends \
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
    npm && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Install Python packages
RUN pip3 install --no-cache-dir \
    Pillow>=10.0.0 \
    requests>=2.31.0 \
    jproperties>=2.1.1 \
    pyyaml>=6.0

# Install Node packages globally using npm (more reliable than yarn)
RUN npm install -g spritesheet-js

# Set working directory
WORKDIR /workspace

# Default command
CMD ["/bin/bash"]
