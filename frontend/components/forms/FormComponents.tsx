'use client'

import { useState, forwardRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Calendar,
  Clock,
  MapPin,
  User,
  Mail,
  Phone,
  Building,
  Zap,
  DollarSign,
  AlertCircle,
  CheckCircle,
  Eye,
  EyeOff
} from 'lucide-react'
import { clsx } from 'clsx'

// Base Input Component
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  success?: string
  hint?: string
  icon?: React.ReactNode
  rightIcon?: React.ReactNode
  containerClassName?: string
  showLabel?: boolean
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ 
    label, 
    error, 
    success, 
    hint, 
    icon, 
    rightIcon,
    containerClassName = '', 
    className = '',
    showLabel = true,
    ...props 
  }, ref) => {
    const [isFocused, setIsFocused] = useState(false)

    return (
      <div className={containerClassName}>
        {label && showLabel && (
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {label}
            {props.required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}
        
        <div className="relative">
          {icon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <div className="w-5 h-5 text-gray-400">
                {icon}
              </div>
            </div>
          )}
          
          <input
            ref={ref}
            className={clsx(
              'block w-full rounded-xl border-gray-300 shadow-sm transition-all duration-200',
              'focus:border-blue-500 focus:ring-blue-500 focus:ring-1',
              'disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed',
              {
                'pl-10': icon,
                'pr-10': rightIcon,
                'border-red-300 focus:border-red-500 focus:ring-red-500': error,
                'border-green-300 focus:border-green-500 focus:ring-green-500': success,
              },
              className
            )}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            {...props}
          />
          
          {rightIcon && (
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
              <div className="w-5 h-5 text-gray-400">
                {rightIcon}
              </div>
            </div>
          )}
        </div>
        
        <AnimatePresence>
          {(error || success || hint) && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-2"
            >
              {error && (
                <div className="flex items-center text-sm text-red-600">
                  <AlertCircle className="w-4 h-4 mr-1 flex-shrink-0" />
                  {error}
                </div>
              )}
              {success && (
                <div className="flex items-center text-sm text-green-600">
                  <CheckCircle className="w-4 h-4 mr-1 flex-shrink-0" />
                  {success}
                </div>
              )}
              {hint && !error && !success && (
                <div className="text-sm text-gray-500">
                  {hint}
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    )
  }
)

Input.displayName = 'Input'

// Password Input
interface PasswordInputProps extends Omit<InputProps, 'type' | 'rightIcon'> {
  showStrength?: boolean
}

export function PasswordInput({ showStrength = false, ...props }: PasswordInputProps) {
  const [showPassword, setShowPassword] = useState(false)
  const [strength, setStrength] = useState(0)

  const calculateStrength = (password: string) => {
    let score = 0
    if (password.length >= 8) score++
    if (/[a-z]/.test(password)) score++
    if (/[A-Z]/.test(password)) score++
    if (/[0-9]/.test(password)) score++
    if (/[^A-Za-z0-9]/.test(password)) score++
    return score
  }

  const getStrengthColor = (strength: number) => {
    if (strength <= 2) return 'bg-red-500'
    if (strength <= 3) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  const getStrengthLabel = (strength: number) => {
    if (strength <= 2) return 'Weak'
    if (strength <= 3) return 'Medium'
    return 'Strong'
  }

  return (
    <div>
      <Input
        {...props}
        type={showPassword ? 'text' : 'password'}
        rightIcon={
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="hover:text-gray-600 transition-colors"
          >
            {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
          </button>
        }
        onChange={(e) => {
          if (showStrength) {
            setStrength(calculateStrength(e.target.value))
          }
          props.onChange?.(e)
        }}
      />
      
      {showStrength && props.value && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mt-2"
        >
          <div className="flex items-center space-x-2">
            <div className="flex-1 bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all duration-300 ${getStrengthColor(strength)}`}
                style={{ width: `${(strength / 5) * 100}%` }}
              />
            </div>
            <span className="text-sm font-medium text-gray-600">
              {getStrengthLabel(strength)}
            </span>
          </div>
        </motion.div>
      )}
    </div>
  )
}

// Select Component
interface SelectOption {
  value: string
  label: string
  disabled?: boolean
}

interface SelectProps extends Omit<React.SelectHTMLAttributes<HTMLSelectElement>, 'children'> {
  label?: string
  error?: string
  success?: string
  hint?: string
  icon?: React.ReactNode
  options: SelectOption[]
  placeholder?: string
  containerClassName?: string
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ 
    label, 
    error, 
    success, 
    hint, 
    icon,
    options, 
    placeholder,
    containerClassName = '', 
    className = '', 
    ...props 
  }, ref) => {
    return (
      <div className={containerClassName}>
        {label && (
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {label}
            {props.required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}
        
        <div className="relative">
          {icon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none z-10">
              <div className="w-5 h-5 text-gray-400">
                {icon}
              </div>
            </div>
          )}
          
          <select
            ref={ref}
            className={clsx(
              'block w-full rounded-xl border-gray-300 shadow-sm transition-all duration-200',
              'focus:border-blue-500 focus:ring-blue-500 focus:ring-1',
              'disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed',
              {
                'pl-10': icon,
                'border-red-300 focus:border-red-500 focus:ring-red-500': error,
                'border-green-300 focus:border-green-500 focus:ring-green-500': success,
              },
              className
            )}
            {...props}
          >
            {placeholder && (
              <option value="" disabled>
                {placeholder}
              </option>
            )}
            {options.map((option) => (
              <option key={option.value} value={option.value} disabled={option.disabled}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        
        <AnimatePresence>
          {(error || success || hint) && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-2"
            >
              {error && (
                <div className="flex items-center text-sm text-red-600">
                  <AlertCircle className="w-4 h-4 mr-1 flex-shrink-0" />
                  {error}
                </div>
              )}
              {success && (
                <div className="flex items-center text-sm text-green-600">
                  <CheckCircle className="w-4 h-4 mr-1 flex-shrink-0" />
                  {success}
                </div>
              )}
              {hint && !error && !success && (
                <div className="text-sm text-gray-500">
                  {hint}
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    )
  }
)

Select.displayName = 'Select'

// Textarea Component
interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
  error?: string
  success?: string
  hint?: string
  containerClassName?: string
  showCount?: boolean
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ 
    label, 
    error, 
    success, 
    hint, 
    containerClassName = '', 
    className = '',
    showCount = false,
    maxLength,
    value,
    ...props 
  }, ref) => {
    const currentLength = String(value || '').length
    
    return (
      <div className={containerClassName}>
        {label && (
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {label}
            {props.required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}
        
        <textarea
          ref={ref}
          value={value}
          maxLength={maxLength}
          className={clsx(
            'block w-full rounded-xl border-gray-300 shadow-sm transition-all duration-200',
            'focus:border-blue-500 focus:ring-blue-500 focus:ring-1',
            'disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed',
            'resize-vertical min-h-[100px]',
            {
              'border-red-300 focus:border-red-500 focus:ring-red-500': error,
              'border-green-300 focus:border-green-500 focus:ring-green-500': success,
            },
            className
          )}
          {...props}
        />
        
        <div className="mt-2 flex justify-between">
          <div className="flex-1">
            <AnimatePresence>
              {(error || success || hint) && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                >
                  {error && (
                    <div className="flex items-center text-sm text-red-600">
                      <AlertCircle className="w-4 h-4 mr-1 flex-shrink-0" />
                      {error}
                    </div>
                  )}
                  {success && (
                    <div className="flex items-center text-sm text-green-600">
                      <CheckCircle className="w-4 h-4 mr-1 flex-shrink-0" />
                      {success}
                    </div>
                  )}
                  {hint && !error && !success && (
                    <div className="text-sm text-gray-500">
                      {hint}
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
          
          {showCount && maxLength && (
            <div className={clsx(
              'text-sm',
              currentLength > maxLength * 0.9 ? 'text-red-500' : 'text-gray-500'
            )}>
              {currentLength}/{maxLength}
            </div>
          )}
        </div>
      </div>
    )
  }
)

Textarea.displayName = 'Textarea'

// Checkbox Component
interface CheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string
  description?: string
  error?: string
  containerClassName?: string
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ label, description, error, containerClassName = '', className = '', ...props }, ref) => {
    return (
      <div className={containerClassName}>
        <div className="flex items-start">
          <div className="flex items-center h-5">
            <input
              ref={ref}
              type="checkbox"
              className={clsx(
                'w-4 h-4 rounded border-gray-300 text-blue-600 transition-colors',
                'focus:ring-blue-500 focus:ring-2 focus:ring-offset-0',
                'disabled:opacity-50 disabled:cursor-not-allowed',
                {
                  'border-red-300 focus:ring-red-500': error,
                },
                className
              )}
              {...props}
            />
          </div>
          {(label || description) && (
            <div className="ml-3 text-sm">
              {label && (
                <label className="font-medium text-gray-900 cursor-pointer">
                  {label}
                </label>
              )}
              {description && (
                <p className="text-gray-500 mt-0.5">
                  {description}
                </p>
              )}
            </div>
          )}
        </div>
        
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-2"
            >
              <div className="flex items-center text-sm text-red-600">
                <AlertCircle className="w-4 h-4 mr-1 flex-shrink-0" />
                {error}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    )
  }
)

Checkbox.displayName = 'Checkbox'

// Form Group Component
interface FormGroupProps {
  children: React.ReactNode
  title?: string
  description?: string
  className?: string
}

export function FormGroup({ children, title, description, className = '' }: FormGroupProps) {
  return (
    <div className={clsx('space-y-6', className)}>
      {(title || description) && (
        <div>
          {title && (
            <h3 className="text-lg font-medium text-gray-900">
              {title}
            </h3>
          )}
          {description && (
            <p className="mt-1 text-sm text-gray-600">
              {description}
            </p>
          )}
        </div>
      )}
      <div className="space-y-4">
        {children}
      </div>
    </div>
  )
}

// Field with specific icons for common use cases
export function EmailField(props: Omit<InputProps, 'type' | 'icon'>) {
  return <Input {...props} type="email" icon={<Mail />} />
}

export function PhoneField(props: Omit<InputProps, 'type' | 'icon'>) {
  return <Input {...props} type="tel" icon={<Phone />} />
}

export function DateField(props: Omit<InputProps, 'type' | 'icon'>) {
  return <Input {...props} type="date" icon={<Calendar />} />
}

export function TimeField(props: Omit<InputProps, 'type' | 'icon'>) {
  return <Input {...props} type="time" icon={<Clock />} />
}

export function LocationField(props: Omit<InputProps, 'icon'>) {
  return <Input {...props} icon={<MapPin />} />
}

export function BuildingField(props: Omit<InputProps, 'icon'>) {
  return <Input {...props} icon={<Building />} />
}

export function EnergyField(props: Omit<InputProps, 'icon'>) {
  return <Input {...props} type="number" icon={<Zap />} />
}

export function CurrencyField(props: Omit<InputProps, 'icon'>) {
  return <Input {...props} type="number" icon={<DollarSign />} />
}

export function UserField(props: Omit<InputProps, 'icon'>) {
  return <Input {...props} icon={<User />} />
}
