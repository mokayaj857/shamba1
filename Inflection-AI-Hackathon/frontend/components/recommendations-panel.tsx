"use client"

import type React from "react"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import {
  Sprout,
  AlertTriangle,
  CheckCircle,
  ChevronDown,
  ChevronRight,
  Droplets,
  Sun,
  Thermometer,
  Calendar,
  TrendingUp,
  Shield,
} from "lucide-react"

interface RecommendationsPanelProps {
  score: number
  county: string
}

interface Recommendation {
  id: string
  title: string
  description: string
  icon: React.ReactNode
  priority: "high" | "medium" | "low"
  details: string[]
  actionButtons: { label: string; variant?: "default" | "outline" | "secondary" }[]
}

export function RecommendationsPanel({ score, county }: RecommendationsPanelProps) {
  const [expandedSections, setExpandedSections] = useState<string[]>([])

  const toggleSection = (sectionId: string) => {
    setExpandedSections((prev) =>
      prev.includes(sectionId) ? prev.filter((id) => id !== sectionId) : [...prev, sectionId],
    )
  }

  const getRecommendations = (score: number): Recommendation[] => {
    if (score >= 70) {
      return [
        {
          id: "maintain",
          title: "Maintain Excellent Resilience",
          description:
            "Your crops show excellent drought resilience. Continue current practices and consider optimization.",
          icon: <CheckCircle className="h-5 w-5 text-green-600" />,
          priority: "low",
          details: [
            "Continue current irrigation and soil management practices",
            "Monitor soil moisture levels regularly",
            "Consider drought-resistant maize varieties for next season",
            "Maintain organic matter in soil through composting",
          ],
          actionButtons: [
            { label: "Get Optimization Tips", variant: "default" },
            { label: "View Best Practices", variant: "outline" },
          ],
        },
        {
          id: "enhance",
          title: "Enhancement Opportunities",
          description: "Explore advanced techniques to further improve your crop resilience.",
          icon: <TrendingUp className="h-5 w-5 text-green-600" />,
          priority: "low",
          details: [
            "Implement precision agriculture techniques",
            "Consider cover cropping between seasons",
            "Explore water-efficient irrigation systems",
            "Join local farmer networks for knowledge sharing",
          ],
          actionButtons: [
            { label: "Advanced Techniques", variant: "outline" },
            { label: "Connect with Experts", variant: "secondary" },
          ],
        },
      ]
    } else if (score >= 50) {
      return [
        {
          id: "improve",
          title: "Improve Water Management",
          description: "Your resilience is moderate. Focus on water conservation and soil health improvements.",
          icon: <Droplets className="h-5 w-5 text-orange-600" />,
          priority: "medium",
          details: [
            "Install drip irrigation or improve water efficiency",
            "Add organic matter to improve soil water retention",
            "Consider mulching to reduce water evaporation",
            "Plant drought-tolerant maize varieties next season",
          ],
          actionButtons: [
            { label: "Water Management Guide", variant: "default" },
            { label: "Soil Health Tips", variant: "outline" },
          ],
        },
        {
          id: "monitor",
          title: "Enhanced Monitoring",
          description: "Increase monitoring frequency to catch stress early and respond quickly.",
          icon: <Thermometer className="h-5 w-5 text-orange-600" />,
          priority: "medium",
          details: [
            "Check soil moisture twice weekly",
            "Monitor weather forecasts daily",
            "Watch for early signs of drought stress",
            "Keep irrigation equipment ready",
          ],
          actionButtons: [
            { label: "Monitoring Schedule", variant: "outline" },
            { label: "Weather Alerts", variant: "secondary" },
          ],
        },
      ]
    } else {
      return [
        {
          id: "urgent",
          title: "Urgent Action Required",
          description: "Your crops are at high risk. Immediate intervention is needed to prevent significant losses.",
          icon: <AlertTriangle className="h-5 w-5 text-red-600" />,
          priority: "high",
          details: [
            "Implement emergency irrigation immediately",
            "Apply stress-reducing foliar sprays",
            "Consider early harvest if crops are mature enough",
            "Prepare for potential replanting with drought-resistant varieties",
          ],
          actionButtons: [
            { label: "Emergency Protocol", variant: "default" },
            { label: "Contact Extension Officer", variant: "outline" },
          ],
        },
        {
          id: "prevention",
          title: "Future Prevention Strategies",
          description: "Plan improvements for next season to avoid similar drought stress.",
          icon: <Shield className="h-5 w-5 text-red-600" />,
          priority: "high",
          details: [
            "Invest in water storage systems",
            "Switch to drought-resistant crop varieties",
            "Improve soil organic matter content",
            "Consider crop insurance options",
          ],
          actionButtons: [
            { label: "Prevention Guide", variant: "outline" },
            { label: "Financial Support", variant: "secondary" },
          ],
        },
      ]
    }
  }

  const recommendations = getRecommendations(score)

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "border-red-200 bg-red-50"
      case "medium":
        return "border-orange-200 bg-orange-50"
      case "low":
        return "border-green-200 bg-green-50"
      default:
        return "border-gray-200 bg-gray-50"
    }
  }

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case "high":
        return "bg-red-100 text-red-800"
      case "medium":
        return "bg-orange-100 text-orange-800"
      case "low":
        return "bg-green-100 text-green-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  return (
    <Card className="animate-fade-in">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-foreground text-lg sm:text-xl">
          <Sprout className="h-5 w-5 text-primary flex-shrink-0" />
          <span className="text-balance">Recommendations for {county}</span>
        </CardTitle>
        <p className="text-xs sm:text-sm text-muted-foreground">Based on your drought resilience score of {score}%</p>
      </CardHeader>
      <CardContent className="space-y-4 px-4 sm:px-6">
        {recommendations.map((recommendation) => (
          <div
            key={recommendation.id}
            className={`border rounded-lg p-4 ${getPriorityColor(recommendation.priority)} transition-all duration-200`}
          >
            <Collapsible>
              <CollapsibleTrigger
                onClick={() => toggleSection(recommendation.id)}
                className="w-full min-h-[44px] touch-manipulation"
              >
                <div className="flex items-start justify-between w-full gap-3">
                  <div className="flex items-start gap-3 text-left flex-1 min-w-0">
                    <div className="flex-shrink-0 mt-1">{recommendation.icon}</div>
                    <div className="space-y-2 flex-1 min-w-0">
                      <div className="flex flex-col sm:flex-row sm:items-center gap-2">
                        <h3 className="font-semibold text-sm sm:text-base text-foreground text-balance">
                          {recommendation.title}
                        </h3>
                        <span
                          className={`px-2 py-1 rounded-full text-xs font-medium self-start ${getPriorityBadge(recommendation.priority)}`}
                        >
                          {recommendation.priority.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-xs sm:text-sm text-muted-foreground text-pretty">
                        {recommendation.description}
                      </p>
                    </div>
                  </div>
                  <div className="flex-shrink-0 mt-1">
                    {expandedSections.includes(recommendation.id) ? (
                      <ChevronDown className="h-5 w-5 text-muted-foreground" />
                    ) : (
                      <ChevronRight className="h-5 w-5 text-muted-foreground" />
                    )}
                  </div>
                </div>
              </CollapsibleTrigger>

              <CollapsibleContent className="mt-4">
                <div className="space-y-4 pl-0 sm:pl-8">
                  <div className="space-y-3">
                    <h4 className="font-medium text-sm sm:text-base text-foreground">Detailed Actions:</h4>
                    <ul className="space-y-2">
                      {recommendation.details.map((detail, index) => (
                        <li key={index} className="text-xs sm:text-sm text-muted-foreground flex items-start gap-3">
                          <span className="w-1.5 h-1.5 bg-primary rounded-full mt-2 flex-shrink-0" />
                          <span className="text-pretty">{detail}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="flex flex-col sm:flex-row gap-3">
                    {recommendation.actionButtons.map((button, index) => (
                      <Button
                        key={index}
                        variant={button.variant || "default"}
                        size="sm"
                        className="text-xs sm:text-sm min-h-[44px] touch-manipulation flex-1 sm:flex-none"
                      >
                        {button.label}
                      </Button>
                    ))}
                  </div>
                </div>
              </CollapsibleContent>
            </Collapsible>
          </div>
        ))}

        <div className="mt-6 pt-4 border-t border-border">
          <h3 className="font-semibold text-sm sm:text-base text-foreground mb-4 flex items-center gap-2">
            <Calendar className="h-4 w-4 text-primary flex-shrink-0" />
            Additional Resources
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Button
              variant="outline"
              size="sm"
              className="justify-start min-h-[44px] touch-manipulation text-xs sm:text-sm bg-transparent"
            >
              <Sun className="h-4 w-4 mr-2 flex-shrink-0" />
              7-Day Weather Forecast
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="justify-start min-h-[44px] touch-manipulation text-xs sm:text-sm bg-transparent"
            >
              <Droplets className="h-4 w-4 mr-2 flex-shrink-0" />
              Irrigation Calculator
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="justify-start min-h-[44px] touch-manipulation text-xs sm:text-sm bg-transparent"
            >
              <Sprout className="h-4 w-4 mr-2 flex-shrink-0" />
              Crop Calendar
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="justify-start min-h-[44px] touch-manipulation text-xs sm:text-sm bg-transparent"
            >
              <TrendingUp className="h-4 w-4 mr-2 flex-shrink-0" />
              Market Prices
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
