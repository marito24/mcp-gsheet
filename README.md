# MCP Google Sheets Server

This project provides a Model Context Protocol (MCP) server that allows interaction with Google Sheets.

It exposes tools to:

- List sheets (tabs) within a spreadsheet.
- Read data from specific cell ranges.
- Write data to specific cell ranges.

It explicitly **does not** provide tools for managing Google Drive files (listing, creating, deleting folders/files). Access is restricted to spreadsheet content only.

## Prerequisites

1.  **Python 3.11+**
2.  **Google Cloud Project with the Google Sheets API enabled**
3.  **Service Account Key:**
    - Go to the Google Cloud Console and create a new Service Account.
    - Download the service account key file (JSON format).
    - Grant this service account the "Editor" role for the Google Sheets you want to access.

## How to use

1.  **Clone the repository.**

    ```bash
    git clone https://github.com/shionhonda/mcp-gsheet.git
    ```

2.  **Set up Google Credentials:**

    - Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the _absolute path_ of your downloaded service account JSON key file.

    ```bash
    export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
    ```

    - Alternatively, you can place the key file in a standard location recognized by the Google Cloud client libraries (not recommended for shared environments).

3.  **Install Dependencies:**

    ```bash
    uv venv
    source .venv/bin/activate
    ```

4.  Run the Server

    To develop the server with MCP Inspector:

    ```bash
    mcp dev server.py
    ```

    To run the server:

    ```bash
    mcp run server.py
    ```

    The server will start and listen for MCP requests over standard input/output (stdio).

## Claude Desktop

Add the following to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "gsheet": {
      "command": "/path/to/uv",
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/your/service-account-key.json"
      },
      "args": ["--directory", "/path/to/mcp-gsheet", "run", "server.py"]
    }
  }
}
```

## MCP Tools Provided

- **`list_sheets(spreadsheet_id: str) -> list[str]`**: Lists the names of all sheets in the specified spreadsheet.
- **`read_cells(spreadsheet_id: str, range_name: str) -> list[list[str]]`**: Reads data from the given range (e.g., `'Sheet1!A1:B5'`).
- **`write_cells(spreadsheet_id: str, range_name: str, values: list[list[str]]) -> str`**: Writes the provided 2D list of values to the specified starting cell/range (e.g., `'Sheet1!C1'`).
