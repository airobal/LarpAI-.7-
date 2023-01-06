import pygsheets
import os
from flask import Flask, render_template, request

app = Flask(__name__)

# Set the environment variable for the service account key file
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/runner/Python/credential.json'

# Load the service account key file and authorize pygsheets to access the Google Sheets API
gc = pygsheets.authorize(service_file='/home/runner/Python/credential.json')

SPREADSHEET_ID = "1-bjMr6J96uGQ6Nu8_VsQJclMyVcf1ovPxE8e4VCPwxs"
RANGE_NAME = "B2"

@app.route('/', methods=['GET'])
def index():
    # Retrieve the value of the cell from the Google Sheet
    value = get_cell_value(SPREADSHEET_ID, RANGE_NAME)
    # Render the template and pass the value of the cell to it
    return render_template('index.html', cell_value=value)

def get_cell_value(spreadsheet_id, range_name):
    """
    Retrieve the value of a cell from a Google Sheet.
    
    Parameters:
        spreadsheet_id (str): The ID of the Google Sheet.
        range_name (str): The range of cells to retrieve.
    
    Returns:
        str: The value of the cell.
    """
    try:
        # Open the Google Sheet using pygsheets
        sh = gc.open_by_key(spreadsheet_id)
        # Select the specified range of cells
        values = sh[0].get_values(start=range_name, end=range_name, returnas='cell')
        # Return the cell value
        return values[0][0].value
    except Exception as e:
        print(f'An error occurred: {e}')
        return None

if __name__ == '__main__':
  app.run(host='0.0.0.0')