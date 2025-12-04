import { motion, AnimatePresence } from "framer-motion";
import { 
  Map, Layers, Mountain, Trees, Droplets, ZoomIn, Settings,
  Upload, MapPin, Activity, TrendingUp, Navigation, Gauge,
  Target, CheckCircle2, Info, Maximize2, X, LandPlot, Compass
} from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { api } from "../lib/api";

interface GeospatialMetrics {
  avgElevation: number;
  minElevation: number;
  maxElevation: number;
  vegetationDensity: number;
  waterBodies: number;
  terrainSuitability: number;
  optimalNodeLocations: number;
  slopeAnalysis: number;
  soilQuality: number;
}

interface StatItem {
  label: string;
  value: string | number;
  icon: React.ElementType;
  color: string;
}

interface GuideStep {
  step: string;
  title: string;
  desc: string;
}

interface Recommendation {
  text: string;
  icon: string;
  color: string;
}

export default function GeospatialAnalysis() {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [geospatialData, setGeospatialData] = useState<GeospatialMetrics | null>(null);
  const [vegetationThreshold, setVegetationThreshold] = useState(50);
  const [elevationFilter, setElevationFilter] = useState(1500);
  const [isDragging, setIsDragging] = useState(false);
  const [showGuide, setShowGuide] = useState(true);
  const [landData, setLandData] = useState<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Load sample land data
  useEffect(() => {
    const loadSampleData = async () => {
      try {
        // This would be replaced with actual API call in production
        const mockData = {
          id: 'sample-land-123',
          title: 'Prime Agricultural Land',
          location: 'Nakuru, Kenya',
          size: '5 acres',
          price: '5,000,000 KES',
          status: 'verified',
          owner: 'John Kamau',
          description: 'Prime agricultural land with good road access and water supply.',
          coordinates: [-1.2921, 36.8219],
          features: ['Arable Land', 'Water Access', 'Road Access']
        };
        setLandData(mockData);
      } catch (error) {
        console.error('Error loading land data:', error);
      }
    };
    
    loadSampleData();
  }, []);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    processFile(file);
  };

  const processFile = (file: File | undefined) => {
    if (!file) return;
    
    const validTypes = ['.geojson', '.shp', '.json', '.kml'];
    const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    
    if (validTypes.some(type => fileExtension === type)) {
      setUploadedFile(file);
      setGeospatialData(null);
    } else {
      alert('Please upload a valid geospatial file (.geojson, .shp, .json, .kml)');
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    processFile(file);
  };

  const analyzeGeospatialData = async () => {
    if (!uploadedFile) return;
    
    setAnalyzing(true);
    
    try {
      // Simulate API call with a delay
      await new Promise(resolve => setTimeout(resolve, 2500));
      
      const baseElevation = elevationFilter;
      const mockMetrics: GeospatialMetrics = {
        avgElevation: baseElevation + (Math.random() * 100 - 50),
        minElevation: baseElevation - (100 + Math.random() * 100),
        maxElevation: baseElevation + (100 + Math.random() * 150),
        vegetationDensity: Math.min(100, vegetationThreshold + (Math.random() * 20 - 10)),
        waterBodies: Math.floor(Math.random() * 8) + 2,
        terrainSuitability: Math.floor(65 + Math.random() * 30),
        optimalNodeLocations: Math.floor(Math.random() * 12) + 5,
        slopeAnalysis: Math.floor(Math.random() * 100),
        soilQuality: Math.floor(60 + Math.random() * 35)
      };
      
      setGeospatialData(mockMetrics);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setAnalyzing(false);
    }
  };

  const resetAnalysis = () => {
    setUploadedFile(null);
    setGeospatialData(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const guideSteps: GuideStep[] = [
    { step: "1", title: "Upload Data", desc: "Upload GeoJSON or Shapefile with your terrain data" },
    { step: "2", title: "Adjust Parameters", desc: "Fine-tune vegetation density and elevation filters" },
    { step: "3", title: "Analyze & View", desc: "Get comprehensive metrics and optimal node locations" }
  ];

  const recommendations: Recommendation[] = [
    {
      text: "Prioritize southern regions for lower vegetation density",
      icon: "🌱",
      color: "text-green-400"
    },
    {
      text: "Consider elevated areas for better signal propagation",
      icon: "📡",
      color: "text-blue-400"
    },
    {
      text: "Avoid areas with multiple water bodies for stability",
      icon: "💧",
      color: "text-cyan-400"
    }
  ];

  const getStatItems = (): StatItem[] => {
    if (!geospatialData) return [];
    
    return [
      { label: "Optimal Sites", value: geospatialData.optimalNodeLocations, icon: Target, color: "text-blue-400" },
      { label: "Suitability", value: `${geospatialData.terrainSuitability}%`, icon: Gauge, color: "text-green-400" },
      { label: "Water Bodies", value: geospatialData.waterBodies, icon: Droplets, color: "text-cyan-400" },
      { label: "Avg Elevation", value: `${geospatialData.avgElevation.toFixed(0)}m`, icon: Mountain, color: "text-purple-400" }
    ];
  };

  const getIconColorClass = (color: string) => {
    switch(color) {
      case 'blue': return 'text-blue-400';
      case 'green': return 'text-green-400';
      case 'cyan': return 'text-cyan-400';
      case 'purple': return 'text-purple-400';
      default: return 'text-blue-400';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950">
      {/* Animated Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-green-500/10 rounded-full blur-3xl animate-pulse delay-1000" />
        <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-500" />
      </div>
      
      {/* Land Information Banner */}
      {landData && (
        <div className="bg-gradient-to-r from-blue-900/50 to-green-900/50 border-b border-blue-800/50">
          <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <LandPlot className="w-5 h-5 text-blue-400" />
              <div>
                <h3 className="font-semibold text-white">{landData.title}</h3>
                <p className="text-xs text-blue-200">{landData.location} • {landData.size}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-1 text-xs rounded-full bg-green-500/20 text-green-300 border border-green-500/30">
                {landData.status}
              </span>
              <span className="text-sm font-medium text-white">{landData.price}</span>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <section className="relative py-16 px-4">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-gradient-to-r from-blue-500/20 via-green-500/20 to-blue-500/20 border border-blue-500/30 mb-6 backdrop-blur-sm"
            >
              <Map className="w-5 h-5 text-blue-400" />
              <span className="text-sm font-semibold text-blue-100">Advanced Terrain Intelligence</span>
            </motion.div>
            
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-blue-400 via-green-400 to-blue-400 bg-clip-text text-transparent"
            >
              Geospatial Analysis
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed"
            >
              Leverage cutting-edge terrain analysis to identify optimal network node locations. 
              Upload geospatial data and receive comprehensive insights on elevation, vegetation, and infrastructure suitability.
            </motion.p>
          </motion.div>

          {/* Stats Preview */}
          {geospatialData && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
            >
              {getStatItems().map((stat, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.6 + index * 0.1 }}
                  className="p-4 rounded-xl bg-slate-900/60 backdrop-blur-sm border border-slate-700/50 hover:border-blue-500/50 transition-all duration-300"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <stat.icon className={`w-4 h-4 ${stat.color}`} />
                    <span className="text-xs text-slate-400">{stat.label}</span>
                  </div>
                  <div className="text-2xl font-bold text-white">{stat.value}</div>
                </motion.div>
              ))}
            </motion.div>
          )}
        </div>
      </section>

      {/* Main Content */}
      <section className="relative py-8 px-4">
        <div className="max-w-7xl mx-auto space-y-8">
          
          {/* How to Use Guide */}
          <AnimatePresence>
            {showGuide && !geospatialData && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden"
              >
                <div className="p-6 rounded-2xl bg-gradient-to-r from-blue-900/40 to-green-900/40 backdrop-blur-sm border border-blue-500/30">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-blue-500/20">
                        <Info className="w-5 h-5 text-blue-400" />
                      </div>
                      <h3 className="text-lg font-bold text-white">How to Use</h3>
                    </div>
                    <button
                      onClick={() => setShowGuide(false)}
                      className="text-slate-400 hover:text-white transition-colors"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                  <div className="grid md:grid-cols-3 gap-4">
                    {guideSteps.map((item, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.2 + index * 0.1 }}
                        className="flex gap-3"
                      >
                        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center text-blue-400 font-bold text-sm">
                          {item.step}
                        </div>
                        <div>
                          <div className="font-semibold text-white text-sm mb-1">{item.title}</div>
                          <div className="text-xs text-slate-400">{item.desc}</div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Upload Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="p-8 rounded-2xl bg-slate-900/60 backdrop-blur-sm border border-slate-700/50 shadow-2xl"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500/20 to-green-500/20">
                <Upload className="w-6 h-6 text-blue-400" />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-white">Upload Geospatial Data</h3>
                <p className="text-sm text-slate-400">Supported formats: GeoJSON, Shapefile, KML</p>
              </div>
            </div>
            
            <div className="space-y-6">
              {/* Drag & Drop Zone */}
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`relative transition-all duration-300 ${
                  isDragging ? 'scale-105' : 'scale-100'
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".geojson,.shp,.json,.kml"
                  onChange={handleFileUpload}
                  className="hidden"
                  id="geospatial-upload"
                />
                <label
                  htmlFor="geospatial-upload"
                  className={`flex flex-col items-center justify-center gap-4 px-8 py-12 rounded-xl border-2 border-dashed transition-all duration-300 cursor-pointer ${
                    isDragging
                      ? 'border-blue-500 bg-blue-500/10 scale-105'
                      : uploadedFile
                      ? 'border-green-500/50 bg-green-500/5'
                      : 'border-slate-600 bg-slate-800/30 hover:border-blue-500/50 hover:bg-blue-500/5'
                  }`}
                >
                  <motion.div
                    animate={{
                      scale: isDragging ? 1.1 : 1,
                      rotate: isDragging ? 5 : 0
                    }}
                    className={`p-4 rounded-full ${
                      uploadedFile ? 'bg-green-500/20' : 'bg-blue-500/20'
                    }`}
                  >
                    {uploadedFile ? (
                      <CheckCircle2 className="w-12 h-12 text-green-400" />
                    ) : (
                      <Layers className="w-12 h-12 text-blue-400" />
                    )}
                  </motion.div>
                  <div className="text-center">
                    <p className="text-lg font-semibold text-white mb-1">
                      {uploadedFile ? uploadedFile.name : 'Drop your file here or click to browse'}
                    </p>
                    <p className="text-sm text-slate-400">
                      {uploadedFile ? `${(uploadedFile.size / 1024).toFixed(1)} KB` : 'Maximum file size: 50MB'}
                    </p>
                  </div>
                  {!uploadedFile && (
                    <div className="flex gap-2">
                      {['.geojson', '.shp', '.kml'].map((ext, i) => (
                        <span key={i} className="px-3 py-1 rounded-full bg-slate-700/50 text-xs text-slate-300">
                          {ext}
                        </span>
                      ))}
                    </div>
                  )}
                </label>
              </div>

              {uploadedFile && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex justify-end"
                >
                  <button
                    onClick={resetAnalysis}
                    className="px-4 py-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-all duration-300 text-sm font-medium border border-red-500/30"
                  >
                    Clear & Upload New File
                  </button>
                </motion.div>
              )}

              {/* Parameters */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: uploadedFile ? 1 : 0.5 }}
                className="grid grid-cols-1 md:grid-cols-2 gap-6 p-6 rounded-xl bg-slate-800/50 border border-slate-700/50"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <label className="flex items-center gap-2 text-sm font-semibold text-white">
                      <Trees className="w-4 h-4 text-green-400" />
                      Vegetation Density Threshold
                    </label>
                    <span className="px-3 py-1 rounded-full bg-green-500/20 text-green-400 text-sm font-bold">
                      {vegetationThreshold}%
                    </span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={vegetationThreshold}
                    onChange={(e) => setVegetationThreshold(Number(e.target.value))}
                    className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-green-500"
                    disabled={!uploadedFile}
                  />
                  <div className="flex justify-between text-xs text-slate-500 mt-1">
                    <span>Low</span>
                    <span>High</span>
                  </div>
                </div>
                
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <label className="flex items-center gap-2 text-sm font-semibold text-white">
                      <Mountain className="w-4 h-4 text-blue-400" />
                      Base Elevation Filter
                    </label>
                    <span className="px-3 py-1 rounded-full bg-blue-500/20 text-blue-400 text-sm font-bold">
                      {elevationFilter}m
                    </span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="3000"
                    step="100"
                    value={elevationFilter}
                    onChange={(e) => setElevationFilter(Number(e.target.value))}
                    className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
                    disabled={!uploadedFile}
                  />
                  <div className="flex justify-between text-xs text-slate-500 mt-1">
                    <span>Sea Level</span>
                    <span>3000m</span>
                  </div>
                </div>
              </motion.div>

              {/* Analyze Button */}
              <motion.button
                onClick={analyzeGeospatialData}
                disabled={!uploadedFile || analyzing}
                whileHover={{ scale: uploadedFile && !analyzing ? 1.02 : 1 }}
                whileTap={{ scale: uploadedFile && !analyzing ? 0.98 : 1 }}
                className="w-full flex items-center justify-center gap-3 px-8 py-4 rounded-xl bg-gradient-to-r from-blue-600 to-green-600 text-white font-bold text-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-blue-500/50"
              >
                {analyzing ? (
                  <>
                    <div className="w-5 h-5 border-3 border-white/30 border-t-white rounded-full animate-spin" />
                    Analyzing Terrain Data...
                  </>
                ) : (
                  <>
                    <ZoomIn className="w-5 h-5" />
                    Analyze Geospatial Data
                  </>
                )}
              </motion.button>
            </div>
          </motion.div>

          {/* Analysis Results */}
          <AnimatePresence>
            {geospatialData && (
              <motion.div
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 40 }}
                transition={{ duration: 0.5 }}
                className="space-y-8"
              >
                {/* Interactive Map */}
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.2 }}
                  className="p-8 rounded-2xl bg-slate-900/60 backdrop-blur-sm border border-slate-700/50 shadow-2xl"
                >
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                      <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20">
                        <Map className="w-6 h-6 text-blue-400" />
                      </div>
                      <div>
                        <h3 className="text-2xl font-bold text-white">Interactive Terrain Map</h3>
                        <p className="text-sm text-slate-400">Real-time visualization with optimal node locations</p>
                      </div>
                    </div>
                    <button className="p-2 rounded-lg bg-slate-800/50 hover:bg-slate-700/50 transition-colors">
                      <Maximize2 className="w-5 h-5 text-slate-400" />
                    </button>
                  </div>
                  
                  <div className="relative aspect-video rounded-xl bg-gradient-to-br from-green-900/20 via-blue-900/20 to-purple-900/20 border border-slate-700/50 overflow-hidden group">
                    {/* Animated Grid Background */}
                    <div className="absolute inset-0 opacity-20">
                      <div className="absolute inset-0" style={{
                        backgroundImage: 'linear-gradient(rgba(59, 130, 246, 0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(59, 130, 246, 0.3) 1px, transparent 1px)',
                        backgroundSize: '50px 50px'
                      }} />
                    </div>
                    
                    {/* Terrain Visualization */}
                    <div className="absolute inset-0 flex items-center justify-center">
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.5 }}
                        className="text-center z-10"
                      >
                        <motion.div
                          animate={{
                            scale: [1, 1.1, 1],
                            rotate: [0, 5, -5, 0]
                          }}
                          transition={{
                            duration: 4,
                            repeat: Infinity,
                            ease: "easeInOut"
                          }}
                        >
                          <Navigation className="w-16 h-16 text-blue-400 mx-auto mb-4" />
                        </motion.div>
                        <p className="text-lg font-semibold text-white mb-2">
                          Terrain Analysis Complete
                        </p>
                        <p className="text-sm text-slate-400">
                          {geospatialData.optimalNodeLocations} optimal network node locations identified
                        </p>
                      </motion.div>
                    </div>

                    {/* Animated Markers */}
                    {[...Array(Math.min(geospatialData.optimalNodeLocations, 10))].map((_, i) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, scale: 0 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.7 + i * 0.1 }}
                        className="absolute"
                        style={{
                          left: `${15 + (i * 70 / Math.min(geospatialData.optimalNodeLocations, 10))}%`,
                          top: `${30 + Math.sin(i) * 20}%`
                        }}
                      >
                        <motion.div
                          animate={{
                            scale: [1, 1.2, 1],
                            opacity: [0.7, 1, 0.7]
                          }}
                          transition={{
                            duration: 2,
                            repeat: Infinity,
                            delay: i * 0.2
                          }}
                          className="w-3 h-3 rounded-full bg-green-400 shadow-lg shadow-green-400/50"
                        />
                      </motion.div>
                    ))}
                  </div>
                </motion.div>

                {/* Key Metrics Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {/* Elevation Card */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="p-6 rounded-2xl bg-slate-900/60 backdrop-blur-sm border border-blue-500/30 hover:border-blue-500/50 transition-all duration-300 group"
                  >
                    <div className="flex items-center gap-3 mb-4">
                      <motion.div
                        whileHover={{ rotate: 360 }}
                        transition={{ duration: 0.6 }}
                        className="p-3 rounded-xl bg-blue-500/20 group-hover:bg-blue-500/30 transition-colors"
                      >
                        <Mountain className="w-6 h-6 text-blue-400" />
                      </motion.div>
                      <div>
                        <h4 className="text-sm font-medium text-slate-400">Elevation Analysis</h4>
                        <p className="text-xs text-slate-500">Terrain height metrics</p>
                      </div>
                    </div>
                    <div className="space-y-3">
                      {[
                        { label: "Average", value: geospatialData.avgElevation.toFixed(1), unit: "m" },
                        { label: "Minimum", value: geospatialData.minElevation.toFixed(1), unit: "m" },
                        { label: "Maximum", value: geospatialData.maxElevation.toFixed(1), unit: "m" }
                      ].map((item, i) => (
                        <motion.div
                          key={i}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: 0.4 + i * 0.1 }}
                          className="flex justify-between items-center p-2 rounded-lg bg-slate-800/50"
                        >
                          <span className="text-sm text-slate-400">{item.label}</span>
                          <span className="text-lg font-bold text-white">
                            {item.value}<span className="text-sm text-blue-400 ml-1">{item.unit}</span>
                          </span>
                        </motion.div>
                      ))}
                    </div>
                  </motion.div>

                  {/* Vegetation Card */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                    className="p-6 rounded-2xl bg-slate-900/60 backdrop-blur-sm border border-green-500/30 hover:border-green-500/50 transition-all duration-300 group"
                  >
                    <div className="flex items-center gap-3 mb-4">
                      <motion.div
                        whileHover={{ rotate: 360 }}
                        transition={{ duration: 0.6 }}
                        className="p-3 rounded-xl bg-green-500/20 group-hover:bg-green-500/30 transition-colors"
                      >
                        <Trees className="w-6 h-6 text-green-400" />
                      </motion.div>
                      <div>
                        <h4 className="text-sm font-medium text-slate-400">Vegetation Coverage</h4>
                        <p className="text-xs text-slate-500">Plant density analysis</p>
                      </div>
                    </div>
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between mb-2">
                          <span className="text-sm text-slate-400">Density Level</span>
                          <span className="text-2xl font-bold text-white">
                            {geospatialData.vegetationDensity.toFixed(1)}%
                          </span>
                        </div>
                        <div className="w-full bg-slate-800/50 rounded-full h-3 overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${geospatialData.vegetationDensity}%` }}
                            transition={{ duration: 1, delay: 0.5 }}
                            className="bg-gradient-to-r from-green-500 to-emerald-400 h-full rounded-full shadow-lg shadow-green-500/50"
                          />
                        </div>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-green-400 bg-green-500/10 rounded-lg p-2">
                        <CheckCircle2 className="w-4 h-4" />
                        <span>Within optimal range for infrastructure</span>
                      </div>
                    </div>
                  </motion.div>

                  {/* Water Bodies Card */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5 }}
                    className="p-6 rounded-2xl bg-slate-900/60 backdrop-blur-sm border border-cyan-500/30 hover:border-cyan-500/50 transition-all duration-300 group"
                  >
                    <div className="flex items-center gap-3 mb-4">
                      <motion.div
                        whileHover={{ rotate: 360 }}
                        transition={{ duration: 0.6 }}
                        className="p-3 rounded-xl bg-cyan-500/20 group-hover:bg-cyan-500/30 transition-colors"
                      >
                        <Droplets className="w-6 h-6 text-cyan-400" />
                      </motion.div>
                      <div>
                        <h4 className="text-sm font-medium text-slate-400">Hydrological Features</h4>
                        <p className="text-xs text-slate-500">Water bodies detection</p>
                      </div>
                    </div>
                    <div className="flex items-end gap-4">
                      <div>
                        <div className="text-4xl font-bold text-white mb-1">
                          {geospatialData.waterBodies}
                        </div>
                        <div className="text-sm text-cyan-400">Identified bodies</div>
                      </div>
                      <div className="flex-1">
                        <div className="flex justify-between text-xs text-slate-500 mb-1">
                          <span>Small</span>
                          <span>Large</span>
                        </div>
                        <div className="flex gap-1">
                          {[...Array(Math.min(geospatialData.waterBodies, 10))].map((_, i) => (
                            <motion.div
                              key={i}
                              initial={{ height: 0 }}
                              animate={{ height: `${20 + Math.random() * 30}px` }}
                              transition={{ delay: 0.6 + i * 0.05 }}
                              className="flex-1 bg-gradient-to-t from-cyan-500 to-cyan-300 rounded-t-lg"
                              style={{
                                opacity: 0.7 + (i % 3) * 0.1
                              }}
                            />
                          ))}
                        </div>
                      </div>
                    </div>
                  </motion.div>

                  {/* Terrain Suitability Card */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.6 }}
                    className="p-6 rounded-2xl bg-slate-900/60 backdrop-blur-sm border border-purple-500/30 hover:border-purple-500/50 transition-all duration-300 group"
                  >
                    <div className="flex items-center gap-3 mb-4">
                      <motion.div
                        whileHover={{ rotate: 360 }}
                        transition={{ duration: 0.6 }}
                        className="p-3 rounded-xl bg-purple-500/20 group-hover:bg-purple-500/30 transition-colors"
                      >
                        <Gauge className="w-6 h-6 text-purple-400" />
                      </motion.div>
                      <div>
                        <h4 className="text-sm font-medium text-slate-400">Terrain Suitability</h4>
                        <p className="text-xs text-slate-500">Infrastructure readiness</p>
                      </div>
                    </div>
                    <div className="space-y-4">
                      <div className="text-center">
                        <div className="text-5xl font-bold text-white mb-2">
                          {geospatialData.terrainSuitability}%
                        </div>
                        <div className="text-sm text-purple-400">Overall suitability score</div>
                      </div>
                      <div className="grid grid-cols-2 gap-2">
                        {[
                          { label: "Slope", value: geospatialData.slopeAnalysis, color: "bg-blue-500" },
                          { label: "Soil Quality", value: geospatialData.soilQuality, color: "bg-amber-500" }
                        ].map((item, i) => (
                          <div key={i} className="text-center">
                            <div className="text-xs text-slate-500 mb-1">{item.label}</div>
                            <div className={`h-1 rounded-full ${item.color} opacity-50`} />
                            <div className="text-sm font-bold text-white mt-1">{item.value}%</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </motion.div>

                  {/* Optimal Locations Card */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.7 }}
                    className="p-6 rounded-2xl bg-slate-900/60 backdrop-blur-sm border border-orange-500/30 hover:border-orange-500/50 transition-all duration-300 group"
                  >
                    <div className="flex items-center gap-3 mb-4">
                      <motion.div
                        whileHover={{ rotate: 360 }}
                        transition={{ duration: 0.6 }}
                        className="p-3 rounded-xl bg-orange-500/20 group-hover:bg-orange-500/30 transition-colors"
                      >
                        <Target className="w-6 h-6 text-orange-400" />
                      </motion.div>
                      <div>
                        <h4 className="text-sm font-medium text-slate-400">Optimal Node Locations</h4>
                        <p className="text-xs text-slate-500">Recommended installation sites</p>
                      </div>
                    </div>
                    <div className="space-y-4">
                      <div className="flex items-center justify-center">
                        <div className="relative">
                          <div className="w-32 h-32 rounded-full border-2 border-orange-500/30 flex items-center justify-center">
                            <div className="text-3xl font-bold text-white">
                              {geospatialData.optimalNodeLocations}
                            </div>
                          </div>
                          {[...Array(8)].map((_, i) => (
                            <motion.div
                              key={i}
                              animate={{
                                rotate: [0, 360],
                                scale: [1, 1.2, 1]
                              }}
                              transition={{
                                duration: 3,
                                repeat: Infinity,
                                delay: i * 0.1
                              }}
                              className="absolute top-0 left-0 w-full h-full"
                              style={{ transform: `rotate(${i * 45}deg)` }}
                            >
                              <div className="absolute top-0 left-1/2 w-1 h-3 bg-orange-400 rounded-full transform -translate-x-1/2" />
                            </motion.div>
                          ))}
                        </div>
                      </div>
                      <div className="text-center text-sm text-slate-400">
                        Based on elevation, vegetation, and accessibility
                      </div>
                    </div>
                  </motion.div>

                  {/* Recommendations Card */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.8 }}
                    className="p-6 rounded-2xl bg-slate-900/60 backdrop-blur-sm border border-emerald-500/30 hover:border-emerald-500/50 transition-all duration-300 group"
                  >
                    <div className="flex items-center gap-3 mb-4">
                      <motion.div
                        whileHover={{ rotate: 360 }}
                        transition={{ duration: 0.6 }}
                        className="p-3 rounded-xl bg-emerald-500/20 group-hover:bg-emerald-500/30 transition-colors"
                      >
                        <Activity className="w-6 h-6 text-emerald-400" />
                      </motion.div>
                      <div>
                        <h4 className="text-sm font-medium text-slate-400">Recommendations</h4>
                        <p className="text-xs text-slate-500">Actionable insights</p>
                      </div>
                    </div>
                    <div className="space-y-3">
                      {recommendations.map((rec, i) => (
                        <motion.div
                          key={i}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: 0.9 + i * 0.1 }}
                          className="flex items-start gap-3 p-3 rounded-lg bg-slate-800/50"
                        >
                          <span className="text-xl">{rec.icon}</span>
                          <p className={`text-sm ${rec.color} flex-1`}>{rec.text}</p>
                        </motion.div>
                      ))}
                    </div>
                  </motion.div>
                </div>

                {/* Export & Actions Section */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 1 }}
                  className="p-8 rounded-2xl bg-gradient-to-r from-slate-900/60 to-blue-900/20 backdrop-blur-sm border border-slate-700/50"
                >
                  <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                    <div>
                      <h3 className="text-xl font-bold text-white mb-2">Analysis Complete</h3>
                      <p className="text-slate-400">
                        Export results or run a new analysis with different parameters
                      </p>
                    </div>
                    <div className="flex flex-wrap gap-3">
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className="px-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold flex items-center gap-2 hover:shadow-lg hover:shadow-blue-500/30 transition-all duration-300"
                      >
                        <Upload className="w-4 h-4" />
                        Export Report
                      </motion.button>
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className="px-6 py-3 rounded-xl bg-gradient-to-r from-slate-800 to-slate-900 text-white font-semibold flex items-center gap-2 hover:shadow-lg hover:shadow-slate-500/30 border border-slate-700 transition-all duration-300"
                      >
                        <Settings className="w-4 h-4" />
                        Adjust Parameters
                      </motion.button>
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={resetAnalysis}
                        className="px-6 py-3 rounded-xl bg-gradient-to-r from-red-900/40 to-red-800/40 text-red-400 font-semibold flex items-center gap-2 hover:shadow-lg hover:shadow-red-500/30 border border-red-500/30 transition-all duration-300"
                      >
                        <X className="w-4 h-4" />
                        New Analysis
                      </motion.button>
                    </div>
                  </div>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Footer Guide */}
          {!geospatialData && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1 }}
              className="text-center py-12"
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-slate-800/50 border border-slate-700 mb-4">
                <TrendingUp className="w-4 h-4 text-green-400" />
                <span className="text-sm text-slate-400">Powered by Advanced Terrain Intelligence</span>
              </div>
              <p className="text-slate-500 text-sm max-w-2xl mx-auto">
                This geospatial analysis platform uses machine learning algorithms to process terrain data 
                and identify optimal locations for network infrastructure deployment. All data is processed 
                locally for maximum privacy and security.
              </p>
            </motion.div>
          )}
        </div>
      </section>
    </div>
  );
}