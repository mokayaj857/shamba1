"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Calculator, DollarSign, TrendingUp, Target, AlertTriangle, CheckCircle, Gift, Sprout, Zap } from "lucide-react"

interface InputCostCalculatorProps {
  county: string
  score: number
}

interface CropInput {
  id: string
  name: string
  category: "seeds" | "fertilizer" | "pesticide" | "labor" | "equipment"
  unitCost: number
  unit: string
  recommendedQuantity: number
  isOptional: boolean
  description: string
}

interface CropCostData {
  cropName: string
  inputs: CropInput[]
  expectedYield: number
  marketPrice: number
  subsidyAvailable: boolean
  subsidyAmount: number
}

interface ROIAnalysis {
  totalCost: number
  grossRevenue: number
  netProfit: number
  roiPercentage: number
  breakEvenYield: number
  profitMargin: number
}

export function InputCostCalculator({ county, score }: InputCostCalculatorProps) {
  const [selectedCrop, setSelectedCrop] = useState<string>("maize")
  const [farmSize, setFarmSize] = useState<number>(1)
  const [customInputs, setCustomInputs] = useState<{ [key: string]: number }>({})
  const [roiAnalysis, setROIAnalysis] = useState<ROIAnalysis | null>(null)
  const [cropCostData, setCropCostData] = useState<{ [key: string]: CropCostData }>({});
  const [isLoading, setIsLoading] = useState(true);

  // Show loading state while fetching data
  if (isLoading) {
    return (
      <Card className="animate-fade-in">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-2 text-foreground text-lg sm:text-xl">
            <Calculator className="h-5 w-5 text-primary flex-shrink-0" />
            <span className="text-balance">Input Cost Calculator for {county}</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading market data...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Fetch real market data from backend
  useEffect(() => {
    if (!county) return

    const fetchMarketData = async () => {
      try {
        setIsLoading(true);

        // Fetch market costs and prices
        const [costsResponse, pricesResponse] = await Promise.all([
          fetch('/api/market/costs'),
          fetch('/api/market/prices')
        ]);

        if (costsResponse.ok && pricesResponse.ok) {
          const costs = await costsResponse.json();
          const prices = await pricesResponse.json();

          const marketCosts = costs.market_data;
          const marketPrices = prices.prices;

          // Update crop cost data with real market values
          setCropCostData({
            maize: {
              cropName: "Drought-Tolerant Maize",
              inputs: [
                {
                  id: "seeds",
                  name: "Certified Seeds (DH04/KH500-23A)",
                  category: "seeds",
                  unitCost: marketPrices.inputs?.seed_per_kg || 350,
                  unit: "kg",
                  recommendedQuantity: 25,
                  isOptional: false,
                  description: "Drought-tolerant hybrid maize varieties",
                },
                {
                  id: "dap",
                  name: "DAP Fertilizer",
                  category: "fertilizer",
                  unitCost: marketPrices.inputs?.fertilizer_per_50kg || 5500,
                  unit: "50kg bag",
                  recommendedQuantity: 2,
                  isOptional: false,
                  description: "Diammonium Phosphate for planting",
                },
                {
                  id: "urea",
                  name: "Urea Fertilizer",
                  category: "fertilizer",
                  unitCost: marketPrices.inputs?.fertilizer_per_50kg || 4800,
                  unit: "50kg bag",
                  recommendedQuantity: 1.5,
                  isOptional: false,
                  description: "Top dressing fertilizer",
                },
                {
                  id: "pesticide",
                  name: "Pesticide/Herbicide",
                  category: "pesticide",
                  unitCost: marketPrices.inputs?.pesticide_per_liter || 1200,
                  unit: "liter",
                  recommendedQuantity: 2,
                  isOptional: true,
                  description: "Crop protection chemicals",
                },
                {
                  id: "labor",
                  name: "Labor (Planting to Harvest)",
                  category: "labor",
                  unitCost: marketPrices.inputs?.labor_per_day || 15000,
                  unit: "per acre",
                  recommendedQuantity: 1,
                  isOptional: false,
                  description: "Land preparation, planting, weeding, harvesting",
                },
              ],
              expectedYield: 30,
              marketPrice: marketPrices.maize?.price_per_kg || 3200,
              subsidyAvailable: true,
              subsidyAmount: 6000,
            },
            sorghum: {
              cropName: "Sorghum",
              inputs: [
                {
                  id: "seeds",
                  name: "Sorghum Seeds (Gadam/Serena)",
                  category: "seeds",
                  unitCost: marketPrices.inputs?.seed_per_kg || 200,
                  unit: "kg",
                  recommendedQuantity: 15,
                  isOptional: false,
                  description: "Drought-tolerant sorghum varieties",
                },
                {
                  id: "dap",
                  name: "DAP Fertilizer",
                  category: "fertilizer",
                  unitCost: marketPrices.inputs?.fertilizer_per_50kg || 5500,
                  unit: "50kg bag",
                  recommendedQuantity: 1,
                  isOptional: false,
                  description: "Diammonium Phosphate for planting",
                },
                {
                  id: "labor",
                  name: "Labor (Planting to Harvest)",
                  category: "labor",
                  unitCost: marketPrices.inputs?.labor_per_day || 12000,
                  unit: "per acre",
                  recommendedQuantity: 1,
                  isOptional: false,
                  description: "Land preparation, planting, weeding, harvesting",
                },
              ],
              expectedYield: 20,
              marketPrice: marketPrices.maize?.price_per_kg || 2800,
              subsidyAvailable: true,
              subsidyAmount: 4000,
            },
            beans: {
              cropName: "Common Beans",
              inputs: [
                {
                  id: "seeds",
                  name: "Bean Seeds (KAT B1/Rosecoco)",
                  category: "seeds",
                  unitCost: 400,
                  unit: "kg",
                  recommendedQuantity: 60,
                  isOptional: false,
                  description: "High-yielding bean varieties",
                },
                {
                  id: "dap",
                  name: "DAP Fertilizer",
                  category: "fertilizer",
                  unitCost: 5500,
                  unit: "50kg bag",
                  recommendedQuantity: 1,
                  isOptional: false,
                  description: "Diammonium Phosphate for planting",
                },
                {
                  id: "pesticide",
                  name: "Fungicide/Insecticide",
                  category: "pesticide",
                  unitCost: 1500,
                  unit: "liter",
                  recommendedQuantity: 1.5,
                  isOptional: false,
                  description: "Disease and pest control",
                },
                {
                  id: "labor",
                  name: "Labor (Planting to Harvest)",
                  category: "labor",
                  unitCost: 18000,
                  unit: "per acre",
                  recommendedQuantity: 1,
                  isOptional: false,
                  description: "Land preparation, planting, weeding, harvesting",
                },
              ],
              expectedYield: 10,
              marketPrice: 8500,
              subsidyAvailable: false,
              subsidyAmount: 0,
            },
          });
        }
      } catch (error) {
        console.error('Failed to fetch market data:', error);
        // Fallback to default costs if API fails
        setCropCostData({
          maize: {
            cropName: "Drought-Tolerant Maize",
            inputs: [
              {
                id: "seeds",
                name: "Certified Seeds (DH04/KH500-23A)",
                category: "seeds",
                unitCost: 350,
                unit: "kg",
                recommendedQuantity: 25,
                isOptional: false,
                description: "Drought-tolerant hybrid maize varieties",
              },
              {
                id: "dap",
                name: "DAP Fertilizer",
                category: "fertilizer",
                unitCost: 5500,
                unit: "50kg bag",
                recommendedQuantity: 2,
                isOptional: false,
                description: "Diammonium Phosphate for planting",
              },
              {
                id: "urea",
                name: "Urea Fertilizer",
                category: "fertilizer",
                unitCost: 4800,
                unit: "50kg bag",
                recommendedQuantity: 1.5,
                isOptional: false,
                description: "Top dressing fertilizer",
              },
              {
                id: "pesticide",
                name: "Pesticide/Herbicide",
                category: "pesticide",
                unitCost: 1200,
                unit: "liter",
                recommendedQuantity: 2,
                isOptional: true,
                description: "Crop protection chemicals",
              },
              {
                id: "labor",
                name: "Labor (Planting to Harvest)",
                category: "labor",
                unitCost: 15000,
                unit: "per acre",
                recommendedQuantity: 1,
                isOptional: false,
                description: "Land preparation, planting, weeding, harvesting",
              },
            ],
            expectedYield: 30,
            marketPrice: 3200,
            subsidyAvailable: true,
            subsidyAmount: 6000,
          },
          sorghum: {
            cropName: "Sorghum",
            inputs: [
              {
                id: "seeds",
                name: "Sorghum Seeds (Gadam/Serena)",
                category: "seeds",
                unitCost: 200,
                unit: "kg",
                recommendedQuantity: 15,
                isOptional: false,
                description: "Drought-tolerant sorghum varieties",
              },
              {
                id: "dap",
                name: "DAP Fertilizer",
                category: "fertilizer",
                unitCost: 5500,
                unit: "50kg bag",
                recommendedQuantity: 1,
                isOptional: false,
                description: "Diammonium Phosphate for planting",
              },
              {
                id: "labor",
                name: "Labor (Planting to Harvest)",
                category: "labor",
                unitCost: 12000,
                unit: "per acre",
                recommendedQuantity: 1,
                isOptional: false,
                description: "Land preparation, planting, weeding, harvesting",
              },
            ],
            expectedYield: 20,
            marketPrice: 2800,
            subsidyAvailable: true,
            subsidyAmount: 4000,
          },
          beans: {
            cropName: "Common Beans",
            inputs: [
              {
                id: "seeds",
                name: "Bean Seeds (KAT B1/Rosecoco)",
                category: "seeds",
                unitCost: 400,
                unit: "kg",
                recommendedQuantity: 60,
                isOptional: false,
                description: "High-yielding bean varieties",
              },
              {
                id: "dap",
                name: "DAP Fertilizer",
                category: "fertilizer",
                unitCost: 5500,
                unit: "50kg bag",
                recommendedQuantity: 1,
                isOptional: false,
                description: "Diammonium Phosphate for planting",
              },
              {
                id: "pesticide",
                name: "Fungicide/Insecticide",
                category: "pesticide",
                unitCost: 1500,
                unit: "liter",
                recommendedQuantity: 1.5,
                isOptional: false,
                description: "Disease and pest control",
              },
              {
                id: "labor",
                name: "Labor (Planting to Harvest)",
                category: "labor",
                unitCost: 18000,
                unit: "per acre",
                recommendedQuantity: 1,
                isOptional: false,
                description: "Land preparation, planting, weeding, harvesting",
              },
            ],
            expectedYield: 10,
            marketPrice: 8500,
            subsidyAvailable: false,
            subsidyAmount: 0,
          },
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchMarketData();
  }, [county]); // Added county dependency

  // Government subsidy programs
  const subsidyPrograms = [
    {
      name: "National Cereals and Produce Board (NCPB) Subsidy",
      description: "Subsidized fertilizer and seeds for cereal crops",
      eligibility: "Small-scale farmers with less than 5 acres",
      benefit: "Up to 50% discount on fertilizer and certified seeds",
      applicationPeriod: "March-April, September-October",
    },
    {
      name: "Agricultural Finance Corporation (AFC) Loans",
      description: "Low-interest loans for agricultural inputs",
      eligibility: "Farmers with collateral or group guarantee",
      benefit: "Interest rates as low as 12% per annum",
      applicationPeriod: "Year-round",
    },
    {
      name: "County Government Support",
      description: "Local government agricultural support programs",
      eligibility: "Registered farmers in the county",
      benefit: "Varies by county - seeds, equipment, training",
      applicationPeriod: "Varies by county",
    },
  ]

  const calculateROI = () => {
    const cropData = cropCostData[selectedCrop]
    if (!cropData) return

    let totalCost = 0
    cropData.inputs.forEach((input) => {
      const quantity = customInputs[input.id] || input.recommendedQuantity
      totalCost += input.unitCost * quantity * farmSize
    })

    const subsidyReduction = cropData.subsidyAvailable ? cropData.subsidyAmount * farmSize : 0
    const netCost = totalCost - subsidyReduction

    const grossRevenue = cropData.expectedYield * cropData.marketPrice * farmSize
    const netProfit = grossRevenue - netCost
    const roiPercentage = (netProfit / netCost) * 100
    const breakEvenYield = netCost / cropData.marketPrice
    const profitMargin = (netProfit / grossRevenue) * 100

    setROIAnalysis({
      totalCost: netCost,
      grossRevenue,
      netProfit,
      roiPercentage,
      breakEvenYield,
      profitMargin,
    })
  }

  useEffect(() => {
    calculateROI()
  }, [selectedCrop, farmSize, customInputs])

  const handleInputChange = (inputId: string, value: number) => {
    setCustomInputs((prev) => ({
      ...prev,
      [inputId]: value,
    }))
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "seeds":
        return <Sprout className="h-4 w-4" />
      case "fertilizer":
        return <Zap className="h-4 w-4" />
      case "pesticide":
        return <Target className="h-4 w-4" />
      case "labor":
        return <Calculator className="h-4 w-4" />
      default:
        return <DollarSign className="h-4 w-4" />
    }
  }

  const getROIColor = (roi: number) => {
    if (roi >= 50) return "text-green-600"
    if (roi >= 20) return "text-orange-600"
    return "text-red-600"
  }

  const currentCropData = cropCostData[selectedCrop]

  return (
    <Card className="animate-fade-in">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-foreground text-lg sm:text-xl">
          <Calculator className="h-5 w-5 text-primary flex-shrink-0" />
          <span className="text-balance">Input Cost Calculator & ROI Predictor - {county}</span>
        </CardTitle>
        <p className="text-xs sm:text-sm text-muted-foreground">
          Calculate costs, predict returns, and analyze break-even points
        </p>
      </CardHeader>
      <CardContent className="px-3 sm:px-6">
        <Tabs defaultValue="calculator" className="w-full">
          <TabsList className="grid w-full grid-cols-4 h-12 sm:h-10 mb-6">
            <TabsTrigger
              value="calculator"
              className="flex items-center gap-1 px-1 sm:px-2 min-h-[44px] text-xs sm:text-sm"
            >
              <Calculator className="h-4 w-4 flex-shrink-0" />
              <span className="hidden xs:inline">Calculator</span>
            </TabsTrigger>
            <TabsTrigger
              value="analysis"
              className="flex items-center gap-1 px-1 sm:px-2 min-h-[44px] text-xs sm:text-sm"
            >
              <TrendingUp className="h-4 w-4 flex-shrink-0" />
              <span className="hidden xs:inline">Analysis</span>
            </TabsTrigger>
            <TabsTrigger
              value="comparison"
              className="flex items-center gap-1 px-1 sm:px-2 min-h-[44px] text-xs sm:text-sm"
            >
              <Target className="h-4 w-4 flex-shrink-0" />
              <span className="hidden xs:inline">Compare</span>
            </TabsTrigger>
            <TabsTrigger
              value="subsidies"
              className="flex items-center gap-1 px-1 sm:px-2 min-h-[44px] text-xs sm:text-sm"
            >
              <Gift className="h-4 w-4 flex-shrink-0" />
              <span className="hidden xs:inline">Subsidies</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="calculator" className="mt-0">
            <div className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="crop-select" className="text-sm font-medium">
                    Select Crop
                  </Label>
                  <Select value={selectedCrop} onValueChange={setSelectedCrop}>
                    <SelectTrigger className="min-h-[44px] touch-manipulation">
                      <SelectValue placeholder="Choose crop" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="maize">Drought-Tolerant Maize</SelectItem>
                      <SelectItem value="sorghum">Sorghum</SelectItem>
                      <SelectItem value="beans">Common Beans</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="farm-size" className="text-sm font-medium">
                    Farm Size (Acres)
                  </Label>
                  <Input
                    id="farm-size"
                    type="number"
                    value={farmSize}
                    onChange={(e) => setFarmSize(Number(e.target.value) || 1)}
                    min="0.25"
                    step="0.25"
                    className="min-h-[44px] touch-manipulation"
                  />
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-base font-semibold text-foreground">Input Costs Breakdown</h3>
                <div className="space-y-4">
                  {currentCropData?.inputs.map((input) => (
                    <div key={input.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-start gap-3 flex-1 min-w-0">
                          <div className="flex-shrink-0 mt-1 text-primary">{getCategoryIcon(input.category)}</div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <h4 className="font-medium text-sm text-foreground">{input.name}</h4>
                              {input.isOptional && (
                                <Badge variant="outline" className="text-xs">
                                  Optional
                                </Badge>
                              )}
                            </div>
                            <p className="text-xs text-muted-foreground text-pretty mb-2">{input.description}</p>
                            <p className="text-xs text-muted-foreground">
                              KSh {input.unitCost.toLocaleString()} per {input.unit}
                            </p>
                          </div>
                        </div>
                        <div className="flex-shrink-0 ml-4">
                          <div className="text-right mb-2">
                            <p className="text-lg font-bold text-primary">
                              KSh{" "}
                              {(
                                input.unitCost *
                                (customInputs[input.id] || input.recommendedQuantity) *
                                farmSize
                              ).toLocaleString()}
                            </p>
                            <p className="text-xs text-muted-foreground">Total cost</p>
                          </div>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label className="text-xs">Recommended Quantity</Label>
                          <div className="text-sm font-medium">
                            {input.recommendedQuantity} {input.unit}
                            {farmSize > 1 && ` × ${farmSize} acres`}
                          </div>
                        </div>
                        <div className="space-y-2">
                          <Label className="text-xs">Custom Quantity (per acre)</Label>
                          <Input
                            type="number"
                            value={customInputs[input.id] || input.recommendedQuantity}
                            onChange={(e) => handleInputChange(input.id, Number(e.target.value) || 0)}
                            min="0"
                            step="0.1"
                            className="min-h-[40px] text-sm"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {currentCropData?.subsidyAvailable && (
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Gift className="h-4 w-4 text-green-600" />
                    <h4 className="font-medium text-sm text-green-900">Subsidy Available</h4>
                  </div>
                  <p className="text-xs text-green-700 mb-2">
                    Government subsidy reduces your costs by KSh {currentCropData.subsidyAmount.toLocaleString()} per
                    acre
                  </p>
                  <p className="text-xs text-green-600 font-medium">
                    Total subsidy for {farmSize} acres: KSh{" "}
                    {(currentCropData.subsidyAmount * farmSize).toLocaleString()}
                  </p>
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="analysis" className="mt-0">
            <div className="space-y-6">
              <div className="px-1">
                <h3 className="text-base sm:text-lg font-semibold text-foreground mb-2 text-balance">
                  ROI Analysis for {currentCropData?.cropName}
                </h3>
                <p className="text-xs sm:text-sm text-muted-foreground mb-4">
                  Financial projections based on current inputs and market prices
                </p>
              </div>

              {roiAnalysis && (
                <>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg text-center">
                      <DollarSign className="h-6 w-6 text-blue-600 mx-auto mb-2" />
                      <p className="text-2xl font-bold text-blue-600">KSh {roiAnalysis.totalCost.toLocaleString()}</p>
                      <p className="text-xs text-blue-700">Total Investment</p>
                    </div>

                    <div className="p-4 bg-green-50 border border-green-200 rounded-lg text-center">
                      <TrendingUp className="h-6 w-6 text-green-600 mx-auto mb-2" />
                      <p className="text-2xl font-bold text-green-600">
                        KSh {roiAnalysis.grossRevenue.toLocaleString()}
                      </p>
                      <p className="text-xs text-green-700">Expected Revenue</p>
                    </div>

                    <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg text-center">
                      <Target className="h-6 w-6 text-purple-600 mx-auto mb-2" />
                      <p className="text-2xl font-bold text-purple-600">KSh {roiAnalysis.netProfit.toLocaleString()}</p>
                      <p className="text-xs text-purple-700">Net Profit</p>
                    </div>

                    <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg text-center">
                      <Calculator className="h-6 w-6 text-orange-600 mx-auto mb-2" />
                      <p className={`text-2xl font-bold ${getROIColor(roiAnalysis.roiPercentage)}`}>
                        {roiAnalysis.roiPercentage.toFixed(1)}%
                      </p>
                      <p className="text-xs text-orange-700">ROI</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <h4 className="font-semibold text-sm text-foreground">Break-Even Analysis</h4>
                      <div className="space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-muted-foreground">Break-even yield:</span>
                          <span className="font-medium text-sm">{roiAnalysis.breakEvenYield.toFixed(1)} bags</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-muted-foreground">Expected yield:</span>
                          <span className="font-medium text-sm">
                            {(currentCropData?.expectedYield || 0) * farmSize} bags
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-muted-foreground">Safety margin:</span>
                          <span
                            className={`font-medium text-sm ${((currentCropData?.expectedYield || 0) * farmSize - roiAnalysis.breakEvenYield) > 0
                              ? "text-green-600"
                              : "text-red-600"
                              }`}
                          >
                            {(
                              (((currentCropData?.expectedYield || 0) * farmSize - roiAnalysis.breakEvenYield) /
                                roiAnalysis.breakEvenYield) *
                              100
                            ).toFixed(1)}
                            %
                          </span>
                        </div>
                      </div>
                      <Progress
                        value={Math.min(
                          (roiAnalysis.breakEvenYield / ((currentCropData?.expectedYield || 0) * farmSize)) * 100,
                          100,
                        )}
                        className="h-3"
                      />
                    </div>

                    <div className="space-y-4">
                      <h4 className="font-semibold text-sm text-foreground">Risk Assessment</h4>
                      <div className="space-y-3">
                        <div className="flex items-center gap-2">
                          {roiAnalysis.roiPercentage >= 50 ? (
                            <CheckCircle className="h-4 w-4 text-green-600" />
                          ) : roiAnalysis.roiPercentage >= 20 ? (
                            <AlertTriangle className="h-4 w-4 text-orange-600" />
                          ) : (
                            <AlertTriangle className="h-4 w-4 text-red-600" />
                          )}
                          <span className="text-sm">
                            {roiAnalysis.roiPercentage >= 50
                              ? "Excellent investment opportunity"
                              : roiAnalysis.roiPercentage >= 20
                                ? "Moderate risk, good returns"
                                : "High risk, consider alternatives"}
                          </span>
                        </div>
                        <div className="text-xs text-muted-foreground space-y-1">
                          <p>• Market price volatility: ±15-25%</p>
                          <p>• Weather risk impact: ±20-30% yield</p>
                          <p>• Input cost inflation: ±5-10% annually</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="p-4 bg-muted/50 rounded-lg">
                    <h4 className="font-semibold text-sm text-foreground mb-3">Financial Summary</h4>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Profit margin:</span>
                        <span className="ml-2 font-medium">{roiAnalysis.profitMargin.toFixed(1)}%</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Cost per bag:</span>
                        <span className="ml-2 font-medium">
                          KSh {(roiAnalysis.totalCost / ((currentCropData?.expectedYield || 1) * farmSize)).toFixed(0)}
                        </span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Revenue per acre:</span>
                        <span className="ml-2 font-medium">
                          KSh {(roiAnalysis.grossRevenue / farmSize).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </>
              )}
            </div>
          </TabsContent>

          <TabsContent value="comparison" className="mt-0">
            <div className="space-y-4">
              <div className="px-1">
                <h3 className="text-base sm:text-lg font-semibold text-foreground mb-2 text-balance">
                  Crop Comparison Analysis
                </h3>
                <p className="text-xs sm:text-sm text-muted-foreground mb-4">
                  Compare ROI and risk profiles across different crops
                </p>
              </div>

              <div className="grid gap-4">
                {Object.entries(cropCostData).map(([cropKey, cropData]) => {
                  const totalCost = cropData.inputs.reduce(
                    (sum, input) => sum + input.unitCost * input.recommendedQuantity,
                    0,
                  )
                  const subsidyReduction = cropData.subsidyAvailable ? cropData.subsidyAmount : 0
                  const netCost = totalCost - subsidyReduction
                  const grossRevenue = cropData.expectedYield * cropData.marketPrice
                  const netProfit = grossRevenue - netCost
                  const roi = (netProfit / netCost) * 100

                  return (
                    <div key={cropKey} className="border rounded-lg p-4 min-h-[120px] touch-manipulation">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1 min-w-0">
                          <h4 className="font-semibold text-sm sm:text-base text-foreground mb-1">
                            {cropData.cropName}
                          </h4>
                          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                            <div>
                              <span className="text-muted-foreground">Investment:</span>
                              <div className="font-medium">KSh {netCost.toLocaleString()}</div>
                            </div>
                            <div>
                              <span className="text-muted-foreground">Revenue:</span>
                              <div className="font-medium">KSh {grossRevenue.toLocaleString()}</div>
                            </div>
                            <div>
                              <span className="text-muted-foreground">Profit:</span>
                              <div className={`font-medium ${netProfit > 0 ? "text-green-600" : "text-red-600"}`}>
                                KSh {netProfit.toLocaleString()}
                              </div>
                            </div>
                            <div>
                              <span className="text-muted-foreground">ROI:</span>
                              <div className={`font-medium ${getROIColor(roi)}`}>{roi.toFixed(1)}%</div>
                            </div>
                          </div>
                        </div>
                        <div className="flex-shrink-0 ml-4">
                          {cropData.subsidyAvailable && (
                            <Badge className="bg-green-100 text-green-800 text-xs">Subsidy Available</Badge>
                          )}
                        </div>
                      </div>
                      <Progress value={Math.max(0, Math.min(roi, 100))} className="h-2" />
                    </div>
                  )
                })}
              </div>

              <div className="p-4 bg-muted/50 rounded-lg">
                <h4 className="font-semibold text-sm text-foreground mb-3">Comparison Insights</h4>
                <div className="space-y-2 text-xs sm:text-sm text-muted-foreground">
                  <p className="text-pretty">
                    • Beans offer highest ROI but require more intensive management and pest control
                  </p>
                  <p className="text-pretty">
                    • Maize provides balanced returns with government subsidy support and established markets
                  </p>
                  <p className="text-pretty">
                    • Sorghum offers lowest risk with good drought tolerance but lower market prices
                  </p>
                  <p className="text-pretty">• Consider diversification to balance risk and maximize returns</p>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="subsidies" className="mt-0">
            <div className="space-y-4">
              <div className="px-1">
                <h3 className="text-base sm:text-lg font-semibold text-foreground mb-2 text-balance">
                  Government Subsidies & Support Programs
                </h3>
                <p className="text-xs sm:text-sm text-muted-foreground mb-4">
                  Available financial assistance and support programs for farmers
                </p>
              </div>

              <div className="grid gap-4">
                {subsidyPrograms.map((program, index) => (
                  <div key={index} className="border rounded-lg p-4 min-h-[120px] touch-manipulation">
                    <div className="flex items-start gap-3 mb-3">
                      <Gift className="h-5 w-5 text-primary flex-shrink-0 mt-1" />
                      <div className="flex-1 min-w-0">
                        <h4 className="font-semibold text-sm sm:text-base text-foreground mb-2">{program.name}</h4>
                        <p className="text-xs sm:text-sm text-muted-foreground text-pretty mb-3">
                          {program.description}
                        </p>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                          <div>
                            <span className="font-medium text-foreground">Eligibility:</span>
                            <p className="text-muted-foreground text-pretty">{program.eligibility}</p>
                          </div>
                          <div>
                            <span className="font-medium text-foreground">Benefit:</span>
                            <p className="text-muted-foreground text-pretty">{program.benefit}</p>
                          </div>
                        </div>
                        <div className="mt-3 pt-3 border-t border-border">
                          <div className="flex items-center justify-between">
                            <div>
                              <span className="text-xs text-muted-foreground">Application Period:</span>
                              <span className="ml-2 text-xs font-medium text-foreground">
                                {program.applicationPeriod}
                              </span>
                            </div>
                            <Button size="sm" variant="outline" className="min-h-[36px] text-xs bg-transparent">
                              Learn More
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="p-4 bg-primary/10 rounded-lg border border-primary/20">
                <h4 className="font-semibold text-sm text-foreground mb-3 flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-primary" />
                  How to Apply for Subsidies
                </h4>
                <div className="space-y-2 text-xs sm:text-sm text-muted-foreground">
                  <div className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 bg-primary rounded-full mt-2 flex-shrink-0" />
                    <span className="text-pretty">Register with your local agricultural extension office</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 bg-primary rounded-full mt-2 flex-shrink-0" />
                    <span className="text-pretty">Obtain a National ID and KRA PIN certificate</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 bg-primary rounded-full mt-2 flex-shrink-0" />
                    <span className="text-pretty">Join or form a registered farmer group</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 bg-primary rounded-full mt-2 flex-shrink-0" />
                    <span className="text-pretty">Submit applications during specified periods</span>
                  </div>
                </div>
                <div className="mt-4">
                  <Button size="sm" className="min-h-[44px] touch-manipulation text-xs sm:text-sm">
                    Find Extension Office
                  </Button>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
