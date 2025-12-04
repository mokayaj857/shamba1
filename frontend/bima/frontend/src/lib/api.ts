// Mock data for development
const mockParcels = [
  {
    id: '1',
    title: 'Prime Agricultural Land',
    location: 'Nakuru',
    size: '5 acres',
    price: '5,000,000',
    status: 'pending',
    metadataHash: 'mock-hash-1'
  },
  {
    id: '2',
    title: 'Residential Plot',
    location: 'Kiambu',
    size: '0.25 acres',
    price: '8,000,000',
    status: 'verified',
    metadataHash: 'mock-hash-2'
  }
];

// Mock API client instance
export const api = {
  // Generic fetch wrapper
  async fetch(endpoint: string, options: RequestInit = {}) {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 300));
    
    // Mock responses based on endpoint
    if (endpoint.includes('/parcels')) {
      const status = endpoint.includes('pending') ? 'pending' : 
                   endpoint.includes('verified') ? 'verified' : 'all';
      
      const filtered = status === 'all' 
        ? mockParcels 
        : mockParcels.filter(p => p.status === status);
      
      return { items: [...filtered] };
    }

    // Default mock response
    return { success: true, endpoint, method: options.method || 'GET' };
  },

  // Mock IPFS methods
  ipfs: {
    async getJson(cid: string) {
      return {
        title: 'Land Title Document',
        description: 'Official land ownership document',
        owner: 'John Doe',
        location: 'Nairobi, Kenya',
        size: '5 acres',
        coordinates: { lat: -1.2921, lng: 36.8219 }
      };
    },
    
    async getRaw(cid: string) {
      // Return a simple text blob
      return new Blob(['Mock IPFS content for ' + cid], { type: 'text/plain' });
    }
  },

  // Mock parcel methods
  async getParcels(status: string = 'all') {
    return this.fetch(`/parcels?status=${status}`);
  },

  async getParcelById(id: string) {
    const parcel = mockParcels.find(p => p.id === id);
    if (!parcel) throw new Error('Parcel not found');
    return { ...parcel };
  },

  async createParcel(data: any) {
    const newParcel = {
      id: String(mockParcels.length + 1),
      ...data,
      status: 'pending',
      createdAt: new Date().toISOString()
    };
    mockParcels.push(newParcel);
    return newParcel;
  },

  async updateParcelStatus(id: string, status: string) {
    const index = mockParcels.findIndex(p => p.id === id);
    if (index === -1) throw new Error('Parcel not found');
    mockParcels[index].status = status;
    return mockParcels[index];
  }
};

export default api;
