#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2024 Valory AG
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------
"""Bridge provider."""


import copy
import enum
import logging
import time
import typing as t
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass

from aea.crypto.base import LedgerApi
from aea.helpers.logging import setup_logger
from autonomy.chain.tx import TxSettler
from web3 import Web3
from web3.middleware import geth_poa_middleware

from operate.constants import (
    ON_CHAIN_INTERACT_RETRIES,
    ON_CHAIN_INTERACT_SLEEP,
    ON_CHAIN_INTERACT_TIMEOUT,
    ZERO_ADDRESS,
)
from operate.operate_types import Chain
from operate.resource import LocalResource
from operate.wallet.master import MasterWalletManager


PLACEHOLDER_NATIVE_TOKEN_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"  # nosec

DEFAULT_MAX_QUOTE_RETRIES = 3
BRIDGE_REQUEST_PREFIX = "r-"
MESSAGE_QUOTE_ZERO = "Zero-amount quote requested."
MESSAGE_EXECUTION_SKIPPED = "Execution skipped."
MESSAGE_EXECUTION_FAILED = "Execution failed:"
MESSAGE_EXECUTION_FAILED_ETA = f"{MESSAGE_EXECUTION_FAILED} bridge ETA exceeded."
MESSAGE_EXECUTION_FAILED_QUOTE_FAILED = f"{MESSAGE_EXECUTION_FAILED} quote failed."
MESSAGE_EXECUTION_FAILED_REVERTED = (
    f"{MESSAGE_EXECUTION_FAILED} bridge transaction reverted."
)
MESSAGE_EXECUTION_FAILED_SETTLEMENT = (
    f"{MESSAGE_EXECUTION_FAILED} transaction settlement failed."
)

ERC20_APPROVE_SELECTOR = "0x095ea7b3"  # First 4 bytes of Web3.keccak(text='approve(address,uint256)').hex()[:10]

GAS_ESTIMATE_BUFFER = 1.10


@dataclass
class QuoteData(LocalResource):
    """QuoteData"""

    bridge_eta: t.Optional[int]
    elapsed_time: float
    message: t.Optional[str]
    timestamp: int
    provider_data: t.Optional[t.Dict]  # Provider-specific data


@dataclass
class ExecutionData(LocalResource):
    """ExecutionData"""

    elapsed_time: float
    message: t.Optional[str]
    timestamp: int
    from_tx_hash: t.Optional[str]
    to_tx_hash: t.Optional[str]
    provider_data: t.Optional[t.Dict]  # Provider-specific data


class BridgeRequestStatus(str, enum.Enum):
    """BridgeRequestStatus"""

    CREATED = "CREATED"
    QUOTE_DONE = "QUOTE_DONE"
    QUOTE_FAILED = "QUOTE_FAILED"
    EXECUTION_PENDING = "EXECUTION_PENDING"
    EXECUTION_DONE = "EXECUTION_DONE"
    EXECUTION_FAILED = "EXECUTION_FAILED"
    EXECUTION_UNKNOWN = "EXECUTION_UNKNOWN"

    def __str__(self) -> str:
        """__str__"""
        return self.value


@dataclass
class BridgeRequest(LocalResource):
    """BridgeRequest"""

    params: t.Dict
    bridge_provider_id: str
    id: str
    status: BridgeRequestStatus
    quote_data: t.Optional[QuoteData]
    execution_data: t.Optional[ExecutionData]


class BridgeProvider(ABC):
    """(Abstract) BridgeProvider.

    Expected usage:
        params = {...}

        1. request = bridge.create_request(params)
        2. bridge.quote(request)
        3. bridge.requirements(request)
        4. bridge.execute(request)
        5. bridge.status_json(request)

    Derived classes must implement the following methods:
        - description
        - quote
        - _update_execution_status
        - _get_approve_tx
        - _get_bridge_tx
        - _get_explorer_link
    """

    def __init__(
        self,
        wallet_manager: MasterWalletManager,
        provider_id: str,
        logger: t.Optional[logging.Logger] = None,
    ) -> None:
        """Initialize the bridge provider."""
        self.wallet_manager = wallet_manager
        self.provider_id = provider_id
        self.logger = logger or setup_logger(name="operate.bridge.BridgeProvider")

    def description(self) -> str:
        """Get a human-readable description of the bridge provider."""
        return self.__class__.__name__

    def _validate(self, bridge_request: BridgeRequest) -> None:
        """Validate theat the bridge request was created by this bridge."""
        if bridge_request.bridge_provider_id != self.provider_id:
            raise ValueError(
                f"Bridge request provider id {bridge_request.bridge_provider_id} does not match the bridge provider id {self.provider_id}"
            )

    def can_handle_request(self, params: t.Dict) -> bool:
        """Returns 'true' if the bridge can handle a request for 'params'."""

        if "from" not in params or "to" not in params:
            self.logger.error(
                "[BRIDGE PROVIDER] Invalid input: All requests must contain exactly one 'from' and one 'to' sender."
            )
            return False

        from_ = params["from"]
        to = params["to"]

        if (
            not isinstance(from_, t.Dict)
            or "chain" not in from_
            or "address" not in from_
            or "token" not in from_
        ):
            self.logger.error(
                "[BRIDGE PROVIDER] Invalid input: 'from' must contain 'chain', 'address', and 'token'."
            )
            return False

        if (
            not isinstance(to, t.Dict)
            or "chain" not in to
            or "address" not in to
            or "token" not in to
            or "amount" not in to
        ):
            self.logger.error(
                "[BRIDGE PROVIDER] Invalid input: 'to' must contain 'chain', 'address', 'token', and 'amount'."
            )
            return False

        return True

    def create_request(self, params: t.Dict) -> BridgeRequest:
        """Create a bridge request."""

        if not self.can_handle_request(params):
            raise ValueError("Invalid input: Cannot process bridge request.")

        w3 = Web3()
        params = copy.deepcopy(params)
        params["from"]["address"] = w3.to_checksum_address(params["from"]["address"])
        params["from"]["token"] = w3.to_checksum_address(params["from"]["token"])
        params["to"]["address"] = w3.to_checksum_address(params["to"]["address"])
        params["to"]["token"] = w3.to_checksum_address(params["to"]["token"])
        params["to"]["amount"] = int(params["to"]["amount"])

        return BridgeRequest(
            params=params,
            bridge_provider_id=self.provider_id,
            id=f"{BRIDGE_REQUEST_PREFIX}{uuid.uuid4()}",
            quote_data=None,
            execution_data=None,
            status=BridgeRequestStatus.CREATED,
        )

    def _from_ledger_api(self, bridge_request: BridgeRequest) -> LedgerApi:
        """Get the from ledger api."""
        from_chain = bridge_request.params["from"]["chain"]
        chain = Chain(from_chain)
        wallet = self.wallet_manager.load(chain.ledger_type)
        ledger_api = wallet.ledger_api(chain)

        # TODO: Backport to open aea/autonomy
        if chain == Chain.OPTIMISTIC:
            ledger_api.api.middleware_onion.inject(geth_poa_middleware, layer=0)

        return ledger_api

    def _to_ledger_api(self, bridge_request: BridgeRequest) -> LedgerApi:
        """Get the from ledger api."""
        from_chain = bridge_request.params["to"]["chain"]
        chain = Chain(from_chain)
        wallet = self.wallet_manager.load(chain.ledger_type)
        ledger_api = wallet.ledger_api(chain)

        # TODO: Backport to open aea/autonomy
        if chain == Chain.OPTIMISTIC:
            ledger_api.api.middleware_onion.inject(geth_poa_middleware, layer=0)

        return ledger_api

    @abstractmethod
    def quote(self, bridge_request: BridgeRequest) -> None:
        """Update the request with the quote."""
        raise NotImplementedError()

    @abstractmethod
    def _get_approve_tx(self, bridge_request: BridgeRequest) -> t.Optional[t.Dict]:
        """Get the approve transaction."""
        raise NotImplementedError()

    @abstractmethod
    def _get_bridge_tx(self, bridge_request: BridgeRequest) -> t.Optional[t.Dict]:
        """Get the bridge transaction."""
        raise NotImplementedError()

    def bridge_requirements(self, bridge_request: BridgeRequest) -> t.Dict:
        """Gets the bridge requirements to execute the quote, with updated gas estimation."""
        self.logger.info(
            f"[BRIDGE PROVIDER] Bridge requirements for request {bridge_request.id}."
        )

        self._validate(bridge_request)

        from_chain = bridge_request.params["from"]["chain"]
        from_address = bridge_request.params["from"]["address"]
        from_token = bridge_request.params["from"]["token"]
        from_ledger_api = self._from_ledger_api(bridge_request)

        txs = []

        approve_tx = self._get_approve_tx(bridge_request)
        if approve_tx:
            txs.append(("approve_tx", approve_tx))
        bridge_tx = self._get_bridge_tx(bridge_request)
        if bridge_tx:
            txs.append(("bridge_tx", bridge_tx))

        if not txs:
            return {
                from_chain: {
                    from_address: {
                        ZERO_ADDRESS: 0,
                        from_token: 0,
                    }
                }
            }

        total_native = 0
        total_gas_fees = 0
        total_token = 0

        for tx_label, tx in txs:
            self.logger.debug(
                f"[BRIDGE PROVIDER] Processing transaction {tx_label} for bridge request {bridge_request.id}."
            )
            self._update_with_gas_pricing(tx, from_ledger_api)
            gas_key = "gasPrice" if "gasPrice" in tx else "maxFeePerGas"
            gas_fees = tx.get(gas_key, 0) * tx["gas"]
            tx_value = int(tx.get("value", 0))
            total_gas_fees += gas_fees
            total_native += tx_value + gas_fees

            self.logger.debug(
                f"[BRIDGE PROVIDER] Transaction {gas_key}={tx.get(gas_key, 0)} maxPriorityFeePerGas={tx.get('maxPriorityFeePerGas', -1)} gas={tx['gas']} {gas_fees=} {tx_value=}"
            )
            self.logger.debug(f"[BRIDGE PROVIDER] {from_ledger_api.api.eth.gas_price=}")
            self.logger.debug(
                f"[BRIDGE PROVIDER] {from_ledger_api.api.eth.get_block('latest').baseFeePerGas=}"
            )

            if tx.get("to", "").lower() == from_token.lower() and tx.get(
                "data", ""
            ).startswith(ERC20_APPROVE_SELECTOR):
                try:
                    amount = int(tx["data"][-64:], 16)
                    total_token += amount
                except Exception as e:
                    raise RuntimeError("Malformed ERC20 approve transaction.") from e

        self.logger.info(
            f"[BRIDGE PROVIDER] Total gas fees for bridge request {bridge_request.id}: {total_gas_fees} native units."
        )

        result = {
            from_chain: {
                from_address: {
                    ZERO_ADDRESS: total_native,
                }
            }
        }

        if from_token != ZERO_ADDRESS:
            result[from_chain][from_address][from_token] = total_token

        return result

    def execute(self, bridge_request: BridgeRequest) -> None:
        """Execute the request."""
        self.logger.info(
            f"[BRIDGE PROVIDER] Executing bridge request {bridge_request.id}."
        )

        self._validate(bridge_request)

        if bridge_request.status in (BridgeRequestStatus.QUOTE_FAILED):
            self.logger.info(
                f"[BRIDGE PROVIDER] {MESSAGE_EXECUTION_FAILED_QUOTE_FAILED}."
            )
            execution_data = ExecutionData(
                elapsed_time=0,
                message=f"{MESSAGE_EXECUTION_FAILED_QUOTE_FAILED}",
                timestamp=int(time.time()),
                from_tx_hash=None,
                to_tx_hash=None,
                provider_data=None,
            )
            bridge_request.execution_data = execution_data
            bridge_request.status = BridgeRequestStatus.EXECUTION_FAILED
            return

        if bridge_request.status not in (BridgeRequestStatus.QUOTE_DONE,):
            raise RuntimeError(
                f"Cannot execute bridge request {bridge_request.id} with status {bridge_request.status}."
            )
        if not bridge_request.quote_data:
            raise RuntimeError(
                f"Cannot execute bridge request {bridge_request.id}: quote data not present."
            )
        if bridge_request.execution_data:
            raise RuntimeError(
                f"Cannot execute bridge request {bridge_request.id}: execution data already present."
            )

        txs = []

        approve_tx = self._get_approve_tx(bridge_request)
        if approve_tx:
            txs.append(("approve_tx", approve_tx))
        bridge_tx = self._get_bridge_tx(bridge_request)
        if bridge_tx:
            txs.append(("bridge_tx", bridge_tx))

        if not txs:
            self.logger.info(
                f"[BRIDGE PROVIDER] {MESSAGE_EXECUTION_SKIPPED} ({bridge_request.status=})"
            )
            execution_data = ExecutionData(
                elapsed_time=0,
                message=f"{MESSAGE_EXECUTION_SKIPPED} ({bridge_request.status=})",
                timestamp=int(time.time()),
                from_tx_hash=None,
                to_tx_hash=None,
                provider_data=None,
            )
            bridge_request.execution_data = execution_data
            bridge_request.status = BridgeRequestStatus.EXECUTION_DONE
            return

        try:
            self.logger.info(
                f"[BRIDGE PROVIDER] Executing bridge request {bridge_request.id}."
            )
            timestamp = time.time()
            chain = Chain(bridge_request.params["from"]["chain"])
            from_address = bridge_request.params["from"]["address"]
            wallet = self.wallet_manager.load(chain.ledger_type)
            from_ledger_api = self._from_ledger_api(bridge_request)
            tx_settler = TxSettler(
                ledger_api=from_ledger_api,
                crypto=wallet.crypto,
                chain_type=Chain(bridge_request.params["from"]["chain"]),
                timeout=ON_CHAIN_INTERACT_TIMEOUT,
                retries=ON_CHAIN_INTERACT_RETRIES,
                sleep=ON_CHAIN_INTERACT_SLEEP,
            )
            tx_hashes = []

            for tx_label, tx in txs:
                self.logger.info(f"[BRIDGE] Executing transaction {tx_label}.")
                nonce = from_ledger_api.api.eth.get_transaction_count(from_address)
                tx["nonce"] = nonce  # TODO: backport to TxSettler
                setattr(  # noqa: B010
                    tx_settler, "build", lambda *args, **kwargs: tx  # noqa: B023
                )
                tx_receipt = tx_settler.transact(
                    method=lambda: {},
                    contract="",
                    kwargs={},
                    dry_run=False,
                )
                self.logger.info(f"[BRIDGE] Transaction {tx_label} settled.")
                tx_hashes.append(tx_receipt.get("transactionHash", "").hex())

            execution_data = ExecutionData(
                elapsed_time=time.time() - timestamp,
                message=None,
                timestamp=int(timestamp),
                from_tx_hash=tx_hashes[-1],
                to_tx_hash=None,
                provider_data=None,
            )
            bridge_request.execution_data = execution_data
            if len(tx_hashes) == len(txs):
                bridge_request.status = BridgeRequestStatus.EXECUTION_PENDING
            else:
                bridge_request.execution_data.message = (
                    MESSAGE_EXECUTION_FAILED_SETTLEMENT
                )
                bridge_request.status = BridgeRequestStatus.EXECUTION_FAILED

        except Exception as e:  # pylint: disable=broad-except
            self.logger.error(f"[BRIDGE PROVIDER] Error executing bridge request: {e}")
            execution_data = ExecutionData(
                elapsed_time=time.time() - timestamp,
                message=f"{MESSAGE_EXECUTION_FAILED} {str(e)}",
                timestamp=int(time.time()),
                from_tx_hash=None,
                to_tx_hash=None,
                provider_data=None,
            )
            bridge_request.execution_data = execution_data
            bridge_request.status = BridgeRequestStatus.EXECUTION_FAILED

    @abstractmethod
    def _update_execution_status(self, bridge_request: BridgeRequest) -> None:
        """Update the execution status."""
        raise NotImplementedError()

    @abstractmethod
    def _get_explorer_link(self, bridge_request: BridgeRequest) -> t.Optional[str]:
        """Get the explorer link for a transaction."""
        raise NotImplementedError()

    def status_json(self, bridge_request: BridgeRequest) -> t.Dict:
        """JSON representation of the status."""
        self._validate(bridge_request)

        if bridge_request.execution_data and bridge_request.quote_data:
            self._update_execution_status(bridge_request)
            tx_hash = None
            if bridge_request.execution_data.from_tx_hash:
                tx_hash = bridge_request.execution_data.from_tx_hash

            return {
                "eta": bridge_request.quote_data.bridge_eta,
                "explorer_link": self._get_explorer_link(bridge_request),
                "message": bridge_request.execution_data.message,
                "status": bridge_request.status.value,
                "tx_hash": tx_hash,
            }
        if bridge_request.quote_data:
            return {
                "eta": bridge_request.quote_data.bridge_eta,
                "message": bridge_request.quote_data.message,
                "status": bridge_request.status.value,
            }

        return {"message": None, "status": bridge_request.status.value}

    @staticmethod
    def _tx_timestamp(tx_hash: str, ledger_api: LedgerApi) -> int:
        receipt = ledger_api.api.eth.get_transaction_receipt(tx_hash)
        block = ledger_api.api.eth.get_block(receipt.blockNumber)
        return block.timestamp

    # TODO backport to open aea/autonomy
    # TODO This gas pricing management should possibly be done at a lower level in the library
    @staticmethod
    def _update_with_gas_pricing(tx: t.Dict, ledger_api: LedgerApi) -> None:
        tx.pop("maxFeePerGas", None)
        tx.pop("gasPrice", None)
        tx.pop("maxPriorityFeePerGas", None)

        gas_pricing = ledger_api.try_get_gas_pricing()
        if gas_pricing is None:
            raise RuntimeError("Unable to retrieve gas pricing.")

        if "maxFeePerGas" in gas_pricing and "maxPriorityFeePerGas" in gas_pricing:
            tx["maxFeePerGas"] = gas_pricing["maxFeePerGas"]
            tx["maxPriorityFeePerGas"] = gas_pricing["maxPriorityFeePerGas"]
        elif "gasPrice" in gas_pricing:
            tx["gasPrice"] = gas_pricing["gasPrice"]
        else:
            raise RuntimeError("Retrieved invalid gas pricing.")

    # TODO backport to open aea/autonomy
    @staticmethod
    def _update_with_gas_estimate(tx: t.Dict, ledger_api: LedgerApi) -> None:
        original_gas = tx.get("gas", 1)
        tx["gas"] = 1
        ledger_api.update_with_gas_estimate(tx)

        if tx["gas"] > 1:
            return

        original_from = tx["from"]
        tx["from"] = PLACEHOLDER_NATIVE_TOKEN_ADDRESS
        ledger_api.update_with_gas_estimate(tx)
        tx["from"] = original_from

        if tx["gas"] > 1:
            return

        tx["gas"] = original_gas
