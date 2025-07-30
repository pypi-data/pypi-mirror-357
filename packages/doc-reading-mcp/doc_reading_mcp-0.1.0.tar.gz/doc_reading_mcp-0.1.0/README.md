**Use Case: Document Reading Tool**

The goal is to have a tool that can read and edit files, using Cursor or Claude Desktop.

The `filesystem` MCP already allows reading, writing and editing documents, but is limited in that it cannot:

- Read pdfs or docx files
- Reads the full document, which can cause context overflow

To address these issues, we create:

- A fresh `doc-reading-mcp` mcp service allowing for document conversions between pdf, docx and markdown.


# Doc Reading and Converter MCP Server

## Features

- PDF to Markdown conversion using marker-pdf
- DOCX to Markdown conversion using pandoc
- Markdown to DOCX conversion using pandoc
- Markdown to PDF conversion using pandoc

## Prerequisites

- Python 3.10 or higher
- [pandoc] (https://pandoc.org/installing.html) installed on your system
- [uv] (https://docs.astral.sh/uv/) for Python package management 

If you were running with pip, you would:

```bash
python -m venv docEnv
source docEnv/bin/activate
pip install .
python -m doc_reading_mcp
```

To run the package with uv:
```bash
uv run -m doc_reading_mcp
```

## Running the server

Run the server using the inspector:
```bash
npx @modelcontextprotocol/inspector uv run -m doc_reading_mcp
```
This starts the server with the MCP Inspector UI, which is helpful for testing and debugging.

Run in Cursor/Windsurf/Claude using the following configuration:
```json
    "doc-reading-mcp": {
        "command": "uv",
        "args": [
            "--directory",
            "/absolute/path/to/mffrydman/doc-reading-mcp",
            "run",
            "-m",
            "doc_reading_mcp"
        ]
    }
```

Replace"
- `/absolute/path/to/` with the actual path on your system.

## Installing as a package from Github

You can go much faster by using `uvx` and just running:
```bash
uvx git+https://github.com/mffrydman/doc-reading-mcp
```
to run the service.

Configure your MCP client:
````json
{
    "mcpServers": {
        "doc-reading-mcp": {
            "command": "uvx",
            "args": [
                "git+https://github.com/mffrydman/doc-reading-mcp",
            ]
        }
    }
}