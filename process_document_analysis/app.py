import json
import logging
import os
import re
from datetime import datetime

import boto3
import psycopg2

logger = logging.getLogger()
logger.setLevel("INFO")

s3_client = boto3.client("s3")

due_date_tags = ["Payment Due Date"]
amount_tags = ["Total Amout Due"]
HOST = os.getenv("POSTGRES_EC2_INSTANCE_HOST_DNS")
USER = os.getenv("POSTGRES_EC2_INSTANCE_USER")
PASSWORD = os.getenv("POSTGRES_EC2_INSTANCE_PASSWORD")
DATABASE = os.getenv("POSTGRES_EC2_INSTANCE_DATABASE")


def lambda_handler(event, context):
    invoice_analyses_bucket_name = event["invoice_analyses_bucket_name"]
    invoice_analyses_bucket_key = event["invoice_analyses_bucket_key"]
    response = s3_client.get_object(
        Bucket=invoice_analyses_bucket_name, Key=invoice_analyses_bucket_key
    )
    body = json.loads(response["Body"].read().decode("utf-8"))
    key_map, value_map, block_map = get_kv_map(body["Blocks"])
    kvs = get_kv_relationship(key_map, value_map, block_map)
    lines = get_line_list(body["Blocks"])
    logger.info("\n\n== FOUND KEY : VALUE pairs ===\n")
    print_kvs(kvs)
    logger.info("\n\n== LINES ===\n")
    print_lines(lines)

    payment_info = {}
    payment_info["payee_name"] = get_payee_name(lines)
    payment_info["amount"] = get_amount(kvs, lines)
    payment_info["due_date"] = get_due_date(kvs)
    payment_info["memo"] = get_memo(kvs)
    payment_info["invoice_key"] = event["job_name"]
    event["payment_info"] = payment_info

    conn = psycopg2.connect(
        database=DATABASE, user=USER, password=PASSWORD, host=HOST, port="5432"
    )
    conn.autocommit = True
    cursor = conn.cursor()
    query = f"""  
        insert into invoices (invoice_key, invoice_desc, due_date, name, amount)
        values ('{payment_info['invoice_key']}', '{payment_info['memo']}{payment_info['due_date']}', '{payment_info['due_date']}', '{payment_info['payee_name']}', {payment_info['amount'].replace(',', '.')})
        """
    cursor.execute(query)

    return event


def get_kv_map(blocks):
    key_map = {}
    value_map = {}
    block_map = {}
    for block in blocks:
        block_id = block["Id"]
        block_map[block_id] = block
        if block["BlockType"] == "KEY_VALUE_SET":
            if "KEY" in block["EntityTypes"]:
                key_map[block_id] = block
            else:
                value_map[block_id] = block
    return key_map, value_map, block_map


def get_kv_relationship(key_map, value_map, block_map):
    kvs = {}
    for block_id, key_block in key_map.items():
        value_block = find_value_block(key_block, value_map)
        key = get_text(key_block, block_map)
        val = get_text(value_block, block_map)
        kvs[key] = val
    return kvs


def find_value_block(key_block, value_map):
    for relationship in key_block["Relationships"]:
        if relationship["Type"] == "VALUE":
            for value_id in relationship["Ids"]:
                value_block = value_map[value_id]
    return value_block


def get_text(result, blocks_map):
    text = ""
    if "Relationships" in result:
        for relationship in result["Relationships"]:
            if relationship["Type"] == "CHILD":
                for child_id in relationship["Ids"]:
                    word = blocks_map[child_id]
                    if word["BlockType"] == "WORD":
                        text += word["Text"] + " "
                    if word["BlockType"] == "SELECTION_ELEMENT":
                        if word["SelectionStatus"] == "SELECTED":
                            text += "X "
    return text


def print_kvs(kvs):
    for key, value in kvs.items():
        logger.info(key, ":", value)


def search_value(kvs, search_key):
    for key, value in kvs.items():
        if re.search(search_key, key, re.IGNORECASE):
            return value


def get_line_list(blocks):
    line_list = []
    for block in blocks:
        if block["BlockType"] == "LINE":
            if "Text" in block:
                line_list.append(block["Text"])
    return line_list


def print_lines(lines):
    for line in lines:
        logger.info(line)


def get_payee_name(lines):
    payee_name = ""
    payable_to = "payable to"
    payee_lines = [line for line in lines if payable_to in line.lower()]
    if len(payee_lines) > 0:
        payee_line = payee_lines[0]
        payee_line = payee_line.strip()
        pos = payee_line.lower().find(payable_to)
        if pos > -1:
            payee_line = payee_line[pos + len(payable_to) :]
            if payee_line[0:1] == ":":
                payee_line = payee_line[1:]
            payee_name = payee_line.strip()
    return payee_name


def get_amount(kvs, lines):
    amount = None
    amounts = [
        search_value(kvs, amount_tag)
        for amount_tag in amount_tags
        if search_value(kvs, amount_tag) is not None
    ]
    if len(amounts) > 0:
        amount = amounts[0]
    else:
        for idx, line in enumerate(lines):
            if line.lower() in amount_tags:
                amount = lines[idx + 1]
                break
    if amount is not None:
        amount = amount.strip()
        if amount[0:1] == "$":
            amount = amount[1:]
    return amount


def get_due_date(kvs):
    due_date = None
    due_dates = [
        search_value(kvs, due_date_tag)
        for due_date_tag in due_date_tags
        if search_value(kvs, due_date_tag) is not None
    ]
    if len(due_dates) > 0:
        due_date = due_dates[0]
    if due_date is not None:
        date_parts = due_date.split("/")
        if len(date_parts) == 3:
            due_date = datetime(
                int(date_parts[2]), int(date_parts[0]), int(date_parts[1])
            ).isoformat()
        else:
            date_parts = [
                date_part
                for date_part in re.split("\s+|,", due_date)
                if len(date_part) > 0
            ]
            if len(date_parts) == 3:
                datetime_object = datetime.strptime(date_parts[0], "%b")
                month_number = datetime_object.month
                due_date = datetime(
                    int(date_parts[2]), int(month_number), int(date_parts[1])
                ).isoformat()
    else:
        due_date = datetime.now().isoformat()
    return due_date


def get_memo(kvs):
    memo = None
    account_number = search_value(kvs, "account number")
    if account_number is not None:
        memo = " ".join(("Account Number:", account_number))
    return memo


if __name__ == "__main__":
    results = lambda_handler(
        {},
        None,
    )
