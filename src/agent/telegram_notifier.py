"""
Telegram notification module for trade alerts.
Sends buy/sell/LP alerts when the agent executes trades on Meteora DLMM.
"""

import logging
import os
from enum import Enum
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class TradeType(Enum):
    """Trade action types."""
    BUY = "BUY"
    SELL = "SELL"
    LP = "LP"


class TelegramNotifier:
    """
    Sends trade alerts to Telegram when the agent executes trades.
    Uses the Telegram Bot API to send messages.
    """

    BASE_URL = "https://api.telegram.org/bot{token}/sendMessage"

    # Emoji mapping for trade types
    EMOJI = {
        TradeType.BUY: "🟢",
        TradeType.SELL: "🔴",
        TradeType.LP: "🔵",
    }

    def __init__(self):
        """Initialize Telegram notifier with credentials from environment."""
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

    def _is_configured(self) -> bool:
        """Check if Telegram credentials are configured."""
        return bool(self.bot_token and self.chat_id)

    def _shorten_signature(self, signature: str, prefix_length: int = 8) -> str:
        """Shorten a transaction signature for display."""
        if len(signature) <= prefix_length * 2 + 3:
            return signature
        return f"{signature[:prefix_length]}...{signature[-prefix_length:]}"

    def _format_amount(self, amount: float) -> str:
        """Format amount for display."""
        if amount >= 1_000_000:
            return f"{amount / 1_000_000:.2f}M"
        elif amount >= 1_000:
            return f"{amount / 1_000:.2f}K"
        return f"{amount:.4f}"

    def send_trade_alert(
        self,
        trade_type: TradeType,
        token_symbol: str,
        amount: float,
        tx_signature: Optional[str] = None,
        pool_address: Optional[str] = None,
    ) -> bool:
        """
        Send a trade alert to Telegram.

        Args:
            trade_type: Type of trade (BUY, SELL, LP)
            token_symbol: Symbol of the token being traded
            amount: Amount of the trade
            tx_signature: Optional transaction signature
            pool_address: Optional pool address

        Returns:
            True if message was sent successfully, False otherwise
        """
        if not self._is_configured():
            logger.debug("Telegram notifier not configured, skipping alert")
            return False

        emoji = self.EMOJI.get(trade_type, "📢")
        amount_str = self._format_amount(amount)

        # Build message
        message_parts = [
            f"{emoji} *{trade_type.value}*",
            f"Token: `{token_symbol}`",
            f"Amount: {amount_str}",
        ]

        if tx_signature:
            short_sig = self._shorten_signature(tx_signature)
            message_parts.append(f"Tx: `{short_sig}`")

        if pool_address:
            short_pool = self._shorten_signature(pool_address)
            message_parts.append(f"Pool: `{short_pool}`")

        message = "\n".join(message_parts)

        # Send via Telegram API
        url = self.BASE_URL.format(token=self.bot_token)
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Telegram alert sent: {trade_type.value} {token_symbol}")
            return True
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to send Telegram alert: {e}")
            return False


# Global notifier instance
telegram_notifier = TelegramNotifier()
