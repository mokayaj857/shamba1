import { motion } from "framer-motion";
import { TrendingUp, DollarSign, BarChart3, LineChart, Calendar, ArrowUpRight, CheckCircle } from "lucide-react";
import { useState } from "react";

// Sample data - will be replaced with backend API calls
const performanceData = [
  { month: "Jan", connectivity: 65, yield: 45, roi: 20 },
  { month: "Feb", connectivity: 70, yield: 52, roi: 28 },
  { month: "Mar", connectivity: 75, yield: 61, roi: 38 },
  { month: "Apr", connectivity: 82, yield: 68, roi: 45 },
  { month: "May", connectivity: 88, yield: 75, roi: 58 },
  { month: "Jun", connectivity: 92, yield: 82, roi: 67 },
];

const roiMetrics = [
  {
    label: "Total Investment",
    value: "$2.4M",
    subtext: "Infrastructure & Operations",
    icon: DollarSign,
    color: "from-emerald-500 to-teal-600",
    change: "Initial Capital"
  },
  {
    label: "Current Returns",
    value: "$1.6M",
    subtext: "Revenue Generated",
    icon: TrendingUp,
    color: "from-blue-500 to-indigo-600",
    change: "+23% Growth"
  },
  {
    label: "Break-Even Timeline",
    value: "18 months",
    subtext: "Projected Q3 2025",
    icon: Calendar,
    color: "from-purple-500 to-violet-600",
    change: "On Track"
  },
  {
    label: "ROI Percentage",
    value: "67%",
    subtext: "YTD Performance",
    icon: BarChart3,
    color: "from-orange-500 to-red-600",
    change: "+12% QoQ"
  }
];

const PerformanceChart = () => {
  const [activeMetric, setActiveMetric] = useState("connectivity");
  
  const maxValue = 100;
  const getMetricColor = () => {
    if (activeMetric === "connectivity") return "from-blue-500 to-indigo-600";
    if (activeMetric === "yield") return "from-emerald-500 to-teal-600";
    return "from-purple-500 to-violet-600";
  };
  
  return (
    <div className="space-y-8">
      {/* Metric Selector */}
      <div className="flex gap-3 flex-wrap justify-center">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setActiveMetric("connectivity")}
          className={`px-6 py-3 rounded-xl text-sm font-semibold transition-all duration-300 ${
            activeMetric === "connectivity"
              ? "bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg shadow-blue-500/30"
              : "bg-card/50 text-muted-foreground hover:bg-card border border-border"
          }`}
        >
          Connectivity Score
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setActiveMetric("yield")}
          className={`px-6 py-3 rounded-xl text-sm font-semibold transition-all duration-300 ${
            activeMetric === "yield"
              ? "bg-gradient-to-r from-emerald-500 to-teal-600 text-white shadow-lg shadow-emerald-500/30"
              : "bg-card/50 text-muted-foreground hover:bg-card border border-border"
          }`}
        >
          Yield Improvement
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setActiveMetric("roi")}
          className={`px-6 py-3 rounded-xl text-sm font-semibold transition-all duration-300 ${
            activeMetric === "roi"
              ? "bg-gradient-to-r from-purple-500 to-violet-600 text-white shadow-lg shadow-purple-500/30"
              : "bg-card/50 text-muted-foreground hover:bg-card border border-border"
          }`}
        >
          ROI Progress
        </motion.button>
      </div>

      {/* Chart */}
      <div className="relative h-80 flex items-end justify-between gap-4 p-8 rounded-2xl bg-card/30 border border-border/50">
        {/* Y-axis labels */}
        <div className="absolute left-4 top-8 bottom-16 flex flex-col justify-between text-xs text-muted-foreground">
          <span>100%</span>
          <span>75%</span>
          <span>50%</span>
          <span>25%</span>
          <span>0%</span>
        </div>

        {/* Chart bars */}
        <div className="flex-1 flex items-end justify-around gap-3 ml-8">
          {performanceData.map((data, index) => {
            const value = data[activeMetric];
            const height = (value / maxValue) * 100;
            
            return (
              <div key={data.month} className="flex-1 flex flex-col items-center gap-3">
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: `${height}%`, opacity: 1 }}
                  transition={{ duration: 0.8, delay: index * 0.1, ease: "easeOut" }}
                  className={`w-full rounded-t-xl bg-gradient-to-t ${getMetricColor()} relative group cursor-pointer min-h-[20px] shadow-lg`}
                  whileHover={{ scale: 1.05 }}
                >
                  {/* Hover tooltip */}
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    whileHover={{ opacity: 1, y: -40 }}
                    className="absolute -top-12 left-1/2 -translate-x-1/2 bg-card border border-primary/50 px-3 py-2 rounded-lg text-sm font-bold whitespace-nowrap shadow-xl z-10"
                  >
                    <span className="text-primary">{value}%</span>
                  </motion.div>
                  
                  {/* Shine effect */}
                  <div className="absolute inset-0 bg-gradient-to-t from-transparent to-white/20 rounded-t-xl" />
                </motion.div>
                <span className="text-sm text-muted-foreground font-semibold">{data.month}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Chart Legend & Stats */}
      <div className="flex items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <div className={`w-4 h-4 rounded bg-gradient-to-r ${getMetricColor()}`} />
          <span className="text-sm text-muted-foreground font-medium">
            {activeMetric === "connectivity" && "Network Coverage Performance"}
            {activeMetric === "yield" && "Agricultural Yield Growth"}
            {activeMetric === "roi" && "Return on Investment Trend"}
          </span>
        </div>
        <div className="flex items-center gap-2 text-emerald-400">
          <ArrowUpRight className="w-4 h-4" />
          <span className="text-sm font-semibold">
            {activeMetric === "connectivity" && "+42%"}
            {activeMetric === "yield" && "+82%"}
            {activeMetric === "roi" && "+235%"}
          </span>
        </div>
      </div>
    </div>
  );
};

export default function ImpactTracker() {
  return (
    <div className="min-h-screen bg-background">
      <section className="relative py-24 px-4 overflow-hidden">
        {/* Animated Background */}
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-accent/5" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_50%,rgba(120,119,198,0.1),transparent_50%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_50%,rgba(74,222,128,0.1),transparent_50%)]" />
        
        {/* Animated Grid */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(120,119,198,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(120,119,198,0.05)_1px,transparent_1px)] bg-[size:64px_64px] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_50%,black,transparent)]" />
        
        {/* Floating Orbs */}
        <motion.div
          className="absolute top-20 left-10 w-72 h-72 bg-primary/20 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
            x: [0, 30, 0],
            y: [0, -30, 0],
          }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute bottom-20 right-10 w-96 h-96 bg-accent/20 rounded-full blur-3xl"
          animate={{
            scale: [1.2, 1, 1.2],
            opacity: [0.3, 0.5, 0.3],
            x: [0, -40, 0],
            y: [0, 40, 0],
          }}
          transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
        />

        <div className="relative max-w-7xl mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-20"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              whileInView={{ scale: 1, opacity: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-primary/20 to-accent/20 border border-primary/20 mb-6"
            >
              <BarChart3 className="w-4 h-4 text-primary" />
              <span className="text-sm font-semibold text-foreground">Real-Time Analytics</span>
            </motion.div>

            <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent animate-gradient-shift bg-[length:200%_auto]">
              Impact Tracker
            </h1>
            
            <motion.p
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8"
            >
              Track connectivity scores, yield improvements, and ROI timelines with actionable insights
            </motion.p>

            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4 }}
              className="flex flex-wrap justify-center gap-4 text-sm"
            >
              <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full">📊 ROI Analysis</span>
              <span className="px-3 py-1 bg-emerald-500/20 text-emerald-400 rounded-full">📈 Performance Tracking</span>
              <span className="px-3 py-1 bg-purple-500/20 text-purple-400 rounded-full">⚡ Real-Time Data</span>
            </motion.div>
          </motion.div>

          {/* ROI Analysis Section */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="mb-24"
          >
            <div className="text-center mb-12">
              <h2 className="text-4xl font-bold mb-3">
                <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">ROI Analysis</span>
              </h2>
              <p className="text-muted-foreground">Financial performance metrics and investment returns</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {roiMetrics.map((metric, index) => {
                const MetricIcon = metric.icon;
                return (
                  <motion.div
                    key={metric.label}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: index * 0.1 }}
                    whileHover={{ y: -8, scale: 1.02 }}
                    className="relative p-8 rounded-2xl bg-card/50 backdrop-blur-sm border border-border hover:border-primary/50 transition-all duration-300 hover:shadow-2xl group"
                  >
                    {/* Icon */}
                    <motion.div
                      animate={{
                        rotate: [0, 5, -5, 0],
                      }}
                      transition={{
                        duration: 3,
                        repeat: Infinity,
                        ease: "easeInOut"
                      }}
                      className="mb-6"
                    >
                      <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${metric.color} p-1 group-hover:scale-110 transition-transform duration-300`}>
                        <div className="w-full h-full bg-card rounded-xl flex items-center justify-center">
                          <MetricIcon className="w-8 h-8 text-primary" />
                        </div>
                      </div>
                    </motion.div>

                    {/* Content */}
                    <p className="text-sm text-muted-foreground mb-2">{metric.label}</p>
                    <p className="text-3xl font-bold text-foreground mb-2">{metric.value}</p>
                    <p className="text-xs text-muted-foreground mb-4">{metric.subtext}</p>

                    {/* Change indicator */}
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-primary" />
                      <span className="text-xs text-primary font-semibold">{metric.change}</span>
                    </div>

                    {/* Hover Glow Effect */}
                    <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-primary/0 to-accent/0 group-hover:from-primary/5 group-hover:to-accent/5 transition-all duration-300 pointer-events-none" />
                  </motion.div>
                );
              })}
            </div>
          </motion.div>

          {/* Performance Over Time Section */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <div className="text-center mb-12">
              <h2 className="text-4xl font-bold mb-3">
                <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">Performance Over Time</span>
              </h2>
              <p className="text-muted-foreground">Monitor progress across connectivity, yield, and ROI metrics</p>
            </div>

            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4 }}
              className="p-8 rounded-2xl bg-card/50 backdrop-blur-sm border border-border hover:border-primary/30 transition-all duration-300"
            >
              <PerformanceChart />
            </motion.div>
          </motion.div>

          {/* Bottom CTA */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.6 }}
            className="mt-20 text-center"
          >
            <div className="inline-flex items-center gap-3 px-6 py-3 rounded-full bg-card/50 backdrop-blur-sm border border-primary/20">
              <motion.div
                animate={{
                  scale: [1, 1.2, 1],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
                className="w-2 h-2 rounded-full bg-primary"
              />
              <span className="text-sm font-medium text-foreground">
                Live data updates • Powered by <span className="font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">real-time analytics</span>
              </span>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}