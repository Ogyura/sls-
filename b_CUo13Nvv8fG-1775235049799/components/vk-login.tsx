"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Spinner } from "@/components/ui/spinner"
import { Eye, EyeOff, Mail, Lock, User, Phone, Shield, Building2, MapPin, ChevronRight } from "lucide-react"
import { useAuth } from "@/lib/auth-context"

export function VKLogin() {
  const { login, register } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [mode, setMode] = useState<"login" | "register">("login")
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  
  // Форма входа
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  
  // Форма регистрации
  const [lastName, setLastName] = useState("")
  const [firstName, setFirstName] = useState("")
  const [middleName, setMiddleName] = useState("")
  const [regEmail, setRegEmail] = useState("")
  const [regPhone, setRegPhone] = useState("")
  const [regPassword, setRegPassword] = useState("")
  const [regPasswordConfirm, setRegPasswordConfirm] = useState("")
  const [confirmationCode, setConfirmationCode] = useState("")
  const [generatedCode, setGeneratedCode] = useState("")
  const [showCode, setShowCode] = useState(false)
  const [role, setRole] = useState<"user" | "minister" | "department_head" | "situation_center">("user")

  // Генерация кода подтверждения
  const generateConfirmationCode = () => {
    const code = Math.floor(1000 + Math.random() * 9000).toString()
    setGeneratedCode(code)
    setShowCode(true)
    return code
  }

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setSuccess("")
    
    if (!lastName || !firstName || !middleName) {
      setError("Заполните ФИО")
      return
    }
    
    if (!regEmail.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
      setError("Введите корректный email")
      return
    }
    
    if (!regPhone.match(/^\+7\s?\(?\d{3}\)?\s?\d{3}[-\s]?\d{2}[-\s]?\d{2}$/)) {
      setError("Введите корректный номер телефона")
      return
    }
    
    if (regPassword.length < 6) {
      setError("Пароль должен быть не менее 6 символов")
      return
    }
    
    if (regPassword !== regPasswordConfirm) {
      setError("Пароли не совпадают")
      return
    }
    
    if (!confirmationCode) {
      setError("Введите код подтверждения")
      return
    }
    
    // Проверяем код подтверждения
    if (confirmationCode !== generatedCode) {
      setError("Неверный код подтверждения")
      return
    }

    setIsLoading(true)
    
    try {
      // Регистрация через localStorage
      const result = await register({
        lastName,
        firstName,
        middleName,
        email: regEmail,
        phone: regPhone,
        password: regPassword,
        role,
      })
      
      if (!result.success) {
        throw new Error(result.error || 'Ошибка регистрации')
      }
      
      setSuccess("Регистрация прошла успешно! Теперь вы можете войти.")
      setTimeout(() => {
        setMode("login")
        // Очищаем форму
        setLastName("")
        setFirstName("")
        setMiddleName("")
        setRegEmail("")
        setRegPhone("")
        setRegPassword("")
        setRegPasswordConfirm("")
        setConfirmationCode("")
        setShowCode(false)
        setRole("user")
      }, 2000)
      
    } catch (err: any) {
      setError(err.message || "Ошибка регистрации")
    } finally {
      setIsLoading(false)
    }
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    
    if (!email || !password) {
      setError("Заполните email и пароль")
      return
    }
    
    setIsLoading(true)
    
    try {
      // Вход через localStorage
      const result = await login(email, password)
      
      if (!result.success) {
        throw new Error(result.error || 'Неверный email или пароль')
      }
      
      setSuccess("Вход выполнен успешно!")
      // Перезагружаем страницу для входа в систему
      setTimeout(() => {
        window.location.reload()
      }, 1000)
      
    } catch (err: any) {
      setError(err.message || "Ошибка входа")
    } finally {
      setIsLoading(false)
    }
  }

  const formatPhoneNumber = (value: string) => {
    const digits = value.replace(/\D/g, "")
    if (digits.length === 0) return ""
    if (digits.length <= 1) return `+${digits}`
    if (digits.length <= 4) return `+${digits.slice(0, 1)} (${digits.slice(1)}`
    if (digits.length <= 7) return `+${digits.slice(0, 1)} (${digits.slice(1, 4)}) ${digits.slice(4)}`
    if (digits.length <= 9) return `+${digits.slice(0, 1)} (${digits.slice(1, 4)}) ${digits.slice(4, 7)}-${digits.slice(7)}`
    return `+${digits.slice(0, 1)} (${digits.slice(1, 4)}) ${digits.slice(4, 7)}-${digits.slice(7, 9)}-${digits.slice(9, 11)}`
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 p-4">
      {/* Декоративные элементы фона */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-20 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-blue-400/10 rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-radial from-blue-500/5 to-transparent rounded-full" />
      </div>

      <div className="w-full max-w-lg space-y-6 relative z-10">
        {/* Герб и заголовок - улучшенный дизайн */}
        <div className="text-center space-y-4">
          <div className="flex flex-col items-center gap-4">
            <div className="relative w-28 h-32 drop-shadow-2xl">
              <div className="absolute inset-0 bg-white/10 rounded-2xl blur-xl" />
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
            <div className="space-y-2">
              <h1 className="text-2xl font-bold text-white tracking-wide drop-shadow-md">
                РОСТОВСКАЯ ОБЛАСТЬ
              </h1>
              <div className="h-0.5 w-32 mx-auto bg-gradient-to-r from-transparent via-blue-400 to-transparent" />
            </div>
          </div>
          
          <div className="space-y-1">
            <h2 className="text-xl font-semibold text-white/90">
              Центр управления регионом
            </h2>
            <p className="text-sm text-blue-200/80">
              ИИ-ассистент объективной аналитики
            </p>
          </div>
        </div>

        {/* Основная карточка с градиентом */}
        <Card className="border-0 shadow-2xl shadow-black/30 bg-gradient-to-b from-white to-slate-50 overflow-hidden">
          {/* Шапка карточки с градиентом */}
          <div className="bg-gradient-to-r from-[#0D4CD3] to-blue-600 px-6 py-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-white/20 rounded-lg">
                {mode === "login" ? (
                  <Lock className="w-5 h-5 text-white" />
                ) : (
                  <User className="w-5 h-5 text-white" />
                )}
              </div>
              <div>
                <CardTitle className="text-lg font-semibold text-white">
                  {mode === "login" ? "Вход в систему" : "Регистрация"}
                </CardTitle>
                <CardDescription className="text-sm text-blue-100">
                  {mode === "login" 
                    ? "Авторизуйтесь для доступа к панели" 
                    : "Создайте учётную запись для работы"}
                </CardDescription>
              </div>
            </div>
          </div>
          
          <CardContent className="space-y-4 px-6 py-5">
            {mode === "login" ? (
              <>
                {/* Форма входа - улучшенная */}
                <form onSubmit={handleLogin} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="email" className="text-sm font-medium text-slate-700 flex items-center gap-2">
                      <Mail className="w-4 h-4 text-blue-500" />
                      Email
                    </Label>
                    <div className="relative">
                      <Input
                        id="email"
                        type="email"
                        placeholder="example@gov.ru"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="h-11 border-slate-200 focus:border-blue-500 focus:ring-blue-500/20"
                        required
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="password" className="text-sm font-medium text-slate-700 flex items-center gap-2">
                      <Lock className="w-4 h-4 text-blue-500" />
                      Пароль
                    </Label>
                    <div className="relative">
                      <Input
                        id="password"
                        type={showPassword ? "text" : "password"}
                        placeholder="Введите пароль"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="h-11 pr-10 border-slate-200 focus:border-blue-500 focus:ring-blue-500/20"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                      >
                        {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                      </button>
                    </div>
                  </div>

                  {error && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                      <p className="text-sm text-red-600 text-center">{error}</p>
                    </div>
                  )}

                  {success && (
                    <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                      <p className="text-sm text-green-600 text-center">{success}</p>
                    </div>
                  )}

                  <Button 
                    type="submit"
                    disabled={isLoading}
                    className="w-full h-11 bg-gradient-to-r from-[#0D4CD3] to-blue-600 hover:from-[#0D4CD3]/90 hover:to-blue-600/90 text-white font-medium shadow-lg shadow-blue-500/30"
                  >
                    {isLoading ? (
                      <>
                        <Spinner className="mr-2" />
                        Вход...
                      </>
                    ) : (
                      <>
                        Войти
                        <ChevronRight className="w-4 h-4 ml-2" />
                      </>
                    )}
                  </Button>
                </form>

                <div className="text-center pt-2">
                  <button
                    onClick={() => { setMode("register"); setError(""); setSuccess("") }}
                    className="text-sm text-[#0D4CD3] hover:text-blue-700 font-medium hover:underline transition-colors"
                  >
                    Нет аккаунта? Зарегистрируйтесь
                  </button>
                </div>
              </>
            ) : (
              <>
                {/* Форма регистрации - улучшенная */}
                <form onSubmit={handleRegister} className="space-y-4">
                  {/* ФИО */}
                  <div className="space-y-2">
                    <Label className="text-sm font-medium text-slate-700 flex items-center gap-2">
                      <User className="w-4 h-4 text-blue-500" />
                      ФИО
                    </Label>
                    <div className="grid grid-cols-3 gap-2">
                      <Input
                        type="text"
                        placeholder="Фамилия"
                        value={lastName}
                        onChange={(e) => setLastName(e.target.value)}
                        className="h-10 border-slate-200 focus:border-blue-500"
                        required
                      />
                      <Input
                        type="text"
                        placeholder="Имя"
                        value={firstName}
                        onChange={(e) => setFirstName(e.target.value)}
                        className="h-10 border-slate-200 focus:border-blue-500"
                        required
                      />
                      <Input
                        type="text"
                        placeholder="Отчество"
                        value={middleName}
                        onChange={(e) => setMiddleName(e.target.value)}
                        className="h-10 border-slate-200 focus:border-blue-500"
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="reg-email" className="text-sm font-medium text-slate-700 flex items-center gap-2">
                      <Mail className="w-4 h-4 text-blue-500" />
                      Email
                    </Label>
                    <Input
                      id="reg-email"
                      type="email"
                      placeholder="example@gov.ru"
                      value={regEmail}
                      onChange={(e) => setRegEmail(e.target.value)}
                      className="h-11 border-slate-200 focus:border-blue-500 focus:ring-blue-500/20"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="reg-phone" className="text-sm font-medium text-slate-700 flex items-center gap-2">
                      <Phone className="w-4 h-4 text-blue-500" />
                      Номер телефона
                    </Label>
                    <Input
                      id="reg-phone"
                      type="tel"
                      placeholder="+7 (___) ___-__-__"
                      value={regPhone}
                      onChange={(e) => setRegPhone(formatPhoneNumber(e.target.value))}
                      className="h-11 border-slate-200 focus:border-blue-500 focus:ring-blue-500/20"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label className="text-sm font-medium text-slate-700 flex items-center gap-2">
                      <Building2 className="w-4 h-4 text-blue-500" />
                      Должность / Роль
                    </Label>
                    <select
                      value={role}
                      onChange={(e) => setRole(e.target.value as "user" | "minister" | "department_head" | "situation_center")}
                      className="w-full h-11 px-3 rounded-md border border-slate-200 bg-white text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500/20"
                      required
                    >
                      <option value="user">Пользователь</option>
                      <option value="minister">Министр</option>
                      <option value="department_head">Руководитель ведомства</option>
                      <option value="situation_center">Ситуационный центр</option>
                    </select>
                    <p className="text-xs text-slate-500">
                      Выберите вашу должность для доступа к соответствующим функциям
                    </p>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="reg-password" className="text-sm font-medium text-slate-700 flex items-center gap-2">
                      <Lock className="w-4 h-4 text-blue-500" />
                      Пароль
                    </Label>
                    <div className="relative">
                      <Input
                        id="reg-password"
                        type={showPassword ? "text" : "password"}
                        placeholder="Минимум 6 символов"
                        value={regPassword}
                        onChange={(e) => setRegPassword(e.target.value)}
                        className="h-11 pr-10 border-slate-200 focus:border-blue-500 focus:ring-blue-500/20"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                      >
                        {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                      </button>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="reg-password-confirm" className="text-sm font-medium text-slate-700 flex items-center gap-2">
                      <Lock className="w-4 h-4 text-blue-500" />
                      Подтверждение пароля
                    </Label>
                    <Input
                      id="reg-password-confirm"
                      type={showPassword ? "text" : "password"}
                      placeholder="Повторите пароль"
                      value={regPasswordConfirm}
                      onChange={(e) => setRegPasswordConfirm(e.target.value)}
                      className="h-11 border-slate-200 focus:border-blue-500 focus:ring-blue-500/20"
                      required
                    />
                  </div>

                  {/* Код подтверждения - улучшенный */}
                  <div className="space-y-2">
                    <Label htmlFor="confirmation-code" className="text-sm font-medium text-slate-700 flex items-center gap-2">
                      <Shield className="w-4 h-4 text-blue-500" />
                      Код подтверждения
                    </Label>
                    <div className="flex gap-2">
                      <Input
                        id="confirmation-code"
                        type="text"
                        placeholder="Введите код"
                        value={confirmationCode}
                        onChange={(e) => setConfirmationCode(e.target.value)}
                        className="h-11 flex-1 border-slate-200 focus:border-blue-500 focus:ring-blue-500/20"
                        required
                      />
                      <Button
                        type="button"
                        onClick={generateConfirmationCode}
                        variant="outline"
                        className="px-4 h-11 border-blue-300 text-blue-700 hover:bg-blue-50"
                      >
                        Получить код
                      </Button>
                    </div>
                    {showCode && (
                      <div className="mt-2 p-3 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg">
                        <p className="text-sm text-blue-800 font-medium">
                          Код подтверждения: <span className="text-lg font-bold tracking-wider">{generatedCode}</span>
                        </p>
                        <p className="text-xs text-blue-600 mt-1">
                          Введите этот код в поле выше для завершения регистрации
                        </p>
                      </div>
                    )}
                  </div>

                  {error && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                      <p className="text-sm text-red-600 text-center">{error}</p>
                    </div>
                  )}

                  {success && (
                    <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                      <p className="text-sm text-green-600 text-center">{success}</p>
                    </div>
                  )}

                  <Button 
                    type="submit"
                    disabled={isLoading}
                    className="w-full h-11 bg-gradient-to-r from-[#0D4CD3] to-blue-600 hover:from-[#0D4CD3]/90 hover:to-blue-600/90 text-white font-medium shadow-lg shadow-blue-500/30"
                  >
                    {isLoading ? (
                      <>
                        <Spinner className="mr-2" />
                        Регистрация...
                      </>
                    ) : (
                      <>
                        Зарегистрироваться
                        <ChevronRight className="w-4 h-4 ml-2" />
                      </>
                    )}
                  </Button>
                </form>

                <div className="text-center pt-2">
                  <button
                    onClick={() => { setMode("login"); setError(""); setSuccess("") }}
                    className="text-sm text-[#0D4CD3] hover:text-blue-700 font-medium hover:underline transition-colors"
                  >
                    Уже есть аккаунт? Войдите
                  </button>
                </div>
              </>
            )}

            {/* Информация о доступе */}
            <div className="pt-4 space-y-3 border-t border-slate-200">
              <div className="flex items-center justify-center gap-2 text-xs text-slate-500">
                <Building2 className="w-4 h-4" />
                <span>Доступ для сотрудников органов исполнительной власти</span>
              </div>
              <div className="flex items-center justify-center gap-2 text-xs text-slate-400">
                <MapPin className="w-3.5 h-3.5" />
                <span>Ростовская область</span>
                <span className="w-1 h-1 rounded-full bg-slate-300" />
                <span>2026</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Футер с информацией о безопасности */}
        <div className="flex items-center justify-center gap-2 text-xs text-blue-200/70">
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
          <span>Защищенное соединение SSL</span>
        </div>
      </div>
    </div>
  )
}
