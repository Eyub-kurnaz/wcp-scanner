# WCP Scanner

A lightweight, modular prototype for exploring Web Cache Poisoning (WCP) attack surfaces.

Version: v0.1.0

## Overview

WCP Scanner is an early-stage CLI tool that helps with:

- target crawling
- HTML and JavaScript URL discovery
- candidate filtering
- basic categorization
- cache hint detection from response headers
- attack request generation
- limited attack execution with baseline / attack / validation comparison
- TXT and JSON report output

This project is currently focused on building a clean, extensible architecture for future WCP research and testing.

## Current Features

- Recursive crawl with configurable depth and page limits
- HTML-based URL extraction
- JavaScript-based URL discovery
- URL normalization and filtering
- Candidate selection for likely scan-worthy targets
- URL categorization:
  - page
  - asset
  - api
  - auth
  - marketing
  - environment
  - unknown
- Cache hint detection using known response headers such as:
  - X-Cache
  - CF-Cache-Status
  - X-Cache-Status
  - X-Cache-Lookup
  - X-Rack-Cache
  - X-Proxy-Cache
  - Cache-Status
- Attack modules:
  - forwarded_headers
  - auth_headers
- Balanced attack sample selection
- 3-request validation model:
  - baseline request
  - attack request
  - validation request
- Report output:
  - .txt
  - .json

## Requirements

Tested with:

- Python 3.12+

Python dependencies used in the current prototype:

aiohttp
selectolax

If you want to create a requirements.txt, a minimal version for the current state can be:

aiohttp
selectolax

## Installation

Clone the repository and create a virtual environment.

### Windows PowerShell

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install aiohttp selectolax

### Linux / macOS

python3 -m venv .venv
source .venv/bin/activate
pip install aiohttp selectolax

## Usage

Basic usage:

python main.py --url https://example.com

With crawl options:

python main.py --url https://bbc.com --max-depth 1 --max-pages 10

With report output:

python main.py --url https://bbc.com --max-depth 1 --max-pages 10 -o reports/bbc.txt

JSON output:

python main.py --url https://bbc.com --max-depth 1 --max-pages 10 -o reports/bbc.json

## CLI Options

- --url
  Target URL to scan. Required.

- --timeout
  HTTP timeout in seconds. Default: 10

- --concurrency
  Maximum concurrent HTTP requests. Default: 10

- --max-depth
  Maximum crawl depth. Default: 1

- --max-pages
  Maximum number of pages to crawl. Default: 10

- -o, --output
  Output report path. Supported extensions:
  - .txt
  - .json

## Current Execution Model

For each selected attack request, the validator currently uses a 3-request model:

1. baseline request
2. attack request
3. validation request

This is used to check whether a mutated request causes a visible response difference, and whether that difference appears to persist across a follow-up validation request.

At the current stage, this is still a heuristic validation model, not a full exploitation framework.

## Output

### Console Output

The scanner currently prints:

- crawl summary
- cache hint details
- discovered URL samples
- scan candidate samples
- generated attack request samples
- selected attack execution sample
- execution results

### TXT Report

The TXT report contains:

- target
- summary
- crawled pages
- sample discovered URLs
- sample scan candidates
- execution results

### JSON Report

The JSON report contains structured data for:

- target
- summary
- crawled pages
- discovered URLs
- scan candidates
- execution results

## Notes

- This is v0.1.0, an initial prototype focused on architecture and extensibility.
- Many heuristics are intentionally conservative or simplified.
- Discovery is intentionally broader than attack execution.
- Not every discovered URL is a scan candidate.
- Cache hints are informational and should not be treated as proof of cache behavior on their own.

## Planned Improvements

Some likely next steps include:

- proxy support for Burp Suite inspection
- better category-aware execution policies
- additional attack modules
- stronger diff heuristics
- improved cache validation logic
- richer reporting
- rate limiting / batching strategies
- output cleanup and result prioritization

## Disclaimer

Use only on systems you are authorized to test.
This tool is intended for legitimate security research and testing in approved environments.
