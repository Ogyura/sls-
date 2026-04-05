"use client"

import { useAuth } from "@/lib/auth-context"
import { useTheme } from "@/lib/theme-context"
import { cn } from "@/lib/utils"
import { 
  LayoutDashboard, 
  MessageSquare, 
  Settings, 
  Users, 
  FileText, 
  Bell, 
  MapPin,
  BarChart3,
  Shield,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Bot,
  UserCircle,
  Key,
  TrendingUp,
  Sun,
  Moon,
  Star
} from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { useState } from "react"

interface NavItem {
  label: string
  icon: React.ElementType
  href: string
  badge?: number
}

const navItems: NavItem[] = [
  { label: "Дашборд", icon: LayoutDashboard, href: "#dashboard" },
  { label: "ТОП-10 вопросов", icon: TrendingUp, href: "#top10" },
  { label: "Избранное", icon: Star, href: "#favorites" },
  { label: "Агент-аналитик", icon: Bot, href: "#agent" },
  { label: "Источники", icon: Settings, href: "#sources" },
  { label: "Карта региона", icon: MapPin, href: "#map" },
  { label: "Админпанель", icon: Shield, href: "#admin" },
]

interface AppSidebarProps {
  activeSection: string
  onSectionChange: (section: string) => void
}

export function AppSidebar({ activeSection, onSectionChange }: AppSidebarProps) {
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const [collapsed, setCollapsed] = useState(false)

  const roleLabels: Record<string, string> = {
    admin: "Администратор",
    operator: "Оператор ЦУР",
    head: "Глава МО",
    minister: "Министр",
    governor: "Губернатор",
    department_head: "Руководитель ведомства",
    situation_center: "Ситуационный центр",
    user: "Пользователь"
  }

  return (
    <aside className={cn(
      "min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 text-white flex flex-col border-r border-blue-800/50 transition-all duration-300 shadow-xl",
      collapsed ? "w-20" : "w-72"
    )}>
      {/* Header с гербом - улучшенный дизайн */}
      <div className="p-4 border-b border-blue-800/50 bg-gradient-to-r from-blue-900/50 to-transparent">
        <div className="flex items-center gap-3">
          <div className="relative w-12 h-14 flex-shrink-0 bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg p-1 shadow-lg flex items-center justify-center overflow-hidden">
            {/* Логотип ЦУР */}
            <svg viewBox="0 0 100 100" className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#60A5FA"/>
                  <stop offset="100%" stopColor="#3B82F6"/>
                </linearGradient>
              </defs>
              {/* Фон круга */}
              <circle cx="50" cy="50" r="45" fill="url(#logoGrad)" stroke="#FFD700" strokeWidth="2"/>
              {/* Буквы ЦУР */}
              <text x="50" y="58" textAnchor="middle" fontSize="32" fontWeight="bold" fill="white" fontFamily="Arial, sans-serif">ЦУР</text>
              {/* Декоративные элементы */}
              <circle cx="50" cy="22" r="4" fill="#FFD700"/>
              <path d="M50,26 L50,35" stroke="#FFD700" strokeWidth="2"/>
            </svg>
          </div>
          {!collapsed && (
            <div className="overflow-hidden">
              <h2 className="font-bold text-sm truncate text-white drop-shadow-sm">
                РОСТОВСКАЯ ОБЛАСТЬ
              </h2>
              <p className="text-xs text-blue-200/80 truncate font-medium">
                Центр управления регионом
              </p>
            </div>
          )}
        </div>
      </div>

      {/* User section - moved to top */}
      <div className="p-3 border-b border-blue-800/50 bg-gradient-to-r from-blue-900/50 to-transparent">
        <div className="flex items-center gap-3">
          <Avatar className="w-10 h-10 flex-shrink-0 ring-2 ring-blue-400/50 shadow-lg">
            <AvatarImage src={user?.photo} />
            <AvatarFallback className="bg-gradient-to-br from-[#0D4CD3] to-blue-600 text-white text-sm font-semibold">
              {user?.name.split(" ").map(n => n[0]).join("").slice(0, 2)}
            </AvatarFallback>
          </Avatar>
          {!collapsed && (
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold truncate text-white">{user?.name}</p>
              <p className="text-xs text-blue-200/70 truncate">
                {user?.role ? roleLabels[user.role] : ""}
              </p>
            </div>
          )}
          <Button 
            variant="ghost" 
            size="icon"
            onClick={logout}
            className="text-blue-200/60 hover:text-white hover:bg-red-500/20 flex-shrink-0 transition-colors"
            title="Выйти из системы"
          >
            <LogOut className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Theme toggle - moved to top */}
      <button
        onClick={toggleTheme}
        className="p-2 mx-3 mt-2 rounded-lg bg-white/5 hover:bg-white/10 transition-all flex items-center justify-center text-blue-200/60 hover:text-white border border-white/10 hover:border-white/20"
        title={theme === "dark" ? "Переключить на светлую тему" : "Переключить на темную тему"}
      >
        {theme === "dark" ? (
          <>
            <Sun className="w-5 h-5" />
            {!collapsed && <span className="text-xs ml-2">Светлая тема</span>}
          </>
        ) : (
          <>
            <Moon className="w-5 h-5" />
            {!collapsed && <span className="text-xs ml-2">Темная тема</span>}
          </>
        )}
      </button>

      {/* Collapse toggle - moved to top */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="p-2 mx-3 mt-2 mb-2 rounded-lg bg-white/5 hover:bg-white/10 transition-all flex items-center justify-center text-blue-200/60 hover:text-white border border-white/10 hover:border-white/20"
      >
        {collapsed ? (
          <ChevronRight className="w-5 h-5" />
        ) : (
          <>
            <ChevronLeft className="w-5 h-5" />
            {!collapsed && <span className="text-xs ml-2">Свернуть</span>}
          </>
        )}
      </button>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = activeSection === item.href.replace("#", "")
          
          return (
            <button
              key={item.href}
              onClick={() => onSectionChange(item.href.replace("#", ""))}
              className={cn(
                "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all text-left relative group",
                isActive 
                  ? "bg-gradient-to-r from-[#0D4CD3] to-[#1a5ce3] text-white shadow-lg shadow-blue-500/30 border-l-4 border-white" 
                  : "hover:bg-white/10 text-blue-100/80 hover:text-white hover:translate-x-1"
              )}
            >
              <div className={cn(
                "p-1.5 rounded-lg transition-colors",
                isActive ? "bg-white/20" : "bg-white/5 group-hover:bg-white/10"
              )}>
                <Icon className={cn(
                  "w-5 h-5 flex-shrink-0",
                  isActive && "text-white"
                )} />
              </div>
              {!collapsed && (
                <>
                  <span className="flex-1 text-sm font-medium truncate">{item.label}</span>
                  {item.badge && (
                    <span className={cn(
                      "px-2 py-0.5 text-xs font-semibold rounded-full",
                      isActive 
                        ? "bg-white/20 text-white" 
                        : "bg-destructive text-destructive-foreground"
                    )}>
                      {item.badge}
                    </span>
                  )}
                </>
              )}
              {collapsed && item.badge && (
                <span className="absolute -top-1 -right-1 w-5 h-5 text-[10px] font-bold bg-destructive text-destructive-foreground rounded-full flex items-center justify-center">
                  {item.badge}
                </span>
              )}
            </button>
          )
        })}
      </nav>
    </aside>
  )
}
