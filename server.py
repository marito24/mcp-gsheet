from mcp.server.fastmcp import FastMCP

from googleapiclient.errors import HttpError

from gsheet_service import gsheet_service

mcp = FastMCP("Google Sheets Controller")


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
        service = gsheet_service()
        sheet_metadata = (
            service.spreadsheets()
            .get(spreadsheetId=spreadsheet_id, fields="sheets.properties.title")
            .execute()
        )
        sheets = sheet_metadata.get("sheets", [])
        titles = [sheet.get("properties", {}).get("title", "") for sheet in sheets]
        return titles
    except HttpError as err:
        if err.resp.status == 404:
            return [f"Error: Spreadsheet not found with ID: {spreadsheet_id}"]
        else:
            return [f"Error listing sheets: {str(err)}"]
    except Exception as e:
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
        service = gsheet_service()
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range_name)
            .execute()
        )
        values = result.get("values", [])
        return [[str(cell) for cell in row] for row in values]
    except HttpError as err:
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
            return [[f"Error reading cells: {str(err)}"]]
    except Exception as e:
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
        service = gsheet_service()
        body = {"values": values}
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
        updated_range = result.get("updatedRange")
        updated_cells = result.get("updatedCells")
        return (
            f"Successfully updated {updated_cells} cells " f"in range {updated_range}."
        )

    except HttpError as err:
        if err.resp.status == 404:
            return f"Error: Spreadsheet not found with ID: {spreadsheet_id}"
        elif err.resp.status == 400:
            error_details = err.content.decode("utf-8")
            if "Unable to parse range" in error_details:
                return (
                    f"Error: Invalid range '{range_name}'. Ensure it includes "
                    f"sheet name (e.g., 'Sheet1!A1') or is valid for "
                    f"the first sheet."
                )
            else:
                return f"Error writing cells (Bad Request): {error_details}"
        else:
            return f"Error writing cells: {str(err)}"
    except Exception as e:
        return f"Unexpected error writing cells: {str(e)}"


if __name__ == "__main__":
    print("Starting Google Sheets MCP Server...")
    print("Ensure GOOGLE_APPLICATION_CREDENTIALS environment variable is set.")
    mcp.run(transport="stdio")
