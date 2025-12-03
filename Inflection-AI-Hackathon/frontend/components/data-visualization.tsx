"use client"

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts"
import { TrendingUp, PieChartIcon, BarChart3, Calendar } from "lucide-react"

// API configuration
const API_BASE_URL = 'http://localhost:8000'

interface DataVisualizationProps {
  county: string
  score: number
}

export function DataVisualization({ county, score }: DataVisualizationProps) {
  const [historicalData, setHistoricalData] = useState<any>(null);
  const [factorData, setFactorData] = useState<any[]>([]);
  const [weatherData, setWeatherData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch real data from backend
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);

        // Fetch historical data
        const historicalResponse = await fetch(`${API_BASE_URL}/api/historical/${county}?year=2023`);
        if (historicalResponse.ok) {
          const historical = await historicalResponse.json();
          setHistoricalData(historical);
        }

        // Fetch feature importance for factor breakdown
        const featureResponse = await fetch(`${API_BASE_URL}/api/model/feature-importance`);
        if (featureResponse.ok) {
          const features = await featureResponse.json();
          const factorBreakdown = Object.entries(features.feature_importance).map(([name, value]: [string, any]) => ({
            name,
            value: Math.round(value * 100),
            color: getRandomColor(name)
          }));
          setFactorData(factorBreakdown);
        }

        // Fetch weather data
        const weatherResponse = await fetch(`${API_BASE_URL}/api/weather/${county}/monthly?year=2023`);
        if (weatherResponse.ok) {
          const weather = await weatherResponse.json();
          setWeatherData(weather);
        }

      } catch (err) {
        setError('Failed to load data');
        console.error('Error fetching data:', err);
      } finally {
        setIsLoading(false);
      }
    };

    if (county) {
      fetchData();
    }
  }, [county]);

  // Generate random colors for factors
  const getRandomColor = (name: string) => {
    const colors = ['#4caf50', '#2196f3', '#ff9800', '#9c27b0', '#607d8b', '#e91e63', '#00bcd4', '#8bc34a'];
    return colors[name.length % colors.length];
  };

  // Show loading state
  if (isLoading) {
    return (
      <Card className="animate-fade-in">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-2 text-foreground text-lg sm:text-xl">
            <BarChart3 className="h-5 w-5 text-primary flex-shrink-0" />
            <span className="text-balance">Data Analytics for {county}</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading data...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Show error state
  if (error) {
    return (
      <Card className="animate-fade-in">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-2 text-foreground text-lg sm:text-xl">
            <BarChart3 className="h-5 w-5 text-primary flex-shrink-0" />
            <span className="text-balance">Data Analytics for {county}</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center py-12">
          <div className="text-center text-red-500">
            <p>{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
            >
              Retry
            </button>
          </div>
        </CardContent>
      </Card>
    );
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-card border border-border rounded-lg p-3 shadow-lg max-w-xs">
          <p className="font-medium text-foreground text-sm sm:text-base">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-xs sm:text-sm mt-1" style={{ color: entry.color }}>
              {entry.name}: {entry.value}
              {entry.name === "Temperature"
                ? "°C"
                : entry.name === "Rainfall"
                  ? "mm"
                  : entry.name === "Humidity"
                    ? "%"
                    : "%"}
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  const CustomPieTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-card border border-border rounded-lg p-3 shadow-lg max-w-xs">
          <p className="font-medium text-foreground text-sm sm:text-base">{payload[0].name}</p>
          <p className="text-xs sm:text-sm text-muted-foreground mt-1">{payload[0].value}% contribution</p>
        </div>
      )
    }
    return null
  }

  return (
    <Card className="animate-fade-in">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-foreground text-lg sm:text-xl">
          <BarChart3 className="h-5 w-5 text-primary flex-shrink-0" />
          <span className="text-balance">Data Analytics for {county}</span>
        </CardTitle>
        <p className="text-sm text-muted-foreground">Detailed insights and historical trends</p>
      </CardHeader>
      <CardContent className="px-3 sm:px-6">
        <Tabs defaultValue="trends" className="w-full">
          <TabsList className="grid w-full grid-cols-3 h-12 sm:h-10 mb-6">
            <TabsTrigger
              value="trends"
              className="flex items-center gap-1 sm:gap-2 px-2 sm:px-4 min-h-[44px] text-xs sm:text-sm"
            >
              <TrendingUp className="h-4 w-4 flex-shrink-0" />
              <span className="hidden xs:inline sm:inline">Trends</span>
            </TabsTrigger>
            <TabsTrigger
              value="factors"
              className="flex items-center gap-1 sm:gap-2 px-2 sm:px-4 min-h-[44px] text-xs sm:text-sm"
            >
              <PieChartIcon className="h-4 w-4 flex-shrink-0" />
              <span className="hidden xs:inline sm:inline">Factors</span>
            </TabsTrigger>
            <TabsTrigger
              value="weather"
              className="flex items-center gap-1 sm:gap-2 px-2 sm:px-4 min-h-[44px] text-xs sm:text-sm"
            >
              <Calendar className="h-4 w-4 flex-shrink-0" />
              <span className="hidden xs:inline sm:inline">Weather</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="trends" className="mt-0">
            <div className="space-y-4">
              <div className="px-1">
                <h3 className="text-base sm:text-lg font-semibold text-foreground mb-2 text-balance">
                  Historical Resilience Trends
                </h3>
                <p className="text-xs sm:text-sm text-muted-foreground mb-4">
                  12-month resilience score progression with rainfall correlation
                </p>
              </div>
              <div className="h-64 sm:h-80 w-full overflow-hidden">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={historicalData?.monthly_resilience || []} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                    <XAxis
                      dataKey="month"
                      stroke="hsl(var(--muted-foreground))"
                      fontSize={10}
                      tick={{ fontSize: 10 }}
                      interval={0}
                      angle={-45}
                      textAnchor="end"
                      height={60}
                    />
                    <YAxis stroke="hsl(var(--muted-foreground))" fontSize={10} tick={{ fontSize: 10 }} width={40} />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend wrapperStyle={{ fontSize: "12px" }} iconSize={12} />
                    <Line
                      type="monotone"
                      dataKey="resilience"
                      stroke="hsl(var(--primary))"
                      strokeWidth={2}
                      dot={{ fill: "hsl(var(--primary))", strokeWidth: 2, r: 3 }}
                      activeDot={{ r: 5, stroke: "hsl(var(--primary))", strokeWidth: 2 }}
                      name="Resilience Score"
                    />
                    <Line
                      type="monotone"
                      dataKey="rainfall"
                      stroke="hsl(var(--chart-2))"
                      strokeWidth={2}
                      dot={{ fill: "hsl(var(--chart-2))", strokeWidth: 2, r: 2 }}
                      name="Rainfall (mm)"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="factors" className="mt-0">
            <div className="space-y-4">
              <div className="px-1">
                <h3 className="text-base sm:text-lg font-semibold text-foreground mb-2 text-balance">
                  Resilience Factor Breakdown
                </h3>
                <p className="text-xs sm:text-sm text-muted-foreground mb-4">
                  Contributing factors to your current resilience score
                </p>
              </div>
              <div className="h-64 sm:h-80 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={factorData}
                      cx="50%"
                      cy="50%"
                      innerRadius={40}
                      outerRadius={80}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {factorData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip content={<CustomPieTooltip />} />
                    <Legend
                      verticalAlign="bottom"
                      height={36}
                      wrapperStyle={{ fontSize: "11px", paddingTop: "10px" }}
                      formatter={(value, entry) => <span style={{ color: entry.color }}>{value}</span>}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="grid grid-cols-1 gap-3 mt-4 px-1">
                {factorData.map((factor, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-3 p-4 bg-muted/50 rounded-lg min-h-[60px] touch-manipulation"
                  >
                    <div className="w-4 h-4 rounded-full flex-shrink-0" style={{ backgroundColor: factor.color }} />
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm text-foreground truncate">{factor.name}</p>
                      <p className="text-xs text-muted-foreground">{factor.value}% contribution</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="weather" className="mt-0">
            <div className="space-y-4">
              <div className="px-1">
                <h3 className="text-base sm:text-lg font-semibold text-foreground mb-2 text-balance">
                  Monthly Weather Patterns
                </h3>
                <p className="text-xs sm:text-sm text-muted-foreground mb-4">
                  Rainfall, temperature, and humidity trends throughout the year
                </p>
              </div>
              <div className="h-64 sm:h-80 w-full overflow-hidden">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={weatherData?.monthly_data || []} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                    <XAxis
                      dataKey="month"
                      stroke="hsl(var(--muted-foreground))"
                      fontSize={10}
                      tick={{ fontSize: 10 }}
                      interval={0}
                      angle={-45}
                      textAnchor="end"
                      height={60}
                    />
                    <YAxis stroke="hsl(var(--muted-foreground))" fontSize={10} tick={{ fontSize: 10 }} width={40} />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend wrapperStyle={{ fontSize: "12px" }} iconSize={12} />
                    <Bar dataKey="rainfall" fill="hsl(var(--chart-2))" name="Rainfall (mm)" radius={[2, 2, 0, 0]} />
                    <Bar
                      dataKey="temperature"
                      fill="hsl(var(--secondary))"
                      name="Temperature (°C)"
                      radius={[2, 2, 0, 0]}
                    />
                    <Bar dataKey="humidity" fill="hsl(var(--chart-3))" name="Humidity (%)" radius={[2, 2, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
