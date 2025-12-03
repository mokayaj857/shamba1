"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import {
  Sprout,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Calendar,
  Users,
  Leaf,
  Target,
  AlertCircle,
  CheckCircle,
  Star,
} from "lucide-react"

interface CropRecommendationEngineProps {
  county: string
  score: number
}

interface CropRecommendation {
  id: string
  name: string
  variety?: string
  suitability: "excellent" | "good" | "moderate" | "poor"
  droughtTolerance: number
  expectedYield: string
  marketPrice: number
  profitPotential: "high" | "medium" | "low"
  plantingWindow: string
  maturityPeriod: string
  waterRequirement: "low" | "medium" | "high"
  riskLevel: "low" | "medium" | "high"
  description: string
  pros: string[]
  cons: string[]
  companionPlants?: string[]
}

interface MarketData {
  crop: string
  currentPrice: number
  trend: "up" | "down" | "stable"
  demandLevel: "high" | "medium" | "low"
  seasonalVariation: number
}

export function CropRecommendationEngine({ county, score }: CropRecommendationEngineProps) {
  const [selectedCrop, setSelectedCrop] = useState<string | null>(null)

  // Mock crop recommendations based on resilience score
  const getCropRecommendations = (score: number): CropRecommendation[] => {
    const baseCrops: CropRecommendation[] = [
      {
        id: "maize-drought-tolerant",
        name: "Maize",
        variety: "Drought-Tolerant Varieties (DH04, KH500-23A)",
        suitability: score >= 60 ? "excellent" : score >= 40 ? "good" : "moderate",
        droughtTolerance: 75,
        expectedYield: "25-35 bags/acre",
        marketPrice: 3200,
        profitPotential: "high",
        plantingWindow: "March-April, October-November",
        maturityPeriod: "4-5 months",
        waterRequirement: "medium",
        riskLevel: score >= 60 ? "low" : "medium",
        description: "Improved drought-tolerant maize varieties specifically bred for semi-arid conditions.",
        pros: [
          "Higher drought tolerance than traditional varieties",
          "Good market demand and established value chains",
          "Familiar crop with known farming practices",
          "Government support and subsidies available",
        ],
        cons: [
          "Still requires some irrigation during dry spells",
          "Higher seed costs than local varieties",
          "Market price fluctuations",
        ],
        companionPlants: ["Beans", "Cowpeas", "Sweet Potato"],
      },
      {
        id: "sorghum",
        name: "Sorghum",
        variety: "Gadam, Serena, Kari Mtama-1",
        suitability: score <= 50 ? "excellent" : "good",
        droughtTolerance: 90,
        expectedYield: "15-25 bags/acre",
        marketPrice: 2800,
        profitPotential: "medium",
        plantingWindow: "March-May",
        maturityPeriod: "4-6 months",
        waterRequirement: "low",
        riskLevel: "low",
        description: "Highly drought-tolerant cereal crop ideal for arid and semi-arid areas.",
        pros: [
          "Excellent drought tolerance",
          "Low water requirements",
          "Multiple uses (grain, fodder, brewing)",
          "Deep root system improves soil",
        ],
        cons: ["Lower market price than maize", "Limited processing facilities", "Bird damage can be significant"],
        companionPlants: ["Cowpeas", "Groundnuts", "Pigeon Peas"],
      },
      {
        id: "millet",
        name: "Pearl Millet",
        variety: "Okashana-1, KAT/PM/14",
        suitability: score <= 40 ? "excellent" : score <= 60 ? "good" : "moderate",
        droughtTolerance: 95,
        expectedYield: "8-15 bags/acre",
        marketPrice: 3500,
        profitPotential: "medium",
        plantingWindow: "March-June",
        maturityPeriod: "3-4 months",
        waterRequirement: "low",
        riskLevel: "low",
        description: "Extremely drought-tolerant cereal with high nutritional value.",
        pros: [
          "Highest drought tolerance",
          "Short maturity period",
          "High nutritional value",
          "Growing market demand for health foods",
        ],
        cons: ["Small grain size affects marketability", "Limited local consumption habits", "Processing challenges"],
        companionPlants: ["Cowpeas", "Sesame", "Groundnuts"],
      },
      {
        id: "beans",
        name: "Common Beans",
        variety: "KAT B1, KAT B9, Rosecoco",
        suitability: score >= 50 ? "excellent" : "good",
        droughtTolerance: 60,
        expectedYield: "8-12 bags/acre",
        marketPrice: 8500,
        profitPotential: "high",
        plantingWindow: "March-April, October-November",
        maturityPeriod: "3-4 months",
        waterRequirement: "medium",
        riskLevel: "medium",
        description: "High-value legume crop that fixes nitrogen and improves soil fertility.",
        pros: ["High market price", "Nitrogen fixation improves soil", "Short maturity period", "High protein content"],
        cons: ["Susceptible to drought stress", "Pest and disease pressure", "Market price volatility"],
        companionPlants: ["Maize", "Sweet Potato", "Kale"],
      },
      {
        id: "cowpeas",
        name: "Cowpeas",
        variety: "M66, KVU 27-1, Kunde",
        suitability: score <= 60 ? "excellent" : "good",
        droughtTolerance: 80,
        expectedYield: "6-10 bags/acre",
        marketPrice: 7200,
        profitPotential: "medium",
        plantingWindow: "March-May",
        maturityPeriod: "3-4 months",
        waterRequirement: "low",
        riskLevel: "low",
        description: "Drought-tolerant legume excellent for soil improvement and nutrition.",
        pros: ["Good drought tolerance", "Nitrogen fixation", "Dual purpose (grain and leaves)", "Fast growing"],
        cons: ["Lower yield than beans", "Limited market channels", "Storage pest issues"],
        companionPlants: ["Sorghum", "Millet", "Maize"],
      },
      {
        id: "sweet-potato",
        name: "Sweet Potato",
        variety: "Orange Fleshed (Kabode, Vita, Ejumula)",
        suitability: score >= 40 ? "excellent" : "good",
        droughtTolerance: 70,
        expectedYield: "200-300 bags/acre",
        marketPrice: 50,
        profitPotential: "medium",
        plantingWindow: "March-May, September-November",
        maturityPeriod: "4-6 months",
        waterRequirement: "medium",
        riskLevel: "low",
        description: "Nutritious root crop with good drought tolerance and multiple harvest options.",
        pros: [
          "High nutritional value (Vitamin A)",
          "Multiple harvests possible",
          "Good storage life",
          "Growing health food market",
        ],
        cons: ["Lower price per unit", "Bulky transport", "Processing required for value addition"],
        companionPlants: ["Beans", "Maize", "Kale"],
      },
    ]

    return baseCrops.sort((a, b) => {
      const suitabilityOrder = { excellent: 4, good: 3, moderate: 2, poor: 1 }
      return suitabilityOrder[b.suitability] - suitabilityOrder[a.suitability]
    })
  }

  // Mock market data
  const marketData: MarketData[] = [
    { crop: "Maize", currentPrice: 3200, trend: "up", demandLevel: "high", seasonalVariation: 15 },
    { crop: "Sorghum", currentPrice: 2800, trend: "stable", demandLevel: "medium", seasonalVariation: 10 },
    { crop: "Pearl Millet", currentPrice: 3500, trend: "up", demandLevel: "medium", seasonalVariation: 20 },
    { crop: "Common Beans", currentPrice: 8500, trend: "down", demandLevel: "high", seasonalVariation: 25 },
    { crop: "Cowpeas", currentPrice: 7200, trend: "stable", demandLevel: "medium", seasonalVariation: 18 },
    { crop: "Sweet Potato", currentPrice: 50, trend: "up", demandLevel: "medium", seasonalVariation: 12 },
  ]

  const cropRecommendations = getCropRecommendations(score)

  const getSuitabilityColor = (suitability: string) => {
    switch (suitability) {
      case "excellent":
        return "bg-green-100 text-green-800"
      case "good":
        return "bg-blue-100 text-blue-800"
      case "moderate":
        return "bg-orange-100 text-orange-800"
      case "poor":
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const getProfitColor = (profit: string) => {
    switch (profit) {
      case "high":
        return "text-green-600"
      case "medium":
        return "text-orange-600"
      case "low":
        return "text-red-600"
      default:
        return "text-gray-600"
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "up":
        return <TrendingUp className="h-4 w-4 text-green-600" />
      case "down":
        return <TrendingDown className="h-4 w-4 text-red-600" />
      case "stable":
        return <Target className="h-4 w-4 text-blue-600" />
      default:
        return <Target className="h-4 w-4 text-gray-600" />
    }
  }

  const getMultiCropPlan = () => {
    if (score >= 70) {
      return {
        title: "Diversified High-Resilience Plan",
        crops: ["Drought-Tolerant Maize (60%)", "Beans (25%)", "Sweet Potato (15%)"],
        benefits: ["Balanced risk", "Multiple income streams", "Soil health improvement"],
        expectedROI: "High",
      }
    } else if (score >= 50) {
      return {
        title: "Moderate-Risk Diversification Plan",
        crops: ["Sorghum (40%)", "Cowpeas (30%)", "Drought-Tolerant Maize (30%)"],
        benefits: ["Reduced drought risk", "Nitrogen fixation", "Market diversification"],
        expectedROI: "Medium-High",
      }
    } else {
      return {
        title: "Low-Risk Survival Plan",
        crops: ["Pearl Millet (50%)", "Sorghum (30%)", "Cowpeas (20%)"],
        benefits: ["Maximum drought tolerance", "Food security", "Soil improvement"],
        expectedROI: "Medium",
      }
    }
  }

  const multiCropPlan = getMultiCropPlan()

  return (
    <Card className="animate-fade-in">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-foreground text-lg sm:text-xl">
          <Sprout className="h-5 w-5 text-primary flex-shrink-0" />
          <span className="text-balance">Crop Recommendation Engine - {county}</span>
        </CardTitle>
        <p className="text-xs sm:text-sm text-muted-foreground">
          Smart crop suggestions based on your {score}% resilience score
        </p>
      </CardHeader>
      <CardContent className="px-3 sm:px-6">
        <Tabs defaultValue="recommendations" className="w-full">
          <TabsList className="grid w-full grid-cols-4 h-12 sm:h-10 mb-6">
            <TabsTrigger
              value="recommendations"
              className="flex items-center gap-1 px-1 sm:px-2 min-h-[44px] text-xs sm:text-sm"
            >
              <Star className="h-4 w-4 flex-shrink-0" />
              <span className="hidden xs:inline">Crops</span>
            </TabsTrigger>
            <TabsTrigger
              value="varieties"
              className="flex items-center gap-1 px-1 sm:px-2 min-h-[44px] text-xs sm:text-sm"
            >
              <Leaf className="h-4 w-4 flex-shrink-0" />
              <span className="hidden xs:inline">Varieties</span>
            </TabsTrigger>
            <TabsTrigger
              value="multicrop"
              className="flex items-center gap-1 px-1 sm:px-2 min-h-[44px] text-xs sm:text-sm"
            >
              <Users className="h-4 w-4 flex-shrink-0" />
              <span className="hidden xs:inline">Multi-Crop</span>
            </TabsTrigger>
            <TabsTrigger
              value="market"
              className="flex items-center gap-1 px-1 sm:px-2 min-h-[44px] text-xs sm:text-sm"
            >
              <DollarSign className="h-4 w-4 flex-shrink-0" />
              <span className="hidden xs:inline">Market</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="recommendations" className="mt-0">
            <div className="space-y-4">
              <div className="px-1">
                <h3 className="text-base sm:text-lg font-semibold text-foreground mb-2 text-balance">
                  Recommended Crops for Your Conditions
                </h3>
                <p className="text-xs sm:text-sm text-muted-foreground mb-4">
                  Crops ranked by suitability for your {score}% resilience score
                </p>
              </div>

              <div className="grid gap-4">
                {cropRecommendations.slice(0, 4).map((crop) => (
                  <div
                    key={crop.id}
                    className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer min-h-[120px] touch-manipulation"
                    onClick={() => setSelectedCrop(selectedCrop === crop.id ? null : crop.id)}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-2">
                          <h4 className="font-semibold text-sm sm:text-base text-foreground">{crop.name}</h4>
                          <Badge className={`text-xs ${getSuitabilityColor(crop.suitability)}`}>
                            {crop.suitability}
                          </Badge>
                        </div>
                        {crop.variety && (
                          <p className="text-xs text-muted-foreground mb-2 text-pretty">{crop.variety}</p>
                        )}
                        <p className="text-xs sm:text-sm text-muted-foreground text-pretty">{crop.description}</p>
                      </div>
                      <div className="flex-shrink-0 ml-4">
                        <div className="text-right">
                          <p className="text-lg font-bold text-primary">KSh {crop.marketPrice.toLocaleString()}</p>
                          <p className="text-xs text-muted-foreground">per bag</p>
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-3">
                      <div className="text-center">
                        <div className="text-xs text-muted-foreground">Drought Tolerance</div>
                        <div className="font-medium text-sm">{crop.droughtTolerance}%</div>
                      </div>
                      <div className="text-center">
                        <div className="text-xs text-muted-foreground">Expected Yield</div>
                        <div className="font-medium text-sm">{crop.expectedYield}</div>
                      </div>
                      <div className="text-center">
                        <div className="text-xs text-muted-foreground">Water Need</div>
                        <div className="font-medium text-sm capitalize">{crop.waterRequirement}</div>
                      </div>
                      <div className="text-center">
                        <div className="text-xs text-muted-foreground">Profit Potential</div>
                        <div className={`font-medium text-sm capitalize ${getProfitColor(crop.profitPotential)}`}>
                          {crop.profitPotential}
                        </div>
                      </div>
                    </div>

                    {selectedCrop === crop.id && (
                      <div className="mt-4 pt-4 border-t border-border space-y-4 animate-fade-in">
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                          <div>
                            <h5 className="font-medium text-sm text-green-700 mb-2 flex items-center gap-1">
                              <CheckCircle className="h-4 w-4" />
                              Advantages
                            </h5>
                            <ul className="space-y-1">
                              {crop.pros.map((pro, index) => (
                                <li key={index} className="text-xs text-muted-foreground flex items-start gap-2">
                                  <span className="w-1 h-1 bg-green-500 rounded-full mt-2 flex-shrink-0" />
                                  <span className="text-pretty">{pro}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                          <div>
                            <h5 className="font-medium text-sm text-orange-700 mb-2 flex items-center gap-1">
                              <AlertCircle className="h-4 w-4" />
                              Considerations
                            </h5>
                            <ul className="space-y-1">
                              {crop.cons.map((con, index) => (
                                <li key={index} className="text-xs text-muted-foreground flex items-start gap-2">
                                  <span className="w-1 h-1 bg-orange-500 rounded-full mt-2 flex-shrink-0" />
                                  <span className="text-pretty">{con}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>

                        {crop.companionPlants && (
                          <div>
                            <h5 className="font-medium text-sm text-primary mb-2">Companion Plants:</h5>
                            <div className="flex flex-wrap gap-2">
                              {crop.companionPlants.map((plant, index) => (
                                <Badge key={index} variant="outline" className="text-xs">
                                  {plant}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}

                        <div className="flex flex-col sm:flex-row gap-2">
                          <Button size="sm" className="min-h-[44px] touch-manipulation text-xs sm:text-sm">
                            Get Planting Guide
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            className="min-h-[44px] touch-manipulation text-xs sm:text-sm bg-transparent"
                          >
                            Find Seeds
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="varieties" className="mt-0">
            <div className="space-y-4">
              <div className="px-1">
                <h3 className="text-base sm:text-lg font-semibold text-foreground mb-2 text-balance">
                  Drought-Tolerant Varieties
                </h3>
                <p className="text-xs sm:text-sm text-muted-foreground mb-4">
                  Specific varieties optimized for your climate conditions
                </p>
              </div>

              <div className="grid gap-4">
                {cropRecommendations
                  .filter((crop) => crop.variety)
                  .map((crop) => (
                    <div key={crop.id} className="border rounded-lg p-4 min-h-[100px] touch-manipulation">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1 min-w-0">
                          <h4 className="font-semibold text-sm sm:text-base text-foreground mb-1">{crop.name}</h4>
                          <p className="text-xs sm:text-sm text-primary font-medium mb-2">{crop.variety}</p>
                          <div className="flex items-center gap-4 text-xs text-muted-foreground">
                            <span>Maturity: {crop.maturityPeriod}</span>
                            <span>Planting: {crop.plantingWindow}</span>
                          </div>
                        </div>
                        <div className="flex-shrink-0">
                          <div className="text-center">
                            <div className="text-lg font-bold text-primary">{crop.droughtTolerance}%</div>
                            <div className="text-xs text-muted-foreground">Drought Tolerance</div>
                          </div>
                        </div>
                      </div>
                      <Progress value={crop.droughtTolerance} className="h-2 mb-2" />
                      <p className="text-xs text-muted-foreground text-pretty">{crop.description}</p>
                    </div>
                  ))}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="multicrop" className="mt-0">
            <div className="space-y-4">
              <div className="px-1">
                <h3 className="text-base sm:text-lg font-semibold text-foreground mb-2 text-balance">
                  Multi-Crop Planning
                </h3>
                <p className="text-xs sm:text-sm text-muted-foreground mb-4">
                  Diversification strategy for risk management and soil health
                </p>
              </div>

              <div className="p-6 bg-primary/10 rounded-lg border border-primary/20">
                <h4 className="font-semibold text-base text-foreground mb-4 flex items-center gap-2">
                  <Users className="h-5 w-5 text-primary" />
                  {multiCropPlan.title}
                </h4>

                <div className="space-y-4">
                  <div>
                    <h5 className="font-medium text-sm text-foreground mb-2">Recommended Crop Mix:</h5>
                    <div className="space-y-2">
                      {multiCropPlan.crops.map((crop, index) => (
                        <div key={index} className="flex items-center gap-3">
                          <div className="w-3 h-3 bg-primary rounded-full flex-shrink-0" />
                          <span className="text-sm text-foreground">{crop}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h5 className="font-medium text-sm text-foreground mb-2">Key Benefits:</h5>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                      {multiCropPlan.benefits.map((benefit, index) => (
                        <div key={index} className="flex items-center gap-2 p-3 bg-white rounded-lg">
                          <CheckCircle className="h-4 w-4 text-green-600 flex-shrink-0" />
                          <span className="text-xs sm:text-sm text-foreground">{benefit}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-4 border-t border-primary/20">
                    <div>
                      <span className="text-sm text-muted-foreground">Expected ROI:</span>
                      <span className={`ml-2 font-semibold ${getProfitColor(multiCropPlan.expectedROI.toLowerCase())}`}>
                        {multiCropPlan.expectedROI}
                      </span>
                    </div>
                    <Button size="sm" className="min-h-[44px] touch-manipulation text-xs sm:text-sm">
                      Get Detailed Plan
                    </Button>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-4 border rounded-lg">
                  <h5 className="font-medium text-sm text-foreground mb-3 flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-primary" />
                    Planting Schedule
                  </h5>
                  <div className="space-y-2 text-xs">
                    <div className="flex justify-between">
                      <span>March-April:</span>
                      <span className="text-muted-foreground">Main season crops</span>
                    </div>
                    <div className="flex justify-between">
                      <span>June-July:</span>
                      <span className="text-muted-foreground">Short season varieties</span>
                    </div>
                    <div className="flex justify-between">
                      <span>October-November:</span>
                      <span className="text-muted-foreground">Second season</span>
                    </div>
                  </div>
                </div>

                <div className="p-4 border rounded-lg">
                  <h5 className="font-medium text-sm text-foreground mb-3 flex items-center gap-2">
                    <Leaf className="h-4 w-4 text-primary" />
                    Companion Benefits
                  </h5>
                  <div className="space-y-2 text-xs">
                    <div className="flex items-start gap-2">
                      <span className="w-1.5 h-1.5 bg-green-500 rounded-full mt-2 flex-shrink-0" />
                      <span className="text-muted-foreground">Nitrogen fixation from legumes</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="w-1.5 h-1.5 bg-green-500 rounded-full mt-2 flex-shrink-0" />
                      <span className="text-muted-foreground">Pest and disease management</span>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="w-1.5 h-1.5 bg-green-500 rounded-full mt-2 flex-shrink-0" />
                      <span className="text-muted-foreground">Improved soil structure</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="market" className="mt-0">
            <div className="space-y-4">
              <div className="px-1">
                <h3 className="text-base sm:text-lg font-semibold text-foreground mb-2 text-balance">
                  Market Price Analysis
                </h3>
                <p className="text-xs sm:text-sm text-muted-foreground mb-4">
                  Current prices and trends to balance risk vs. profit potential
                </p>
              </div>

              <div className="grid gap-3">
                {marketData.map((market, index) => (
                  <div key={index} className="border rounded-lg p-4 min-h-[80px] touch-manipulation">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-semibold text-sm text-foreground">{market.crop}</h4>
                      <div className="flex items-center gap-2">
                        {getTrendIcon(market.trend)}
                        <span className="text-lg font-bold text-primary">
                          KSh {market.currentPrice.toLocaleString()}
                        </span>
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-xs">
                      <div>
                        <span className="text-muted-foreground">Demand:</span>
                        <span
                          className={`ml-1 capitalize ${market.demandLevel === "high" ? "text-green-600" : market.demandLevel === "medium" ? "text-orange-600" : "text-red-600"}`}
                        >
                          {market.demandLevel}
                        </span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Trend:</span>
                        <span className="ml-1 capitalize">{market.trend}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Variation:</span>
                        <span className="ml-1">±{market.seasonalVariation}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-6 p-4 bg-muted/50 rounded-lg">
                <h4 className="font-semibold text-sm text-foreground mb-3 flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-primary" />
                  Market Insights
                </h4>
                <div className="space-y-2 text-xs sm:text-sm text-muted-foreground">
                  <p className="text-pretty">• Beans show highest profit potential but with higher price volatility</p>
                  <p className="text-pretty">• Drought-tolerant crops (sorghum, millet) showing increasing demand</p>
                  <p className="text-pretty">• Sweet potato prices trending up due to health food market growth</p>
                  <p className="text-pretty">• Consider value addition for better profit margins</p>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
