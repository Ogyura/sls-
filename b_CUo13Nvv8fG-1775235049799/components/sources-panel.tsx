"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Globe, Newspaper, MessageSquare, ExternalLink, RefreshCw } from "lucide-react"

const sources = [
  { name: "РостовГазета", type: "news", url: "https://rostov-gazeta.ru", status: "active", mentions: 1250 },
  { name: "161.ru", type: "news", url: "https://161.ru", status: "active", mentions: 890 },
  { name: "ВКонтакте Ростов", type: "social", url: "https://vk.com/rostov", status: "active", mentions: 3400 },
  { name: "Telegram Канал", type: "social", url: "https://t.me/rostov", status: "active", mentions: 2100 },
  { name: "ТАСС ЮФО", type: "news", url: "https://tass.ru/uf", status: "active", mentions: 560 },
  { name: "Дон-ТР", type: "news", url: "https://dontr.ru", status: "inactive", mentions: 0 },
]

export function SourcesPanel() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Источники</h1>
          <p className="text-muted-foreground">Управление источниками мониторинга</p>
        </div>
        <Button variant="outline">
          <RefreshCw className="w-4 h-4 mr-2" />
          Обновить
        </Button>
      </div>

      <div className="grid gap-4">
        {sources.map((source) => (
          <Card key={source.name}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    {source.type === "news" ? (
                      <Newspaper className="w-6 h-6 text-primary" />
                    ) : (
                      <MessageSquare className="w-6 h-6 text-primary" />
                    )}
                  </div>
                  <div>
                    <h3 className="font-semibold">{source.name}</h3>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Globe className="w-3 h-3" />
                      {source.url}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <Badge variant={source.status === "active" ? "default" : "secondary"}>
                    {source.status === "active" ? "Активен" : "Неактивен"}
                  </Badge>
                  <div className="text-right">
                    <p className="text-2xl font-bold">{source.mentions}</p>
                    <p className="text-xs text-muted-foreground">упоминаний</p>
                  </div>
                  <Button variant="ghost" size="sm">
                    <ExternalLink className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
