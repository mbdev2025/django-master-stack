---
name: create-frontend
description: Génère automatiquement un frontend React/Next.js avec Tailwind, shadcn/ui, et intégration API Django
---

# Skill: Create Frontend

Crée instantanément un frontend moderne React/Next.js connecté à votre API Django.

## Utilisation

```
/create-frontend <project_name> [options]
```

## Exemples

```bash
# Frontend Next.js complet
/create-frontend dashboard

# Frontend avec options spécifiques
/create-frontend admin-panel --framework:nextjs --ui:shadcn --auth:nextauth

# Frontend React simple
/create-frontend webapp --framework:react --ui:tailwind

# Frontend avec features e-commerce
/create-frontend store --with:cart,checkout,products
```

## Options

- `--framework:nextjs` | `--framework:react` (défaut: nextjs)
- `--ui:shadcn` | `--ui:tailwind` | `--ui:mantine` (défaut: shadcn)
- `--auth:nextauth` | `--auth:clerk` | `--auth:auth0`
- `--with:features` (ex: `--with:dashboard,analytics,settings`)
- `--api:url` (URL de votre API Django)
- `--pages:liste` (pages à générer)

## Ce qui est généré

### 1. Structure Projet Next.js

```bash
frontend/
├── app/
│   ├── layout.tsx          # Root layout avec providers
│   ├── page.tsx            # Landing page
│   ├── globals.css         # Styles globaux
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx      # Dashboard layout
│   │   ├── page.tsx        # Dashboard home
│   │   ├── products/page.tsx
│   │   ├── settings/page.tsx
│   │   └── analytics/page.tsx
│   └── api/
│       └── auth/
│           └── [...nextauth]/route.ts
├── components/
│   ├── ui/                 # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── table.tsx
│   │   └── ...
│   ├── layout/
│   │   ├── header.tsx
│   │   ├── sidebar.tsx
│   │   └── footer.tsx
│   ├── auth/
│   │   ├── login-form.tsx
│   │   └── register-form.tsx
│   └── dashboard/
│       ├── stats-card.tsx
│       ├── chart.tsx
│       └── data-table.tsx
├── lib/
│   ├── api.ts              # API client
│   ├── auth.ts             # Auth utilities
│   └── utils.ts            # Helpers
├── hooks/
│   ├── use-api.ts          # Custom API hook
│   ├── use-auth.ts         # Auth hook
│   └── use-pagination.ts   # Pagination hook
├── types/
│   ├── api.ts              # TypeScript API types
│   └── models.ts           # Model types
└── public/
    └── images/
```

### 2. API Client Django Intégré

```typescript
// lib/api.ts
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor pour ajouter le token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor pour rafraîchir le token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config

    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      const refreshToken = localStorage.getItem('refresh_token')

      if (refreshToken) {
        try {
          const response = await axios.post(`${API_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          })

          const { access } = response.data
          localStorage.setItem('access_token', access)

          original.headers.Authorization = `Bearer ${access}`
          return api(original)
        } catch (refreshError) {
          // Logout si refresh échoue
          localStorage.clear()
          window.location.href = '/login'
        }
      }
    }

    return Promise.reject(error)
  }
)

// API methods
export const productsApi = {
  list: (params?: any) => api.get('/products/', { params }),
  get: (id: number) => api.get(`/products/${id}/`),
  create: (data: any) => api.post('/products/', data),
  update: (id: number, data: any) => api.put(`/products/${id}/`, data),
  delete: (id: number) => api.delete(`/products/${id}/`),
}

export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login/', { email, password }),
  register: (data: any) => api.post('/users/register/', data),
  logout: () => api.post('/users/logout/'),
  me: () => api.get('/users/me/'),
}

export const organizationsApi = {
  list: () => api.get('/tenants/organizations/'),
  create: (data: any) => api.post('/tenants/organizations/create_org/', data),
  getTeams: (id: number) => api.get(`/tenants/organizations/${id}/teams/`),
  getMembers: (id: number) => api.get(`/tenants/organizations/${id}/members/`),
}
```

### 3. Auth avec NextAuth

```typescript
// app/api/auth/[...nextauth]/route.ts
import NextAuth from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import { authApi } from '@/lib/api'

const handler = NextAuth({
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        try {
          const response = await authApi.login(
            credentials?.email || '',
            credentials?.password || ''
          )

          if (response.data.access) {
            return {
              id: response.data.user.id.toString(),
              email: response.data.user.email,
              name: response.data.user.first_name,
              accessToken: response.data.access,
              refreshToken: response.data.refresh,
            }
          }
          return null
        } catch (error) {
          return null
        }
      }
    })
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.accessToken = user.accessToken
        token.refreshToken = user.refreshToken
      }
      return token
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken
      return session
    }
  },
  pages: {
    signIn: '/login',
  },
})

export { handler as GET, handler as POST }
```

### 4. Components UI avec shadcn/ui

```typescript
// components/dashboard/data-table.tsx
"use client"

import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table"

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[]
  data: TData[]
}

export function DataTable<TData, TValue>({
  columns,
  data,
}: DataTableProps<TData, TValue>) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  })

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow key={headerGroup.id}>
              {headerGroup.headers.map((header) => {
                return (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </TableHead>
                )
              })}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody>
          {table.getRowModel().rows?.length ? (
            table.getRowModel().rows.map((row) => (
              <TableRow
                key={row.id}
                data-state={row.getIsSelected() && "selected"}
              >
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id}>
                    {flexRender(
                      cell.column.columnDef.cell,
                      cell.getContext()
                    )}
                  </TableCell>
                ))}
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell
                colSpan={columns.length}
                className="h-24 text-center"
              >
                No results.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  )
}
```

### 5. Page Dashboard

```typescript
// app/(dashboard)/page.tsx
import { StatsCard } from '@/components/dashboard/stats-card'
import { RecentSales } from '@/components/dashboard/recent-sales'
import { Chart } from '@/components/dashboard/chart'

export default function DashboardPage() {
  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total Revenue"
          value="€45,231.89"
          change="+20.1% from last month"
        />
        <StatsCard
          title="Subscriptions"
          value="+2350"
          change="+180.1% from last month"
        />
        <StatsCard
          title="Sales"
          value="+12,234"
          change="+19% from last month"
        />
        <StatsCard
          title="Active Now"
          value="+573"
          change="+201 since last hour"
        />
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Chart className="col-span-4" />
        <RecentSales className="col-span-3" />
      </div>
    </div>
  )
}
```

### 6. Custom Hooks

```typescript
// hooks/use-api.ts
import { useState, useEffect } from 'react'
import { api } from '@/lib/api'

export function useApi<T>(
  endpoint: string,
  initialData: T[] = []
) {
  const [data, setData] = useState<T[]>(initialData)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const response = await api.get(endpoint)
        setData(response.data.results || response.data)
      } catch (err) {
        setError(err as Error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [endpoint])

  const refetch = () => {
    setLoading(true)
    api.get(endpoint)
      .then(response => setData(response.data.results || response.data))
      .catch(err => setError(err))
      .finally(() => setLoading(false))
  }

  return { data, loading, error, refetch }
}

// hooks/use-pagination.ts
import { useState } from 'react'

export function usePagination(initialPage = 1, pageSize = 20) {
  const [page, setPage] = useState(initialPage)
  const [pageSize, setPageSize] = useState(pageSize)

  const nextPage = () => setPage(p => p + 1)
  const prevPage = () => setPage(p => Math.max(1, p - 1))
  const goToPage = (page: number) => setPage(page)

  return {
    page,
    pageSize,
    setPageSize,
    nextPage,
    prevPage,
    goToPage,
  }
}
```

### 7. Types TypeScript

```typescript
// types/api.ts
export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  role: 'admin' | 'user' | 'manager'
  organization: number
}

export interface Product {
  id: number
  name: string
  price: number
  description: string
  category: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Organization {
  id: number
  name: string
  slug: string
  email: string
  industry: string
  member_count: number
  created_at: string
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface ApiResponse<T> {
  data: T
  message?: string
}
```

### 8. Login Page

```typescript
// app/(auth)/login/page.tsx
"use client"

import { useState } from 'react'
import { signIn } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const result = await signIn('credentials', {
        email,
        password,
        redirect: false,
      })

      if (result?.error) {
        setError('Invalid credentials')
      } else {
        router.push('/dashboard')
        router.refresh()
      }
    } catch (error) {
      setError('Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-screen w-full items-center justify-center">
      <form onSubmit={handleSubmit} className="w-full max-w-md space-y-4">
        <h1 className="text-2xl font-bold">Welcome Back</h1>

        {error && (
          <div className="rounded-md bg-red-50 p-4 text-red-800">
            {error}
          </div>
        )}

        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <Button type="submit" className="w-full" disabled={loading}>
          {loading ? 'Signing in...' : 'Sign In'}
        </Button>
      </form>
    </div>
  )
}
```

## Fonctionnalités Inclues

### 🎨 UI Components
- shadcn/ui (composants modernes)
- Tailwind CSS (styling)
- Lucide Icons (icônes)
- Recharts (graphiques)
- React Hook Form (formulaires)
- Zod (validation)

### 🔐 Authentification
- NextAuth.js
- Login/Register pages
- Protected routes
- Token refresh automatique
- OAuth2 (Google, GitHub)

### 📊 Dashboard
- Stats cards
- Charts/graphiques
- Data tables avec pagination
- Filtres et recherche
- Export (CSV, Excel)

### 🚀 Performance
- Server Components
- Static Generation
- Image optimization
- Code splitting
- Lazy loading

## Commandes Disponibles

```bash
# Créer le frontend
/create-frontend dashboard

# Avec options spécifiques
/create-frontend admin --framework:nextjs --ui:shadcn --auth:nextauth

# Avec pages spécifiques
/create-frontend store --pages:products,cart,checkout,orders

# Connecter à API Django existante
/create-frontend webapp --api:https://api.mysaas.com
```

Créez des frontends modernes connectés à Django en quelques minutes ! 🚀
