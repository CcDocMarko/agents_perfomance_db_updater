from dotenv import load_dotenv
import os
import gspread

load_dotenv()

local = 'LOCAL'
prod = 'PRODUCTION'

environment = os.getenv('ENV', local)  # default to local if not specified
viciMasterFilename = os.getenv('DEV_VICI_MASTER_SH') if environment == local else os.getenv(
    'PROD_VICI_MASTER_SH')
outputBaseName = os.getenv('DEV_OUTPUT_BASENAME') if environment == local else os.getenv(
    'PROD_OUTPUT_BASENAME')
emails = os.getenv('SHARE_USER') if environment == local else os.getenv(
    'SHARE_USER_PROD')
shareUsers = emails.split(',') if emails else []
vicidialBaseURL = os.getenv('VICIDIAL_BASE_URL')
path = os.getenv('KEY_PATH') if environment == local else os.getenv(
    'KEY_PROD_PATH')

# Add more scopes here if needed
scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def authenticate():
    try:
        if path:
            return gspread.service_account(filename=path, scopes=scopes)
        raise ValueError('Credentials path for deployment not configured')
    except ValueError as err:
        print("An exception happened: " + str(err))


gc = authenticate()
