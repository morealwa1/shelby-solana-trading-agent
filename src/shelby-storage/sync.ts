/**
 * Shelby Protocol blob upload for audit trail.
 * Stores trading signals as immutable blobs on Shelby decentralized storage.
 */

import { Shelby } from "@shelby-protocol/sdk";

export interface AuditBlob {
  timestamp: string;
  pool_address: string;
  signal: "BUY" | "SELL" | "HOLD";
  confidence: number;
  indicators: {
    rsi: number;
    volatility: number;
    trend: number;
  };
  reasoning: string;
  agent_version: string;
  shelby_blob_id?: string;
}

export class ShelbySync {
  private client: Shelby;
  private wallet: any;

  constructor(apiKey: string, wallet: any) {
    this.client = new Shelby({ apiKey });
    this.wallet = wallet;
  }

  /**
   * Upload a single audit blob to Shelby storage.
   *
   * @param blob - The audit data to store
   * @returns The blob ID from Shelby
   */
  async uploadAudit(blob: AuditBlob): Promise<string> {
    const blobId = await this.client.blobs.upload({
      data: JSON.stringify(blob),
      metadata: {
        type: "trading_signal",
        agent: "shelby-solana-trading-agent",
        version: blob.agent_version,
        pool: blob.pool_address,
        signal: blob.signal,
      },
      owner: this.wallet.publicKey.toBase58(),
    });

    return blobId;
  }

  /**
   * Upload multiple audit blobs in batch.
   *
   * @param blobs - Array of audit data
   * @returns Array of blob IDs
   */
  async uploadAuditBatch(blobs: AuditBlob[]): Promise<string[]> {
    const blobIds: string[] = [];

    for (const blob of blobs) {
      const blobId = await this.uploadAudit(blob);
      blobIds.push(blobId);
      console.log(`Uploaded blob: ${blobId}`);
    }

    return blobIds;
  }

  /**
   * Verify a blob exists on Shelby storage.
   *
   * @param blobId - The blob ID to verify
   * @returns True if blob exists
   */
  async verifyBlob(blobId: string): Promise<boolean> {
    try {
      const blob = await this.client.blobs.get(blobId);
      return blob !== null;
    } catch {
      return false;
    }
  }
}
