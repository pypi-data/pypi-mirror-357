# GPay API Python Client Library
# Equivalent to the Node.js implementation in GpayApiClient.node.js

import base64
import hashlib
import hmac
import json
import os
import time
import requests
from typing import Dict, Any, Optional
from enum import Enum
from .response_models import (
    Balance, PaymentRequest, PaymentStatus, SendMoneyResult, Statement, StatementTransaction, WalletCheck, OutstandingTransaction, OutstandingTransactions
)

class HashTokenGenerator:
    @staticmethod
    def generate_salt() -> str:
        return base64.b64encode(os.urandom(32)).decode('utf-8')

    @staticmethod
    def generate_hash_token(salt: str, password: str) -> str:
        return f"{salt}{password}"

class VerificationHashGenerator:
    @staticmethod
    def generate_verification_hash(hash_token: str, parameters: Dict[str, Any], secret_key: str) -> str:
        # Sort parameters by key, use empty string for None, include all keys (even if optional and not provided)
        sorted_params = sorted(parameters.items())

        def _format_value(v):
            if isinstance(v, bool):
                return "true" if v else "false"
            return "" if v is None else str(v)
        
        query_string = '&'.join(f"{k}={_format_value(v)}" for k, v in sorted_params)
        verification_string = f"{hash_token}{query_string}"
        hmac_hash = hmac.new(secret_key.encode('utf-8'), verification_string.encode('utf-8'), hashlib.sha256).digest()
        return base64.b64encode(hmac_hash).decode('utf-8')

class BaseUrl(Enum):
    STAGING = 'https://gpay-staging.libyaguide.net/banking/api/onlinewallet/v1'
    PRODUCTION = 'https://gpay.ly/banking/api/onlinewallet/v1'

class GPayApiClient:
    """
    GPayApiClient provides a client for interacting with the GPay Payment API.
    It handles authentication, request signing, response verification, and parsing of all supported endpoints.

    Args:
        api_key (str): The API key for authentication.
        secret_key (str): The secret key for signing requests.
        password (str): The password for hash token generation.
        base_url (BaseUrl): The base URL enum value (BaseUrl.STAGING or BaseUrl.PRODUCTION).
        language (str, optional): The language for the response (default: 'en').
    """
    def __init__(self, api_key: str, secret_key: str, password: str, base_url: BaseUrl, language: str = 'en'):
        """
        Initializes the GPayApiClient.

        Args:
            api_key (str): The API key for authentication.
            secret_key (str): The secret key for signing requests.
            password (str): The password for hash token generation.
            base_url (BaseUrl): The base URL enum value (BaseUrl.STAGING or BaseUrl.PRODUCTION).
            language (str, optional): The language for the response (default: 'en').
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.password = password
        if not isinstance(base_url, BaseUrl):
            raise ValueError('base_url must be an instance of BaseUrl enum')
        self.base_url = base_url.value.rstrip('/')
        self.language = language

    def _send_request(self, path: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal method to send a signed POST request to the GPay API.

        Args:
            path (str): The endpoint path (e.g., '/info/balance').
            parameters (Dict[str, Any]): The request parameters.

        Returns:
            Dict[str, Any]: The response JSON and headers.
        """
        salt = HashTokenGenerator.generate_salt()
        hash_token = HashTokenGenerator.generate_hash_token(salt, self.password)
        verification_hash = VerificationHashGenerator.generate_verification_hash(hash_token, parameters, self.secret_key)
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Accept-Language': self.language,
            'X-Signature-Salt': salt,
            'X-Signature-Hash': verification_hash,
            'Content-Type': 'application/json',
        }
        url = f"{self.base_url}{path}"
        response = requests.post(url, headers=headers, data=json.dumps(parameters))
        response.raise_for_status()
        return {
            'data': response.json(),
            'headers': response.headers
        }

    def _verify_response(self, headers, response_fields: dict):
        """
        Internal method to verify the authenticity of a response using the response headers and response fields.
        Raises ValueError if verification fails.

        Args:
            headers (dict): The response headers.
            response_fields (dict): The response fields to use for verification.
        """
        received_hash = headers.get('X-Signature-Hash') or headers.get('x-signature-hash')
        received_salt = headers.get('X-Signature-Salt') or headers.get('x-signature-salt')
        if not received_hash or not received_salt:
            raise ValueError('Missing X-Signature-Hash or X-Signature-Salt in response headers')
        hash_token = HashTokenGenerator.generate_hash_token(received_salt, self.password)
        verification_hash = VerificationHashGenerator.generate_verification_hash(hash_token, response_fields, self.secret_key)
        if verification_hash != received_hash:
            raise ValueError('Response verification failed: hash mismatch')

    def get_balance(self) -> Balance:
        """
        Retrieves the current wallet balance.

        Returns:
            Balance: An object containing the current available balance and response time.
        Raises:
            ValueError: If response verification fails.
        """
        path = '/info/balance'
        parameters = {
            'request_timestamp': str(int(time.time() * 1000))
        }
        result = self._send_request(path, parameters)
        data = result['data']['data']
        headers = result['headers']
        self._verify_response(headers, {
            'balance': data['balance'],
            'response_timestamp': data['response_timestamp'],
        })
        return Balance(data['balance'], data['response_timestamp'])

    def create_payment_request(self, amount: str, reference_no: Optional[str] = None, description: Optional[str] = None) -> PaymentRequest:
        """
        Creates a payment request for a specified amount.

        Args:
            amount (str): The amount to request.
            reference_no (Optional[str]): Optional reference number.
            description (Optional[str]): Optional description.

        Returns:
            PaymentRequest: An object with details of the created payment request.
        Raises:
            ValueError: If response verification fails.
        """
        path = '/payment/create-payment-request'
        parameters = {
            'request_timestamp': str(int(time.time() * 1000)),
            'amount': amount,
            'reference_no': reference_no or '',
            'description': description or ''
        }
        result = self._send_request(path, parameters)
        data = result['data']['data']
        headers = result['headers']
        self._verify_response(headers, {
            'requester_username': data['requester_username'],
            'request_id': data['request_id'],
            'request_time': data['request_time'],
            'amount': data['amount'],
            'reference_no': data.get('reference_no'),
            'response_timestamp': data['response_timestamp'],
        })
        return PaymentRequest(
            data['requester_username'],
            data['request_id'],
            data['request_time'],
            data['amount'],
            data.get('reference_no'),
            data['response_timestamp']
        )

    def check_payment_status(self, request_id: str) -> PaymentStatus:
        """
        Checks the status of a payment request by its request ID.

        Args:
            request_id (str): The payment request ID.

        Returns:
            PaymentStatus: An object with the status of the payment request.
        Raises:
            ValueError: If response verification fails.
        """
        path = '/payment/check-payment-status'
        parameters = {
            'request_timestamp': str(int(time.time() * 1000)),
            'request_id': request_id
        }
        result = self._send_request(path, parameters)
        data = result['data']['data']
        headers = result['headers']
        self._verify_response(headers, {
            'request_id': data['request_id'],
            'transaction_id': data.get('transaction_id'),
            'amount': data['amount'],
            'payment_timestamp': data.get('payment_timestamp'),
            'reference_no': data.get('reference_no'),
            'description': data['description'],
            'is_paid': data['is_paid'],
            'response_timestamp': data['response_timestamp'],
        })
        return PaymentStatus(
            data['request_id'],
            data.get('transaction_id'),
            data['amount'],
            data.get('payment_timestamp'),
            data.get('reference_no'),
            data['description'],
            data['is_paid'],
            data['response_timestamp']
        )

    def send_money(self, amount: str, wallet_gateway_id: str, description: Optional[str] = None, reference_no: Optional[str] = None) -> SendMoneyResult:
        """
        Sends money to another wallet.

        Args:
            amount (str): The amount to send.
            wallet_gateway_id (str): The recipient's wallet gateway ID.
            description (Optional[str]): Optional description.
            reference_no (Optional[str]): Optional reference number.

        Returns:
            SendMoneyResult: An object with details of the transaction.
        Raises:
            ValueError: If response verification fails.
        """
        path = '/payment/send-money'
        parameters = {
            'request_timestamp': str(int(time.time() * 1000)),
            'amount': amount,
            'wallet_gateway_id': wallet_gateway_id,
            'description': description or '',
            'reference_no': reference_no or ''
        }
        result = self._send_request(path, parameters)
        data = result['data']['data']
        headers = result['headers']
        self._verify_response(headers, {
            'amount': data['amount'],
            'sender_fee': data['sender_fee'],
            'transaction_id': data['transaction_id'],
            'old_balance': data['old_balance'],
            'new_balance': data['new_balance'],
            'timestamp': data['timestamp'],
            'reference_no': data.get('reference_no'),
            'response_timestamp': data['response_timestamp'],
        })
        return SendMoneyResult(
            data['amount'],
            data['sender_fee'],
            data['transaction_id'],
            data['old_balance'],
            data['new_balance'],
            data['timestamp'],
            data.get('reference_no'),
            data['response_timestamp']
        )

    def get_day_statement(self, date: str) -> Statement:
        """
        Retrieves the wallet's transaction statement for a specific day.

        Args:
            date (str): The date in YYYY-MM-DD format.

        Returns:
            Statement: An object containing the day's transactions and balances.
        Raises:
            ValueError: If response verification fails.
        """
        path = '/info/statement'
        parameters = {
            'request_timestamp': str(int(time.time() * 1000)),
            'date': date
        }
        result = self._send_request(path, parameters)
        data = result['data']['data']
        headers = result['headers']
        self._verify_response(headers, {
            'available_balance': data['available_balance'],
            'outstanding_credit': data['outstanding_credit'],
            'outstanding_debit': data['outstanding_debit'],
            'day_balance': data['day_balance'],
            'day_total_in': data['day_total_in'],
            'day_total_out': data['day_total_out'],
            'response_timestamp': data['response_timestamp'],
        })
        day_statement = [
            StatementTransaction(
                tx['transaction_id'],
                tx['datetime'],
                tx['timestamp'],
                tx['description'],
                tx.get('amount'),
                tx.get('balance'),
                tx.get('reference_no'),
                tx['op_type_id'],
                tx['status'],
                tx['created_at']
            ) for tx in data.get('day_statement', [])
        ]
        return Statement(
            data['available_balance'],
            data['outstanding_credit'],
            data['outstanding_debit'],
            data['day_balance'],
            data['day_total_in'],
            data['day_total_out'],
            data['response_timestamp'],
            day_statement
        )

    def check_wallet(self, wallet_gateway_id: str) -> WalletCheck:
        """
        Checks if a wallet exists and retrieves its details.

        Args:
            wallet_gateway_id (str): The wallet gateway ID to check.

        Returns:
            WalletCheck: An object with wallet details.
        Raises:
            ValueError: If response verification fails.
        """
        path = '/info/check-wallet'
        parameters = {
            'request_timestamp': str(int(time.time() * 1000)),
            'wallet_gateway_id': wallet_gateway_id
        }
        result = self._send_request(path, parameters)
        data = result['data']['data']
        headers = result['headers']
        self._verify_response(headers, {
            'exists': data['exists'],
            'wallet_gateway_id': data['wallet_gateway_id'],
            'wallet_name': data.get('wallet_name'),
            'user_account_name': data.get('user_account_name'),
            'can_receive_money': data['can_receive_money'],
            'response_timestamp': data['response_timestamp'],
        })
        return WalletCheck(
            data['exists'],
            data['wallet_gateway_id'],
            data.get('wallet_name'),
            data.get('user_account_name'),
            data['can_receive_money'],
            data['response_timestamp']
        )

    def get_outstanding_transactions(self) -> OutstandingTransactions:
        """
        Retrieves a list of outstanding transactions.

        Returns:
            OutstandingTransactions: An object containing outstanding credits, debits, and transactions.
        Raises:
            ValueError: If response verification fails.
        """
        path = '/info/outstanding-transactions'
        parameters = {
            'request_timestamp': str(int(time.time() * 1000))
        }
        result = self._send_request(path, parameters)
        data = result['data']['data']
        headers = result['headers']
        self._verify_response(headers, {
            'outstanding_credit': data['outstanding_credit'],
            'outstanding_debit': data['outstanding_debit'],
            'response_timestamp': data['response_timestamp'],
        })
        outstanding_transactions = [
            OutstandingTransaction(
                tx['transaction_id'],
                tx['datetime'],
                tx['timestamp'],
                tx['description'],
                tx.get('amount'),
                tx.get('balance'),
                tx.get('reference_no'),
                tx['op_type_id'],
                tx['status'],
                tx['created_at']
            ) for tx in data.get('outstanding_transactions', [])
        ]
        return OutstandingTransactions(
            data['outstanding_credit'],
            data['outstanding_debit'],
            data['response_timestamp'],
            outstanding_transactions
        )
