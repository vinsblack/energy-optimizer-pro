'use client'

import { motion } from 'framer-motion'
import { Loader2, Zap } from 'lucide-react'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  text?: string
  color?: 'blue' | 'green' | 'purple' | 'gray'
  variant?: 'spinner' | 'dots' | 'pulse' | 'bars'
  className?: string
}

export default function LoadingSpinner({
  size = 'md',
  text,
  color = 'blue',
  variant = 'spinner',
  className = ''
}: LoadingSpinnerProps) {
  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return { spinner: 'w-4 h-4', text: 'text-sm' }
      case 'lg':
        return { spinner: 'w-8 h-8', text: 'text-lg' }
      case 'xl':
        return { spinner: 'w-12 h-12', text: 'text-xl' }
      default:
        return { spinner: 'w-6 h-6', text: 'text-base' }
    }
  }

  const getColorClasses = () => {
    switch (color) {
      case 'green':
        return 'text-green-600'
      case 'purple':
        return 'text-purple-600'
      case 'gray':
        return 'text-gray-600'
      default:
        return 'text-blue-600'
    }
  }

  const sizeClasses = getSizeClasses()
  const colorClasses = getColorClasses()

  if (variant === 'spinner') {
    return (
      <div className={`flex flex-col items-center justify-center ${className}`}>
        <Loader2 className={`${sizeClasses.spinner} ${colorClasses} animate-spin`} />
        {text && (
          <p className={`mt-2 ${sizeClasses.text} text-gray-600 font-medium`}>
            {text}
          </p>
        )}
      </div>
    )
  }

  if (variant === 'dots') {
    return (
      <div className={`flex flex-col items-center justify-center ${className}`}>
        <div className="flex space-x-1">
          {[0, 1, 2].map((index) => (
            <motion.div
              key={index}
              className={`w-2 h-2 ${colorClasses.replace('text-', 'bg-')} rounded-full`}
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.7, 1, 0.7]
              }}
              transition={{
                duration: 1,
                repeat: Infinity,
                delay: index * 0.2
              }}
            />
          ))}
        </div>
        {text && (
          <p className={`mt-3 ${sizeClasses.text} text-gray-600 font-medium`}>
            {text}
          </p>
        )}
      </div>
    )
  }

  if (variant === 'pulse') {
    return (
      <div className={`flex flex-col items-center justify-center ${className}`}>
        <motion.div
          className={`${sizeClasses.spinner} ${colorClasses.replace('text-', 'bg-')} rounded-full`}
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.8, 0.4, 0.8]
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity
          }}
        />
        {text && (
          <p className={`mt-3 ${sizeClasses.text} text-gray-600 font-medium`}>
            {text}
          </p>
        )}
      </div>
    )
  }

  if (variant === 'bars') {
    return (
      <div className={`flex flex-col items-center justify-center ${className}`}>
        <div className="flex space-x-1">
          {[0, 1, 2, 3].map((index) => (
            <motion.div
              key={index}
              className={`w-1 bg-gradient-to-t from-blue-600 to-purple-600`}
              style={{ height: '20px' }}
              animate={{
                scaleY: [1, 2, 1]
              }}
              transition={{
                duration: 0.8,
                repeat: Infinity,
                delay: index * 0.1
              }}
            />
          ))}
        </div>
        {text && (
          <p className={`mt-3 ${sizeClasses.text} text-gray-600 font-medium`}>
            {text}
          </p>
        )}
      </div>
    )
  }

  return null
}

// Full page loading overlay
interface LoadingOverlayProps {
  text?: string
  show: boolean
  className?: string
}

export function LoadingOverlay({ text = 'Loading...', show, className = '' }: LoadingOverlayProps) {
  if (!show) return null

  return (
    <motion.div
      className={`fixed inset-0 bg-white/80 backdrop-blur-sm z-50 flex items-center justify-center ${className}`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="text-center">
        <div className="relative">
          <motion.div
            className="w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center"
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
          >
            <Zap className="w-8 h-8 text-white" />
          </motion.div>
          
          {/* Orbital dots */}
          <motion.div
            className="absolute inset-0 rounded-full border-2 border-blue-200"
            animate={{ rotate: -360 }}
            transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
          >
            <div className="w-3 h-3 bg-blue-600 rounded-full absolute -top-1.5 left-1/2 transform -translate-x-1/2" />
          </motion.div>
        </div>
        
        <motion.p
          className="mt-4 text-lg font-medium text-gray-700"
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          {text}
        </motion.p>
      </div>
    </motion.div>
  )
}

// Loading skeleton for cards
export function LoadingSkeleton({ className = '' }: { className?: string }) {
  return (
    <div className={`animate-pulse ${className}`}>
      <div className="bg-gray-200 rounded-lg h-4 w-3/4 mb-2" />
      <div className="bg-gray-200 rounded-lg h-4 w-1/2 mb-2" />
      <div className="bg-gray-200 rounded-lg h-4 w-5/6" />
    </div>
  )
}

// Loading state for data tables
export function TableLoadingSkeleton({ rows = 5, cols = 4 }) {
  return (
    <div className="animate-pulse">
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="flex space-x-4 py-3 border-b border-gray-100">
          {Array.from({ length: cols }).map((_, colIndex) => (
            <div
              key={colIndex}
              className="flex-1 bg-gray-200 rounded h-4"
              style={{
                width: colIndex === 0 ? '25%' : colIndex === cols - 1 ? '15%' : '20%'
              }}
            />
          ))}
        </div>
      ))}
    </div>
  )
}

// Loading state for charts
export function ChartLoadingSkeleton({ className = '' }: { className?: string }) {
  return (
    <div className={`animate-pulse ${className}`}>
      <div className="flex items-end justify-between h-64 space-x-2">
        {Array.from({ length: 12 }).map((_, index) => (
          <div
            key={index}
            className="flex-1 bg-gray-200 rounded-t"
            style={{
              height: `${Math.random() * 60 + 40}%`
            }}
          />
        ))}
      </div>
      <div className="flex justify-between mt-4">
        {Array.from({ length: 6 }).map((_, index) => (
          <div key={index} className="bg-gray-200 rounded h-3 w-12" />
        ))}
      </div>
    </div>
  )
}

// Loading button state
interface LoadingButtonProps {
  children: React.ReactNode
  loading: boolean
  className?: string
  disabled?: boolean
  onClick?: () => void
}

export function LoadingButton({
  children,
  loading,
  className = '',
  disabled,
  onClick
}: LoadingButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={`
        inline-flex items-center justify-center px-4 py-2 rounded-lg font-medium
        transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
        disabled:opacity-50 disabled:cursor-not-allowed
        ${loading ? 'cursor-wait' : ''}
        ${className}
      `}
    >
      {loading && (
        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
      )}
      {children}
    </button>
  )
}
