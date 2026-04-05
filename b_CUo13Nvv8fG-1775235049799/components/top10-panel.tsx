"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, MessageSquare, ThumbsUp, ArrowUpRight } from "lucide-react"

const topQuestions = [
  { rank: 1, question: "Когда отремонтируют дорогу на Ленина?", mentions: 456, sentiment: "negative", trend: "up" },
  { rank: 2, question: "Почему отключили свет в Советском районе?", mentions: 398, sentiment: "negative", trend: "up" },
  { rank: 3, question: "Куда податься с детьми на выходных?", mentions: 345, sentiment: "positive", trend: "stable" },
  { rank: 4, question: "Когда откроют новый детский сад?", mentions: 289, sentiment: "neutral", trend: "down" },
  { rank: 5, question: "Почему повысили тарифы на проезд?", mentions: 267, sentiment: "negative", trend: "up" },
  { rank: 6, question: "Где вкусно поесть в центре?", mentions: 234, sentiment: "positive", trend: "stable" },
  { rank: 7, question: "Когда уберут мусор на Пушкинской?", mentions: 198, sentiment: "negative", trend: "up" },
  { rank: 8, question: "Где купить билеты на концерт?", mentions: 176, sentiment: "positive", trend: "down" },
  { rank: 9, question: "Почему нет воды на Западном?", mentions: 165, sentiment: "negative", trend: "up" },
  { rank: 10, question: "Когда построят новую школу?", mentions: 154, sentiment: "neutral", trend: "stable" },
]

export function Top10Panel() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <TrendingUp className="w-6 h-6" />
          ТОП-10 вопросов
        </h1>
        <p className="text-muted-foreground">Самые обсуждаемые темы в регионе</p>
      </div>

      <div className="space-y-4">
        {topQuestions.map((item) => (
          <Card key={item.rank}>
            <CardContent className="p-6">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-bold">
                  {item.rank}
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-lg mb-2">{item.question}</h3>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <MessageSquare className="w-4 h-4" />
                      {item.mentions} упоминаний
                    </span>
                    <Badge variant={item.sentiment === "positive" ? "default" : item.sentiment === "negative" ? "destructive" : "secondary"}>
                      {item.sentiment}
                    </Badge>
                    <span className="flex items-center gap-1">
                      <ArrowUpRight className={`w-4 h-4 ${item.trend === "up" ? "text-green-500" : item.trend === "down" ? "text-red-500 rotate-90" : "text-gray-500"}`} />
                      {item.trend === "up" ? "Растёт" : item.trend === "down" ? "Падает" : "Стабильно"}
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
