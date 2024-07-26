from datetime import date, timedelta, datetime

def today():
    return date.today()

yesterday = today() - timedelta(days=1)

def convertIntoDate(dateString: str):
    return datetime.strptime(dateString, "%Y-%m-%d")

def worksheetDate(dateToFormat: date):
    return dateToFormat.strftime("%d-%b-%Y")

def nameTitle(userTitle: str):
    return f'{userTitle} {yesterday.strftime("%b-%Y")}'

def set_filter_criterias(criterias: list):
    def filterRecords(record):
        for key, criteria in criterias:
            if record[key] == criteria:
                return False
        return True
    return filterRecords
