"use client"

import { useState, useEffect } from "react"
import { Shield, Users, Star, Eye, Download, Upload, LogOut, Trash2, CheckCircle, XCircle, FileSpreadsheet } from "lucide-react"
import * as XLSX from "xlsx"

const ADMIN_KEY = "rostov-admin-2026-secret"

interface UserStat {
  id: string
  name: string
  email: string
  role: string
  isActive: boolean
  createdAt: string
  favoritesCount: number
  viewedComplaints: number
}

export function AdminPanel() {
  const [isAuth, setIsAuth] = useState(false)
  const [keyInput, setKeyInput] = useState("")
  const [error, setError] = useState(false)
  const [users, setUsers] = useState<UserStat[]>([])
  const [importJson, setImportJson] = useState("")

  useEffect(() => {
    if (isAuth) {
      const saved = localStorage.getItem("admin-users-data")
      if (saved) {
        try {
          setUsers(JSON.parse(saved))
        } catch {
          setUsers([])
        }
      }
    }
  }, [isAuth])

  useEffect(() => {
    if (users.length > 0) {
      localStorage.setItem("admin-users-data", JSON.stringify(users))
    }
  }, [users])

  const login = (e: React.FormEvent) => {
    e.preventDefault()
    if (keyInput === ADMIN_KEY) {
      setIsAuth(true)
      setError(false)
      localStorage.setItem("admin-auth", "true")
    } else {
      setError(true)
      setTimeout(() => setError(false), 2000)
    }
  }

  const logout = () => {
    setIsAuth(false)
    setKeyInput("")
    localStorage.removeItem("admin-auth")
  }

  const exportData = () => {
    const data = {
      exportedAt: new Date().toISOString(),
      users,
      stats: {
        totalUsers: users.length,
        activeUsers: users.filter(u => u.isActive).length,
        totalFavorites: users.reduce((sum, u) => sum + u.favoritesCount, 0),
        totalViews: users.reduce((sum, u) => sum + u.viewedComplaints, 0)
      }
    }
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" })
    const url = URL.createObjectURL(blob)
    const link = document.createElement("a")
    link.href = url
    link.download = `admin-export-${new Date().toISOString().split("T")[0]}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const exportToExcel = () => {
    // Prepare data for Excel
    const data = users.map(user => ({
      "ID": user.id,
      "Имя": user.name,
      "Email": user.email,
      "Роль": user.role,
      "Статус": user.isActive ? "Активен" : "Неактивен",
      "Избранное": user.favoritesCount,
      "Просмотры": user.viewedComplaints,
      "Дата регистрации": new Date(user.createdAt).toLocaleDateString("ru-RU")
    }))
    
    // Create worksheet
    const ws = XLSX.utils.json_to_sheet(data)
    
    // Set column widths
    ws['!cols'] = [
      { wch: 5 },   // ID
      { wch: 25 },  // Имя
      { wch: 25 },  // Email
      { wch: 10 },  // Роль
      { wch: 12 },  // Статус
      { wch: 12 },  // Избранное
      { wch: 12 },  // Просмотры
      { wch: 15 }   // Дата
    ]
    
    // Create workbook
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, "Пользователи")
    
    // Generate file
    const date = new Date().toISOString().split("T")[0]
    XLSX.writeFile(wb, `users-export-${date}.xlsx`)
  }

  const importData = () => {
    try {
      const data = JSON.parse(importJson)
      if (data.users && Array.isArray(data.users)) {
        setUsers(data.users)
        alert("Данные импортированы!")
        setImportJson("")
      }
    } catch {
      alert("Ошибка импорта JSON")
    }
  }

  const toggleUser = (id: string) => {
    setUsers(users.map(u => u.id === id ? { ...u, isActive: !u.isActive } : u))
  }

  const deleteUser = (id: string) => {
    if (confirm("Удалить пользователя?")) {
      setUsers(users.filter(u => u.id !== id))
    }
  }

  const addDemoUsers = () => {
    const demo: UserStat[] = [
      { id: "1", name: "Иван Петров", email: "ivan@test.ru", role: "user", isActive: true, createdAt: new Date().toISOString(), favoritesCount: 5, viewedComplaints: 12 },
      { id: "2", name: "Мария Сидорова", email: "maria@test.ru", role: "user", isActive: true, createdAt: new Date().toISOString(), favoritesCount: 3, viewedComplaints: 8 },
      { id: "3", name: "Алексей Иванов", email: "alex@test.ru", role: "user", isActive: false, createdAt: new Date().toISOString(), favoritesCount: 0, viewedComplaints: 2 }
    ]
    setUsers([...users, ...demo])
  }

  if (!isAuth) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="w-full max-w-md bg-white rounded-lg shadow-lg p-6">
          <div className="text-center mb-6">
            <div className="mx-auto w-16 h-16 bg-slate-900 rounded-full flex items-center justify-center mb-4">
              <Shield className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold">Админ-панель</h1>
            <p className="text-gray-500">Введите секретный ключ</p>
          </div>
          <form onSubmit={login} className="space-y-4">
            <input
              type="password"
              placeholder="Секретный ключ..."
              value={keyInput}
              onChange={e => setKeyInput(e.target.value)}
              className="w-full px-4 py-2 border rounded-lg"
            />
            {error && <p className="text-sm text-red-500 text-center">Неверный ключ!</p>}
            <button type="submit" className="w-full bg-slate-900 text-white py-2 rounded-lg">
              Войти
            </button>
            <p className="text-xs text-center text-gray-400">Ключ: rostov-admin-2026-secret</p>
          </form>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-3">
            <div className="p-2 bg-slate-900 rounded-lg"><Shield className="w-6 h-6 text-white" /></div>
            Админ-панель
          </h1>
          <p className="text-slate-600 mt-1">Управление пользователями и статистика</p>
        </div>
        <div className="flex gap-2">
          <button onClick={addDemoUsers} className="px-4 py-2 border rounded-lg hover:bg-gray-50">+ Demo</button>
          <button onClick={logout} className="px-4 py-2 border rounded-lg hover:bg-gray-50 flex items-center gap-2">
            <LogOut className="w-4 h-4" />Выйти
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center gap-3">
            <Users className="w-8 h-8 text-blue-500" />
            <div><p className="text-sm text-gray-500">Пользователей</p><p className="text-2xl font-bold">{users.length}</p></div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center gap-3">
            <CheckCircle className="w-8 h-8 text-green-500" />
            <div><p className="text-sm text-gray-500">Активных</p><p className="text-2xl font-bold">{users.filter(u => u.isActive).length}</p></div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center gap-3">
            <Star className="w-8 h-8 text-amber-500" />
            <div><p className="text-sm text-gray-500">Всего избранного</p><p className="text-2xl font-bold">{users.reduce((s, u) => s + u.favoritesCount, 0)}</p></div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center gap-3">
            <Eye className="w-8 h-8 text-purple-500" />
            <div><p className="text-sm text-gray-500">Просмотров</p><p className="text-2xl font-bold">{users.reduce((s, u) => s + u.viewedComplaints, 0)}</p></div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-bold mb-4">Управление данными</h2>
        <div className="flex gap-2 mb-4">
          <button onClick={exportData} className="px-4 py-2 border rounded-lg flex items-center gap-2 hover:bg-gray-50">
            <Download className="w-4 h-4" />Экспорт JSON
          </button>
          <button onClick={exportToExcel} className="px-4 py-2 border rounded-lg flex items-center gap-2 hover:bg-gray-50 bg-green-50 border-green-200">
            <FileSpreadsheet className="w-4 h-4 text-green-600" />
            <span className="text-green-700">Экспорт Excel</span>
          </button>
        </div>
        <textarea value={importJson} onChange={e => setImportJson(e.target.value)} placeholder="Вставьте JSON для импорта..." className="w-full h-24 p-2 text-xs font-mono border rounded mb-2" />
        <button onClick={importData} disabled={!importJson.trim()} className="px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 disabled:opacity-50">
          <Upload className="w-4 h-4 inline mr-2" />Импорт JSON
        </button>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b">
          <h2 className="text-lg font-bold">Пользователи</h2>
          <p className="text-gray-500">{users.length} пользователей</p>
        </div>
        <div className="overflow-x-auto p-6">
          <table className="w-full text-sm">
            <thead><tr className="border-b"><th className="text-left py-2">Пользователь</th><th className="text-left py-2">Роль</th><th className="text-center py-2">Статус</th><th className="text-center py-2">Избранное</th><th className="text-center py-2">Просмотры</th><th className="text-left py-2">Дата</th><th className="text-center py-2">Действия</th></tr></thead>
            <tbody>
              {users.map(user => (
                <tr key={user.id} className="border-b">
                  <td className="py-2"><div><p className="font-medium">{user.name}</p><p className="text-xs text-gray-500">{user.email}</p></div></td>
                  <td className="py-2"><span className="px-2 py-1 bg-gray-100 rounded text-xs">{user.role}</span></td>
                  <td className="py-2 text-center"><span className={`px-2 py-1 rounded text-xs ${user.isActive ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`}>{user.isActive ? "Активен" : "Неактивен"}</span></td>
                  <td className="py-2 text-center">{user.favoritesCount}</td>
                  <td className="py-2 text-center">{user.viewedComplaints}</td>
                  <td className="py-2 text-xs text-gray-500">{new Date(user.createdAt).toLocaleDateString("ru-RU")}</td>
                  <td className="py-2 text-center">
                    <div className="flex gap-1 justify-center">
                      <button onClick={() => toggleUser(user.id)} className="p-1 hover:bg-gray-100 rounded">{user.isActive ? <XCircle className="w-4 h-4" /> : <CheckCircle className="w-4 h-4" />}</button>
                      <button onClick={() => deleteUser(user.id)} className="p-1 hover:bg-gray-100 rounded"><Trash2 className="w-4 h-4 text-red-500" /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {users.length === 0 && <p className="text-center py-8 text-gray-500">Нет пользователей. Нажмите "+ Demo" для добавления.</p>}
        </div>
      </div>
    </div>
  )
}
