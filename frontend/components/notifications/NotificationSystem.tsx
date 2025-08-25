'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { formatters, dateUtils } from '@/lib/utils'
import {
  Bell,
  X,
  Check,
  AlertTriangle,
  Info,
  CheckCircle,
  XCircle,
  Zap,
  DollarSign,
  TrendingUp,
  Building,
  Clock,
  Users,
  Settings,
  Mail,
  Smartphone,
  Eye,
  EyeOff,
  Trash2,
  Archive
} from 'lucide-react'

export interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error' | 'energy' | 'cost' | 'system'
  title: string
  message: string
  timestamp: Date
  read: boolean
  priority: 'low' | 'medium' | 'high' | 'critical'
  source?: string
  buildingId?: string
  action?: {
    label: string
    onClick: () => void
  }
  data?: Record<string, any>
}

interface NotificationCenterProps {
  notifications: Notification[]
  onMarkAsRead: (id: string) => void
  onMarkAllAsRead: () => void
  onRemove: (id: string) => void
  onClearAll: () => void
  isOpen: boolean
  onClose: () => void
}

export function NotificationCenter({
  notifications,
  onMarkAsRead,
  onMarkAllAsRead,
  onRemove,
  onClearAll,
  isOpen,
  onClose
}: NotificationCenterProps) {
  const [filter, setFilter] = useState<'all' | Notification['type']>('all')
  const [showUnreadOnly, setShowUnreadOnly] = useState(false)

  const filteredNotifications = notifications.filter(notification => {
    const matchesFilter = filter === 'all' || notification.type === filter
    const matchesReadStatus = !showUnreadOnly || !notification.read
    return matchesFilter && matchesReadStatus
  })

  const unreadCount = notifications.filter(n => !n.read).length
  const criticalCount = notifications.filter(n => n.priority === 'critical' && !n.read).length

  const getNotificationIcon = (type: Notification['type'], priority: Notification['priority']) => {
    const iconProps = {
      className: `w-5 h-5 ${priority === 'critical' ? 'animate-pulse' : ''}`
    }

    switch (type) {
      case 'success':
        return <CheckCircle {...iconProps} className={`${iconProps.className} text-green-600`} />
      case 'warning':
        return <AlertTriangle {...iconProps} className={`${iconProps.className} text-yellow-600`} />
      case 'error':
        return <XCircle {...iconProps} className={`${iconProps.className} text-red-600`} />
      case 'energy':
        return <Zap {...iconProps} className={`${iconProps.className} text-blue-600`} />
      case 'cost':
        return <DollarSign {...iconProps} className={`${iconProps.className} text-green-600`} />
      case 'system':
        return <Settings {...iconProps} className={`${iconProps.className} text-purple-600`} />
      default:
        return <Info {...iconProps} className={`${iconProps.className} text-blue-600`} />
    }
  }

  const getNotificationStyles = (type: Notification['type'], priority: Notification['priority']) => {
    const baseStyles = "border-l-4"
    
    let typeStyles = ""
    switch (type) {
      case 'success':
        typeStyles = "border-green-500 bg-green-50"
        break
      case 'warning':
        typeStyles = "border-yellow-500 bg-yellow-50"
        break
      case 'error':
        typeStyles = "border-red-500 bg-red-50"
        break
      case 'energy':
        typeStyles = "border-blue-500 bg-blue-50"
        break
      case 'cost':
        typeStyles = "border-green-500 bg-green-50"
        break
      case 'system':
        typeStyles = "border-purple-500 bg-purple-50"
        break
      default:
        typeStyles = "border-blue-500 bg-blue-50"
    }

    const priorityStyles = priority === 'critical' ? "ring-2 ring-red-500 ring-opacity-50" : ""
    
    return `${baseStyles} ${typeStyles} ${priorityStyles}`
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black bg-opacity-25 z-40"
          />
          
          {/* Notification Panel */}
          <motion.div
            initial={{ opacity: 0, x: 400 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 400 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed right-0 top-0 h-full w-full max-w-md bg-white shadow-2xl z-50 flex flex-col"
          >
            {/* Header */}
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900">
                  Notifications
                </h2>
                <button
                  onClick={onClose}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-gray-500" />
                </button>
              </div>

              {/* Stats */}
              <div className="flex items-center space-x-4 text-sm">
                <div className="flex items-center text-gray-600">
                  <Bell className="w-4 h-4 mr-1" />
                  {notifications.length} total
                </div>
                {unreadCount > 0 && (
                  <div className="flex items-center text-blue-600">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mr-1" />
                    {unreadCount} unread
                  </div>
                )}
                {criticalCount > 0 && (
                  <div className="flex items-center text-red-600">
                    <AlertTriangle className="w-4 h-4 mr-1" />
                    {criticalCount} critical
                  </div>
                )}
              </div>

              {/* Controls */}
              <div className="flex items-center justify-between mt-4">
                <div className="flex items-center space-x-2">
                  <select
                    value={filter}
                    onChange={(e) => setFilter(e.target.value as any)}
                    className="text-sm border-gray-300 rounded-lg focus:border-blue-500 focus:ring-blue-500"
                  >
                    <option value="all">All Types</option>
                    <option value="energy">Energy</option>
                    <option value="cost">Cost</option>
                    <option value="system">System</option>
                    <option value="warning">Warnings</option>
                    <option value="error">Errors</option>
                  </select>
                  
                  <button
                    onClick={() => setShowUnreadOnly(!showUnreadOnly)}
                    className={`p-2 rounded-lg transition-colors ${
                      showUnreadOnly 
                        ? 'bg-blue-100 text-blue-700' 
                        : 'text-gray-400 hover:text-gray-600 hover:bg-gray-50'
                    }`}
                    title={showUnreadOnly ? 'Show all' : 'Show unread only'}
                  >
                    {showUnreadOnly ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                  </button>
                </div>

                <div className="flex items-center space-x-2">
                  {unreadCount > 0 && (
                    <button
                      onClick={onMarkAllAsRead}
                      className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                    >
                      Mark all read
                    </button>
                  )}
                  
                  {notifications.length > 0 && (
                    <button
                      onClick={onClearAll}
                      className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                      title="Clear all notifications"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Notifications List */}
            <div className="flex-1 overflow-y-auto">
              {filteredNotifications.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-gray-500">
                  <Bell className="w-12 h-12 mb-4 opacity-50" />
                  <h3 className="text-lg font-medium mb-2">No notifications</h3>
                  <p className="text-sm text-center px-6">
                    {showUnreadOnly 
                      ? "You're all caught up! No unread notifications."
                      : "You don't have any notifications yet."
                    }
                  </p>
                </div>
              ) : (
                <div className="p-4 space-y-3">
                  <AnimatePresence>
                    {filteredNotifications.map((notification, index) => (
                      <NotificationItem
                        key={notification.id}
                        notification={notification}
                        onMarkAsRead={onMarkAsRead}
                        onRemove={onRemove}
                        index={index}
                      />
                    ))}
                  </AnimatePresence>
                </div>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

// Individual Notification Item
function NotificationItem({
  notification,
  onMarkAsRead,
  onRemove,
  index
}: {
  notification: Notification
  onMarkAsRead: (id: string) => void
  onRemove: (id: string) => void
  index: number
}) {
  const [isExpanded, setIsExpanded] = useState(false)

  const icon = getNotificationIcon(notification.type, notification.priority)
  const styles = getNotificationStyles(notification.type, notification.priority)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: 400 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
      className={`p-4 rounded-lg border bg-white shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer ${
        !notification.read ? 'ring-2 ring-blue-500 ring-opacity-20' : ''
      } ${styles}`}
      onClick={() => {
        if (!notification.read) {
          onMarkAsRead(notification.id)
        }
        setIsExpanded(!isExpanded)
      }}
    >
      <div className="flex items-start space-x-3">
        {/* Icon */}
        <div className="flex-shrink-0 mt-0.5">
          {icon}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h4 className={`text-sm font-medium ${!notification.read ? 'text-gray-900' : 'text-gray-700'}`}>
                {notification.title}
              </h4>
              <p className={`text-sm mt-1 ${!notification.read ? 'text-gray-700' : 'text-gray-500'}`}>
                {notification.message}
              </p>
            </div>
            
            {/* Priority Indicator */}
            {notification.priority === 'critical' && (
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
            )}
          </div>

          {/* Metadata */}
          <div className="flex items-center justify-between mt-3">
            <div className="flex items-center space-x-3 text-xs text-gray-500">
              <div className="flex items-center">
                <Clock className="w-3 h-3 mr-1" />
                {formatters.relativeTime(notification.timestamp)}
              </div>
              
              {notification.source && (
                <div className="flex items-center">
                  <Building className="w-3 h-3 mr-1" />
                  {notification.source}
                </div>
              )}
              
              {notification.priority !== 'low' && (
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                  notification.priority === 'critical' ? 'bg-red-100 text-red-700' :
                  notification.priority === 'high' ? 'bg-orange-100 text-orange-700' :
                  'bg-yellow-100 text-yellow-700'
                }`}>
                  {notification.priority}
                </span>
              )}
            </div>

            <div className="flex items-center space-x-1">
              {!notification.read && (
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    onMarkAsRead(notification.id)
                  }}
                  className="p-1 text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded"
                  title="Mark as read"
                >
                  <Check className="w-3 h-3" />
                </button>
              )}
              
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onRemove(notification.id)
                }}
                className="p-1 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded"
                title="Remove notification"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          </div>

          {/* Expanded Content */}
          <AnimatePresence>
            {isExpanded && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-3 pt-3 border-t border-gray-200"
              >
                {/* Additional Data */}
                {notification.data && (
                  <div className="mb-3">
                    <h5 className="text-xs font-medium text-gray-700 mb-2">Details:</h5>
                    <div className="bg-gray-50 rounded-lg p-3 text-xs">
                      {Object.entries(notification.data).map(([key, value]) => (
                        <div key={key} className="flex justify-between py-1">
                          <span className="text-gray-600 capitalize">
                            {key.replace('_', ' ')}:
                          </span>
                          <span className="text-gray-900 font-medium">
                            {typeof value === 'number' ? formatters.number(value, 1) : String(value)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Action Button */}
                {notification.action && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      notification.action!.onClick()
                    }}
                    className="btn-primary btn-sm w-full"
                  >
                    {notification.action.label}
                  </button>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.div>
  )
}

// Notification Bell Icon with Badge
interface NotificationBellProps {
  unreadCount: number
  criticalCount: number
  onClick: () => void
  size?: 'sm' | 'md' | 'lg'
}

export function NotificationBell({ 
  unreadCount, 
  criticalCount, 
  onClick, 
  size = 'md' 
}: NotificationBellProps) {
  const iconSizes = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6'
  }

  const buttonSizes = {
    sm: 'p-1.5',
    md: 'p-2',
    lg: 'p-3'
  }

  return (
    <motion.button
      onClick={onClick}
      className={`relative ${buttonSizes[size]} text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-all duration-200`}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      <Bell className={`${iconSizes[size]} ${criticalCount > 0 ? 'animate-pulse' : ''}`} />
      
      {/* Badge */}
      <AnimatePresence>
        {unreadCount > 0 && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            exit={{ scale: 0 }}
            className={`absolute -top-1 -right-1 ${
              criticalCount > 0 ? 'bg-red-500' : 'bg-blue-500'
            } text-white text-xs rounded-full min-w-[1.25rem] h-5 flex items-center justify-center px-1`}
          >
            {unreadCount > 99 ? '99+' : unreadCount}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.button>
  )
}

// Toast Notification Component
interface ToastNotificationProps {
  notification: {
    id: string
    type: 'success' | 'error' | 'warning' | 'info'
    title: string
    message?: string
    duration?: number
  }
  onRemove: (id: string) => void
}

export function ToastNotification({ notification, onRemove }: ToastNotificationProps) {
  const [isVisible, setIsVisible] = useState(true)

  useEffect(() => {
    const duration = notification.duration || 5000
    
    const timer = setTimeout(() => {
      setIsVisible(false)
      setTimeout(() => onRemove(notification.id), 300)
    }, duration)

    return () => clearTimeout(timer)
  }, [notification.id, notification.duration, onRemove])

  const getToastStyles = () => {
    switch (notification.type) {
      case 'success':
        return 'bg-green-50 border-green-200 text-green-800'
      case 'error':
        return 'bg-red-50 border-red-200 text-red-800'
      case 'warning':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800'
      default:
        return 'bg-blue-50 border-blue-200 text-blue-800'
    }
  }

  const getToastIcon = () => {
    switch (notification.type) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'error':
        return <XCircle className="w-5 h-5 text-red-600" />
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />
      default:
        return <Info className="w-5 h-5 text-blue-600" />
    }
  }

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: -50, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -50, scale: 0.95 }}
          className={`max-w-sm mx-auto bg-white rounded-lg shadow-lg border p-4 ${getToastStyles()}`}
        >
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              {getToastIcon()}
            </div>
            
            <div className="flex-1 min-w-0">
              <h4 className="text-sm font-medium">
                {notification.title}
              </h4>
              {notification.message && (
                <p className="text-sm mt-1 opacity-90">
                  {notification.message}
                </p>
              )}
            </div>
            
            <button
              onClick={() => {
                setIsVisible(false)
                setTimeout(() => onRemove(notification.id), 300)
              }}
              className="flex-shrink-0 text-current opacity-70 hover:opacity-100"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

// Toast Container
interface ToastContainerProps {
  notifications: Array<{
    id: string
    type: 'success' | 'error' | 'warning' | 'info'
    title: string
    message?: string
    duration?: number
  }>
  onRemove: (id: string) => void
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center'
}

export function ToastContainer({ 
  notifications, 
  onRemove, 
  position = 'top-right' 
}: ToastContainerProps) {
  const getPositionStyles = () => {
    switch (position) {
      case 'top-left':
        return 'top-4 left-4'
      case 'top-center':
        return 'top-4 left-1/2 transform -translate-x-1/2'
      case 'top-right':
        return 'top-4 right-4'
      case 'bottom-left':
        return 'bottom-4 left-4'
      case 'bottom-center':
        return 'bottom-4 left-1/2 transform -translate-x-1/2'
      case 'bottom-right':
        return 'bottom-4 right-4'
      default:
        return 'top-4 right-4'
    }
  }

  return (
    <div className={`fixed z-50 ${getPositionStyles()}`}>
      <div className="space-y-2">
        {notifications.map((notification) => (
          <ToastNotification
            key={notification.id}
            notification={notification}
            onRemove={onRemove}
          />
        ))}
      </div>
    </div>
  )
}

// Hook per generare notifiche di sistema
export function useSystemNotifications() {
  const [notifications, setNotifications] = useState<Notification[]>([])

  const addNotification = (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
    const newNotification: Notification = {
      ...notification,
      id: Math.random().toString(36).substr(2, 9),
      timestamp: new Date(),
      read: false
    }
    
    setNotifications(prev => [newNotification, ...prev].slice(0, 100))
  }

  // Notifiche predefinite per eventi comuni
  const notifyOptimizationComplete = (buildingName: string, savingsPercent: number, costSavings: number) => {
    addNotification({
      type: 'success',
      title: 'Optimization Complete',
      message: `${buildingName} optimization finished with ${savingsPercent.toFixed(1)}% energy savings`,
      priority: 'medium',
      source: buildingName,
      action: {
        label: 'View Results',
        onClick: () => console.log('Navigate to results')
      },
      data: {
        savings_percent: savingsPercent,
        cost_savings: costSavings,
        building: buildingName
      }
    })
  }

  const notifyThresholdExceeded = (buildingName: string, metric: string, value: number, threshold: number) => {
    addNotification({
      type: 'warning',
      title: 'Threshold Exceeded',
      message: `${metric} in ${buildingName} has exceeded the warning threshold`,
      priority: 'high',
      source: buildingName,
      action: {
        label: 'Check Building',
        onClick: () => console.log('Navigate to building')
      },
      data: {
        metric,
        current_value: value,
        threshold,
        building: buildingName
      }
    })
  }

  const notifySystemError = (error: string, component: string) => {
    addNotification({
      type: 'error',
      title: 'System Error',
      message: `Error in ${component}: ${error}`,
      priority: 'critical',
      source: 'System',
      data: {
        component,
        error_message: error
      }
    })
  }

  const notifyDataUpdate = (source: string, recordCount: number) => {
    addNotification({
      type: 'info',
      title: 'Data Updated',
      message: `New data available from ${source} (${recordCount} records)`,
      priority: 'low',
      source,
      data: {
        record_count: recordCount,
        data_source: source
      }
    })
  }

  const notifyCostSavings = (buildingName: string, monthlySavings: number) => {
    addNotification({
      type: 'cost',
      title: 'Cost Savings Achieved',
      message: `${buildingName} saved ${formatters.currency(monthlySavings)} this month`,
      priority: 'medium',
      source: buildingName,
      action: {
        label: 'View Report',
        onClick: () => console.log('Navigate to cost report')
      },
      data: {
        monthly_savings: monthlySavings,
        building: buildingName
      }
    })
  }

  return {
    notifications,
    addNotification,
    notifyOptimizationComplete,
    notifyThresholdExceeded,
    notifySystemError,
    notifyDataUpdate,
    notifyCostSavings,
    markAsRead: (id: string) => {
      setNotifications(prev => 
        prev.map(n => n.id === id ? { ...n, read: true } : n)
      )
    },
    markAllAsRead: () => {
      setNotifications(prev => prev.map(n => ({ ...n, read: true })))
    },
    remove: (id: string) => {
      setNotifications(prev => prev.filter(n => n.id !== id))
    },
    clearAll: () => {
      setNotifications([])
    }
  }
}

// In-app notification banner
interface NotificationBannerProps {
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  action?: {
    label: string
    onClick: () => void
  }
  onDismiss?: () => void
  className?: string
}

export function NotificationBanner({
  type,
  title,
  message,
  action,
  onDismiss,
  className = ''
}: NotificationBannerProps) {
  const getStyles = () => {
    switch (type) {
      case 'success':
        return 'bg-green-50 border-green-200 text-green-800'
      case 'error':
        return 'bg-red-50 border-red-200 text-red-800'
      case 'warning':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800'
      default:
        return 'bg-blue-50 border-blue-200 text-blue-800'
    }
  }

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'error':
        return <XCircle className="w-5 h-5 text-red-600" />
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />
      default:
        return <Info className="w-5 h-5 text-blue-600" />
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={`border rounded-lg p-4 ${getStyles()} ${className}`}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            {getIcon()}
          </div>
          
          <div className="flex-1">
            <h3 className="text-sm font-medium">
              {title}
            </h3>
            <p className="text-sm mt-1 opacity-90">
              {message}
            </p>
            
            {action && (
              <button
                onClick={action.onClick}
                className="text-sm font-medium underline hover:no-underline mt-2"
              >
                {action.label}
              </button>
            )}
          </div>
        </div>

        {onDismiss && (
          <button
            onClick={onDismiss}
            className="flex-shrink-0 text-current opacity-70 hover:opacity-100"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    </motion.div>
  )
}

// Utility functions (moved outside of components to avoid recreating them)
function getNotificationIcon(type: Notification['type'], priority: Notification['priority']) {
  const iconProps = {
    className: `w-5 h-5 ${priority === 'critical' ? 'animate-pulse' : ''}`
  }

  switch (type) {
    case 'success':
      return <CheckCircle {...iconProps} className={`${iconProps.className} text-green-600`} />
    case 'warning':
      return <AlertTriangle {...iconProps} className={`${iconProps.className} text-yellow-600`} />
    case 'error':
      return <XCircle {...iconProps} className={`${iconProps.className} text-red-600`} />
    case 'energy':
      return <Zap {...iconProps} className={`${iconProps.className} text-blue-600`} />
    case 'cost':
      return <DollarSign {...iconProps} className={`${iconProps.className} text-green-600`} />
    case 'system':
      return <Settings {...iconProps} className={`${iconProps.className} text-purple-600`} />
    default:
      return <Info {...iconProps} className={`${iconProps.className} text-blue-600`} />
  }
}

function getNotificationStyles(type: Notification['type'], priority: Notification['priority']) {
  const baseStyles = "border-l-4"
  
  let typeStyles = ""
  switch (type) {
    case 'success':
      typeStyles = "border-green-500 bg-green-50"
      break
    case 'warning':
      typeStyles = "border-yellow-500 bg-yellow-50"
      break
    case 'error':
      typeStyles = "border-red-500 bg-red-50"
      break
    case 'energy':
      typeStyles = "border-blue-500 bg-blue-50"
      break
    case 'cost':
      typeStyles = "border-green-500 bg-green-50"
      break
    case 'system':
      typeStyles = "border-purple-500 bg-purple-50"
      break
    default:
      typeStyles = "border-blue-500 bg-blue-50"
  }

  const priorityStyles = priority === 'critical' ? "ring-2 ring-red-500 ring-opacity-50" : ""
  
  return `${baseStyles} ${typeStyles} ${priorityStyles}`
}
