# NTH-Bank

Simple, secure banking backend built with FastAPI.

## Features

* User Registration
* User Authentication (JWT)
* Account Management
* Money Transfers
* Transaction History
* Rate Limiting
* Secure API Endpoints

## Project Structure

```text
NTH-Bank
├── .vscode
│   └── settings.json
├── models
│   ├── auth
│   │   ├── login.py
│   │   ├── register.py
│   │   ├── user.py
│   │   └── _Test.py
│   ├── bank
│   │   ├── account.py
│   │   ├── me.py
│   │   ├── transaction.py
│   │   └── transfer.py
│   ├── databases
│   │   └── database.py
│   └── security
│       ├── deps.py
│       ├── jwt.py
│       └── ratelimiter.py
├── .env
└── main.py
```

## Authentication

The API uses JWT authentication.

Example login request:

```json
{
  "username": "admin",
  "password": "password"
}
```

Example response:

```json
{
  "success": true,
  "token": "jwt_token_here",
  "user": {
    "id": 1,
    "username": "admin"
  },
  "balance": 1000.00
}
```

## Installation

```bash
git clone https://github.com/yourusername/NTH-Bank.git

cd NTH-Bank

pip install -r requirements.txt

python main.py
```

## Run

```bash
uvicorn main:app --reload
```
