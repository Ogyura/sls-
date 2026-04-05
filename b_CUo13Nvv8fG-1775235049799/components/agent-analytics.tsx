"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Bot, TrendingUp, MessageSquare, Clock } from "lucide-react"

const agentStats = {
  processedMessages: 15420,
  autoReplies: 2340,
  sentimentAnalysis: 8760,
  alertsGenerated: 145,
  accuracy: 94.5
}

const recentActivity = [
  { action: "Анализ тональности", count: 45, time: "2 мин назад" },
  { action: "Автоответ отправлен", count: 12, time: "5 мин назад" },
  { action: "Алерт создан", count: 3, time: "10 мин назад" },
  { action: "Классификация", count: 89, time: "15 мин назад" },
]

export function AgentAnalytics() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Bot className="w-6 h-6" />
          Агент-аналитик
        </h1>
        <p className="text-muted-foreground">AI-ассистент для анализа данных</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <MessageSquare className="w-4 h-4" />
              Обработано сообщений
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{agentStats.processedMessages.toLocaleString()}</div>
            <Progress value={75} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Точность
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{agentStats.accuracy}%</div>
            <Progress value={agentStats.accuracy} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Алерты</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{agentStats.alertsGenerated}</div>
            <p className="text-xs text-muted-foreground">за последние 24ч</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Последняя активность</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {recentActivity.map((item, index) => (
              <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center gap-3">
                  <Badge variant="outline">{item.count}</Badge>
                  <span>{item.action}</span>
                </div>
                <div className="flex items-center gap-1 text-sm text-muted-foreground">
                  <Clock className="w-3 h-3" />
                  {item.time}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
