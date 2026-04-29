"""
Configuration management for Shelby Solana Trading Agent.
Loads settings from environment variables with validation.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class TradingConfig:
    """Trading agent configuration."""

    # Solana
    solana_private_key: str
    solana_rpc_url: str

    # Meteora
    meteora_api_key: str
    meteora_rpc_url: str

    # Shelby
    shelby_api_key: str

    # Trading params
    max_position_size: float
    min_pool_liquidity: float
    signal_confidence_threshold: float

    @classmethod
    def from_env(cls) -> "TradingConfig":
        """Load configuration from environment variables."""
        return cls(
            solana_private_key=os.getenv("SOLANA_PRIVATE_KEY", ""),
            solana_rpc_url=os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com"),
            meteora_api_key=os.getenv("METEORA_API_KEY", ""),
            meteora_rpc_url=os.getenv("METEORA_RPC_URL", "https://dlmm-api.meteora.ag"),
            shelby_api_key=os.getenv("SHELBY_API_KEY", ""),
            max_position_size=float(os.getenv("MAX_POSITION_SIZE", "0.1")),
            min_pool_liquidity=float(os.getenv("MIN_POOL_LIQUIDITY", "1000")),
            signal_confidence_threshold=float(os.getenv("SIGNAL_CONFIDENCE_THRESHOLD", "0.65")),
        )

    def validate(self) -> bool:
        """Validate required configuration fields."""
        if not self.solana_private_key:
            raise ValueError("SOLANA_PRIVATE_KEY is required")
        if not self.shelby_api_key:
            raise ValueError("SHELBY_API_KEY is required")
        if self.max_position_size <= 0:
            raise ValueError("MAX_POSITION_SIZE must be positive")
        if self.signal_confidence_threshold <= 0 or self.signal_confidence_threshold > 1:
            raise ValueError("SIGNAL_CONFIDENCE_THRESHOLD must be between 0 and 1")
        return True


# Global config instance
config = TradingConfig.from_env()
