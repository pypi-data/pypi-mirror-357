# gleaner

A simple web scraper that finds all the pages on a domain using breadth-first search.

## Installation

```bash
pipx install gleaner
```

## Usage

```bash
glean https://example.com -o output.txt
```

This will

- Start at given URL
- Search through HTML to find pages on the same domain
- Follow those links and repeat the process
- Save all discovered URLs to output.txt

## Options

- `-o, --output` - Output file (default: `urls.txt`)

## Limitations

- Only follows `<a>`-tag links
- No rate limiting
