# Parse modified_sms_v2.xml into a list of dicts and save it as JSON
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XML_FILE = os.path.join(ROOT, "data", "modified_sms_v2.xml")
JSON_FILE = os.path.join(ROOT, "data", "transactions.json")


def get_type(body):
    b = body.lower()
    if "received" in b:
        return "incoming"
    if "airtime" in b:
        return "airtime"
    if "bank deposit" in b or "deposit" in b:
        return "deposit"
    if "withdrawn" in b or "withdraw" in b:
        return "withdrawal"
    if "transferred to" in b or "sent" in b:
        return "transfer"
    if "payment" in b:
        return "payment"
    return "other"


def get_amount(body):
    # first number followed by RWF is the transaction amount
    m = re.search(r"([\d,]+)\s*RWF", body)
    if m:
        return int(m.group(1).replace(",", ""))
    return 0


def get_parties(body, tx_type, address):
    sender, receiver = address, "me"
    m = re.search(r"from ([A-Za-z ]+?)\s*\(", body)
    if tx_type == "incoming" and m:
        sender = m.group(1).strip()
    m = re.search(r"(?:to|transferred to) ([A-Za-z ]+?)\s*(?:\(|\d|has been)", body)
    if tx_type in ("payment", "transfer", "airtime") and m:
        sender, receiver = "me", m.group(1).strip()
    return sender, receiver


def get_timestamp(sms):
    ms = sms.get("date")
    if ms and ms.isdigit():
        return datetime.fromtimestamp(int(ms) / 1000).strftime("%Y-%m-%d %H:%M:%S")
    return sms.get("readable_date", "")


def parse(xml_file=XML_FILE):
    tree = ET.parse(xml_file)
    records = []
    for i, sms in enumerate(tree.getroot().findall("sms"), start=1):
        body = sms.get("body", "")
        tx_type = get_type(body)
        sender, receiver = get_parties(body, tx_type, sms.get("address", ""))
        records.append({
            "id": i,
            "type": tx_type,
            "amount": get_amount(body),
            "sender": sender,
            "receiver": receiver,
            "timestamp": get_timestamp(sms),
            "body": body,
        })
    return records


def save(records, json_file=JSON_FILE):
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else XML_FILE
    data = parse(path)
    save(data)
    print(f"Parsed {len(data)} records -> {JSON_FILE}")
    if data:
        print(json.dumps(data[0], indent=2))
