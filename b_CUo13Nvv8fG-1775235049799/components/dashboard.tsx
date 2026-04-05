"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { 
  MessageSquare, 
  Users, 
  AlertTriangle,
  TrendingUp,
  RefreshCw,
  Search,
  Loader2,
  Newspaper,
  Eye,
  Clock,
  ThumbsUp,
  MessageCircle,
  Share2,
  Bell
} from "lucide-react"
import { cn } from "@/lib/utils"
import { apiFetch } from "@/lib/api"

interface NewsItem {
  id: string
  title: string
  summary: string
  category: string
  sentiment: "positive" | "negative" | "neutral"
  engagement: number
  createdAt: string
}

interface AlertItem {
  id: string
  title: string
  description: string
  severity: "low" | "medium" | "high" | "critical"
  createdAt: string
}

export function Dashboard() {
  const [news, setNews] = useState<NewsItem[]>([])
  const [alerts, setAlerts] = useState<AlertItem[]>([])
  const [loading, setLoading] = useState(true)
  const [filterCategory, setFilterCategory] = useState("all")
  const [searchQuery, setSearchQuery] = useState("")

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    setLoading(true)
    try {
      const [newsRes, alertsRes] = await Promise.all([
        apiFetch("/api/v1/news?limit=10"),
        apiFetch("/api/v1/alerts?limit=5")
      ])

      if (newsRes.ok) {
        const newsData = await newsRes.json()
        setNews(newsData.items || [])
      }

      if (alertsRes.ok) {
        const alertsData = await alertsRes.json()
        setAlerts(alertsData.items || [])
      }
    } catch (error) {
      console.error("Error fetching dashboard data:", error)
    } finally {
      setLoading(false)
    }
  }

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case "positive": return "bg-green-100 text-green-700"
      case "negative": return "bg-red-100 text-red-700"
      default: return "bg-gray-100 text-gray-700"
    }
  }

  const filteredNews = news.filter(item => {
    const matchesCategory = filterCategory === "all" || item.category === filterCategory
    const matchesSearch = searchQuery === "" || 
      item.title.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesCategory && matchesSearch
  })

  const categories = ["all", ...new Set(news.map(item => item.category))]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Всего сообщений</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12,345</div>
            <p className="text-xs text-muted-foreground">+12% с прошлой недели</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Активные обсуждения</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">156</div>
            <p className="text-xs text-muted-foreground">В 24 районах</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Алерты</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{alerts.length}</div>
            <p className="text-xs text-muted-foreground">Требуют внимания</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Тональность</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">Позитивная</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Newspaper className="w-5 h-5" />
              Лента новостей
            </CardTitle>
            <Button variant="outline" size="sm" onClick={fetchDashboardData}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Обновить
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2 mb-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Поиск по новостям..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
            <div className="flex gap-1">
              {categories.slice(0, 4).map((category) => (
                <Button
                  key={category}
                  variant={filterCategory === category ? "default" : "outline"}
                  size="sm"
                  onClick={() => setFilterCategory(category)}
                >
                  {category === "all" ? "Все" : category}
                </Button>
              ))}
            </div>
          </div>

          <ScrollArea className="h-[400px]">
            <div className="space-y-4">
              {filteredNews.map((item) => (
                <div key={item.id} className="p-4 border rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge className={getSentimentColor(item.sentiment)}>
                      {item.sentiment === "positive" ? "Позитив" :
                       item.sentiment === "negative" ? "Негатив" : "Нейтрал"}
                    </Badge>
                    <Badge variant="secondary">{item.category}</Badge>
                    <span className="text-xs text-muted-foreground">
                      {new Date(item.createdAt).toLocaleDateString("ru-RU")}
                    </span>
                  </div>
                  <h3 className="font-semibold mb-2">{item.title}</h3>
                  <p className="text-sm text-muted-foreground mb-3">{item.summary}</p>
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Eye className="w-3 h-3" />
                      {item.engagement}
                    </span>
                    <span className="flex items-center gap-1">
                      <ThumbsUp className="w-3 h-3" />
                      {Math.floor(item.engagement * 0.1)}
                    </span>
                    <span className="flex items-center gap-1">
                      <MessageCircle className="w-3 h-3" />
                      {Math.floor(item.engagement * 0.05)}
                    </span>
                    <span className="flex items-center gap-1">
                      <Share2 className="w-3 h-3" />
                      {Math.floor(item.engagement * 0.02)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="w-5 h-5" />
            Последние алерты
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {alerts.map((alert) => (
              <div key={alert.id} className="flex items-start gap-3 p-3 border rounded-lg">
                <div className={cn(
                  "w-2 h-2 rounded-full mt-2",
                  alert.severity === "critical" ? "bg-red-500" :
                  alert.severity === "high" ? "bg-orange-500" :
                  alert.severity === "medium" ? "bg-yellow-500" : "bg-blue-500"
                )} />
                <div className="flex-1">
                  <p className="font-medium text-sm">{alert.title}</p>
                  <p className="text-xs text-muted-foreground">{alert.description}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
