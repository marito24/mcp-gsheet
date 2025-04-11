import os

from mcp.server.fastmcp import FastMCP
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- Configuration ---
# See: https://docs.gspread.org/en/latest/oauth2.html
# Service account key path expected in GOOGLE_APPLICATION_CREDENTIALS env var
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# --- MCP Server Setup ---
mcp = FastMCP("Google Sheets Controller")


# --- Google Sheets Client Setup ---
def get_sheets_service():
    """Builds and returns an authorized Google Sheets API service object."""
    if not SERVICE_ACCOUNT_FILE:
        raise ValueError(
            "Environment variable GOOGLE_APPLICATION_CREDENTIALS is not set."
        )
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(
            f"Service account key file not found at: {SERVICE_ACCOUNT_FILE}"
        )

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(
        filename=SERVICE_ACCOUNT_FILE, scopes=scopes
    )

    try:
        service = build(
            serviceName="sheets",
            version="v4",
            credentials=creds,
            static_discovery=False,
        )
        return service
    except HttpError as err:
        print(f"Error building Sheets service: {err}")
        raise


# Lazy initialization of the service
_sheets_service = None


def sheets_service():
    """Returns a cached Sheets service object, initializing if needed."""
    global _sheets_service
    if _sheets_service is None:
        _sheets_service = get_sheets_service()
    return _sheets_service


# --- MCP Tools for Google Sheets ---


@mcp.tool(
    name="list_sheets",
    description="Lists all sheets (tabs) in a specific Google Spreadsheet.",
)
def list_sheets(spreadsheet_id: str) -> list[str]:
    """Lists the names of all sheets in the spreadsheet.

    Args:
        spreadsheet_id: The ID of the Google Spreadsheet.

    Returns:
        A list of sheet names (strings).
    """
    try:
        service = sheets_service()
        # Call the Sheets API
        sheet_metadata = (
            service.spreadsheets()
            # Get only sheet titles
            .get(
                spreadsheetId=spreadsheet_id, fields="sheets.properties.title"
            ).execute()
        )
        sheets = sheet_metadata.get("sheets", [])
        # Extract titles, handling potential missing properties
        titles = [sheet.get("properties", {}).get("title", "") for sheet in sheets]
        return titles
    except HttpError as err:
        # Handle API errors
        if err.resp.status == 404:
            return [f"Error: Spreadsheet not found with ID: {spreadsheet_id}"]
        else:
            return [f"Error listing sheets: {str(err)}"]
    except Exception as e:
        # General error handling
        return [f"Error listing sheets: {str(e)}"]


@mcp.tool(
    name="read_cells",
    description="Reads data from a specified range in a Google Sheet.",
)
def read_cells(spreadsheet_id: str, range_name: str) -> list[list[str]]:
    """Reads data from a specified cell range (e.g., 'Sheet1!A1:B2').

    Args:
        spreadsheet_id: The ID of the Google Spreadsheet.
        range_name: The A1 notation of the range to read
            (e.g., 'Sheet1!A1:C5').

    Returns:
        A 2D list of strings representing the cell values.
    """
    try:
        service = sheets_service()
        # Call the Sheets API
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range_name)
            .execute()
        )
        values = result.get("values", [])
        # Ensure all inner elements are lists for consistent typing, even empty rows
        # and convert all cell values to strings
        return [[str(cell) for cell in row] for row in values]
    except HttpError as err:
        # Handle API errors
        if err.resp.status == 404:
            return [[f"Error: Spreadsheet not found with ID: {spreadsheet_id}"]]
        elif "Unable to parse range" in str(err):
            return [
                [
                    f"Error: Invalid range '{range_name}'.",
                    "Ensure it includes sheet name (e.g., 'Sheet1!A1:B2')",
                    "or is valid for the first sheet.",
                ]
            ]
        else:
            # Catch-all for other HTTP errors during read
            return [[f"Error reading cells: {str(err)}"]]
    except Exception as e:
        # General error handling
        # Ensure the return type matches the function signature (list[list[str]])
        return [[f"Unexpected error reading cells: {str(e)}"]]


@mcp.tool(
    name="write_cells",
    description=("Writes data to a specified range in a Google Sheet."),
)
def write_cells(spreadsheet_id: str, range_name: str, values: list[list[str]]) -> str:
    """Writes data to a specified cell range (e.g., 'Sheet1!A1').

    Args:
        spreadsheet_id: The ID of the Google Spreadsheet.
        range_name: The A1 notation of the starting cell for the write
            (e.g., 'Sheet1!A1').
        values: A 2D list of strings containing the data to write.

    Returns:
        A confirmation message or an error string.
    """
    try:
        service = sheets_service()
        body = {"values": values}
        # Call the Sheets API
        result = (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",  # Interprets input as if typed by user
                body=body,
            )
            .execute()
        )
        # result contains information like updatedCells, updatedRange, etc.
        updated_range = result.get("updatedRange")
        updated_cells = result.get("updatedCells")
        return (
            f"Successfully updated {updated_cells} cells " f"in range {updated_range}."
        )

    except HttpError as err:
        # Handle API errors
        if err.resp.status == 404:
            return f"Error: Spreadsheet not found with ID: {spreadsheet_id}"
        elif err.resp.status == 400:
            # More specific error for bad range or data
            error_details = err.content.decode("utf-8")
            if "Unable to parse range" in error_details:
                return (
                    f"Error: Invalid range '{range_name}'. Ensure it includes "
                    f"sheet name (e.g., 'Sheet1!A1') or is valid for "
                    f"the first sheet."
                )
            else:
                # More specific error from API content
                return f"Error writing cells (Bad Request): {error_details}"
        else:
            # Catch-all for other HTTP errors during write
            return f"Error writing cells: {str(err)}"
    except Exception as e:
        # General error handling
        return f"Unexpected error writing cells: {str(e)}"


# --- Run the Server ---
if __name__ == "__main__":
    # This allows running the server directly using
    # `python gsheet_mcp_server.py` or using the mcp command:
    # `mcp run gsheet_mcp_server.py`
    # The server will be available via stdio
    print("Starting Google Sheets MCP Server...")
    print("Ensure GOOGLE_APPLICATION_CREDENTIALS environment variable is set.")
    # The mcp.run() command needs to be invoked via the mcp CLI runner
    # This __main__ block is primarily for informational purposes when run
    # directly.
    pass
