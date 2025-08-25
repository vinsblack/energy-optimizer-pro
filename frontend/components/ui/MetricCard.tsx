'use client'

import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown } from 'lucide-react'

interface MetricCardProps {
  icon: React.ReactNode
  title: string
  value: string | number
  change?: string
  trend?: 'positive' | 'negative' | 'neutral'
  subtitle?: string
  className?: string
  loading?: boolean
}

export default function MetricCard({
  icon,
  title,
  value,
  change,
  trend = 'neutral',
  subtitle,
  className = '',
  loading = false
}: MetricCardProps) {
  const getTrendColor = () => {
    switch (trend) {
      case 'positive':
        return 'text-green-600 bg-green-50'
      case 'negative':
        return 'text-red-600 bg-red-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  const getTrendIcon = () => {
    switch (trend) {
      case 'positive':
        return <TrendingUp className="w-4 h-4" />
      case 'negative':
        return <TrendingDown className="w-4 h-4" />
      default:
        return null
    }
  }

  if (loading) {
    return (
      <div className={`card ${className}`}>
        <div className="animate-pulse">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-gray-200 rounded-xl"></div>
            <div className="w-16 h-6 bg-gray-200 rounded"></div>
          </div>
          <div className="w-20 h-8 bg-gray-200 rounded mb-2"></div>
          <div className="w-24 h-4 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <motion.div
      className={`card-hover ${className}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ scale: 1.02 }}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-xl bg-gray-50 text-gray-600">
              {icon}
            </div>
            
            {change && (
              <div className={`flex items-center space-x-1 px-2 py-1 rounded-lg text-sm font-medium ${getTrendColor()}`}>
                {getTrendIcon()}
                <span>{change}</span>
              </div>
            )}
          </div>
          
          <div className="space-y-1">
            <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide">
              {title}
            </h3>
            
            <div className="text-3xl font-bold text-gray-900">
              {value}
            </div>
            
            {subtitle && (
              <p className="text-sm text-gray-600">
                {subtitle}
              </p>
            )}
          </div>
        </div>
      </div>
      
      {/* Subtle background pattern */}
      <div className="absolute top-0 right-0 w-32 h-32 opacity-5 overflow-hidden rounded-2xl">
        <div className="absolute -top-4 -right-4 w-16 h-16 bg-current rounded-full"></div>
        <div className="absolute top-8 right-8 w-8 h-8 bg-current rounded-full"></div>
        <div className="absolute top-16 right-2 w-4 h-4 bg-current rounded-full"></div>
      </div>
    </motion.div>
  )
}

// Skeleton component for loading states
export function MetricCardSkeleton({ className = '' }: { className?: string }) {
  return (
    <div className={`card ${className}`}>
      <div className="animate-pulse">
        <div className="flex items-center justify-between mb-4">
          <div className="w-12 h-12 bg-gray-200 rounded-xl"></div>
          <div className="w-16 h-6 bg-gray-200 rounded-lg"></div>
        </div>
        <div className="space-y-2">
          <div className="w-24 h-4 bg-gray-200 rounded"></div>
          <div className="w-20 h-8 bg-gray-200 rounded"></div>
          <div className="w-32 h-4 bg-gray-200 rounded"></div>
        </div>
      </div>
    </div>
  )
}

// Compact version for smaller spaces
export function CompactMetricCard({
  icon,
  title,
  value,
  change,
  trend = 'neutral',
  className = ''
}: Omit<MetricCardProps, 'subtitle'>) {
  const getTrendColor = () => {
    switch (trend) {
      case 'positive':
        return 'text-green-600'
      case 'negative':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  return (
    <motion.div
      className={`bg-white rounded-xl p-4 border border-gray-100 hover:shadow-md transition-all duration-200 ${className}`}
      whileHover={{ scale: 1.01 }}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-gray-50">
            {icon}
          </div>
          <div>
            <div className="text-sm font-medium text-gray-500">
              {title}
            </div>
            <div className="text-xl font-bold text-gray-900">
              {value}
            </div>
          </div>
        </div>
        
        {change && (
          <div className={`text-sm font-medium ${getTrendColor()}`}>
            {change}
          </div>
        )}
      </div>
    </motion.div>
  )
}

// Grid wrapper for multiple metric cards
interface MetricGridProps {
  children: React.ReactNode
  columns?: 1 | 2 | 3 | 4 | 5
  className?: string
}

export function MetricGrid({ 
  children, 
  columns = 4, 
  className = '' 
}: MetricGridProps) {
  const getGridCols = () => {
    switch (columns) {
      case 1: return 'grid-cols-1'
      case 2: return 'grid-cols-1 md:grid-cols-2'
      case 3: return 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
      case 4: return 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4'
      case 5: return 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5'
      default: return 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4'
    }
  }

  return (
    <div className={`grid ${getGridCols()} gap-6 ${className}`}>
      {children}
    </div>
  )
}
