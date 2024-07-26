import datetime
import os
import re
from typing import Union
import gspread


class SpreadSheetMetadata():
    __metadata: dict = {}

    def __init__(self, name: str, targetWsKeys: Union[dict, None]) -> None:
        self.__metadata = targetWsKeys.copy() if targetWsKeys else {}
        self.__metadata["name"] = name

    def getInfo(self) -> dict:
        return self.__metadata

    def verify(self, header) -> bool:
        if not len(header):
            return True

        for value in header:
            if not value:
                continue
            if not value in self.__metadata["header"]:
                return False
        return True


class GoogleSpreadSheet(SpreadSheetMetadata):
    _sh: gspread.Spreadsheet
    _worksheet: gspread.Worksheet

    def __init__(self, name: str, targetWsKeys: Union[dict, None], gc: gspread.Client) -> None:
        super().__init__(name, targetWsKeys)
        self._sh = gc.open(name)
        # Skip if worksheet header verification is not provided
        if not targetWsKeys:
            return
        wsTitle = self.getInfo()["worksheet"]
        if isinstance(wsTitle, str):
            self._worksheet = self._sh.worksheet(wsTitle)
        elif isinstance(wsTitle, int):
            self._worksheet = self._sh.get_worksheet(wsTitle)
        self.verify(self._worksheet.row_values(1))

    def setup_sharing(sh: gspread.Spreadsheet, shareUsers) -> None:
        for user in shareUsers:
            sh.share(user, perm_type='user', role='writer')
        sh.share('ccdocs.com', perm_type='domain', role='reader')

    def spreadsheet(self):
        return self._sh

    def selected_worksheet(self):
        return self._worksheet

    def createBlank(name: str, gc: gspread.Client) -> gspread.Spreadsheet:
        sh = gc.create(name)
        return sh

    def reorder_worksheets(self):
        worksheets = self._sh.worksheets()
        valid_worksheets = []
        for ws in worksheets:
            try:
                datetime.datetime.strptime(ws.title, "%d-%b-%Y")
                valid_worksheets.append(ws)
            except ValueError:
                self._sh.del_worksheet(ws)

        sorted_worksheets = sorted(
            valid_worksheets, key=lambda ws: datetime.datetime.strptime(ws.title, "%d-%b-%Y"), reverse=True)

        self._sh.reorder_worksheets(sorted_worksheets)

        return sorted_worksheets


class URLBuilder():
    _domain: str

    def __init__(self, domain: str) -> None:
        # remove http protocol to properly assign the domain name
        domainPattern = r'https?://([\w.-]+)'
        try:
            matches = re.search(domainPattern, domain)
            if not matches:
                raise (f"Domain not found for the provided string: {domain}")
            domain = matches.group(1)
            self._domain = domain
        except Exception as e:
            print("Error:", e)

    def get_domain(self):
        return self._domain

    def add_admin_pass(self, username: str, password: str):
        self._domain = f'{username}:{password}@{self._domain}'

    def build_url(self, path, f_arg, *args):
        url = f'https://{self._domain}/{path}?{f_arg}'
        for arg in args:
            url += f'&{arg}'
        return url


class Logger:
    def __init__(self, filename: str):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
        logs_dir = os.path.join(src_dir, 'logs')
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        self.filename = os.path.join(logs_dir, filename)
        self.read_or_create_file()
        self.append_line('\n')
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.append_line(
            f"*****************Log Report: {timestamp}*****************\n")

    def read_or_create_file(self):
        if os.path.exists(self.filename):
            # File exists, so read its contents
            with open(self.filename, 'r') as file:
                self.contents = file.read()
        else:
            # File doesn't exist, so create a new one
            self.contents = ''
            with open(self.filename, 'w') as file:
                pass

    def append_line(self, line: str):
        with open(self.filename, 'a') as file:
            file.write(line + '\n')
