# Building and Securing a REST API – Team 8 Report

Team: Olivier Dusabamahoro, Daniel Kenny Kamanzi, Divin Manzi Mulinda Elvis

## 1. Introduction to API security

Our API gives apps access to MoMo SMS transactions. These contain names, amounts and
balances, so only allowed clients should read or change them. We used Basic
Authentication on every endpoint. Requests with missing or wrong credentials get
`401 Unauthorized`. The username and password are read from `.env`, not written in the code.

## 2. Endpoints

Full docs with examples: `docs/api_docs.md`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /transactions | List all transactions |
| GET | /transactions/{id} | Get one transaction |
| POST | /transactions | Add a transaction |
| PUT | /transactions/{id} | Update a transaction |
| DELETE | /transactions/{id} | Delete a transaction |

Error codes: 400 (bad JSON or missing fields), 401 (bad credentials), 404 (not found).

## 3. DSA comparison

`dsa/search.py` finds transactions by id in two ways:

- Linear search: goes through the list one by one, O(n).
- Dictionary lookup: `{id: transaction}`, uses hashing, O(1) on average.

Each result is the average time per lookup over 20 random ids, repeated 1000 times.

| Records | Linear search (µs) | Dict lookup (µs) | Speedup |
|---------|-------------------|------------------|---------|
| 20 | 2.19 | 0.21 | 10x |
| 100 | 5.93 | 0.28 | 21x |
| 500 | 43.02 | 0.26 | 167x |
| 1000 | 57.57 | 0.20 | 286x |
| 1691 (all) | 126.46 | 0.20 | 632x |

(From `python dsa/search.py` on the full dataset of 1691 records. Exact numbers change a bit each run.)

Linear search time grows with the number of records. Dictionary lookup time stays flat at about 0.2 µs.

**Why is the dictionary faster?** Linear search has to compare ids one by one, so it gets
slower as the list grows. A dictionary hashes the id and jumps straight to the right slot,
so the time stays about the same no matter how many records there are.

**Other options:** A binary search on a list sorted by id would be O(log n). A balanced BST
or B-tree (which databases use for indexes) is also O(log n) and supports range queries,
for example all transactions between two dates, which a dictionary can't do.

## 4. Limitations of Basic Auth

- Credentials are only base64 encoded, not encrypted. Anyone who sees the traffic can decode
  them, so without HTTPS they are exposed.
- The password is sent with every request, which gives more chances for it to leak.
- There is no expiry or logout. A stolen password works until it's changed.
- There are no roles or scopes. Every user has full access to everything.

**Better options:**

- **JWT:** the user logs in once and gets a signed token that expires. The server checks the
  signature and doesn't need the password again.
- **OAuth2:** access is given through tokens with scopes (for example read-only) and
  refresh tokens. The client never sees the user's password.
- Always use HTTPS, whatever auth method is used.

## 5. Testing

We tested with curl and Postman. Screenshots are in `screenshots/`:

- GET with correct credentials (200)
- Request with wrong credentials (401)
- POST (201), PUT (200), DELETE (200)
