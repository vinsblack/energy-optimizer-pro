'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { 
  Play, 
  BarChart3, 
  Upload, 
  Settings,
  Brain,
  FileText,
  Zap,
  Database
} from 'lucide-react'

interface QuickAction {
  title: string
  description: string
  icon: React.ReactNode
  href: string
  color: string
  bgColor: string
  hoverColor: string
}

const quickActions: QuickAction[] = [
  {
    title: 'Quick Analysis',
    description: 'Generate sample data and run instant analysis',
    icon: <Play className="w-6 h-6" />,
    href: '/analyze',
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
    hoverColor: 'hover:bg-blue-100'
  },
  {
    title: 'ML Optimization',
    description: 'Run AI-powered energy optimization',
    icon: <Brain className="w-6 h-6" />,
    href: '/optimize',
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    hoverColor: 'hover:bg-green-100'
  },
  {
    title: 'Upload Data',
    description: 'Import your energy consumption data',
    icon: <Upload className="w-6 h-6" />,
    href: '/data/upload',
    color: 'text-purple-600',
    bgColor: 'bg-purple-50',
    hoverColor: 'hover:bg-purple-100'
  },
  {
    title: 'View Reports',
    description: 'Access analytics reports and insights',
    icon: <FileText className="w-6 h-6" />,
    href: '/reports',
    color: 'text-orange-600',
    bgColor: 'bg-orange-50',
    hoverColor: 'hover:bg-orange-100'
  }
]

export default function QuickActions() {
  return (
    <div className="bg-white rounded-2xl shadow-card border border-gray-100 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">
            Quick Actions
          </h2>
          <p className="text-gray-600 text-sm mt-1">
            Get started with common tasks
          </p>
        </div>
        
        <div className="p-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg">
          <Zap className="w-5 h-5 text-white" />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {quickActions.map((action, index) => (
          <motion.div
            key={action.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <Link href={action.href}>
              <div className={`
                p-4 rounded-xl border border-gray-100 transition-all duration-200
                ${action.bgColor} ${action.hoverColor}
                hover:shadow-lg hover:border-gray-200
                cursor-pointer group
              `}>
                <div className="flex items-start space-x-3">
                  <div className={`
                    p-2 rounded-lg ${action.color}
                    group-hover:scale-110 transition-transform duration-200
                  `}>
                    {action.icon}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-gray-900 text-sm mb-1">
                      {action.title}
                    </h3>
                    <p className="text-xs text-gray-600 leading-relaxed">
                      {action.description}
                    </p>
                  </div>
                </div>
                
                {/* Subtle arrow indicator */}
                <div className="mt-3 flex justify-end">
                  <div className="w-6 h-6 rounded-full bg-white/50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                    <svg className="w-3 h-3 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              </div>
            </Link>
          </motion.div>
        ))}
      </div>

      {/* Additional Actions */}
      <div className="mt-6 pt-6 border-t border-gray-100">
        <div className="flex flex-wrap gap-3">
          <Link href="/data">
            <motion.button
              className="inline-flex items-center space-x-2 text-sm text-gray-600 hover:text-gray-900 px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Database className="w-4 h-4" />
              <span>Manage Data</span>
            </motion.button>
          </Link>
          
          <Link href="/settings">
            <motion.button
              className="inline-flex items-center space-x-2 text-sm text-gray-600 hover:text-gray-900 px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Settings className="w-4 h-4" />
              <span>Settings</span>
            </motion.button>
          </Link>
          
          <Link href="/help">
            <motion.button
              className="inline-flex items-center space-x-2 text-sm text-gray-600 hover:text-gray-900 px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <BarChart3 className="w-4 h-4" />
              <span>Documentation</span>
            </motion.button>
          </Link>
        </div>
      </div>
    </div>
  )
}

// Compact version for smaller spaces
export function CompactQuickActions() {
  const compactActions = quickActions.slice(0, 3) // Show only first 3

  return (
    <div className="bg-white rounded-xl p-4 border border-gray-100">
      <h3 className="font-semibold text-gray-900 mb-3">Quick Actions</h3>
      
      <div className="space-y-2">
        {compactActions.map((action, index) => (
          <motion.div
            key={action.title}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
          >
            <Link href={action.href}>
              <div className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer group">
                <div className={`p-1.5 rounded ${action.bgColor} ${action.color}`}>
                  {action.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-900">
                    {action.title}
                  </div>
                </div>
                <svg className="w-4 h-4 text-gray-400 group-hover:text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </Link>
          </motion.div>
        ))}
      </div>
      
      <div className="mt-3 pt-3 border-t border-gray-100">
        <Link href="/dashboard" className="text-sm text-blue-600 hover:text-blue-700">
          View all actions →
        </Link>
      </div>
    </div>
  )
}
