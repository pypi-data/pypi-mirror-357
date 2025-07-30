# gpay/response_models.py
"""
Descriptive response classes for GPay API endpoints.
"""
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class Balance:
    """
    Represents the wallet balance response.

    Attributes:
        balance (Decimal): The current available balance in LYD.
        response_time (datetime): The response timestamp as a datetime object.
    """
    def __init__(self, balance: str, response_timestamp: str):
        """
        Args:
            balance (str): The current available balance as a string.
            response_timestamp (str): The response timestamp in milliseconds since epoch.
        """
        self.balance = Decimal(balance)
        self.response_time = datetime.fromtimestamp(int(response_timestamp) / 1000)

    def __str__(self):
        return f"Balance(balance={self.balance}, response_time={self.response_time})"

class PaymentRequest:
    """
    Represents a payment request response.

    Attributes:
        requester_username (str): The username of the requester.
        request_id (str): The unique ID for the payment request.
        request_time (str): The timestamp of the request in milliseconds since epoch.
        amount (Decimal): The amount requested.
        reference_no (Optional[str]): The reference number provided in the request, if any.
        response_time (datetime): The response timestamp as a datetime object.
    """
    def __init__(self, requester_username: str, request_id: str, request_time: str, amount: str, reference_no: Optional[str], response_timestamp: str):
        """
        Args:
            requester_username (str): The username of the requester.
            request_id (str): The unique ID for the payment request.
            request_time (str): The timestamp of the request in milliseconds since epoch.
            amount (str): The amount requested as a string.
            reference_no (Optional[str]): The reference number provided in the request, if any.
            response_timestamp (str): The response timestamp in milliseconds since epoch.
        """
        self.requester_username = requester_username
        self.request_id = request_id
        self.request_time = request_time
        self.amount = Decimal(amount)
        self.reference_no = reference_no
        self.response_time = datetime.fromtimestamp(int(response_timestamp) / 1000)

    def __str__(self):
        return (f"PaymentRequest(requester_username={self.requester_username}, request_id={self.request_id}, "
                f"request_time={self.request_time}, amount={self.amount}, reference_no={self.reference_no}, "
                f"response_time={self.response_time})")

class PaymentStatus:
    """
    Represents the status of a payment request.

    Attributes:
        request_id (str): The unique ID of the payment request.
        transaction_id (Optional[str]): The transaction ID if payment is completed.
        amount (Decimal): The requested amount.
        payment_timestamp (Optional[str]): The payment timestamp if completed.
        reference_no (Optional[str]): The reference number provided in the request.
        description (str): The description provided in the request.
        is_paid (bool): Indicates whether the payment is completed.
        response_time (datetime): The response timestamp as a datetime object.
    """
    def __init__(self, request_id: str, transaction_id: Optional[str], amount: str, payment_timestamp: Optional[str], reference_no: Optional[str], description: str, is_paid: bool, response_timestamp: str):
        """
        Args:
            request_id (str): The unique ID of the payment request.
            transaction_id (Optional[str]): The transaction ID if payment is completed.
            amount (str): The requested amount as a string.
            payment_timestamp (Optional[str]): The payment timestamp if completed.
            reference_no (Optional[str]): The reference number provided in the request.
            description (str): The description provided in the request.
            is_paid (bool): Indicates whether the payment is completed.
            response_timestamp (str): The response timestamp in milliseconds since epoch.
        """
        self.request_id = request_id
        self.transaction_id = transaction_id
        self.amount = Decimal(amount)
        self.payment_timestamp = payment_timestamp
        self.reference_no = reference_no
        self.description = description
        self.is_paid = is_paid
        self.response_time = datetime.fromtimestamp(int(response_timestamp) / 1000)

    def __str__(self):
        return (f"PaymentStatus(request_id={self.request_id}, transaction_id={self.transaction_id}, amount={self.amount}, "
                f"payment_timestamp={self.payment_timestamp}, reference_no={self.reference_no}, description={self.description}, "
                f"is_paid={self.is_paid}, response_time={self.response_time})")

class SendMoneyResult:
    """
    Represents the result of a send money operation.

    Attributes:
        amount (Decimal): The amount sent.
        sender_fee (Decimal): The fee charged to the sender.
        transaction_id (str): The unique ID for the transaction.
        old_balance (Decimal): The balance before the transaction.
        new_balance (Decimal): The balance after the transaction.
        timestamp (str): The timestamp of the transaction.
        reference_no (Optional[str]): The reference number provided in the request.
        response_time (datetime): The response timestamp as a datetime object.
    """
    def __init__(self, amount: str, sender_fee: str, transaction_id: str, old_balance: str, new_balance: str, timestamp: str, reference_no: Optional[str], response_timestamp: str):
        """
        Args:
            amount (str): The amount sent as a string.
            sender_fee (str): The fee charged to the sender as a string.
            transaction_id (str): The unique ID for the transaction.
            old_balance (str): The balance before the transaction as a string.
            new_balance (str): The balance after the transaction as a string.
            timestamp (str): The timestamp of the transaction.
            reference_no (Optional[str]): The reference number provided in the request.
            response_timestamp (str): The response timestamp in milliseconds since epoch.
        """
        self.amount = Decimal(amount)
        self.sender_fee = Decimal(sender_fee)
        self.transaction_id = transaction_id
        self.old_balance = Decimal(old_balance)
        self.new_balance = Decimal(new_balance)
        self.timestamp = timestamp
        self.reference_no = reference_no
        self.response_time = datetime.fromtimestamp(int(response_timestamp) / 1000)

    def __str__(self):
        return (f"SendMoneyResult(amount={self.amount}, sender_fee={self.sender_fee}, transaction_id={self.transaction_id}, "
                f"old_balance={self.old_balance}, new_balance={self.new_balance}, timestamp={self.timestamp}, "
                f"reference_no={self.reference_no}, response_time={self.response_time})")

class StatementTransaction:
    """
    Represents a transaction in a wallet statement.

    Attributes:
        transaction_id (str): The unique ID of the transaction.
        datetime (str): The date and time of the transaction.
        timestamp (str): The timestamp of the transaction.
        description (str): The description of the transaction.
        amount (Optional[Decimal]): The amount of the transaction.
        balance (Optional[Decimal]): The balance after the transaction.
        reference_no (Optional[str]): The reference number associated with the transaction.
        op_type_id (int): The operation type ID.
        status (int): The status of the transaction.
        created_at (str): The timestamp when the transaction was created.
    """
    def __init__(self, transaction_id: str, datetime_: str, timestamp: str, description: str, amount: Optional[str], balance: Optional[str], reference_no: Optional[str], op_type_id: int, status: int, created_at: str):
        """
        Args:
            transaction_id (str): The unique ID of the transaction.
            datetime_ (str): The date and time of the transaction.
            timestamp (str): The timestamp of the transaction.
            description (str): The description of the transaction.
            amount (Optional[str]): The amount of the transaction as a string, or None.
            balance (Optional[str]): The balance after the transaction as a string, or None.
            reference_no (Optional[str]): The reference number associated with the transaction.
            op_type_id (int): The operation type ID.
            status (int): The status of the transaction.
            created_at (str): The timestamp when the transaction was created.
        """
        self.transaction_id = transaction_id
        self.datetime = datetime_
        self.timestamp = timestamp
        self.description = description
        self.amount = Decimal(amount) if amount is not None else None
        self.balance = Decimal(balance) if balance is not None else None
        self.reference_no = reference_no
        self.op_type_id = op_type_id
        self.status = status
        self.created_at = created_at

    def __str__(self):
        return (f"StatementTransaction(transaction_id={self.transaction_id}, datetime={self.datetime}, timestamp={self.timestamp}, "
                f"description={self.description}, amount={self.amount}, balance={self.balance}, reference_no={self.reference_no}, "
                f"op_type_id={self.op_type_id}, status={self.status}, created_at={self.created_at})")

class Statement:
    """
    Represents a wallet statement for a specific day.

    Attributes:
        available_balance (Decimal): The available balance at the time of the request.
        outstanding_credit (Decimal): The total outstanding credit.
        outstanding_debit (Decimal): The total outstanding debit.
        day_balance (Decimal): The balance at the end of the given day.
        day_total_in (Decimal): The total credited on the given day.
        day_total_out (Decimal): The total debited on the given day.
        response_time (datetime): The response timestamp as a datetime object.
        day_statement (List[StatementTransaction]): The list of transactions for the given day.
    """
    def __init__(self, available_balance: str, outstanding_credit: str, outstanding_debit: str, day_balance: str, day_total_in: str, day_total_out: str, response_timestamp: str, day_statement: List[StatementTransaction]):
        """
        Args:
            available_balance (str): The available balance at the time of the request as a string.
            outstanding_credit (str): The total outstanding credit as a string.
            outstanding_debit (str): The total outstanding debit as a string.
            day_balance (str): The balance at the end of the given day as a string.
            day_total_in (str): The total credited on the given day as a string.
            day_total_out (str): The total debited on the given day as a string.
            response_timestamp (str): The response timestamp in milliseconds since epoch.
            day_statement (List[StatementTransaction]): The list of transactions for the given day.
        """
        self.available_balance = Decimal(available_balance)
        self.outstanding_credit = Decimal(outstanding_credit)
        self.outstanding_debit = Decimal(outstanding_debit)
        self.day_balance = Decimal(day_balance)
        self.day_total_in = Decimal(day_total_in)
        self.day_total_out = Decimal(day_total_out)
        self.response_time = datetime.fromtimestamp(int(response_timestamp) / 1000)
        self.day_statement = day_statement

    def __str__(self):
        return (f"Statement(available_balance={self.available_balance}, outstanding_credit={self.outstanding_credit}, "
                f"outstanding_debit={self.outstanding_debit}, day_balance={self.day_balance}, day_total_in={self.day_total_in}, "
                f"day_total_out={self.day_total_out}, response_time={self.response_time}, "
                f"day_statement=[{', '.join(str(tx) for tx in self.day_statement)}])")

class WalletCheck:
    """
    Represents the result of checking a wallet.

    Attributes:
        exists (bool): Whether the wallet exists.
        wallet_gateway_id (str): The wallet gateway ID.
        wallet_name (Optional[str]): The name of the wallet.
        user_account_name (Optional[str]): The user account name.
        can_receive_money (bool): Whether the wallet can receive money.
        response_time (datetime): The response timestamp as a datetime object.
    """
    def __init__(self, exists: bool, wallet_gateway_id: str, wallet_name: Optional[str], user_account_name: Optional[str], can_receive_money: bool, response_timestamp: str):
        """
        Args:
            exists (bool): Whether the wallet exists.
            wallet_gateway_id (str): The wallet gateway ID.
            wallet_name (Optional[str]): The name of the wallet.
            user_account_name (Optional[str]): The user account name.
            can_receive_money (bool): Whether the wallet can receive money.
            response_timestamp (str): The response timestamp in milliseconds since epoch.
        """
        self.exists = exists
        self.wallet_gateway_id = wallet_gateway_id
        self.wallet_name = wallet_name
        self.user_account_name = user_account_name
        self.can_receive_money = can_receive_money
        self.response_time = datetime.fromtimestamp(int(response_timestamp) / 1000)

    def __str__(self):
        return (f"WalletCheck(exists={self.exists}, wallet_gateway_id={self.wallet_gateway_id}, wallet_name={self.wallet_name}, "
                f"user_account_name={self.user_account_name}, can_receive_money={self.can_receive_money}, response_time={self.response_time})")

class OutstandingTransaction:
    """
    Represents an outstanding transaction.

    Attributes:
        transaction_id (str): The unique ID of the transaction.
        datetime (str): The date and time of the transaction.
        timestamp (str): The timestamp of the transaction.
        description (str): The description of the transaction.
        amount (Optional[Decimal]): The amount of the transaction.
        balance (Optional[Decimal]): The balance after the transaction.
        reference_no (Optional[str]): The reference number associated with the transaction.
        op_type_id (int): The operation type ID.
        status (int): The status of the transaction.
        created_at (str): The timestamp when the transaction was created.
    """
    def __init__(self, transaction_id: str, datetime_: str, timestamp: str, description: str, amount: Optional[str], balance: Optional[str], reference_no: Optional[str], op_type_id: int, status: int, created_at: str):
        """
        Args:
            transaction_id (str): The unique ID of the transaction.
            datetime_ (str): The date and time of the transaction.
            timestamp (str): The timestamp of the transaction.
            description (str): The description of the transaction.
            amount (Optional[str]): The amount of the transaction as a string, or None.
            balance (Optional[str]): The balance after the transaction as a string, or None.
            reference_no (Optional[str]): The reference number associated with the transaction.
            op_type_id (int): The operation type ID.
            status (int): The status of the transaction.
            created_at (str): The timestamp when the transaction was created.
        """
        self.transaction_id = transaction_id
        self.datetime = datetime_
        self.timestamp = timestamp
        self.description = description
        self.amount = Decimal(amount) if amount is not None else None
        self.balance = Decimal(balance) if balance is not None else None
        self.reference_no = reference_no
        self.op_type_id = op_type_id
        self.status = status
        self.created_at = created_at

    def __str__(self):
        return (f"OutstandingTransaction(transaction_id={self.transaction_id}, datetime={self.datetime}, timestamp={self.timestamp}, "
                f"description={self.description}, amount={self.amount}, balance={self.balance}, reference_no={self.reference_no}, "
                f"op_type_id={self.op_type_id}, status={self.status}, created_at={self.created_at})")

class OutstandingTransactions:
    """
    Represents a list of outstanding transactions.

    Attributes:
        outstanding_credit (Decimal): The total outstanding credit.
        outstanding_debit (Decimal): The total outstanding debit.
        response_time (datetime): The response timestamp as a datetime object.
        outstanding_transactions (List[OutstandingTransaction]): The list of outstanding transactions.
    """
    def __init__(self, outstanding_credit: str, outstanding_debit: str, response_timestamp: str, outstanding_transactions: List[OutstandingTransaction]):
        """
        Args:
            outstanding_credit (str): The total outstanding credit as a string.
            outstanding_debit (str): The total outstanding debit as a string.
            response_timestamp (str): The response timestamp in milliseconds since epoch.
            outstanding_transactions (List[OutstandingTransaction]): The list of outstanding transactions.
        """
        self.outstanding_credit = Decimal(outstanding_credit)
        self.outstanding_debit = Decimal(outstanding_debit)
        self.response_time = datetime.fromtimestamp(int(response_timestamp) / 1000)
        self.outstanding_transactions = outstanding_transactions

    def __str__(self):
        return (f"OutstandingTransactions(outstanding_credit={self.outstanding_credit}, outstanding_debit={self.outstanding_debit}, "
                f"response_time={self.response_time}, outstanding_transactions=[{', '.join(str(tx) for tx in self.outstanding_transactions)}])")
