# Name shall be setup by environment

from collections import namedtuple

vici_master = {
    'header': [
        'pr',	'SSH',	'Password', 'DynaPortal URL', 'Vici URL',	'Vici Admin User',
        'Pass',	'Server IP', 'Signalmash',
        'Tiltx',	'Ionos',	'Ovh',	'Namecheap',
        'Mysql', 'Changed',	'Dynoportal', 'Activate Report',	'Live Date',
    ],
    'worksheet': 'Log In'
}

excluding_criteria_for_viciMaster = [
    ('Server IP', ''),
    ('Activate Report', 'N'),
    ('Activate Report', ''),
]

DBCredentials = namedtuple(
    'Credentials', 'callCenter host user database password')
