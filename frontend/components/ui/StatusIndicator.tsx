'use client'

import { motion } from 'framer-motion'
import { CheckCircle, AlertCircle, XCircle, Clock } from 'lucide-react'

export type StatusType = 'online' | 'offline' | 'warning' | 'pending'

interface StatusIndicatorProps {
  status: StatusType
  label?: string
  showIcon?: boolean
  showLabel?: boolean
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const statusConfig = {
  online: {
    color: 'text-green-600',
    bgColor: 'bg-green-100',
    dotColor: 'bg-green-500',
    icon: CheckCircle,
    label: 'Online'
  },
  offline: {
    color: 'text-red-600',
    bgColor: 'bg-red-100',
    dotColor: 'bg-red-500',
    icon: XCircle,
    label: 'Offline'
  },
  warning: {
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-100',
    dotColor: 'bg-yellow-500',
    icon: AlertCircle,
    label: 'Warning'
  },
  pending: {
    color: 'text-blue-600',
    bgColor: 'bg-blue-100',
    dotColor: 'bg-blue-500',
    icon: Clock,
    label: 'Pending'
  }
}

export default function StatusIndicator({
  status,
  label,
  showIcon = false,
  showLabel = true,
  size = 'md',
  className = ''
}: StatusIndicatorProps) {
  const config = statusConfig[status]
  const Icon = config.icon
  
  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return {
          dot: 'w-2 h-2',
          icon: 'w-3 h-3',
          text: 'text-xs',
          padding: 'px-2 py-1'
        }
      case 'lg':
        return {
          dot: 'w-4 h-4',
          icon: 'w-5 h-5',
          text: 'text-sm',
          padding: 'px-3 py-2'
        }
      default:
        return {
          dot: 'w-3 h-3',
          icon: 'w-4 h-4',
          text: 'text-sm',
          padding: 'px-2 py-1'
        }
    }
  }

  const sizeClasses = getSizeClasses()
  const displayLabel = label || config.label

  if (showIcon) {
    return (
      <div className={`inline-flex items-center space-x-2 ${config.bgColor} ${config.color} rounded-full ${sizeClasses.padding} ${className}`}>
        <Icon className={sizeClasses.icon} />
        {showLabel && (
          <span className={`font-medium ${sizeClasses.text}`}>
            {displayLabel}
          </span>
        )}
      </div>
    )
  }

  return (
    <div className={`inline-flex items-center space-x-2 ${className}`}>
      <motion.div
        className={`${sizeClasses.dot} ${config.dotColor} rounded-full relative`}
        animate={status === 'online' ? { scale: [1, 1.2, 1] } : {}}
        transition={{ duration: 2, repeat: Infinity }}
      >
        {/* Pulse effect for online status */}
        {status === 'online' && (
          <div className={`absolute inset-0 ${config.dotColor} rounded-full animate-ping opacity-75`} />
        )}
      </motion.div>
      
      {showLabel && (
        <span className={`font-medium ${sizeClasses.text} ${config.color}`}>
          {displayLabel}
        </span>
      )}
    </div>
  )
}

// Status badge with more detailed info
interface StatusBadgeProps {
  status: StatusType
  title: string
  description?: string
  timestamp?: string
  className?: string
}

export function StatusBadge({ 
  status, 
  title, 
  description, 
  timestamp, 
  className = '' 
}: StatusBadgeProps) {
  const config = statusConfig[status]
  const Icon = config.icon

  return (
    <motion.div
      className={`${config.bgColor} border border-gray-200 rounded-lg p-3 ${className}`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="flex items-start space-x-3">
        <div className={`flex-shrink-0 ${config.color}`}>
          <Icon className="w-5 h-5" />
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <h4 className={`text-sm font-medium ${config.color}`}>
              {title}
            </h4>
            {timestamp && (
              <span className="text-xs text-gray-500">
                {timestamp}
              </span>
            )}
          </div>
          
          {description && (
            <p className="text-sm text-gray-600 mt-1">
              {description}
            </p>
          )}
        </div>
      </div>
    </motion.div>
  )
}

// System health indicator
interface SystemHealthProps {
  services: Array<{
    name: string
    status: StatusType
    uptime?: string
    lastCheck?: string
  }>
  className?: string
}

export function SystemHealth({ services, className = '' }: SystemHealthProps) {
  const overallStatus: StatusType = services.some(s => s.status === 'offline') 
    ? 'offline' 
    : services.some(s => s.status === 'warning') 
    ? 'warning' 
    : 'online'

  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-4 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          System Health
        </h3>
        <StatusIndicator status={overallStatus} showIcon />
      </div>

      <div className="space-y-3">
        {services.map((service, index) => (
          <motion.div
            key={service.name}
            className="flex items-center justify-between p-2 rounded hover:bg-gray-50"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
          >
            <div className="flex items-center space-x-3">
              <StatusIndicator status={service.status} showLabel={false} />
              <div>
                <div className="text-sm font-medium text-gray-900">
                  {service.name}
                </div>
                {service.uptime && (
                  <div className="text-xs text-gray-500">
                    Uptime: {service.uptime}
                  </div>
                )}
              </div>
            </div>
            
            {service.lastCheck && (
              <div className="text-xs text-gray-500">
                {service.lastCheck}
              </div>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  )
}

// Status timeline for showing status changes over time
interface StatusTimelineProps {
  events: Array<{
    timestamp: string
    status: StatusType
    message: string
    details?: string
  }>
  className?: string
}

export function StatusTimeline({ events, className = '' }: StatusTimelineProps) {
  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-4 ${className}`}>
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Status History
      </h3>
      
      <div className="space-y-4">
        {events.map((event, index) => {
          const config = statusConfig[event.status]
          const Icon = config.icon
          
          return (
            <motion.div
              key={index}
              className="flex items-start space-x-3"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              <div className={`flex-shrink-0 ${config.color}`}>
                <Icon className="w-4 h-4" />
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-gray-900">
                    {event.message}
                  </p>
                  <span className="text-xs text-gray-500">
                    {event.timestamp}
                  </span>
                </div>
                
                {event.details && (
                  <p className="text-sm text-gray-600 mt-1">
                    {event.details}
                  </p>
                )}
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
