# MoMo Transactions API

Base URL: `http://localhost:8000`

All endpoints need Basic Auth (`Authorization: Basic base64(username:password)`).
Credentials are set in `.env` (`API_USERNAME`, `API_PASSWORD`).

Transaction object:

```json
{
  "id": 1,
  "type": "incoming",
  "amount": 2000,
  "sender": "Jane Smith",
  "receiver": "me",
  "timestamp": "2024-05-10 16:30:58",
  "body": "You have received 2000 RWF from Jane Smith ..."
}
```

`type` is one of: `incoming`, `payment`, `transfer`, `deposit`, `withdrawal`, `airtime`, `other`.

---

## GET /transactions

List all transactions.

```bash
curl -u admin:change_me http://localhost:8000/transactions
```

Response `200`:

```json
[
  { "id": 1, "type": "incoming", "amount": 2000, "sender": "Jane Smith", "receiver": "me", "timestamp": "2024-05-10 16:30:58", "body": "..." },
  { "id": 2, "type": "payment", "amount": 1000, "sender": "me", "receiver": "Jane Smith", "timestamp": "2024-05-10 16:31:45", "body": "..." }
]
```

## GET /transactions/{id}

Get one transaction.

```bash
curl -u admin:change_me http://localhost:8000/transactions/1
```

Response `200`: the transaction object.
Response `404`: `{"error": "Transaction not found"}`

## POST /transactions

Add a transaction. Required fields: `type`, `amount`, `sender`, `receiver`, `timestamp`. The id is set by the server.

```bash
curl -u admin:change_me -X POST http://localhost:8000/transactions \
  -H "Content-Type: application/json" \
  -d '{"type":"transfer","amount":5000,"sender":"me","receiver":"Alex","timestamp":"2024-06-01 10:00:00"}'
```

Response `201`:

```json
{ "type": "transfer", "amount": 5000, "sender": "me", "receiver": "Alex", "timestamp": "2024-06-01 10:00:00", "id": 1692 }
```

Response `400`: `{"error": "Missing fields: ['sender']"}` or `{"error": "Invalid JSON"}`

## PUT /transactions/{id}

Update fields of a transaction. Only the fields sent are changed. `id` can't be changed.

```bash
curl -u admin:change_me -X PUT http://localhost:8000/transactions/1692 \
  -H "Content-Type: application/json" -d '{"amount":7500}'
```

Response `200`: the updated transaction.
Response `404`: `{"error": "Transaction not found"}`

## DELETE /transactions/{id}

```bash
curl -u admin:change_me -X DELETE http://localhost:8000/transactions/1692
```

Response `200`:

```json
{ "message": "Deleted", "transaction": { "id": 1692, "...": "..." } }
```

Response `404`: `{"error": "Transaction not found"}`

---

## Error codes

| Code | When |
|------|------|
| 200 | OK (GET, PUT, DELETE) |
| 201 | Created (POST) |
| 400 | Body is not valid JSON, or required fields missing |
| 401 | Missing or wrong credentials |
| 404 | Unknown path or transaction id |
