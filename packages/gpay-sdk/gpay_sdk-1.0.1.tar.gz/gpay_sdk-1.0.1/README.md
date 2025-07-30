# gpay-api-client

A Python client library for the GPay API.

## Official GPay API Documentation

For full API details, see the [GPay API Documentation](https://gpay.ly/banking/doc/index.html).

## Installation

```bash
pip install gpay-sdk
```

## Usage

### Import and Create the Client

```python
from gpay.gpay_api_client import GPayApiClient, BaseUrl

# client: GPayApiClient
client = GPayApiClient(
    api_key='your_api_key',
    secret_key='your_secret_key',
    password='your_password',
    base_url=BaseUrl.STAGING  # or BaseUrl.PRODUCTION
)
```

### Get Wallet Balance

```python
# type: Balance
balance = client.get_balance()  
print(balance.balance, balance.response_time)
```

### Create a Payment Request

```python
# type: PaymentRequest
payment_request = client.create_payment_request(amount='100.00', reference_no='INV-123', description='Invoice Payment')  
print(payment_request.request_id, payment_request.amount)
```

### Check Payment Status

```python
# type: PaymentStatus
status = client.check_payment_status(request_id=payment_request.request_id)  
print(status.is_paid, status.transaction_id)
```

### Send Money

```python
# type: SendMoneyResult
send_result = client.send_money(amount='50.00', wallet_gateway_id='recipient_wallet_id', 
description='Gift', reference_no='GIFT-001')  
print(send_result.transaction_id, send_result.new_balance)
```

### Get Day Statement

```python
# type: Statement
statement = client.get_day_statement(date='2025-06-22')  
print(statement.day_balance)
for tx in statement.day_statement:
    # tx: StatementTransaction
    print(tx.transaction_id, tx.amount)
```

### Check Wallet

```python
 # type: WalletCheck
wallet_info = client.check_wallet(wallet_gateway_id='recipient_wallet_id') 
print(wallet_info.exists, wallet_info.wallet_name)
```

### Get Outstanding Transactions

```python
# type: OutstandingTransactions
outstanding = client.get_outstanding_transactions()  
print(outstanding.outstanding_credit, outstanding.outstanding_debit)
for tx in outstanding.outstanding_transactions:
    # tx: OutstandingTransaction
    print(tx.transaction_id, tx.amount)
```
