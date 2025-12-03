// Wallet/HashPack integration removed.
// The platform will not use HashPack; these functions are stubs that
// provide clear errors or safe defaults when called.

export type WalletConnection = {
  accountIds: string[];
  pairingTopic: string;
};

export async function connectHashpack(_network: 'testnet' | 'mainnet' | 'previewnet' = 'testnet'): Promise<WalletConnection> {
  throw new Error('HashPack wallet support has been disabled in this build.');
}

export function getConnectedAccount(): string | null {
  return null;
}

export function clearHashpackConnection() {
  // no-op
}
