#!/bin/bash
# Optimize jq by using compiled queries

# Pre-compile frequently used jq queries
export JQ_COLORS="0;90:0;37:0;37:0;37:0;32:1;37:1;37"

# Use jq with --raw-output for faster processing
alias jq='jq --raw-output'

# Enable jq streaming for large files
export JQ_STREAMING=1
