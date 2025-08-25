'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  Home,
  BarChart3,
  Brain,
  Database,
  Settings,
  HelpCircle,
  Menu,
  X,
  Zap,
  Building2,
  TrendingUp,
  FileText,
  Users,
  Bell,
  Search,
  User
} from 'lucide-react'

interface DashboardLayoutProps {
  children: React.ReactNode
}

const navigation = [
  {
    name: 'Dashboard',
    href: '/',
    icon: Home,
    description: 'Overview and analytics'
  },
  {
    name: 'Analyze',
    href: '/analyze',
    icon: BarChart3,
    description: 'Data analysis tools'
  },
  {
    name: 'Optimize',
    href: '/optimize',
    icon: Brain,
    description: 'ML optimization engine'
  },
  {
    name: 'Buildings',
    href: '/buildings',
    icon: Building2,
    description: 'Building management'
  },
  {
    name: 'Reports',
    href: '/reports',
    icon: FileText,
    description: 'Analytics reports'
  },
  {
    name: 'Data',
    href: '/data',
    icon: Database,
    description: 'Data management'
  }
]

const secondaryNavigation = [
  {
    name: 'Settings',
    href: '/settings',
    icon: Settings,
    description: 'System configuration'
  },
  {
    name: 'Help',
    href: '/help',
    icon: HelpCircle,
    description: 'Documentation & support'
  }
]

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const pathname = usePathname()

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Mobile sidebar overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 lg:hidden"
          >
            <div
              className="fixed inset-0 bg-gray-600 bg-opacity-75"
              onClick={() => setSidebarOpen(false)}
            />
            
            <motion.div
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              className="fixed inset-y-0 left-0 z-50 w-72 bg-white shadow-xl"
            >
              <SidebarContent 
                navigation={navigation}
                secondaryNavigation={secondaryNavigation}
                pathname={pathname}
                onClose={() => setSidebarOpen(false)}
              />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Desktop sidebar */}
      <div className="hidden lg:flex lg:w-72 lg:flex-col lg:fixed lg:inset-y-0">
        <SidebarContent
          navigation={navigation}
          secondaryNavigation={secondaryNavigation}
          pathname={pathname}
        />
      </div>

      {/* Main content */}
      <div className="flex-1 lg:ml-72">
        {/* Top navigation */}
        <header className="sticky top-0 z-30 bg-white border-b border-gray-200 backdrop-blur-sm bg-white/95">
          <div className="px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              {/* Left side */}
              <div className="flex items-center">
                <button
                  type="button"
                  className="lg:hidden -ml-0.5 -mt-0.5 h-12 w-12 inline-flex items-center justify-center rounded-md text-gray-500 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
                  onClick={() => setSidebarOpen(true)}
                >
                  <span className="sr-only">Open sidebar</span>
                  <Menu className="h-6 w-6" />
                </button>
                
                {/* Search */}
                <div className="flex-1 min-w-0 ml-4 lg:ml-0">
                  <div className="max-w-lg">
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <Search className="h-5 w-5 text-gray-400" />
                      </div>
                      <input
                        type="search"
                        placeholder="Search buildings, reports..."
                        className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Right side */}
              <div className="flex items-center space-x-4">
                {/* Notifications */}
                <button className="p-2 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-lg">
                  <Bell className="h-6 w-6" />
                </button>

                {/* Profile */}
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    <div className="h-8 w-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
                      <User className="h-5 w-5 text-white" />
                    </div>
                  </div>
                  <div className="hidden md:block">
                    <div className="text-sm font-medium text-gray-900">
                      Admin User
                    </div>
                    <div className="text-xs text-gray-500">
                      Energy Analyst
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Main content area */}
        <main className="flex-1">
          <div className="py-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              {children}
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

interface SidebarContentProps {
  navigation: typeof navigation
  secondaryNavigation: typeof secondaryNavigation
  pathname: string
  onClose?: () => void
}

function SidebarContent({ navigation, secondaryNavigation, pathname, onClose }: SidebarContentProps) {
  return (
    <div className="flex flex-col flex-grow bg-white border-r border-gray-200 pt-5 pb-4 overflow-y-auto">
      {/* Logo */}
      <div className="flex items-center flex-shrink-0 px-6">
        <div className="flex items-center">
          <div className="h-10 w-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
            <Zap className="h-6 w-6 text-white" />
          </div>
          <div className="ml-3">
            <h1 className="text-xl font-bold text-gray-900">
              Energy Pro
            </h1>
            <p className="text-xs text-gray-500">
              v2.0 Professional
            </p>
          </div>
        </div>
        
        {onClose && (
          <button
            onClick={onClose}
            className="ml-auto p-2 text-gray-400 hover:text-gray-600 lg:hidden"
          >
            <X className="h-6 w-6" />
          </button>
        )}
      </div>

      {/* Navigation */}
      <div className="mt-8 flex-grow flex flex-col">
        <nav className="flex-1 px-4 space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href
            const Icon = item.icon
            
            return (
              <Link
                key={item.name}
                href={item.href}
                onClick={onClose}
                className={`group flex items-center px-3 py-3 text-sm font-medium rounded-xl transition-all duration-200 ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 border-r-4 border-blue-700'
                    : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <Icon 
                  className={`flex-shrink-0 -ml-1 mr-3 h-5 w-5 ${
                    isActive ? 'text-blue-600' : 'text-gray-400 group-hover:text-gray-500'
                  }`}
                />
                <div>
                  <div className="font-medium">{item.name}</div>
                  <div className="text-xs text-gray-500 mt-0.5">
                    {item.description}
                  </div>
                </div>
              </Link>
            )
          })}
        </nav>

        {/* Secondary Navigation */}
        <div className="mt-8 pt-6 border-t border-gray-200">
          <nav className="px-4 space-y-1">
            {secondaryNavigation.map((item) => {
              const isActive = pathname === item.href
              const Icon = item.icon
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={onClose}
                  className={`group flex items-center px-3 py-3 text-sm font-medium rounded-xl transition-all duration-200 ${
                    isActive
                      ? 'bg-gray-50 text-gray-900'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <Icon 
                    className={`flex-shrink-0 -ml-1 mr-3 h-5 w-5 ${
                      isActive ? 'text-gray-600' : 'text-gray-400 group-hover:text-gray-500'
                    }`}
                  />
                  <div>
                    <div className="font-medium">{item.name}</div>
                    <div className="text-xs text-gray-500 mt-0.5">
                      {item.description}
                    </div>
                  </div>
                </Link>
              )
            })}
          </nav>
        </div>

        {/* System Status */}
        <div className="mt-8 px-6">
          <div className="bg-green-50 border border-green-200 rounded-xl p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <TrendingUp className="h-5 w-5 text-green-600" />
              </div>
              <div className="ml-3">
                <div className="text-sm font-medium text-green-900">
                  System Healthy
                </div>
                <div className="text-xs text-green-700">
                  91.2% accuracy • Online
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
