import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertTriangle, Droplets, CheckCircle, Clock, CloudRain } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

interface IrrigationRecommendationsProps {
    score: number
    county: string
}

// Kenyan maize growth stages with typical timing
const MAIZE_GROWTH_STAGES = [
    { stage: 'Germination & Emergence', weeks: '0-2', waterNeed: 'critical', description: 'Seeds need consistent moisture to sprout' },
    { stage: 'Vegetative Growth', weeks: '2-8', waterNeed: 'moderate', description: 'Leaves and stems develop, moderate water needs' },
    { stage: 'Flowering & Tasseling', weeks: '8-12', waterNeed: 'critical', description: 'Most critical stage - water stress reduces yield significantly' },
    { stage: 'Grain Filling', weeks: '12-16', waterNeed: 'high', description: 'Kernels develop, consistent moisture needed' },
    { stage: 'Maturity & Harvest', weeks: '16-20', waterNeed: 'low', description: 'Plants dry down, minimal water needed' }
]

export function IrrigationRecommendations({ score, county }: IrrigationRecommendationsProps) {
    const [currentStage, setCurrentStage] = useState('Germination & Emergence')
    const [irrigationAlerts, setIrrigationAlerts] = useState<any[]>([])
    const [nextIrrigationDate, setNextIrrigationDate] = useState<string>('')

    useEffect(() => {
        if (!score || !county) return

        // Determine current growth stage based on typical Kenyan planting calendar
        const currentDate = new Date()
        const currentMonth = currentDate.getMonth() + 1 // 1-12

        // Estimate current stage based on typical planting times
        let estimatedStage = 'Germination & Emergence'
        if (currentMonth >= 3 && currentMonth <= 5) {
            // Long rains season - early growth
            estimatedStage = 'Vegetative Growth'
        } else if (currentMonth >= 6 && currentMonth <= 8) {
            // Mid-season - flowering critical
            estimatedStage = 'Flowering & Tasseling'
        } else if (currentMonth >= 9 && currentMonth <= 11) {
            // Late season - grain filling
            estimatedStage = 'Grain Filling'
        } else {
            // Short rains or off-season
            estimatedStage = 'Germination & Emergence'
        }

        setCurrentStage(estimatedStage)

        // Generate irrigation alerts based on resilience score threshold (80%)
        const alerts = []

        if (score >= 80) {
            // Above 80% - No irrigation needed
            alerts.push({
                type: 'success',
                message: 'Excellent moisture levels! No irrigation required.',
                action: 'Monitor soil moisture weekly. Resume irrigation if score drops below 80%.',
                priority: 'low',
                icon: CheckCircle
            })
        } else if (score >= 60) {
            // 60-79% - Light irrigation
            alerts.push({
                type: 'info',
                message: 'Good moisture levels. Light irrigation may be beneficial.',
                action: 'Consider light irrigation (15-20mm) every 5-7 days if no rain expected.',
                priority: 'low',
                icon: CloudRain
            })
        } else if (score >= 40) {
            // 40-59% - Moderate irrigation needed
            alerts.push({
                type: 'warning',
                message: 'Moderate drought stress detected. Irrigation recommended.',
                action: 'Irrigate every 3-4 days with 25-30mm water. Focus on root zone.',
                priority: 'medium',
                icon: AlertTriangle
            })
        } else {
            // Below 40% - Critical irrigation needed
            alerts.push({
                type: 'critical',
                message: 'Severe drought risk! Immediate irrigation required.',
                action: 'Start daily irrigation with 35-40mm water. Consider emergency measures.',
                priority: 'high',
                icon: AlertTriangle
            })
        }

        // Add stage-specific recommendations
        const stageInfo = MAIZE_GROWTH_STAGES.find(s => s.stage === estimatedStage)
        if (stageInfo && score < 80) {
            if (stageInfo.waterNeed === 'critical') {
                alerts.push({
                    type: 'critical',
                    message: `Critical stage: ${stageInfo.stage}`,
                    action: `This stage requires consistent moisture. Increase irrigation frequency immediately.`,
                    priority: 'high',
                    icon: Clock
                })
            }
        }

        setIrrigationAlerts(alerts)

        // Calculate next irrigation date based on score
        let nextDate = new Date()
        if (score >= 80) {
            nextDate.setDate(nextDate.getDate() + 7) // Check in a week
        } else if (score >= 60) {
            nextDate.setDate(nextDate.getDate() + 5) // 5 days
        } else if (score >= 40) {
            nextDate.setDate(nextDate.getDate() + 3) // 3 days
        } else {
            nextDate.setDate(nextDate.getDate() + 1) // Tomorrow
        }

        setNextIrrigationDate(nextDate.toLocaleDateString('en-US', {
            weekday: 'long',
            month: 'short',
            day: 'numeric'
        }))

    }, [score, county])

    return (
        <Card className="animate-fade-in">
            <CardHeader className="pb-4">
                <CardTitle className="flex items-center gap-2 text-foreground text-lg sm:text-xl">
                    <Droplets className="h-5 w-5 text-blue-600 flex-shrink-0" />
                    Smart Irrigation Recommendations
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                {/* Current Growth Stage */}
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                    <h3 className="font-semibold text-blue-900 mb-2">Current Growth Stage</h3>
                    <p className="text-blue-800 font-medium">{currentStage}</p>
                    <p className="text-blue-700 text-sm mt-2">Based on typical Kenyan maize calendar</p>
                </div>

                {/* Resilience Score Status */}
                <div className={`p-4 rounded-lg border ${score >= 80 ? 'border-green-200 bg-green-50' :
                    score >= 60 ? 'border-blue-200 bg-blue-50' :
                        score >= 40 ? 'border-yellow-200 bg-yellow-50' :
                            'border-red-200 bg-red-50'
                    }`}>
                    <div className="flex items-center gap-2 mb-2">
                        {score >= 80 ? (
                            <CheckCircle className="h-5 w-5 text-green-600" />
                        ) : (
                            <Droplets className="h-5 w-5 text-blue-600" />
                        )}
                        <h3 className="font-semibold">
                            {score >= 80 ? 'No Irrigation Needed' : 'Irrigation Required'}
                        </h3>
                    </div>
                    <p className="text-sm">
                        {score >= 80
                            ? `Resilience score of ${score.toFixed(1)}% indicates excellent moisture levels.`
                            : `Resilience score of ${score.toFixed(1)}% indicates irrigation is needed.`
                        }
                    </p>
                </div>

                {/* Irrigation Alerts */}
                <div>
                    <h3 className="font-semibold mb-3">Recommendations</h3>
                    <div className="space-y-3">
                        {irrigationAlerts.map((alert, index) => (
                            <div key={index} className={`p-3 rounded-lg border ${alert.type === 'critical' ? 'border-red-200 bg-red-50' :
                                alert.type === 'warning' ? 'border-yellow-200 bg-yellow-50' :
                                    alert.type === 'info' ? 'border-blue-200 bg-blue-50' :
                                        'border-green-200 bg-green-50'
                                }`}>
                                <div className="flex items-start gap-2">
                                    <alert.icon className={`h-4 w-4 mt-0.5 flex-shrink-0 ${alert.type === 'critical' ? 'text-red-600' :
                                        alert.type === 'warning' ? 'text-yellow-600' :
                                            alert.type === 'info' ? 'text-blue-600' :
                                                'text-green-600'
                                        }`} />
                                    <div className="flex-1">
                                        <p className="font-medium text-sm">{alert.message}</p>
                                        <p className="text-xs mt-1 text-gray-600">{alert.action}</p>
                                    </div>
                                </div>
                                <Badge className={`mt-2 ${alert.priority === 'high' ? 'bg-red-100 text-red-800' :
                                    alert.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                                        'bg-green-100 text-green-800'
                                    }`}>
                                    {alert.priority} priority
                                </Badge>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Next Action */}
                <div className="bg-gray-50 p-4 rounded-lg border">
                    <h3 className="font-semibold text-sm mb-2">Next Action</h3>
                    <p className="text-sm text-gray-600">
                        {score >= 80
                            ? `Check soil moisture again on ${nextIrrigationDate}`
                            : `Next irrigation scheduled for ${nextIrrigationDate}`
                        }
                    </p>
                </div>

                <Button className="w-full bg-blue-600 hover:bg-blue-700">
                    <Droplets className="h-4 w-4 mr-2" />
                    View Detailed Irrigation Schedule
                </Button>
            </CardContent>
        </Card>
    )
}
