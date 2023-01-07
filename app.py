import random
import pygsheets
import os
from flask import url_for, redirect, Flask, render_template, request

app = Flask(__name__)

# Set the environment variable for the service account key file
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/runner/Python/credential.json'

# Load the service account key file and authorize pygsheets to access the Google Sheets API
random_number = random.randint(1, 10)

gc = pygsheets.authorize(service_file='/home/runner/Python/credential.json')

SPREADSHEET_ID = "1-bjMr6J96uGQ6Nu8_VsQJclMyVcf1ovPxE8e4VCPwxs"

RANGE_NAME = f"B{random_number}"

@app.route('/', methods=['GET'])
def index():
    # Retrieve the value of the cell from the Google Sheet
    value = get_cell_value(SPREADSHEET_ID, RANGE_NAME)
    # Render the template and pass the value of the cell and range name to it
    return render_template('index.html', cell_value=value, cell_range=RANGE_NAME)

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
        sh = gc.open_by_key(SPREADSHEET_ID)
        # Select the specified range of cells
        values = sh[0].get_values(start=range_name, end=range_name, returnas='cell')
        # Return the cell value
        return values[0][0].value
    except Exception as e:
        print(f'An error occurred: {e}')
        return None

@app.route('/', methods=['POST'])
def handle_form_submission():
    # Retrieve the text from the form submission
    text = request.form['text']
    # Retrieve the selected cell range
    selected_cell_range = request.form['selected_cell_range']
    # Open the Google Sheet using pygsheets
    sh = gc.open_by_key(SPREADSHEET_ID)
    # Select the first sheet in the spreadsheet
    worksheet = sh[0]
    # Find the row of the selected cell
    row = int(selected_cell_range[1:])
    # Find the next empty cell in the row
    for col in range(2, worksheet.cols):
        col = int(col)
        cell = worksheet.cell((row, col))
        if cell.value == "":
            cell.value = text
            break
    # Save the updated cell
    worksheet.update_cells(cell)
  
    # Redirect to the index page
    return redirect(url_for('thank_you'))

@app.route('/thank_you')
def thank_you():
  return render_template('thank_you.html')
  
if __name__ == '__main__':
    app.run(host = '0.0.0.0')
