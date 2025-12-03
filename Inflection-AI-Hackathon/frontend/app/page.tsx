"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { MapPin, Search, Locate, Loader2 } from "lucide-react"
import { ResilienceGauge } from "@/components/resilience-gauge"
import { RecommendationsPanel } from "@/components/recommendations-panel"
import { DataVisualization } from "@/components/data-visualization"
import { WeatherIntegration } from "@/components/weather-integration"
import { CropRecommendationEngine } from "@/components/crop-recommendation-engine"
import { InputCostCalculator } from "@/components/input-cost-calculator"
import { IrrigationRecommendations } from '@/components/irrigation-recommendations'

// API base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function AgriAdaptDashboard() {
  const [selectedCounty, setSelectedCounty] = useState<string>("")
  const [searchTerm, setSearchTerm] = useState("")
  const [showMap, setShowMap] = useState(false)
  const [showResilienceScore, setShowResilienceScore] = useState(false)
  const [resilienceData, setResilienceData] = useState({
    score: 0,
    confidence: 0,
  })
  const [isLoading, setIsLoading] = useState(false)
  const [locationError, setLocationError] = useState<string>("")
  const [counties, setCounties] = useState<string[]>([])
  const [countyCoordinates, setCountyCoordinates] = useState<{ [key: string]: { lat: number; lng: number; radius: number } }>({})

  // Fetch counties on component mount
  useEffect(() => {
    fetchCounties()
  }, [])

  // Auto-reload data when county changes
  useEffect(() => {
    if (selectedCounty && showResilienceScore) {
      // Automatically reload resilience score when county changes
      handleCheckResilienceScore()
    }
  }, [selectedCounty]) // Only depend on selectedCounty, not showResilienceScore

  const fetchCounties = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/counties`)
      if (!response.ok) {
        throw new Error('Failed to fetch counties')
      }
      const data = await response.json()
      const fetchedCounties = data.counties || []
      setCounties(fetchedCounties)

      // Generate approximate coordinates for fetched counties
      const coordinates: { [key: string]: { lat: number; lng: number; radius: number } } = {}
      data.counties.forEach((county: string, index: number) => {
        // Simple coordinate generation based on index for demonstration
        coordinates[county] = {
          lat: -1.0 + (index * 0.1), // Rough Kenya latitude range
          lng: 34.0 + (index * 0.2),  // Rough Kenya longitude range
          radius: 30 + Math.random() * 20 // Random radius between 30-50km
        }
      })
      setCountyCoordinates(coordinates)
    } catch (error) {
      console.log("Failed to fetch counties from backend")
      setCounties([])
    }
  }

  const filteredCounties = counties.filter((county) =>
    county.toLowerCase().includes(searchTerm.toLowerCase())
  )

  // Calculate distance between two coordinates
  const calculateDistance = (lat1: number, lng1: number, lat2: number, lng2: number): number => {
    const R = 6371 // Earth's radius in kilometers
    const dLat = (lat2 - lat1) * Math.PI / 180
    const dLng = (lng2 - lng1) * Math.PI / 180
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLng / 2) * Math.sin(dLng / 2)
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
    return R * c
  }

  // Find county based on coordinates
  const findCountyByCoordinates = (lat: number, lng: number): string | null => {
    let closestCounty: string | null = null
    let minDistance = Infinity

    for (const [county, coords] of Object.entries(countyCoordinates)) {
      const distance = calculateDistance(lat, lng, coords.lat, coords.lng)
      if (distance <= coords.radius && distance < minDistance) {
        minDistance = distance
        closestCounty = county
      }
    }

    return closestCounty
  }

  const handleLocationDetection = () => {
    if (counties.length === 0) {
      setLocationError("Please wait for counties to load from the backend.")
      return
    }

    setIsLoading(true)
    setLocationError("")

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords
          const detectedCounty = findCountyByCoordinates(latitude, longitude)

          if (detectedCounty) {
            setSelectedCounty(detectedCounty)
            console.log(`Location detected: ${detectedCounty} County`)
          } else {
            setLocationError("Location detected but county not found. Please select manually.")
          }
          setIsLoading(false)
        },
        (error) => {
          console.error("Error getting location:", error)
          let errorMessage = "Unable to get your location."

          switch (error.code) {
            case error.PERMISSION_DENIED:
              errorMessage = "Location access denied. Please enable location services."
              break
            case error.POSITION_UNAVAILABLE:
              errorMessage = "Location information unavailable."
              break
            case error.TIMEOUT:
              errorMessage = "Location request timed out."
              break
          }

          setLocationError(errorMessage)
          setIsLoading(false)
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 60000
        }
      )
    } else {
      setLocationError("Geolocation is not supported by your browser.")
      setIsLoading(false)
    }
  }

  const handleCheckResilienceScore = async () => {
    if (!selectedCounty) return

    setIsLoading(true)
    setShowResilienceScore(true)

    try {
      // For MVP, we'll use default environmental parameters for the county
      // In the future, this could be enhanced with real-time weather data
      const defaultParams = {
        rainfall: 800, // Default annual rainfall in mm
        soil_ph: 6.5,  // Default soil pH
        organic_carbon: 2.1 // Default organic carbon %
      }

      const response = await fetch(`${API_BASE_URL}/api/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...defaultParams,
          county: selectedCounty
        })
      })

      if (response.ok) {
        const data = await response.json()
        const prediction = data.prediction

        setResilienceData({
          score: prediction.resilience_score,
          confidence: prediction.confidence_score ? Math.round(prediction.confidence_score * 100) : 85
        })
      } else {
        setLocationError("Failed to get prediction from backend. Please try again.")
        setShowResilienceScore(false)
      }
    } catch (error) {
      console.error("Error fetching prediction:", error)
      setLocationError("Network error. Please check your connection and try again.")
      setShowResilienceScore(false)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="bg-primary text-primary-foreground py-4 sm:py-6 px-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-center mb-2 text-balance">
            Agri-Adapt AI Dashboard
          </h1>
          <p className="text-center text-primary-foreground/90 text-xs sm:text-sm md:text-base text-pretty">
            Check drought resilience scores for your maize crops
          </p>
        </div>
      </header>

      <main className="max-w-4xl mx-auto p-3 sm:p-4 space-y-4 sm:space-y-6">
        {/* County Selection Card */}
        <Card className="animate-fade-in">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-foreground text-lg sm:text-xl">
              <MapPin className="h-5 w-5 text-primary flex-shrink-0" />
              Select Your County
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 px-4 sm:px-6">
            {/* Search Input */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search for your county..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 min-h-[44px] touch-manipulation text-base"
              />
            </div>

            {/* County Dropdown */}
            <Select value={selectedCounty} onValueChange={setSelectedCounty}>
              <SelectTrigger className="w-full min-h-[44px] touch-manipulation text-base">
                <SelectValue placeholder={counties.length > 0 ? "Choose your county" : "Loading counties..."} />
              </SelectTrigger>
              <SelectContent>
                {filteredCounties.map((county) => (
                  <SelectItem key={county} value={county} className="min-h-[44px] touch-manipulation">
                    {county}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <div className="flex flex-col sm:flex-row gap-3">
              <Button
                onClick={handleLocationDetection}
                variant="outline"
                disabled={isLoading || counties.length === 0}
                className="flex-1 flex items-center gap-2 bg-transparent min-h-[44px] touch-manipulation text-sm"
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 flex-shrink-0 animate-spin" />
                ) : (
                  <Locate className="h-4 w-4 flex-shrink-0" />
                )}
                {isLoading ? "Detecting..." : "Use Current Location"}
              </Button>
              <Button
                onClick={() => setShowMap(!showMap)}
                variant="outline"
                className="flex-1 min-h-[44px] touch-manipulation text-sm"
              >
                {showMap ? "Hide Map" : "Show Map"}
              </Button>
            </div>

            {/* Location Error Display */}
            {locationError && (
              <div className="mt-2 p-3 bg-destructive/10 border border-destructive/20 rounded-lg animate-fade-in">
                <p className="text-destructive text-sm">{locationError}</p>
              </div>
            )}

            {/* Simple Map Placeholder */}
            {showMap && (
              <div className="mt-4 p-4 sm:p-6 bg-muted rounded-lg border-2 border-dashed border-border text-center animate-fade-in">
                <MapPin className="h-10 w-10 sm:h-12 sm:w-12 text-muted-foreground mx-auto mb-2" />
                <p className="text-muted-foreground text-sm sm:text-base">
                  Interactive Kenya map would be displayed here
                </p>
                <p className="text-xs sm:text-sm text-muted-foreground mt-1">Click on your county to select it</p>
              </div>
            )}

            {/* Selected County Display */}
            {selectedCounty && (
              <div className="mt-4 p-4 bg-primary/10 rounded-lg border border-primary/20 animate-fade-in">
                <p className="text-xs sm:text-sm text-muted-foreground">Selected County:</p>
                <p className="text-base sm:text-lg font-semibold text-primary">{selectedCounty}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Next Steps */}
        {selectedCounty && !showResilienceScore && (
          <Card className="animate-fade-in">
            <CardContent className="pt-6 px-4 sm:px-6">
              <div className="text-center space-y-4">
                <div className="h-14 w-14 sm:h-16 sm:w-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto">
                  <MapPin className="h-7 w-7 sm:h-8 sm:w-8 text-primary" />
                </div>
                <h3 className="text-lg sm:text-xl font-semibold text-foreground text-balance">
                  Great! You've selected {selectedCounty}
                </h3>
                <p className="text-muted-foreground text-sm sm:text-base text-pretty">
                  Now let's check the drought resilience score for your area
                </p>
                <Button
                  className="bg-primary hover:bg-primary/90 text-primary-foreground min-h-[44px] touch-manipulation px-6 text-sm sm:text-base"
                  onClick={handleCheckResilienceScore}
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Checking...
                    </>
                  ) : (
                    "Check Resilience Score"
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Resilience Score Display */}
        {showResilienceScore && selectedCounty && (
          <>
            <ResilienceGauge
              key={`resilience-${selectedCounty}`}
              score={resilienceData.score}
              confidence={resilienceData.confidence}
              county={selectedCounty}
            />
            <IrrigationRecommendations
              key={`irrigation-${selectedCounty}`}
              score={resilienceData.score}
              county={selectedCounty}
            />
            <WeatherIntegration
              key={`weather-${selectedCounty}`}
              score={resilienceData.score}
              county={selectedCounty}
            />
            <CropRecommendationEngine
              key={`crops-${selectedCounty}`}
              score={resilienceData.score}
              county={selectedCounty}
            />
            <InputCostCalculator
              key={`costs-${selectedCounty}`}
              score={resilienceData.score}
              county={selectedCounty}
            />
            <RecommendationsPanel
              key={`recommendations-${selectedCounty}`}
              score={resilienceData.score}
              county={selectedCounty}
            />
            <DataVisualization
              key={`visualization-${selectedCounty}`}
              score={resilienceData.score}
              county={selectedCounty}
            />
          </>
        )}
      </main>
    </div>
  )
}
