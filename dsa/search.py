# Compare linear search vs dictionary lookup for finding a transaction by id
import json
import os
import random
import time

from parse_xml import JSON_FILE


def linear_search(records, tx_id):
    for r in records:
        if r["id"] == tx_id:
            return r
    return None


def dict_lookup(table, tx_id):
    return table.get(tx_id)


def measure(func, data, ids, repeat=1000):
    start = time.perf_counter()
    for _ in range(repeat):
        for tx_id in ids:
            func(data, tx_id)
    return (time.perf_counter() - start) / (repeat * len(ids))


if __name__ == "__main__":
    with open(JSON_FILE, encoding="utf-8") as f:
        records = json.load(f)

    table = {r["id"]: r for r in records}

    # check both give the same answer
    for r in records[:20]:
        assert linear_search(records, r["id"]) == dict_lookup(table, r["id"])

    print(f"Total records: {len(records)}")
    print(f"{'n':>6} | {'linear (us)':>12} | {'dict (us)':>10} | speedup")
    sizes = sorted({n for n in (20, 100, 500, 1000) if n < len(records)} | {len(records)})
    for n in sizes:
        subset = records[:n]
        sub_table = {r["id"]: r for r in subset}
        ids = random.sample([r["id"] for r in subset], 20)
        lin = measure(linear_search, subset, ids) * 1e6
        dic = measure(dict_lookup, sub_table, ids) * 1e6
        print(f"{n:>6} | {lin:>12.3f} | {dic:>10.3f} | {lin / dic:.0f}x")
