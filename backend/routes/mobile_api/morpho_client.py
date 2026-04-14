"""
Morpho API Client for FIDUS App
================================
Connects to Lucrum's Morpho platform (ProBroker Systems).
API Docs: https://docs.probrokersystems.com/morpho/

This client handles all communication with the Morpho API.
When MORPHO_API_KEY is not set, all methods return None (graceful fallback).
"""

import httpx
import logging
import os
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class MorphoClient:
    """Async HTTP client for the Morpho API."""

    def __init__(self):
        self.api_key: Optional[str] = os.environ.get("MORPHO_API_KEY")
        self.base_url: str = os.environ.get(
            "MORPHO_BASE_URL", "https://api.morphos.com/api/v1"
        ).rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def is_configured(self) -> bool:
        """Check if the Morpho API key is set."""
        return bool(self.api_key and self.api_key.strip())

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self._get_headers(),
                timeout=30.0,
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    # ------------------------------------------------------------------ #
    #  Generic request helpers
    # ------------------------------------------------------------------ #

    async def _get(self, path: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make a GET request. Returns None on failure or if not configured."""
        if not self.is_configured:
            return None
        try:
            client = await self._get_client()
            response = await client.get(path, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Morpho API error {e.response.status_code} on GET {path}: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Morpho API connection error on GET {path}: {e}")
            return None

    async def _post(self, path: str, json_data: Optional[Dict] = None) -> Optional[Dict]:
        """Make a POST request. Returns None on failure or if not configured."""
        if not self.is_configured:
            return None
        try:
            client = await self._get_client()
            response = await client.post(path, json=json_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Morpho API error {e.response.status_code} on POST {path}: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Morpho API connection error on POST {path}: {e}")
            return None

    # ------------------------------------------------------------------ #
    #  Users API
    #  Docs: https://docs.probrokersystems.com/morpho/api-reference/users.html
    # ------------------------------------------------------------------ #

    async def list_users(
        self,
        page: int = 1,
        limit: int = 50,
        email: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Optional[Dict]:
        """
        GET /users
        Scope: users:read
        Returns paginated list of users. Supports filtering by email, status, etc.
        """
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if email:
            params["email"] = email
        if status:
            params["status"] = status
        return await self._get("/users", params=params)

    async def get_user(self, user_uuid: str) -> Optional[Dict]:
        """
        GET /users/:uuid
        Scope: users:read
        """
        return await self._get(f"/users/{user_uuid}")

    async def find_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Look up a single user by their email address.
        Uses list_users and filters client-side for exact email match
        since the Morpho API may not filter by email server-side.
        """
        result = await self.list_users(email=email, limit=100)
        if result and "data" in result:
            email_lower = email.lower()
            for user in result["data"]:
                if user.get("email", "").lower() == email_lower:
                    return user
        return None

    async def create_user(self, user_data: Dict) -> Optional[Dict]:
        """
        POST /users
        Scope: users:create
        Fields: email, names, phone, countryUuid, etc.
        """
        return await self._post("/users", json_data=user_data)

    async def signup_user(
        self,
        email: str,
        password: str,
        names: str,
        surnames: str,
        phone: str,
        country: str,
        source: str = "fidus-app",
    ) -> Optional[Dict]:
        """
        POST /auth/signup
        Scope: users:write
        Full user registration in Lucrum via Morpho.
        FIDUS is automatically assigned as the referrer/IB.
        Returns user data with UUID on success, error dict on failure.
        """
        if not self.is_configured:
            return None
        try:
            client = await self._get_client()
            response = await client.post("/auth/signup", json={
                "email": email,
                "password": password,
                "names": names,
                "surnames": surnames,
                "phone": phone,
                "country": country,
                "source": source,
            })

            # Handle non-JSON responses (e.g., 503 HTML pages)
            content_type = response.headers.get("content-type", "")
            if "application/json" not in content_type:
                logger.error(f"Morpho signup returned non-JSON ({response.status_code}): {response.text[:200]}")
                return {"success": False, "errors": [{"message": f"Lucrum service temporarily unavailable (HTTP {response.status_code})"}]}

            result = response.json()
            if response.status_code in (200, 201):
                return {"success": True, "data": result.get("data", result)}
            else:
                return {"success": False, "errors": result.get("errors", []), "status": response.status_code}
        except Exception as e:
            logger.error(f"Morpho signup error: {e}")
            return {"success": False, "errors": [{"message": str(e)}]}

    # ------------------------------------------------------------------ #
    #  Accounts API
    #  Docs: https://docs.probrokersystems.com/morpho/api-reference/accounts.html
    # ------------------------------------------------------------------ #

    async def list_accounts(
        self,
        user_uuid: Optional[str] = None,
        page: int = 1,
        limit: int = 50,
    ) -> Optional[Dict]:
        """
        GET /accounts
        Scope: accounts:read
        Returns trading accounts with balance, equity, margin, leverage, etc.
        """
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if user_uuid:
            params["userUuid"] = user_uuid
        return await self._get("/accounts", params=params)

    async def get_account(self, account_uuid: str) -> Optional[Dict]:
        """
        GET /accounts/:uuid
        Scope: accounts:read
        """
        return await self._get(f"/accounts/{account_uuid}")

    async def get_user_accounts(self, user_uuid: str) -> Optional[List[Dict]]:
        """
        Convenience: get all accounts for a specific user.
        Filters by userUuid client-side since the API may return all accounts.
        Returns the filtered data array or empty list.
        """
        result = await self.list_accounts(user_uuid=user_uuid)
        if result and "data" in result:
            # Filter client-side to ensure only this user's accounts
            filtered = [
                a for a in result["data"]
                if a.get("userUuid") == user_uuid
            ]
            return filtered
        return None

    # ------------------------------------------------------------------ #
    #  Deposits API
    #  Docs: https://docs.probrokersystems.com/morpho/api-reference/deposits.html
    # ------------------------------------------------------------------ #

    async def list_deposits(
        self,
        user_uuid: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 50,
    ) -> Optional[Dict]:
        """
        GET /deposits
        Scope: deposits:read
        """
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if user_uuid:
            params["userUuid"] = user_uuid
        if status:
            params["status"] = status
        return await self._get("/deposits", params=params)

    async def get_deposit(self, deposit_uuid: str) -> Optional[Dict]:
        """
        GET /deposits/:uuid
        Scope: deposits:read
        """
        return await self._get(f"/deposits/{deposit_uuid}")

    async def get_user_deposits(self, user_uuid: str, limit: int = 50) -> Optional[List[Dict]]:
        """Convenience: get all deposits for a specific user."""
        result = await self.list_deposits(user_uuid=user_uuid, limit=limit)
        if result and "data" in result:
            # Filter client-side to ensure only this user's deposits
            filtered = [
                d for d in result["data"]
                if d.get("userUuid") == user_uuid
            ]
            return filtered if filtered else result["data"]
        return None

    # ------------------------------------------------------------------ #
    #  Withdrawals API
    #  Docs: https://docs.probrokersystems.com/morpho/api-reference/withdrawals.html
    # ------------------------------------------------------------------ #

    async def list_withdrawals(
        self,
        user_uuid: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 50,
    ) -> Optional[Dict]:
        """
        GET /withdrawals
        Scope: withdrawals:read
        """
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if user_uuid:
            params["userUuid"] = user_uuid
        if status:
            params["status"] = status
        return await self._get("/withdrawals", params=params)

    async def get_withdrawal(self, withdrawal_uuid: str) -> Optional[Dict]:
        """
        GET /withdrawals/:uuid
        Scope: withdrawals:read
        """
        return await self._get(f"/withdrawals/{withdrawal_uuid}")

    async def get_user_withdrawals(self, user_uuid: str, limit: int = 50) -> Optional[List[Dict]]:
        """Convenience: get all withdrawals for a specific user."""
        result = await self.list_withdrawals(user_uuid=user_uuid, limit=limit)
        if result and "data" in result:
            # Filter client-side to ensure only this user's withdrawals
            filtered = [
                w for w in result["data"]
                if w.get("userUuid") == user_uuid
            ]
            return filtered if filtered else result["data"]
        return None

    # ------------------------------------------------------------------ #
    #  Challenges API
    #  Docs: https://docs.probrokersystems.com/morpho/api-reference/challenges.html
    # ------------------------------------------------------------------ #

    async def list_challenge_templates(
        self,
        active: Optional[bool] = None,
        visible: Optional[bool] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Optional[Dict]:
        """
        GET /challenges/templates
        Scope: challenges:read
        """
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if active is not None:
            params["active"] = active
        if visible is not None:
            params["visible"] = visible
        return await self._get("/challenges/templates", params=params)

    async def list_challenges(
        self,
        user_uuid: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 50,
    ) -> Optional[Dict]:
        """
        GET /challenges
        Scope: challenges:read
        """
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if user_uuid:
            params["userUuid"] = user_uuid
        if status:
            params["status"] = status
        return await self._get("/challenges", params=params)

    async def get_challenge(self, challenge_uuid: str) -> Optional[Dict]:
        """
        GET /challenges/:uuid
        Scope: challenges:read
        """
        return await self._get(f"/challenges/{challenge_uuid}")

    # ------------------------------------------------------------------ #
    #  Data Mapping Helpers
    #  Transform Morpho API responses into FIDUS app format
    # ------------------------------------------------------------------ #

    @staticmethod
    def map_user_to_fidus(morpho_user: Dict) -> Dict:
        """
        Map a Morpho user object to FIDUS user format.
        Includes full KYC/security status, introducer, activity info.
        """
        security = morpho_user.get("security", {}) or {}
        country = morpho_user.get("country", {}) or {}
        introductor = morpho_user.get("introductor", {}) or {}
        logins = morpho_user.get("logins", {}) or {}
        operations = morpho_user.get("operations", {}) or {}
        deposit_info = morpho_user.get("deposit", {}) or {}

        return {
            "morpho_uuid": morpho_user.get("uuid"),
            "email": morpho_user.get("email", ""),
            "name": morpho_user.get("names", morpho_user.get("name", "")),
            "phone": morpho_user.get("phone", ""),
            "birthday": morpho_user.get("birthday"),
            "country": {
                "name": country.get("name", "") if isinstance(country, dict) else "",
                "code": country.get("code", "") if isinstance(country, dict) else str(country or ""),
            },
            "is_active": morpho_user.get("isActive", 0) == 1,
            "is_verified": morpho_user.get("isVerified", 0) == 1,
            "language": morpho_user.get("lang", "en"),
            "kyc": {
                "document_validated": security.get("isDocumentValidated", 0) == 1,
                "phone_validated": security.get("isPhoneValidated", 0) == 1,
                "email_validated": security.get("isEmailValidated", 0) == 1,
                "residence_validated": security.get("isResidenceValidated", 0) == 1,
                "fully_verified": (
                    security.get("isDocumentValidated", 0) == 1
                    and security.get("isPhoneValidated", 0) == 1
                    and security.get("isEmailValidated", 0) == 1
                    and security.get("isResidenceValidated", 0) == 1
                ),
            },
            "introducer": {
                "name": introductor.get("names", ""),
                "email": introductor.get("email", ""),
                "username": introductor.get("username", ""),
            } if introductor else None,
            "activity": {
                "days_since_last_login": logins.get("daysSinceLastLogin"),
                "last_device": logins.get("device"),
                "last_order_at": operations.get("lastOrderAt"),
                "days_since_last_order": operations.get("daysSinceLastOrder"),
                "days_since_last_deposit": deposit_info.get("daysSinceLastDeposit"),
            },
            "is_ib": morpho_user.get("isIb", False),
            "is_referral": morpho_user.get("isReferrral", False),
            "status": morpho_user.get("status", "unknown"),
            "created_at": morpho_user.get("createdAt"),
        }

    @staticmethod
    def map_account_to_fidus(morpho_account: Dict) -> Dict:
        """
        Map a Morpho account to FIDUS format.
        Morpho account: uuid, username, balance, equity, margin, leverage, etc.
        """
        return {
            "account_uuid": morpho_account.get("uuid"),
            "account_id": morpho_account.get("username", ""),
            "balance": float(morpho_account.get("balance", 0)),
            "equity": float(morpho_account.get("equity", 0)),
            "margin": float(morpho_account.get("margin", 0)),
            "free_margin": float(morpho_account.get("freeMargin", 0)),
            "leverage": morpho_account.get("leverage", ""),
            "currency": morpho_account.get("currency", "USD"),
            "status": morpho_account.get("status", {}),
            "group": morpho_account.get("group", {}),
            "created_at": morpho_account.get("createdAt"),
        }

    @staticmethod
    def map_deposit_to_transaction(deposit: Dict) -> Dict:
        """Map a Morpho deposit to FIDUS transaction format."""
        # Status mapping: "1" = pending, "2" = approved, "3" = rejected
        status_map = {"1": "pending", "2": "completed", "3": "failed"}
        status_uuid = str(deposit.get("statusUuid", "1"))

        return {
            "id": deposit.get("uuid", ""),
            "type": "deposit",
            "amount": float(deposit.get("amountUsd", deposit.get("amount", 0))),
            "description": f"Deposit - {deposit.get('transactionId', 'N/A')}",
            "status": status_map.get(status_uuid, "pending"),
            "created_at": deposit.get("createdAt"),
            "morpho_uuid": deposit.get("uuid"),
        }

    @staticmethod
    def map_withdrawal_to_transaction(withdrawal: Dict) -> Dict:
        """Map a Morpho withdrawal to FIDUS transaction format."""
        status_map = {"1": "pending", "2": "completed", "3": "failed"}
        status_uuid = str(withdrawal.get("statusUuid", "1"))

        return {
            "id": withdrawal.get("uuid", ""),
            "type": "withdrawal",
            "amount": float(withdrawal.get("amountUsd", withdrawal.get("amount", 0))),
            "description": f"Withdrawal - {withdrawal.get('transactionId', 'N/A')}",
            "status": status_map.get(status_uuid, "pending"),
            "fee": float(withdrawal.get("fee", 0)),
            "gross_amount": float(withdrawal.get("grossAmount", 0)),
            "created_at": withdrawal.get("createdAt"),
            "morpho_uuid": withdrawal.get("uuid"),
        }

    @staticmethod
    def aggregate_account_balance(accounts: List[Dict]) -> Dict:
        """
        Aggregate balance info across all of a user's Morpho accounts.
        Returns total balance, equity, margin.
        """
        total_balance = 0.0
        total_equity = 0.0
        total_margin = 0.0
        total_free_margin = 0.0
        account_details = []

        for acc in accounts:
            mapped = MorphoClient.map_account_to_fidus(acc)
            total_balance += mapped["balance"]
            total_equity += mapped["equity"]
            total_margin += mapped["margin"]
            total_free_margin += mapped["free_margin"]
            account_details.append(mapped)

        return {
            "total_balance": round(total_balance, 2),
            "total_equity": round(total_equity, 2),
            "total_margin": round(total_margin, 2),
            "total_free_margin": round(total_free_margin, 2),
            "account_count": len(accounts),
            "accounts": account_details,
        }


# Singleton instance
morpho = MorphoClient()
