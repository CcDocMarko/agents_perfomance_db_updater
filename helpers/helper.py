from typing import Any, Callable, Optional, TypeVar
import mysql.connector as c
from core import classes, config
from core.const import vici_master, excluding_criteria_for_viciMaster
from core.utils import yesterday, worksheetDate, set_filter_criterias
from gspread import Worksheet

rows = "200"
cols = "20"

# Define a type variable for the function type
F = TypeVar('F', bound=Callable[..., Any])


def call_center_records() -> list:
    vici_master_sh = classes.GoogleSpreadSheet(
        config.viciMasterFilename, vici_master, config.gc)
    filter_vicimaster_records = set_filter_criterias(
        excluding_criteria_for_viciMaster)
    allRecords = vici_master_sh.selected_worksheet().get_all_records()
    call_center_records = list(filter(filter_vicimaster_records, allRecords))
    return call_center_records


def get_formatted_worksheet(filename: str, cc_name: str) -> Worksheet:
    log_new_sh_creation = f'A new spreadsheet has been created for {cc_name}'
    try:
        gs_ss = classes.GoogleSpreadSheet(filename, None, config.gc)
        sh = gs_ss.spreadsheet()
    except:
        classes.GoogleSpreadSheet.createBlank(filename, config.gc)
        gs_ss = classes.GoogleSpreadSheet(filename, None, config.gc)
        sh = gs_ss.spreadsheet()
        classes.GoogleSpreadSheet.setup_sharing(sh, config.shareUsers)
        print(log_new_sh_creation)
    worksheet = sh.add_worksheet(title=worksheetDate(
        yesterday), rows=rows, cols=cols)
    gs_ss.reorder_worksheets()
    return worksheet


def log_and_handle_errors(logger: classes.Logger) -> Callable[[F], F]:
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                logger.append_line(
                    f"Success: {func.__name__} executed successfully.")
                return result
            except Exception as e:
                logger.append_line(f"Error in {func.__name__}: {str(e)}")
                print(f"Error while executing {func.__name__}: {str(e)}")
                return None
        return wrapper
    return decorator


def establish_connection(host: str) -> Optional[c.MySQLConnection]:
    try:
        HOST = host
        DATABASE = "asterisk"
        USER = "cron"
        PASSWORD = "1234"
        db_connection = c.connect(
            host=HOST, user=USER, database=DATABASE, password=PASSWORD)
        print("Connected to:", HOST)
        return db_connection
    except Exception as e:
        print("Connection Failed for", HOST)
        raise


def execute_queries(cursor: any) -> dict:
    results = {}
    try:
        cursor.execute("SELECT campaign_id FROM vicidial_campaigns")
        campaign_ids = cursor.fetchall()
        results['campaign_ids'] = [row[0] for row in campaign_ids]

        cursor.execute("SELECT user_group FROM vicidial_user_groups")
        user_groups = cursor.fetchall()
        results['user_groups'] = [row[0] for row in user_groups]

    except Exception as e:
        raise  # This will ensure the decorator catches and logs the exception.

    return results


def parse_params_from_execute_queries(results: list) -> tuple:
    campaign_id_params = ()
    user_group_params = ()
    for campaign_id in results['campaign_ids']:
        campaign_id_params = campaign_id_params + f"group[]={campaign_id}"
    for user_group in results['user_groups']:
        user_group_params = user_group_params + f"user_group[]={user_group}"

    return {
        'campaign_ids': campaign_id_params,
        'user_groups': user_group_params
    }
