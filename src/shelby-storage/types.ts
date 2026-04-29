/**
 * TypeScript type definitions for Shelby Solana Trading Agent.
 */

export interface PoolData {
  address: string;
  mint_x: string;
  mint_y: string;
  liquidity: number;
  bin_step: number;
  fee_apr: number;
  active_bin: number;
  price: number;
}

export interface TradingSignal {
  pool_address: string;
  signal: "BUY" | "SELL" | "HOLD";
  confidence: number;
  rsi: number;
  volatility: number;
  trend: number;
  reasoning: string;
}

export interface AgentState {
  last_run: string | null;
  cycles_run: number;
  signals: TradingSignal[];
}
