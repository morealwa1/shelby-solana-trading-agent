"""
Shelby Solana Trading Agent - Main Entry Point.

Monitors Meteora DLMM pools, generates trading signals,
and stores audit trail on Shelby Protocol.
"""

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from agent.config import config
from agent.meteora_client import MeteoraClient
from agent.signals import SignalGenerator
from agent.telegram_notifier import telegram_notifier, TradeType


DATA_DIR = Path(__file__).parent.parent / "data"
STATE_FILE = DATA_DIR / "state.json"
AUDIT_FILE = DATA_DIR / "audit.json"


def save_state(data: dict) -> None:
    """Save agent state to local cache."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_state() -> dict:
    """Load agent state from local cache."""
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"last_run": None, "signals": []}


def append_audit(signal_data: dict) -> None:
    """Append signal to audit trail."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    audits = []
    if AUDIT_FILE.exists():
        with open(AUDIT_FILE, "r") as f:
            audits = json.load(f)

    audits.append(signal_data)

    with open(AUDIT_FILE, "w") as f:
        json.dump(audits, f, indent=2)


async def run_agent_cycle() -> None:
    """
    Single agent cycle:
    1. Fetch pools from Meteora
    2. Generate signals
    3. Save to local state + audit trail
    """
    print(f"[{datetime.now(timezone.utc).isoformat()}] Agent cycle starting...")

    client = MeteoraClient()
    generator = SignalGenerator()

    try:
        # Fetch pools
        pools = await client.get_pools(limit=20)

        if not pools:
            print("No pools fetched from Meteora")
            return

        print(f"Fetched {len(pools)} pools")

        # Filter by minimum liquidity
        eligible_pools = [
            p for p in pools
            if p.liquidity >= config.min_pool_liquidity
        ]
        print(f"Eligible pools (liquidity >= {config.min_pool_liquidity}): {len(eligible_pools)}")

        signals_generated = []

        for pool in eligible_pools[:5]:  # Process top 5
            signal = generator.generate_signal(pool)

            signal_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "pool_address": signal.pool_address,
                "signal": signal.signal,
                "confidence": round(signal.confidence, 3),
                "indicators": {
                    "rsi": round(signal.rsi, 2),
                    "volatility": round(signal.volatility, 3),
                    "trend": round(signal.trend, 3),
                },
                "reasoning": signal.reasoning,
                "pool_liquidity": pool.liquidity,
                "fee_apr": pool.fee_apr,
                "agent_version": "1.0.0",
            }

            # Save to audit trail
            append_audit(signal_data)

            # Log signal
            print(f"  [{pool.address[:8]}...] {signal.signal} | "
                  f"Confidence: {signal.confidence:.2f} | "
                  f"RSI: {signal.rsi:.1f}")

            # Send Telegram alert for trade signals
            try:
                trade_type = TradeType(signal.signal.upper())
                telegram_notifier.send_trade_alert(
                    trade_type=trade_type,
                    token_symbol=pool.address[:8],
                    amount=signal.confidence,
                    pool_address=pool.address,
                )
            except ValueError:
                # Unknown signal type, skip alert
                pass

            signals_generated.append(signal_data)

        # Update state
        state = load_state()
        state["last_run"] = datetime.now(timezone.utc).isoformat()
        state["cycles_run"] = state.get("cycles_run", 0) + 1
        state["signals"] = signals_generated
        save_state(state)

        print(f"Cycle complete. {len(signals_generated)} signals generated.")

        # TODO: Integrate Shelby SDK to upload audit trail
        # shelby_sync.upload_audit(audit_data)

    finally:
        await client.close()


def main():
    """Main entry point."""
    print("=" * 50)
    print("Shelby Solana Trading Agent v1.0.0")
    print("=" * 50)

    try:
        config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Copy .env.example to .env and fill in your credentials.")
        sys.exit(1)

    print(f"RPC: {config.solana_rpc_url}")
    print(f"Meteora: {config.meteora_rpc_url}")
    print(f"Min Liquidity: {config.min_pool_liquidity}")
    print(f"Confidence Threshold: {config.signal_confidence_threshold}")
    print("-" * 50)

    asyncio.run(run_agent_cycle())


if __name__ == "__main__":
    main()
