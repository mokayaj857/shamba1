"use client"

import { useEffect, useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"

interface ResilienceGaugeProps {
  score: number
  confidence: number
  county: string
}

export function ResilienceGauge({ score, confidence, county }: ResilienceGaugeProps) {
  const [animatedScore, setAnimatedScore] = useState(0)
  const [animatedConfidence, setAnimatedConfidence] = useState(0)

  useEffect(() => {
    // Animate score counting from 0 to final value
    const scoreTimer = setTimeout(() => {
      const increment = score / 60 // 60 frames for smooth animation
      let current = 0
      const interval = setInterval(() => {
        current += increment
        if (current >= score) {
          setAnimatedScore(score)
          clearInterval(interval)
        } else {
          setAnimatedScore(Math.floor(current))
        }
      }, 25) // 25ms intervals for 60fps

      return () => clearInterval(interval)
    }, 500) // Start after 500ms delay

    // Animate confidence indicator
    const confidenceTimer = setTimeout(() => {
      const increment = confidence / 40
      let current = 0
      const interval = setInterval(() => {
        current += increment
        if (current >= confidence) {
          setAnimatedConfidence(confidence)
          clearInterval(interval)
        } else {
          setAnimatedConfidence(Math.floor(current))
        }
      }, 30)

      return () => clearInterval(interval)
    }, 1000) // Start after score animation

    return () => {
      clearTimeout(scoreTimer)
      clearTimeout(confidenceTimer)
    }
  }, [score, confidence])

  // Determine color based on score ranges
  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600"
    if (score >= 60) return "text-blue-600"
    if (score >= 40) return "text-orange-500"
    return "text-red-500"
  }

  const getGaugeColor = (score: number) => {
    if (score >= 80) return "stroke-green-500"
    if (score >= 60) return "stroke-blue-500"
    if (score >= 40) return "stroke-orange-500"
    return "stroke-red-500"
  }

  const getBackgroundGradient = (score: number) => {
    if (score >= 80) return "from-green-50 to-green-100"
    if (score >= 60) return "from-blue-50 to-blue-100"
    if (score >= 40) return "from-orange-50 to-orange-100"
    return "from-red-50 to-red-100"
  }

  // Calculate stroke dash array for circular progress
  const radius = 90
  const circumference = 2 * Math.PI * radius
  const strokeDasharray = circumference
  const strokeDashoffset = circumference - (animatedScore / 100) * circumference

  return (
    <Card className={`bg-gradient-to-br ${getBackgroundGradient(score)} border-2 animate-fade-in`}>
      <CardContent className="pt-6 pb-6 px-4 sm:px-6">
        <div className="text-center space-y-4 sm:space-y-6">
          <div>
            <h2 className="text-lg sm:text-xl font-semibold text-foreground mb-2 text-balance">
              Drought Resilience Score
            </h2>
            <p className="text-xs sm:text-sm text-muted-foreground">{county} County</p>
          </div>

          <div className="relative flex items-center justify-center">
            <svg className="transform -rotate-90 w-40 h-40 sm:w-48 sm:h-48" viewBox="0 0 200 200">
              {/* Background circle */}
              <circle
                cx="100"
                cy="100"
                r={radius}
                stroke="currentColor"
                strokeWidth="6"
                fill="transparent"
                className="text-muted/30"
              />
              {/* Progress circle */}
              <circle
                cx="100"
                cy="100"
                r={radius}
                stroke="currentColor"
                strokeWidth="6"
                fill="transparent"
                strokeDasharray={strokeDasharray}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                className={`${getGaugeColor(score)} transition-all duration-1000 ease-out`}
                style={{
                  filter:
                    animatedScore >= 80
                      ? "drop-shadow(0 0 8px rgba(34, 197, 94, 0.4))"
                      : animatedScore >= 60
                        ? "drop-shadow(0 0 8px rgba(59, 130, 246, 0.4))"
                        : animatedScore >= 40
                          ? "drop-shadow(0 0 8px rgba(249, 115, 22, 0.4))"
                          : "drop-shadow(0 0 8px rgba(239, 68, 68, 0.4))",
                }}
              />
            </svg>

            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div
                  className={`text-3xl sm:text-4xl font-bold ${getScoreColor(score)} transition-colors duration-500`}
                >
                  {animatedScore}%
                </div>
                <div className="text-xs sm:text-sm text-muted-foreground mt-1">Resilience</div>
              </div>
            </div>
          </div>

          <div className="space-y-2 px-2">
            <div className="flex justify-between items-center text-xs sm:text-sm">
              <span className="text-muted-foreground">Confidence Level</span>
              <span className="font-medium text-foreground">{animatedConfidence}%</span>
            </div>
            <Progress value={animatedConfidence} className="h-2 sm:h-2 bg-muted touch-manipulation" />
          </div>

          <div className="pt-4 border-t border-border/50">
            <div
              className={`inline-flex items-center px-4 py-2 rounded-full text-xs sm:text-sm font-medium min-h-[44px] touch-manipulation ${score >= 80
                ? "bg-green-100 text-green-800"
                : score >= 60
                  ? "bg-blue-100 text-blue-800"
                  : score >= 40
                    ? "bg-orange-100 text-orange-800"
                    : "bg-red-100 text-red-800"
                }`}
            >
              {score >= 80 ? "🌱 No Irrigation Needed" : score >= 60 ? "💧 Light Irrigation" : score >= 40 ? "⚠️ Moderate Irrigation" : "🚨 Critical Irrigation"}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
