import os
import time
import sqlite3
import sys
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseLedger(ABC):
    @abstractmethod
    def is_verified(self, utr: Optional[str] = None, txn_id: Optional[str] = None) -> bool:
        pass

    @abstractmethod
    def save_verification(
        self,
        status: int,
        endpoint: str,
        amount: float,
        utr: Optional[str] = None,
        txn_id: Optional[str] = None,
        sender_name: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> None:
        pass


class MemoryLedger(BaseLedger):
    def __init__(self, ttl_seconds: int = 86400):
        self.cache: Dict[str, float] = {}
        self.ttl = ttl_seconds

    def _prune(self):
        now = time.time()
        expired = [k for k, v in self.cache.items() if now - v > self.ttl]
        for k in expired:
            del self.cache[k]

    def is_verified(self, utr: Optional[str] = None, txn_id: Optional[str] = None) -> bool:
        self._prune()
        key = utr or txn_id
        if not key:
            return False
        return key in self.cache

    def save_verification(
        self,
        status: int,
        endpoint: str,
        amount: float,
        utr: Optional[str] = None,
        txn_id: Optional[str] = None,
        sender_name: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> None:
        self._prune()
        if status == 200:
            key = utr or txn_id
            if key:
                self.cache[key] = time.time()


class SQLiteLedger(BaseLedger):
    def __init__(self, db_path: str = "payments.db", silent: bool = False):
        self.db_path = db_path
        self._init_db()
        if not silent:
            print(
                "\n💡 [FamApp Ledger Tip]: Defaulting to local SQLite storage ('payments.db').\n"
                "   -> For high-availability, serverless, or multi-instance deployments,\n"
                "      we recommend configuring Supabase or another central cloud storage backend.\n",
                file=sys.stderr
            )

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        conn = self._get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    endpoint TEXT NOT NULL,
                    status INTEGER NOT NULL,
                    amount REAL,
                    utr TEXT,
                    txn_id TEXT,
                    sender_name TEXT,
                    user_id TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_utr ON api_logs(utr) WHERE utr IS NOT NULL")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_txn_id ON api_logs(txn_id) WHERE txn_id IS NOT NULL")
            conn.commit()
        finally:
            conn.close()

    def is_verified(self, utr: Optional[str] = None, txn_id: Optional[str] = None) -> bool:
        if not utr and not txn_id:
            return False

        query = "SELECT id FROM api_logs WHERE status = 200 AND "
        params = []
        if utr and txn_id:
            query += "(utr = ? OR txn_id = ?)"
            params.extend([utr, txn_id])
        elif utr:
            query += "utr = ?"
            params.append(utr)
        else:
            query += "txn_id = ?"
            params.append(txn_id)

        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result is not None
        finally:
            conn.close()

    def save_verification(
        self,
        status: int,
        endpoint: str,
        amount: float,
        utr: Optional[str] = None,
        txn_id: Optional[str] = None,
        sender_name: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> None:
        conn = self._get_connection()
        try:
            conn.execute(
                """
                INSERT INTO api_logs (endpoint, status, amount, utr, txn_id, sender_name, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (endpoint, status, amount, utr, txn_id, sender_name, user_id)
            )
            conn.commit()
        finally:
            conn.close()


class SupabaseLedger(BaseLedger):
    def __init__(self, supabase_url: str, supabase_key: str):
        try:
            from supabase import create_client, Client
        except ImportError:
            raise ImportError(
                "The 'supabase' package is required to use SupabaseLedger. "
                "Install it using: pip install famapp-transac-log[supabase]"
            )
        self.client: Client = create_client(supabase_url, supabase_key)

    def is_verified(self, utr: Optional[str] = None, txn_id: Optional[str] = None) -> bool:
        if not utr and not txn_id:
            return False

        query = self.client.table("api_logs").select("id").eq("status", 200)
        
        if utr and txn_id:
            res = query.or_(f"utr.eq.{utr},txn_id.eq.{txn_id}").execute()
        elif utr:
            res = query.eq("utr", utr).execute()
        else:
            res = query.eq("txn_id", txn_id).execute()

        return len(res.data) > 0

    def save_verification(
        self,
        status: int,
        endpoint: str,
        amount: float,
        utr: Optional[str] = None,
        txn_id: Optional[str] = None,
        sender_name: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> None:
        payload = {
            "endpoint": endpoint,
            "status": status,
            "amount": amount,
            "utr": utr,
            "txn_id": txn_id,
            "sender_name": sender_name,
            "user_id": user_id
        }
        self.client.table("api_logs").insert(payload).execute()
