import random
import pygsheets
import os
from flask import url_for, redirect, Flask, render_template, request, session
from flask_session import Session

os.environ[
  'GOOGLE_APPLICATION_CREDENTIALS'] = '/home/runner/Python/credential.json'

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

@app.route('/logout')
def logout():
  # Remove the user's session data
  session.pop('logged_in', None)
  session.pop('email', None)
  session.pop('password', None)
  # Redirect the user to the welcome page
  return redirect(url_for('welcome'))

@app.route('/', methods=['GET'])
def welcome():
    return render_template('welcome.html')

@app.route('/terms_and_conditions', methods=['POST'])
def accept_terms_and_conditions():
    # Start a new session for the user
    session['logged_in'] = True
    # Redirect the user to the login page
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
  # Check if the user is already logged in
  if session.get('logged_in'):
    # Redirect the user to the dashboard page
    return redirect(url_for('dashboard'))

  if request.method == 'POST':
    # Retrieve the form data
    email = request.form['email']
    password = request.form['password']

    # Check if the entered email and password are valid
    if valid_login(email, password):
      # Create a session for the user
      session['logged_in'] = True
      session['email'] = email
      # Redirect the user to the dashboard page
      return redirect(url_for('dashboard'))
    else:
      # Display an error message
      error = 'Invalid email or password'
      return render_template('login.html', error=error)
  else:
    # Render the login template
    return render_template('login.html')

def valid_login(email, password):
  """
  Check if the provided email and password match the values in cells A1 and B2.

  Parameters:
    email (str): The email to check.
    password (str): The password to check.

  Returns:
    bool: True if the email and password match the values in cells A1 and B2, False otherwise.
  """
  # Set the environment variable for the service account key file
  os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/runner/Python/credential.json'

  # Load the service account key file and authorize pygsheets to access the Google Sheets API
  gc = pygsheets.authorize(service_file='/home/runner/Python/credential.json')

  # Open the Google Sheet using pygsheets
  sh = gc.open_by_key('1iHMPBMIcR9Xr6r2_er3MdG-q8sNiAdsgW5epnaPw_fo')

  # Select the first worksheet in the sheet
  worksheet = sh[0]

  # Read the data from cells A1 and B2
  cell_a2 = worksheet.cell('A2').value
  cell_b2 = worksheet.cell('B2').value

  # Check if the provided email and password match the values in cells A1 and B2
  if email == cell_a2 and password == cell_b2:
    return True

  return False


@app.route('/signup', methods=['GET', 'POST'])
def signup():
  if request.method == 'POST':
    # retrieve the form data
    email = request.form['email']
    password = request.form['password']

    # check if the email is already in use
    if email_in_use(email):
      # render the signup template with an error message
      return render_template('signup.html', error='Email already in use')
    else:
      # add the email and password to the Google Sheet
      add_credentials(email, password)
      # create a session for the user
      session['logged_in'] = True
      session['email'] = email
      session['password'] = password
      # redirect the user to the dashboard page
      return redirect(url_for('dashboard'))
  else:
    # render the signup template
    return render_template('signup.html')
    
def email_in_use(email):
  """
  Check if the specified email is already in use.

  Parameters:
      email (str): The email address to check.

  Returns:
      bool: True if the email is already in use, False otherwise.
  """
  # Load the service account key file and authorize pygsheets to access the Google Sheets API
  gc = pygsheets.authorize(service_file='/home/runner/Python/credential.json')

  # Open the Google Sheet using pygsheets
  sh = gc.open_by_key('1iHMPBMIcR9Xr6r2_er3MdG-q8sNiAdsgW5epnaPw_fo')

  # Select the first worksheet in the sheet
  worksheet = sh[0]

  # Retrieve the list of email addresses from the sheet
  email_column = worksheet.get_col(1)

  # Check if the specified email is in the list
  if email in email_column:
    return True
  else:
    return False

def add_credentials(email, password):
  # Load the service account key file and authorize pygsheets to access the Google Sheets API
  gc = pygsheets.authorize(service_file='/home/runner/Python/credential.json')

  # Open the Google Sheet using pygsheets
  sh = gc.open_by_key('1iHMPBMIcR9Xr6r2_er3MdG-q8sNiAdsgW5epnaPw_fo')

  # Select the first sheet in the spreadsheet
  worksheet = sh[0]

  # Update cell A2 with the email
  cell_a2 = worksheet.cell((2, 1))
  cell_a2.value = email
  
  # Update cell B2 with the password
  cell_b2 = worksheet.cell((2, 2))
  cell_b2.value = password

  # Save the updated cells
  worksheet.update_cells([cell_a2, cell_b2])

@app.route('/dashboard', methods=['GET'])
def dashboard():
  # Check if the user is logged in
  if 'logged_in' not in session:
    # Redirect the user to the login page
    return redirect(url_for('login'))

  # Retrieve the email of the logged in user from the session
  email = session['email']

  # Get the user's information from the Google Sheet
  email = get_user_info()

  # Get the number of arguments that the user has submitted
  num_arguments = get_num_arguments(email)

  # Render the template and pass the user's information and number of arguments to it
  return render_template('dashboard.html',
                         email=email,
                         num_arguments=num_arguments)
def get_user_info():
  """
  Retrieve the user's email address from the session.

  Returns:
    str: The email address of the user.
  """
  return session['email']

def get_num_arguments(email):
  """
    Get the number of arguments that the user has submitted.
    
    Parameters:
        email (str): The email of the user.
    
    Returns:
        int: The number of arguments that the user has submitted.
    """

  # Load the service account key file and authorize pygsheets to access the Google Sheets API
  gc = pygsheets.authorize(service_file='/home/runner/Python/credential.json')

  # Open the Google Sheet using pygsheets
  sh = gc.open_by_key('SHEET_ID')

  # Select the second worksheet in the sheet
  worksheet = sh[1]

  # Read all of the data from the sheet
  data = worksheet.get_all_values()

  # Initialize a counter for the number of arguments
  counter = 0

  # Iterate through the rows in the sheet
  for row in data:
    # Check if the email in the row matches the user's email
    if row[0] == email:
      # Increment the counter
      counter += 1

  # Return the total number of arguments that the user has submitted
  return counter


@app.route('/argue_prompt', methods=['GET'])
def argue_prompt():
  # Retrieve the value of the cell from the Google Sheet
  value = get_cell_value(SPREADSHEET_ID, RANGE_NAME)
  # Render the template and pass the value of the cell and range name to it
  return render_template('argue_prompt.html',
                         cell_value=value,
                         cell_range=RANGE_NAME)


# Load the service account key file and authorize pygsheets to access the Google Sheets API
random_number = random.randint(1, 10)

gc = pygsheets.authorize(service_file='/home/runner/Python/credential.json')

SPREADSHEET_ID = "1-bjMr6J96uGQ6Nu8_VsQJclMyVcf1ovPxE8e4VCPwxs"

RANGE_NAME = f"B{random_number}"


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
    values = sh[0].get_values(start=range_name,
                              end=range_name,
                              returnas='cell')
    # Return the cell value
    return values[0][0].value
  except Exception as e:
    print(f'An error occurred: {e}')
    return None


@app.route('/argue_prompt', methods=['POST'])
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
  return redirect(url_for('dashboard'))

  # add "go to my dashboard button next"


if __name__ == '__main__':
  app.run(host='0.0.0.0')
