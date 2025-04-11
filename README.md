# MCP Google Sheets Server

This project provides a Model Context Protocol (MCP) server that allows interaction with Google Sheets.

It exposes tools to:

- List sheets (tabs) within a spreadsheet.
- Read data from specific cell ranges.
- Write data to specific cell ranges.

It explicitly **does not** provide tools for managing Google Drive files (listing, creating, deleting folders/files). Access is restricted to spreadsheet content only.

## Prerequisites

1.  **Python 3.8+**
2.  **Google Cloud Project:** You need a Google Cloud project with the Google Sheets API enabled.
3.  **Service Account Key:**
    - Go to the Google Cloud Console -> APIs & Services -> Credentials.
    - Create a new Service Account.
    - Grant this service account the "Editor" role (or a more restrictive custom role) for the Google Sheets you want to access.
    - Download the service account key file (JSON format).
    - **Important:** Share the specific Google Sheet(s) you want to control with the service account's email address (found in the JSON key file or the Cloud Console).

## Setup

1.  **Clone the repository (or copy the files).**

2.  **Set up Google Credentials:**

    - Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the _absolute path_ of your downloaded service account JSON key file.

    ```bash
    export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
    ```

    - Alternatively, you can place the key file in a standard location recognized by the Google Cloud client libraries (not recommended for shared environments).

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    _Note: You might want to use a virtual environment (`venv`) to keep dependencies isolated._
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

## Running the Server

Use the `mcp` command-line tool (installed as part of `mcp-sdk`) to run the server:

```bash
mcp run gsheet_mcp_server.py
```

The server will start and listen for MCP requests over standard input/output (stdio).

## MCP Tools Provided

- **`list_sheets(spreadsheet_id: str) -> list[str]`**: Lists the names of all sheets in the specified spreadsheet.
- **`read_cells(spreadsheet_id: str, range_name: str) -> list[list[str]]`**: Reads data from the given range (e.g., `'Sheet1!A1:B5'`).
- **`write_cells(spreadsheet_id: str, range_name: str, values: list[list[str]]) -> str`**: Writes the provided 2D list of values to the specified starting cell/range (e.g., `'Sheet1!C1'`).
