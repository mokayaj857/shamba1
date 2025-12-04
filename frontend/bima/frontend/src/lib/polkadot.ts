import { ApiPromise, WsProvider } from '@polkadot/api';

// Create a singleton instance of the API
let apiInstance: ApiPromise | null = null;

export const initPolkadotApi = async () => {
  if (apiInstance) {
    return apiInstance;
  }

  try {
    // Connect to a Substrate node (you can change this to your node's WebSocket endpoint)
    const provider = new WsProvider('wss://rpc.polkadot.io');
    
    // Create the API instance
    apiInstance = await ApiPromise.create({ 
      provider,
      types: {
        // Add any custom types if needed
      },
    });

    // Listen to connection events
    provider.on('connected', () => {
      console.log('Connected to Polkadot network');
    });

    provider.on('error', (error) => {
      console.error('Polkadot provider error:', error);
    });

    return apiInstance;
  } catch (error) {
    console.error('Error initializing Polkadot API:', error);
    throw error;
  }
};

export const disconnectPolkadotApi = async () => {
  if (apiInstance) {
    try {
      await apiInstance.disconnect();
      apiInstance = null;
      console.log('Disconnected from Polkadot network');
    } catch (error) {
      console.error('Error disconnecting from Polkadot API:', error);
    }
  }
};

export const getApi = () => {
  if (!apiInstance) {
    throw new Error('Polkadot API not initialized. Call initPolkadotApi() first.');
  }
  return apiInstance;
};
