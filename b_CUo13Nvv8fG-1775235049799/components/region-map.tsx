"use client"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { MapPin, TrendingUp } from "lucide-react"

const regions = [
  { name: "Ростов-на-Дону", mentions: 1250, sentiment: "positive", lat: 47.2357, lng: 39.7015 },
  { name: "Таганрог", mentions: 340, sentiment: "neutral", lat: 47.2096, lng: 38.9352 },
  { name: "Шахты", mentions: 280, sentiment: "negative", lat: 47.7095, lng: 40.2156 },
  { name: "Новочеркасск", mentions: 195, sentiment: "positive", lat: 47.4201, lng: 40.0953 },
  { name: "Волгодонск", mentions: 156, sentiment: "neutral", lat: 47.5167, lng: 42.1500 },
]

export function RegionMap() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Карта региона</h1>
        <p className="text-muted-foreground">Мониторинг упоминаний по районам Ростовской области</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="lg:col-span-2 h-[400px] flex items-center justify-center bg-muted/50">
          <p className="text-muted-foreground">Карта Ростовской области (заглушка)</p>
        </Card>

        {regions.map((region) => (
          <Card key={region.name}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base flex items-center gap-2">
                  <MapPin className="w-4 h-4" />
                  {region.name}
                </CardTitle>
                <Badge variant={region.sentiment === "positive" ? "default" : region.sentiment === "negative" ? "destructive" : "secondary"}>
                  {region.sentiment}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-muted-foreground" />
                <span className="text-2xl font-bold">{region.mentions}</span>
                <span className="text-sm text-muted-foreground">упоминаний</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
