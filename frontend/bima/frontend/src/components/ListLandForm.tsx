import { motion } from "framer-motion";
import { 
  Shield, MapPin, Clock, CheckCircle2, AlertCircle, 
  FileText, Award, TrendingUp, 
  Eye, Download, Upload, Star, Badge, Coins,
  DollarSign, Users, Map, Wifi, Calculator, PieChart,
  Building, Satellite, RadioTower, Settings, TrendingDown,
  Layers, Zap, Shield as ShieldIcon, Cpu
} from "lucide-react";
import { useState, useEffect } from "react";
import { api } from '../lib/api';
import React from "react";
import { BIMA_CHAIN } from '@/chain';
import { useWalletStore } from '@/state/wallet';
import { useToast } from '@/components/toast/ToastProvider';

interface VerificationRequest {
  id: string;
  propertyId: string;
  location: string;
  area: string;
  sellerName: string;
  sellerDID: string;
  requestDate: string;
  deadline: string;
  status: 'pending' | 'in-progress' | 'completed' | 'disputed';
  priority: 'high' | 'medium' | 'low';
  documents: string[];
  compensation: string;
  requiredInspectors: number;
  currentInspectors: number;
}

interface InspectorStats {
  totalVerifications: number;
  completedThisMonth: number;
  reputationScore: number;
  earningsThisMonth: string;
  averageRating: number;
  specializations: string[];
}

interface CostSimulationInputs {
  areaSize: number;
  targetPopulation: number;
  deploymentStrategy: 'low-cost' | 'balanced' | 'high-performance';
  technology: 'lorawan' | 'cellular' | 'satellite' | 'fiber';
}

interface CostBreakdown {
  equipment: number;
  installation: number;
  maintenance: number;
  infrastructure: number;
  licensing: number;
  total: number;
}

interface ROIProjection {
  monthlyRevenue: number;
  paybackPeriod: number; // in months
  year1ROI: number;
  year3ROI: number;
  breakEvenPoint: number; // in months
}

type VerifyForm = { landId: string; role: 'Chief' | 'Surveyor'; name: string };
type Parcel = { landId: number; status: string; location?: string; size?: string; price?: string; metadataHash?: string };

const mockRequests: VerificationRequest[] = [
  {
    id: "VR-001",
    propertyId: "PROP-2024-001",
    location: "Nairobi, Karen Estate",
    area: "2.5 acres",
    sellerName: "John Kamau",
    sellerDID: "did:kilt:4tGLk...",
    requestDate: "2024-01-15",
    deadline: "2024-01-22",
    status: "pending",
    priority: "high",
    documents: ["Title Deed", "Survey Report", "Tax Certificate"],
    compensation: "2,500 DOT",
    requiredInspectors: 3,
    currentInspectors: 1
  },
  {
    id: "VR-002", 
    propertyId: "PROP-2024-002",
    location: "Kisumu, Milimani",
    area: "1.2 acres",
    sellerName: "Mary Wanjiku",
    sellerDID: "did:kilt:8Hk2c...",
    requestDate: "2024-01-14",
    deadline: "2024-01-21",
    status: "in-progress",
    priority: "medium",
    documents: ["Title Deed", "Survey Report"],
    compensation: "1,800 DOT",
    requiredInspectors: 2,
    currentInspectors: 2
  },
  {
    id: "VR-003",
    propertyId: "PROP-2024-003", 
    location: "Mombasa, Nyali",
    area: "0.8 acres",
    sellerName: "David Ochieng",
    sellerDID: "did:kilt:9Dx7p...",
    requestDate: "2024-01-13",
    deadline: "2024-01-20",
    status: "completed",
    priority: "low",
    documents: ["Title Deed", "Survey Report", "Environmental Clearance"],
    compensation: "2,000 DOT",
    requiredInspectors: 2,
    currentInspectors: 2
  }
];

const inspectorStats: InspectorStats = {
  totalVerifications: 47,
  completedThisMonth: 8,
  reputationScore: 94,
  earningsThisMonth: "18,500 DOT",
  averageRating: 4.8,
  specializations: ["Land Surveying", "Title Verification", "Environmental Assessment"]
};

const statusConfig = {
  pending: {
    label: "Pending Review",
    icon: Clock,
    color: "text-yellow-400",
    bg: "bg-yellow-500/20",
    border: "border-yellow-500/30"
  },
  'in-progress': {
    label: "In Progress", 
    icon: Eye,
    color: "text-blue-400",
    bg: "bg-blue-500/20",
    border: "border-blue-500/30"
  },
  completed: {
    label: "Completed",
    icon: CheckCircle2,
    color: "text-green-400", 
    bg: "bg-green-500/20",
    border: "border-green-500/30"
  },
  disputed: {
    label: "Disputed",
    icon: AlertCircle,
    color: "text-red-400",
    bg: "bg-red-500/20", 
    border: "border-red-500/30"
  }
};

const priorityConfig = {
  high: { color: "text-red-400", bg: "bg-red-500/20" },
  medium: { color: "text-yellow-400", bg: "bg-yellow-500/20" },
  low: { color: "text-green-400", bg: "bg-green-500/20" }
};

const technologyConfig = {
  lorawan: { 
    name: "LoRaWAN", 
    icon: RadioTower, 
    color: "text-purple-400", 
    bg: "bg-purple-500/20",
    description: "Long Range Wide Area Network - Low power, long range"
  },
  cellular: { 
    name: "Cellular", 
    icon: Wifi, 
    color: "text-blue-400", 
    bg: "bg-blue-500/20",
    description: "4G/5G Networks - High bandwidth, reliable"
  },
  satellite: { 
    name: "Satellite", 
    icon: Satellite, 
    color: "text-cyan-400", 
    bg: "bg-cyan-500/20",
    description: "Global coverage, independent of terrestrial infrastructure"
  },
  fiber: { 
    name: "Fiber Optic", 
    icon: Zap, 
    color: "text-green-400", 
    bg: "bg-green-500/20",
    description: "Ultra-high speed, low latency"
  }
};

const deploymentConfig = {
  'low-cost': { 
    name: "Low-Cost", 
    color: "text-green-400", 
    bg: "bg-green-500/20",
    multiplier: 0.8
  },
  'balanced': { 
    name: "Balanced", 
    color: "text-blue-400", 
    bg: "bg-blue-500/20",
    multiplier: 1.0
  },
  'high-performance': { 
    name: "High-Performance", 
    color: "text-purple-400", 
    bg: "bg-purple-500/20",
    multiplier: 1.4
  }
};

export default function InspectorDashboard() {
  const [activeTab, setActiveTab] = useState<'requests' | 'completed' | 'profile' | 'cost-simulation'>('requests');
  const [] = useState<VerificationRequest | null>(null);
  const [verifyForm, setVerifyForm] = useState<VerifyForm>({ landId: '', role: 'Chief', name: '' });
  const [parcels, setParcels] = useState<Parcel[]>([]);
  const [loadingParcels, setLoadingParcels] = useState<boolean>(false);
  
  // Cost Simulation State
  const [simulationInputs, setSimulationInputs] = useState<CostSimulationInputs>({
    areaSize: 10,
    targetPopulation: 1000,
    deploymentStrategy: 'low-cost',
    technology: 'lorawan'
  });
  
  const [costBreakdown, setCostBreakdown] = useState<CostBreakdown>({
    equipment: 0,
    installation: 0,
    maintenance: 0,
    infrastructure: 0,
    licensing: 0,
    total: 0
  });
  
  const [roiProjection, setRoiProjection] = useState<ROIProjection>({
    monthlyRevenue: 0,
    paybackPeriod: 0,
    year1ROI: 0,
    year3ROI: 0,
    breakEvenPoint: 0
  });
  
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  // Substrate-based verification
  const [substrateSender, setSubstrateSender] = useState('');
  const [substrateLandId, setSubstrateLandId] = useState('');
  const [substrateBusy, setSubstrateBusy] = useState(false);
  const [substrateMsg, setSubstrateMsg] = useState<string | null>(null);
  const walletAddress = useWalletStore((s) => s.address);
  const { push } = useToast();

  useEffect(() => {
    if (walletAddress) setSubstrateSender(walletAddress);
  }, [walletAddress]);

  // Calculate cost simulation when inputs change
  useEffect(() => {
    calculateCostSimulation();
  }, [simulationInputs]);

  function calculateCostSimulation() {
    const { areaSize, targetPopulation, deploymentStrategy, technology } = simulationInputs;
    
    // Base calculations
    const baseEquipmentCost = technology === 'lorawan' ? 50 : 
                             technology === 'cellular' ? 200 :
                             technology === 'satellite' ? 500 : 300;
    
    const baseInfrastructure = areaSize * (technology === 'fiber' ? 10000 : 
                                         technology === 'satellite' ? 2000 : 
                                         technology === 'cellular' ? 5000 : 2000);
    
    // Apply deployment strategy multiplier
    const strategyMultiplier = deploymentConfig[deploymentStrategy].multiplier;
    
    // Calculate costs
    const equipment = baseEquipmentCost * targetPopulation * 0.1 * strategyMultiplier;
    const infrastructure = baseInfrastructure * strategyMultiplier;
    const installation = (equipment + infrastructure) * 0.3;
    const maintenance = (equipment + infrastructure) * 0.15;
    const licensing = targetPopulation * 12 * strategyMultiplier;
    
    const total = equipment + installation + maintenance + infrastructure + licensing;
    
    setCostBreakdown({
      equipment: Math.round(equipment),
      installation: Math.round(installation),
      maintenance: Math.round(maintenance),
      infrastructure: Math.round(infrastructure),
      licensing: Math.round(licensing),
      total: Math.round(total)
    });
    
    // Calculate ROI
    const averageRevenuePerUser = 15; // USD per month
    const monthlyRevenue = Math.round(targetPopulation * averageRevenuePerUser * 0.7);
    const paybackPeriod = Math.round(total / monthlyRevenue);
    const year1Revenue = monthlyRevenue * 12;
    const year1ROI = Math.round(((year1Revenue - total) / total) * 100);
    const year3Revenue = monthlyRevenue * 36;
    const year3ROI = Math.round(((year3Revenue - total) / total) * 100);
    const breakEvenPoint = Math.ceil(total / monthlyRevenue);
    
    setRoiProjection({
      monthlyRevenue,
      paybackPeriod,
      year1ROI,
      year3ROI,
      breakEvenPoint
    });
  }

  async function verifyOnChain() {
    setSubstrateMsg(null);
    try {
      setSubstrateBusy(true);
      const idNum = Number(substrateLandId);
      if (!Number.isFinite(idNum)) throw new Error('Invalid landId');
      if (!substrateSender) throw new Error('Sender address required');
      const txHash = await BIMA_CHAIN.verifyWithRole(substrateSender, idNum, verifyForm.role);
      setSubstrateMsg(`Verification (${verifyForm.role}) submitted. Tx: ${txHash}`);
      push({ variant: 'success', title: `Verification (${verifyForm.role})`, description: `Included: ${txHash}` });
    } catch (e: any) {
      setSubstrateMsg(e?.message || String(e));
      push({ variant: 'error', title: 'Verification Failed', description: e?.message || String(e) });
    } finally {
      setSubstrateBusy(false);
    }
  }

  async function loadPendingParcels() {
    try {
      setLoadingParcels(true);
      const res = await api.getParcels('pending');
      const items = Array.isArray(res) ? res : (res?.items ?? res?.data ?? []);
      setParcels(items as Parcel[]);
    } catch (e: any) {
      setParcels([]);
    } finally {
      setLoadingParcels(false);
    }
  }

  useEffect(() => {
    loadPendingParcels();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const pendingRequests = mockRequests.filter(req => req.status === 'pending' || req.status === 'in-progress');
  const completedRequests = mockRequests.filter(req => req.status === 'completed');

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <section className="relative py-12 px-4 bg-gradient-to-br from-primary/5 via-background to-accent/5">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-8"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-primary/20 to-accent/20 border border-primary/20 mb-4">
              <Shield className="w-4 h-4 text-primary" />
              <span className="text-sm font-semibold">Trusted Inspector Portal</span>
            </div>
            
            <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent">
              Inspector Dashboard
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Verify land ownership, earn reputation NFTs, and build trust in the BIMA ecosystem
            </p>
          </motion.div>

          {/* Stats Grid */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
          >
            <div className="p-6 rounded-xl bg-card/40 backdrop-blur-sm border border-border/50">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-lg bg-blue-500/20">
                  <Award className="w-5 h-5 text-blue-400" />
                </div>
                <span className="text-sm text-muted-foreground">Total Verifications</span>
              </div>
              <div className="text-2xl font-bold text-foreground">{inspectorStats.totalVerifications}</div>
            </div>

            <div className="p-6 rounded-xl bg-card/40 backdrop-blur-sm border border-border/50">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-lg bg-green-500/20">
                  <TrendingUp className="w-5 h-5 text-green-400" />
                </div>
                <span className="text-sm text-muted-foreground">This Month</span>
              </div>
              <div className="text-2xl font-bold text-foreground">{inspectorStats.completedThisMonth}</div>
            </div>

            <div className="p-6 rounded-xl bg-card/40 backdrop-blur-sm border border-border/50">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-lg bg-purple-500/20">
                  <Star className="w-5 h-5 text-purple-400" />
                </div>
                <span className="text-sm text-muted-foreground">Reputation Score</span>
              </div>
              <div className="text-2xl font-bold text-foreground">{inspectorStats.reputationScore}/100</div>
            </div>

            <div className="p-6 rounded-xl bg-card/40 backdrop-blur-sm border border-border/50">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-lg bg-orange-500/20">
                  <Coins className="w-5 h-5 text-orange-400" />
                </div>
                <span className="text-sm text-muted-foreground">Earnings</span>
              </div>
              <div className="text-2xl font-bold text-foreground">{inspectorStats.earningsThisMonth}</div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Main Content */}
      <section className="py-12 px-4">
        <div className="max-w-7xl mx-auto">
          {/* Tab Navigation */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="flex flex-wrap gap-2 mb-8 p-1 bg-card/30 rounded-xl border border-border/50 w-fit"
          >
            {[
              { id: 'requests', label: 'Active Requests', icon: Clock },
              { id: 'completed', label: 'Completed', icon: CheckCircle2 },
              { id: 'profile', label: 'Profile & Reputation', icon: Badge },
              { id: 'cost-simulation', label: 'Cost Simulation', icon: Calculator }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'bg-primary text-primary-foreground shadow-lg'
                    : 'text-muted-foreground hover:text-foreground hover:bg-card/50'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                <span className="font-medium">{tab.label}</span>
              </button>
            ))}
          </motion.div>

          {/* Active Requests Tab */}
          {activeTab === 'requests' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="space-y-6"
            >
              {/* ... existing requests content ... */}
            </motion.div>
          )}

          {/* Completed Tab */}
          {activeTab === 'completed' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="space-y-6"
            >
              {/* ... existing completed content ... */}
            </motion.div>
          )}

          {/* Profile Tab */}
          {activeTab === 'profile' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="space-y-8"
            >
              {/* ... existing profile content ... */}
            </motion.div>
          )}

          {/* Cost Simulation Tab */}
          {activeTab === 'cost-simulation' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="space-y-8"
            >
              {/* Header */}
              <div className="text-center mb-8">
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-primary/20 to-green-500/20 border border-primary/30 mb-4">
                  <Calculator className="w-4 h-4 text-primary" />
                  <span className="text-sm font-semibold">Infrastructure Planning Tool</span>
                </div>
                <h2 className="text-3xl font-bold mb-4">Cost Simulation Module</h2>
                <p className="text-muted-foreground max-w-3xl mx-auto">
                  Simulate infrastructure costs based on area size and population. Plan budgets and estimate ROI for connectivity projects.
                </p>
              </div>

              {/* Main Content Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Input Panel */}
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="lg:col-span-2 space-y-6"
                >
                  <div className="p-6 rounded-2xl bg-card/40 backdrop-blur-sm border border-border/50">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="p-3 rounded-xl bg-gradient-to-br from-primary/20 to-accent/20">
                        <Settings className="w-6 h-6 text-primary" />
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-foreground">Simulation Parameters</h3>
                        <p className="text-sm text-muted-foreground">Adjust inputs to see real-time cost changes</p>
                      </div>
                    </div>

                    <div className="space-y-6">
                      {/* Area Size */}
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <label className="flex items-center gap-2 text-sm font-semibold text-foreground">
                            <Map className="w-4 h-4 text-blue-400" />
                            Area Size (sq km)
                          </label>
                          <span className="px-3 py-1 rounded-full bg-blue-500/20 text-blue-400 text-sm font-bold">
                            {simulationInputs.areaSize} km²
                          </span>
                        </div>
                        <input
                          type="range"
                          min="1"
                          max="1000"
                          value={simulationInputs.areaSize}
                          onChange={(e) => setSimulationInputs({...simulationInputs, areaSize: Number(e.target.value)})}
                          className="w-full h-2 bg-card rounded-lg appearance-none cursor-pointer accent-blue-500"
                        />
                        <div className="flex justify-between text-xs text-muted-foreground">
                          <span>1 km²</span>
                          <span>1000 km²</span>
                        </div>
                      </div>

                      {/* Target Population */}
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <label className="flex items-center gap-2 text-sm font-semibold text-foreground">
                            <Users className="w-4 h-4 text-green-400" />
                            Target Population
                          </label>
                          <span className="px-3 py-1 rounded-full bg-green-500/20 text-green-400 text-sm font-bold">
                            {simulationInputs.targetPopulation.toLocaleString()}
                          </span>
                        </div>
                        <input
                          type="range"
                          min="100"
                          max="1000000"
                          step="100"
                          value={simulationInputs.targetPopulation}
                          onChange={(e) => setSimulationInputs({...simulationInputs, targetPopulation: Number(e.target.value)})}
                          className="w-full h-2 bg-card rounded-lg appearance-none cursor-pointer accent-green-500"
                        />
                        <div className="flex justify-between text-xs text-muted-foreground">
                          <span>100 people</span>
                          <span>1M people</span>
                        </div>
                      </div>

                      {/* Deployment Strategy */}
                      <div className="space-y-3">
                        <label className="flex items-center gap-2 text-sm font-semibold text-foreground">
                          <Layers className="w-4 h-4 text-purple-400" />
                          Deployment Strategy
                        </label>
                        <div className="grid grid-cols-3 gap-3">
                          {Object.entries(deploymentConfig).map(([key, config]) => (
                            <button
                              key={key}
                              onClick={() => setSimulationInputs({...simulationInputs, deploymentStrategy: key as any})}
                              className={`flex flex-col items-center gap-2 p-3 rounded-xl border transition-all duration-200 ${
                                simulationInputs.deploymentStrategy === key
                                  ? `${config.bg} ${config.color} border-current shadow-lg`
                                  : 'border-border/50 hover:border-primary/50'
                              }`}
                            >
                              <TrendingUp className="w-5 h-5" />
                              <span className="text-xs font-medium">{config.name}</span>
                              <span className="text-xs opacity-75">×{config.multiplier.toFixed(1)}</span>
                            </button>
                          ))}
                        </div>
                      </div>

                      {/* Technology Selection */}
                      <div className="space-y-3">
                        <label className="flex items-center gap-2 text-sm font-semibold text-foreground">
                          <Wifi className="w-4 h-4 text-cyan-400" />
                          Technology
                        </label>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                          {Object.entries(technologyConfig).map(([key, tech]) => {
                            const Icon = tech.icon;
                            return (
                              <button
                                key={key}
                                onClick={() => setSimulationInputs({...simulationInputs, technology: key as any})}
                                className={`flex flex-col items-center gap-2 p-3 rounded-xl border transition-all duration-200 ${
                                  simulationInputs.technology === key
                                    ? `${tech.bg} ${tech.color} border-current shadow-lg`
                                    : 'border-border/50 hover:border-primary/50'
                                }`}
                              >
                                <Icon className="w-5 h-5" />
                                <span className="text-xs font-medium">{tech.name}</span>
                                <span className="text-xs opacity-75 text-center">{tech.description}</span>
                              </button>
                            );
                          })}
                        </div>
                      </div>

                      {/* Advanced Toggle */}
                      <button
                        onClick={() => setShowAdvanced(!showAdvanced)}
                        className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
                      >
                        <Zap className="w-4 h-4" />
                        {showAdvanced ? 'Hide Advanced Options' : 'Show Advanced Options'}
                      </button>

                      {showAdvanced && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          className="space-y-4 p-4 rounded-lg bg-card/30 border border-border/50"
                        >
                          <h4 className="font-semibold text-sm">Advanced Parameters</h4>
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <label className="text-xs text-muted-foreground mb-1 block">Terrain Complexity</label>
                              <select className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                                <option>Flat</option>
                                <option>Hilly</option>
                                <option>Mountainous</option>
                              </select>
                            </div>
                            <div>
                              <label className="text-xs text-muted-foreground mb-1 block">Infrastructure Age</label>
                              <select className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm">
                                <option>New Development</option>
                                <option>Existing Upgrade</option>
                                <option>Legacy Modernization</option>
                              </select>
                            </div>
                          </div>
                        </motion.div>
                      )}
                    </div>
                  </div>
                </motion.div>

                {/* Results Panel */}
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 }}
                  className="space-y-6"
                >
                  {/* Cost Breakdown */}
                  <div className="p-6 rounded-2xl bg-card/40 backdrop-blur-sm border border-border/50">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="p-3 rounded-xl bg-gradient-to-br from-green-500/20 to-blue-500/20">
                        <DollarSign className="w-6 h-6 text-green-400" />
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-foreground">Cost Breakdown</h3>
                        <p className="text-sm text-muted-foreground">Total: ${costBreakdown.total.toLocaleString()}</p>
                      </div>
                    </div>

                    <div className="space-y-4">
                      {[
                        { label: "Equipment", value: costBreakdown.equipment, color: "bg-blue-500", icon: Cpu },
                        { label: "Installation", value: costBreakdown.installation, color: "bg-purple-500", icon: Building },
                        { label: "Maintenance (annual)", value: costBreakdown.maintenance, color: "bg-yellow-500", icon: ShieldIcon },
                        { label: "Infrastructure", value: costBreakdown.infrastructure, color: "bg-green-500", icon: RadioTower },
                        { label: "Licensing", value: costBreakdown.licensing, color: "bg-red-500", icon: FileText }
                      ].map((item, index) => {
                        const percentage = (item.value / costBreakdown.total) * 100;
                        const Icon = item.icon;
                        return (
                          <div key={index} className="space-y-2">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <Icon className="w-4 h-4 text-muted-foreground" />
                                <span className="text-sm font-medium">{item.label}</span>
                              </div>
                              <span className="font-bold">${item.value.toLocaleString()}</span>
                            </div>
                            <div className="w-full h-2 bg-card rounded-full overflow-hidden">
                              <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${percentage}%` }}
                                transition={{ duration: 1, delay: index * 0.1 }}
                                className={`h-full rounded-full ${item.color} shadow-lg`}
                              />
                            </div>
                            <div className="text-right text-xs text-muted-foreground">
                              {percentage.toFixed(1)}% of total
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* ROI Projection */}
                  <div className="p-6 rounded-2xl bg-gradient-to-br from-primary/10 to-accent/10 backdrop-blur-sm border border-primary/20">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="p-3 rounded-xl bg-gradient-to-br from-orange-500/20 to-yellow-500/20">
                        <TrendingUp className="w-6 h-6 text-orange-400" />
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-foreground">ROI Projection</h3>
                        <p className="text-sm text-muted-foreground">Based on average revenue per user</p>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="p-3 rounded-lg bg-card/30 border border-border/50">
                          <div className="text-xs text-muted-foreground mb-1">Monthly Revenue</div>
                          <div className="text-xl font-bold text-green-400">
                            ${roiProjection.monthlyRevenue.toLocaleString()}
                          </div>
                        </div>
                        <div className="p-3 rounded-lg bg-card/30 border border-border/50">
                          <div className="text-xs text-muted-foreground mb-1">Payback Period</div>
                          <div className="text-xl font-bold text-blue-400">
                            {roiProjection.paybackPeriod} months
                          </div>
                        </div>
                      </div>

                      <div className="p-3 rounded-lg bg-card/30 border border-border/50">
                        <div className="text-xs text-muted-foreground mb-2">ROI Timeline</div>
                        <div className="space-y-3">
                          <div className="flex items-center justify-between">
                            <span className="text-sm">Year 1 ROI</span>
                            <span className={`font-bold ${roiProjection.year1ROI >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                              {roiProjection.year1ROI >= 0 ? '+' : ''}{roiProjection.year1ROI}%
                            </span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm">Year 3 ROI</span>
                            <span className={`font-bold ${roiProjection.year3ROI >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                              {roiProjection.year3ROI >= 0 ? '+' : ''}{roiProjection.year3ROI}%
                            </span>
                          </div>
                        </div>
                      </div>

                      <div className="p-3 rounded-lg bg-gradient-to-r from-green-500/10 to-blue-500/10 border border-green-500/20">
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="text-xs text-muted-foreground">Break-even Point</div>
                            <div className="text-lg font-bold text-foreground">
                              Month {roiProjection.breakEvenPoint}
                            </div>
                          </div>
                          <TrendingUp className="w-8 h-8 text-green-400" />
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="space-y-3">
                    <button className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-primary text-primary-foreground font-semibold hover:bg-primary/90 transition-colors">
                      <Download className="w-4 h-4" />
                      Export Simulation Report
                    </button>
                    <button className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-card border border-border/50 text-foreground font-semibold hover:border-primary/50 transition-colors">
                      <PieChart className="w-4 h-4" />
                      Compare Strategies
                    </button>
                  </div>
                </motion.div>
              </div>

              {/* Comparison Section */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="p-6 rounded-2xl bg-card/40 backdrop-blur-sm border border-border/50"
              >
                <h3 className="text-lg font-bold mb-6">Compare Deployment Strategies</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {Object.entries(deploymentConfig).map(([key, config]) => {
                    const calcCost = Math.round(costBreakdown.total * (config.multiplier / deploymentConfig[simulationInputs.deploymentStrategy].multiplier));
                    return (
                      <div
                        key={key}
                        className={`p-4 rounded-xl border ${config.bg} ${config.color} border-current/30`}
                      >
                        <div className="flex items-center gap-2 mb-3">
                          <div className={`p-2 rounded-lg ${config.bg}`}>
                            <TrendingUp className="w-4 h-4" />
                          </div>
                          <span className="font-semibold">{config.name}</span>
                        </div>
                        <div className="text-2xl font-bold mb-2">${calcCost.toLocaleString()}</div>
                        <div className="text-sm opacity-75 mb-3">
                          {key === 'low-cost' && 'Minimal viable deployment'}
                          {key === 'balanced' && 'Optimal performance per cost'}
                          {key === 'high-performance' && 'Maximum reliability & speed'}
                        </div>
                        <div className="text-xs space-y-1">
                          <div className="flex justify-between">
                            <span>Cost Factor:</span>
                            <span>×{config.multiplier.toFixed(1)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>ROI Time:</span>
                            <span>{Math.round(roiProjection.paybackPeriod * (config.multiplier / deploymentConfig[simulationInputs.deploymentStrategy].multiplier))}m</span>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </motion.div>
            </motion.div>
          )}
        </div>
      </section>
    </div>
  );
}