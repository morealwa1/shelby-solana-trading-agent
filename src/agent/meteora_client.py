"""
Meteora DLMM API client.
Fetches pool data, liquidity info, and bin prices.
"""

import httpx
from dataclasses import dataclass
from typing import Optional
from .config import config


@dataclass
class PoolData:
    """Meteora DLMM pool data."""
    address: str
    mint_x: str
    mint_y: str
    liquidity: float
    bin_step: int
    fee_apr: float
    active_bin: int
    price: float


class MeteoraClient:
    """Client for Meteora DLMM API."""

    def __init__(self, rpc_url: Optional[str] = None, api_key: Optional[str] = None):
        self.rpc_url = rpc_url or config.meteora_rpc_url
        self.api_key = api_key or config.meteora_api_key
        self._client = httpx.AsyncClient(timeout=30.0)

    async def get_pools(self, limit: int = 50) -> list[PoolData]:
        """
        Fetch active DLMM pools from Meteora.

        Args:
            limit: Maximum number of pools to fetch

        Returns:
            List of PoolData objects
        """
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            response = self._client.get(
                f"{self.rpc_url}/v1/pools",
                params={"limit": limit},
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

            pools = []
            for pool in data.get("pools", []):
                pools.append(PoolData(
                    address=pool.get("address", ""),
                    mint_x=pool.get("mint_x", ""),
                    mint_y=pool.get("mint_y", ""),
                    liquidity=float(pool.get("liquidity", 0)),
                    bin_step=int(pool.get("bin_step", 0)),
                    fee_apr=float(pool.get("fee_apr", 0)),
                    active_bin=int(pool.get("active_bin", 0)),
                    price=float(pool.get("price", 0)),
                ))
            return pools

        except httpx.HTTPError as e:
            print(f"Meteora API error: {e}")
            return []

    async def get_pool_bins(self, pool_address: str) -> list[dict]:
        """
        Fetch bin data for a specific pool.

        Args:
            pool_address: The pool's Solana address

        Returns:
            List of bin data dictionaries
        """
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            response = self._client.get(
                f"{self.rpc_url}/v1/pools/{pool_address}/bins",
                headers=headers,
            )
            response.raise_for_status()
            return response.json().get("bins", [])

        except httpx.HTTPError as e:
            print(f"Failed to fetch bins for {pool_address}: {e}")
            return []

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()
