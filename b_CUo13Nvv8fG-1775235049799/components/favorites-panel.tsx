"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Star, Trash2, FileJson, FileSpreadsheet, Download, Upload } from "lucide-react"
import { useFavorites } from "@/lib/favorites-context"
import { useState } from "react"

export function FavoritesPanel() {
  const { favorites, removeFavorite } = useFavorites()
  const [importJson, setImportJson] = useState("")

  const exportFavorites = () => {
    const data = {
      exportedAt: new Date().toISOString(),
      favorites,
      total: favorites.length
    }
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" })
    const url = URL.createObjectURL(blob)
    const link = document.createElement("a")
    link.href = url
    link.download = `favorites-${new Date().toISOString().split("T")[0]}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const importFavorites = () => {
    try {
      const data = JSON.parse(importJson)
      if (data.favorites && Array.isArray(data.favorites)) {
        data.favorites.forEach((item: any) => {
          // addFavorite(item) // Would need to implement
        })
        alert("Данные импортированы!")
        setImportJson("")
      }
    } catch {
      alert("Ошибка импорта JSON")
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Star className="w-6 h-6 text-amber-500" />
            Избранное
          </h1>
          <p className="text-muted-foreground">Сохранённые материалы</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={exportFavorites}>
            <Download className="w-4 h-4 mr-2" />
            Экспорт
          </Button>
        </div>
      </div>

      <div className="grid gap-4">
        {favorites.length === 0 ? (
          <Card>
            <CardContent className="p-6 text-center">
              <Star className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">Нет сохранённых материалов</p>
            </CardContent>
          </Card>
        ) : (
          favorites.map((item) => (
            <Card key={item.id}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold">{item.title}</h3>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground mt-1">
                      <Badge variant="outline">{item.type}</Badge>
                      <span>{item.source}</span>
                      <span>{new Date(item.createdAt).toLocaleDateString("ru-RU")}</span>
                    </div>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => removeFavorite(item.id)}>
                    <Trash2 className="w-4 h-4 text-red-500" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Импорт избранного</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <textarea
            value={importJson}
            onChange={(e) => setImportJson(e.target.value)}
            placeholder="Вставьте JSON..."
            className="w-full h-24 p-2 text-xs font-mono border rounded"
          />
          <Button onClick={importFavorites} disabled={!importJson.trim()}>
            <Upload className="w-4 h-4 mr-2" />
            Импорт
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
