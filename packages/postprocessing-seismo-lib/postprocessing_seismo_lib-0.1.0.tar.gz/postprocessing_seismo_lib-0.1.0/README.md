# postprocessing_seismo_lib

`postprocessing_seismo_lib` is a lightweight Python library for building and parsing structured API messages, especially for use with nested JSON structures used in event-based data systems.

## Features

- Build a full message with metadata and body using `build_message`
- Extract the `body` section from a structured JSON file using `extract_body_from_file`

## Installation

You can install the library locally for development:

```bash
pip install -e .