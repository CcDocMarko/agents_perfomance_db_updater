from typing import Any, Callable, Optional, TypeVar
import mysql.connector as c
from core import classes, config
from core.const import vici_master, excluding_criteria_for_viciMaster
from core.utils import set_filter_criterias


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