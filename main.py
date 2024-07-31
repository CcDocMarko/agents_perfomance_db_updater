from core.classes import Logger
from core.utils import yesterday
import mysql.connector as c
from helpers.helper import call_center_records, log_and_handle_errors
from mysql.connector.cursor import MySQLCursor
from decimal import Decimal
records = call_center_records()

SQL_QUERY = """
SELECT
    agent_log.agent_id,
    agent_log.full_name,
    IFNULL(log_data.total_calls, 0) AS total_calls,
    IFNULL(human_answered_data.human_answered_calls, 0) AS human_answered_calls,
    IFNULL(drop_data.drop_calls, 0) AS drop_calls,
    IFNULL(booked_data.booked_calls, 0) AS booked_calls,
    IFNULL(answering_machine_data.answering_machine_calls, 0) AS answering_machine_calls,
    IFNULL(adc_data.adc_calls, 0) AS adc_calls,
    IFNULL(wait_time_data.average_wait_sec, 0) AS average_wait_sec,
    IFNULL(total_agent_dialer.total_dialer_hrs, 0) AS total_dialer_time
FROM
    (SELECT
         DISTINCT vicidial_agent_log.user AS agent_id,
         vicidial_users.full_name
     FROM
         vicidial_agent_log
     JOIN
         vicidial_users ON vicidial_agent_log.user = vicidial_users.user
     WHERE
         vicidial_agent_log.event_time >= (SELECT CONCAT(DATE_SUB(CURDATE(), INTERVAL 1 DAY), ' 00:00:00'))
         AND vicidial_agent_log.event_time <= (SELECT CONCAT(DATE_SUB(CURDATE(), INTERVAL 1 DAY), ' 23:59:59'))
    ) AS agent_log
LEFT JOIN
    (SELECT
         vicidial_log.user AS agent_id,
         COUNT(*) AS total_calls
     FROM
         vicidial_log
     WHERE
         vicidial_log.call_date >= (SELECT CONCAT(DATE_SUB(CURDATE(), INTERVAL 1 DAY), ' 00:00:00'))
         AND vicidial_log.call_date <= (SELECT CONCAT(DATE_SUB(CURDATE(), INTERVAL 1 DAY), ' 23:59:59'))
     GROUP BY
         vicidial_log.user
    ) AS log_data ON agent_log.agent_id = log_data.agent_id
LEFT JOIN
    (SELECT
         vicidial_log.user AS agent_id,
         COUNT(*) AS human_answered_calls
     FROM
         vicidial_log
     WHERE
         vicidial_log.call_date >= (SELECT CONCAT(DATE_SUB(CURDATE(), INTERVAL 1 DAY), ' 00:00:00'))
         AND vicidial_log.call_date <= (SELECT CONCAT(DATE_SUB(CURDATE(), INTERVAL 1 DAY), ' 23:59:59'))
         AND vicidial_log.status IN (SELECT status FROM vicidial_statuses WHERE human_answered = 'Y')
     GROUP BY
         vicidial_log.user
    ) AS human_answered_data ON agent_log.agent_id = human_answered_data.agent_id
LEFT JOIN
    (SELECT
         vicidial_log.user AS agent_id,
         COUNT(*) AS drop_calls
     FROM
         vicidial_log
     WHERE
         vicidial_log.call_date >= (SELECT CONCAT(DATE_SUB(CURDATE(), INTERVAL 1 DAY), ' 00:00:00'))
         AND vicidial_log.call_date <= (SELECT CONCAT(DATE_SUB(CURDATE(), INTERVAL 1 DAY), ' 23:59:59'))
         AND vicidial_log.status = 'DROP'
     GROUP BY
         vicidial_log.user
    ) AS drop_data ON agent_log.agent_id = drop_data.agent_id
LEFT JOIN
    (SELECT
         vicidial_agent_log.user AS agent_id,
         COUNT(*) AS booked_calls
     FROM
         vicidial_agent_log
     WHERE
         vicidial_agent_log.event_time >= (SELECT CONCAT(DATE_SUB(CURDATE(), INTERVAL 1 DAY), ' 00:00:00'))
         AND vicidial_agent_log.event_time <= (SELECT CONCAT(DATE_SUB(CURDATE(), INTERVAL 1 DAY), ' 23:59:59'))
         AND vicidial_agent_log.status IN (
             SELECT status FROM vicidial_campaign_statuses WHERE sale = 'Y'
             UNION
             SELECT status FROM vicidial_statuses WHERE sale = 'Y'
         )
     GROUP BY
         vicidial_agent_log.user
    ) AS booked_data ON agent_log.agent_id = booked_data.agent_id
LEFT JOIN
    (SELECT
         vicidial_agent_log.user AS agent_id,
         COUNT(*) AS answering_machine_calls
     FROM
         vicidial_agent_log
     WHERE
         vicidial_agent_log.event_time >= (SELECT CONCAT(DATE_SUB(CURDATE(), INTERVAL 1 DAY), ' 00:00:00'))
         AND vicidial_agent_log.event_time <= (SELECT CONCAT(DATE_SUB(CURDATE(), INTERVAL 1 DAY), ' 23:59:59'))
         AND vicidial_agent_log.status = 'A'
     GROUP BY
         vicidial_agent_log.user
    ) AS answering_machine_data ON agent_log.agent_id = answering_machine_data.agent_id
LEFT JOIN
    (SELECT
         vicidial_log.user AS agent_id,
         SUM(IF(vicidial_log.status = 'ADC', 1, 0)) AS adc_calls
     FROM
         vicidial_log
     WHERE
         vicidial_log.call_date >= (SELECT CONCAT(DATE_SUB(CURDATE(), INTERVAL 1 DAY), ' 00:00:00'))
         AND vicidial_log.call_date <= (SELECT CONCAT(DATE_SUB(CURDATE(), INTERVAL 1 DAY), ' 23:59:59'))
     GROUP BY
         vicidial_log.user
    ) AS adc_data ON agent_log.agent_id = adc_data.agent_id
LEFT JOIN
    (SELECT
         vicidial_agent_log.user AS agent_id,
         AVG(vicidial_agent_log.wait_sec) AS average_wait_sec
     FROM
         vicidial_agent_log
     WHERE
         vicidial_agent_log.event_time >= (SELECT CONCAT(DATE_SUB(CURDATE(), INTERVAL 1 DAY), ' 00:00:00'))
         AND vicidial_agent_log.event_time <= (SELECT CONCAT(DATE_SUB(CURDATE(), INTERVAL 1 DAY), ' 23:59:59'))
     GROUP BY
         vicidial_agent_log.user
    ) AS wait_time_data ON agent_log.agent_id = wait_time_data.agent_id
LEFT JOIN
    (SELECT
        DISTINCT vicidial_agent_log.user AS agent_id,
        (SUM(talk_sec) + SUM(wait_sec) + SUM(pause_sec) + SUM(dispo_sec) + SUM(dead_sec)) / 3600 AS total_dialer_hrs
    FROM 
        vicidial_agent_log
    JOIN
         vicidial_users ON vicidial_agent_log.user = vicidial_users.user
    WHERE  event_time >= (SELECT CONCAT(DATE_SUB(CURDATE(), INTERVAL 1 DAY), ' 00:00:00')) AND event_time <= (SELECT CONCAT(DATE_SUB(CURDATE(), INTERVAL 1 DAY), ' 23:59:59'))
    GROUP BY 
        agent_id) AS total_agent_dialer ON agent_log.agent_id = total_agent_dialer.agent_id
"""

SQL_INSERT = """
    INSERT INTO AGENTS_PERFORMANCE_TABLE (
        call_center,
        agent_id,
        full_name,
        total_calls,
        human_answered_calls,
        drop_calls,
        booked_calls,
        answering_machine_calls,
        adc_calls,
        average_wait_sec,
        log_date,
        total_dialer_time
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

for record in records:
    cb_name = record['pr']
    cc_domain = record['Vici URL']

log_file = Logger('agents_perfomance_log.txt')


@log_and_handle_errors(log_file)
def create_db_connection(*connection_params):
    HOST, DATABASE, USER, PASSWORD = connection_params
    db_connection = c.connect(
        host=HOST,
        user=USER,
        database=DATABASE,
        password=PASSWORD
    )
    return db_connection


@log_and_handle_errors(log_file)
def execute_query(cursor: MySQLCursor, query: str):
    cursor.execute(query)
    result = cursor.fetchall()
    return result


"""
+-------------------------+--------------+------+-----+---------+----------------+
| Field                   | Type         | Null | Key | Default | Extra          |
+-------------------------+--------------+------+-----+---------+----------------+
| id                      | int(11)      | NO   | PRI | NULL    | auto_increment |
| call_center             | varchar(255) | YES  |     | NULL    |                |
| agent_id                | varchar(255) | YES  |     | NULL    |                |
| full_name               | varchar(255) | YES  |     | NULL    |                |
| total_calls             | int(11)      | YES  |     | NULL    |                |
| human_answered_calls    | int(11)      | YES  |     | NULL    |                |
| drop_calls              | int(11)      | YES  |     | NULL    |                |
| booked_calls            | int(11)      | YES  |     | NULL    |                |
| answering_machine_calls | int(11)      | YES  |     | NULL    |                |
| adc_calls               | int(11)      | YES  |     | NULL    |                |
| average_wait_sec        | float        | YES  |     | NULL    |                |
| log_date                | date         | NO   |     | NULL    |                |
| total_dialer_time       | float        | YES  |     | NULL    |                |
+-------------------------+--------------+------+-----+---------+----------------+  
"""


def map_to_table(data, call_center):
    return [
        {
            "call_center": call_center,
            "agent_id": record[0],
            "full_name": record[1],
            "total_calls": record[2],
            "human_answered_calls": record[3],
            "drop_calls": record[4],
            "booked_calls": record[5],
            "answering_machine_calls": record[6],
            "adc_calls": float(record[7]) if isinstance(record[8], Decimal) else record[8],
            "average_wait_sec": float(record[8]) if isinstance(record[8], Decimal) else record[8],
            "log_date": yesterday,
            "total_dialer_time": float(record[9])
        }
        for record in data
    ]


if __name__ == '__main__':
    db_connection = create_db_connection(
        "148.72.132.231", "asterisk", "cron", "1234")
    if not db_connection:
        log_file.append_line(
            f"Error: Failed connection to local server database")
        exit()
    cursor = db_connection.cursor()
    for record in records:
        cc_name = record['pr']
        client_db_connection = create_db_connection(
            record['Server IP'], "asterisk", "cron", "1234")
        if not client_db_connection:
            continue
        log_file.append_line(f"Succesfully connected to {cc_name} asterisk db")
        client_cursor = client_db_connection.cursor()
        agents_performance = execute_query(client_cursor, SQL_QUERY)
        mapped_records = map_to_table(agents_performance, cc_name)
        for record in mapped_records:
            cursor.execute(SQL_INSERT, (
                record['call_center'],
                record['agent_id'],
                record['full_name'],
                record['total_calls'],
                record['human_answered_calls'],
                record['drop_calls'],
                record['booked_calls'],
                record['answering_machine_calls'],
                record['adc_calls'],
                record['average_wait_sec'],
                record['log_date'],
                record['total_dialer_time']
            ))
        db_connection.commit()
    print(f"client {record['Server IP']} agent logs were created!")
