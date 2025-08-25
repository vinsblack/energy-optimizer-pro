// 🏢⚡ Energy Optimizer Pro - Global Type Definitions
// ==================================================

// Window object extensions
declare global {
  interface Window {
    // Google Analytics
    gtag?: (...args: any[]) => void
    dataLayer?: any[]
    
    // Energy Optimizer specific
    EnergyOptimizer?: {
      version: string
      buildTime: string
      environment: string
    }
    
    // WebSocket connection
    wsConnection?: WebSocket
    
    // PWA related
    workbox?: any
    
    // Performance monitoring
    performance?: Performance & {
      measureUserAgentSpecificMemory?: () => Promise<any>
    }
  }

  // Environment variables
  namespace NodeJS {
    interface ProcessEnv {
      // Next.js public variables
      NEXT_PUBLIC_API_URL: string
      NEXT_PUBLIC_WS_URL: string
      NEXT_PUBLIC_APP_NAME: string
      NEXT_PUBLIC_APP_VERSION: string
      NEXT_PUBLIC_ENVIRONMENT: 'development' | 'staging' | 'production'
      
      // Feature flags
      NEXT_PUBLIC_ENABLE_ANALYTICS: string
      NEXT_PUBLIC_ENABLE_NOTIFICATIONS: string
      NEXT_PUBLIC_ENABLE_REALTIME: string
      NEXT_PUBLIC_ENABLE_ML_FEATURES: string
      
      // External services
      NEXT_PUBLIC_GA_ID?: string
      NEXT_PUBLIC_MIXPANEL_TOKEN?: string
      NEXT_PUBLIC_HOTJAR_ID?: string
      NEXT_PUBLIC_GOOGLE_MAPS_API_KEY?: string
      NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN?: string
      
      // Performance settings
      NEXT_PUBLIC_MAX_FILE_SIZE: string
      NEXT_PUBLIC_CHUNK_SIZE: string
      NEXT_PUBLIC_CACHE_TTL: string
      
      // Development settings
      NEXT_PUBLIC_DEBUG: string
      NEXT_PUBLIC_SHOW_DEV_TOOLS: string
      NEXT_PUBLIC_MOCK_API: string
      
      // Server-only variables
      SECRET_API_KEY?: string
      DATABASE_URL?: string
      REDIS_URL?: string
    }
  }
}

// ================================
// 🏢 Energy Optimizer Types
// ================================

// Building-related types
export interface Building {
  id: string
  name: string
  address: string
  type: BuildingType
  size_sqft: number
  floors: number
  year_built: number
  occupancy: number
  efficiency_score: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export type BuildingType = 'office' | 'retail' | 'warehouse' | 'hospital' | 'school' | 'hotel'

// Energy data types
export interface EnergyData {
  id: string
  building_id: string
  timestamp: string
  energy_consumption: number
  temperature: number
  humidity: number
  occupancy: number
  cost: number
  power_factor: number
  demand_kw: number
  created_at: string
}

// ML optimization types
export interface OptimizationJob {
  id: string
  building_id: string
  algorithm: MLAlgorithm
  status: JobStatus
  energy_savings_percent?: number
  cost_savings_annual?: number
  carbon_reduction_tons?: number
  confidence_score?: number
  recommendations?: string[]
  created_at: string
  completed_at?: string
  error_message?: string
}

export type MLAlgorithm = 'xgboost' | 'lightgbm' | 'random_forest'
export type JobStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'

// Dashboard types
export interface DashboardMetrics {
  total_buildings: number
  total_energy_consumption: number
  total_cost_savings: number
  average_efficiency: number
  carbon_footprint_reduction: number
  active_optimizations: number
}

// Chart data types
export interface ChartDataPoint {
  timestamp: string
  value: number
  label?: string
}

export interface ChartConfig {
  type: 'line' | 'bar' | 'area' | 'pie'
  data: ChartDataPoint[]
  xAxis?: string
  yAxis?: string
  color?: string
  height?: number
}

// User and authentication types
export interface User {
  id: string
  email: string
  username: string
  full_name: string
  role: UserRole
  is_active: boolean
  created_at: string
  last_login?: string
}

export type UserRole = 'admin' | 'manager' | 'analyst' | 'operator' | 'viewer'

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

// API response types
export interface ApiResponse<T = any> {
  data: T
  message?: string
  status: 'success' | 'error'
  timestamp: string
}

export interface PaginatedResponse<T = any> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// WebSocket message types
export interface WebSocketMessage {
  type: 'energy_update' | 'optimization_progress' | 'alert' | 'system_status'
  data: any
  timestamp: string
  building_id?: string
  user_id?: string
}

// Notification types
export interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  duration?: number
  actions?: NotificationAction[]
  timestamp: string
}

export interface NotificationAction {
  label: string
  action: () => void
  style?: 'primary' | 'secondary' | 'danger'
}

// Form and input types
export interface FormField {
  name: string
  label: string
  type: 'text' | 'number' | 'email' | 'password' | 'select' | 'textarea' | 'checkbox' | 'date'
  placeholder?: string
  required?: boolean
  validation?: ValidationRule[]
  options?: SelectOption[]
}

export interface ValidationRule {
  type: 'required' | 'email' | 'min' | 'max' | 'pattern'
  value?: any
  message: string
}

export interface SelectOption {
  value: string | number
  label: string
  disabled?: boolean
}

// ================================
// 🎨 UI Component Types
// ================================

export interface ComponentProps {
  className?: string
  children?: React.ReactNode
  style?: React.CSSProperties
}

export interface ButtonProps extends ComponentProps {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  onClick?: () => void
  type?: 'button' | 'submit' | 'reset'
}

export interface CardProps extends ComponentProps {
  title?: string
  subtitle?: string
  actions?: React.ReactNode
  hover?: boolean
}

export interface ModalProps extends ComponentProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  closeOnOverlayClick?: boolean
}

// ================================
// 📊 Data Visualization Types
// ================================

export interface ChartTheme {
  primary: string
  secondary: string
  success: string
  warning: string
  error: string
  info: string
  background: string
  text: string
  border: string
}

export interface ChartTooltipProps {
  active?: boolean
  payload?: any[]
  label?: string
  coordinate?: { x: number; y: number }
}

// ================================
// 🔄 State Management Types
// ================================

export interface AppState {
  user: User | null
  buildings: Building[]
  selectedBuilding: Building | null
  dashboardMetrics: DashboardMetrics | null
  notifications: Notification[]
  isLoading: boolean
  error: string | null
}

export interface EnergyState {
  currentData: EnergyData[]
  historicalData: EnergyData[]
  realTimeEnabled: boolean
  updateInterval: number
  isLoading: boolean
}

export interface OptimizationState {
  activeJobs: OptimizationJob[]
  results: OptimizationJob[]
  isRunning: boolean
  progress: number
  selectedAlgorithm: MLAlgorithm
}

// ================================
// 🔌 API Hook Types
// ================================

export interface UseApiOptions {
  enabled?: boolean
  refetchInterval?: number
  onSuccess?: (data: any) => void
  onError?: (error: Error) => void
  retry?: number | boolean
}

export interface MutationOptions<T = any> {
  onSuccess?: (data: T) => void
  onError?: (error: Error) => void
  onSettled?: () => void
}

// ================================
// 📱 Responsive Design Types
// ================================

export type Breakpoint = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl'

export interface ResponsiveValue<T> {
  xs?: T
  sm?: T
  md?: T
  lg?: T
  xl?: T
  '2xl'?: T
}

// ================================
// 🌐 Internationalization Types
// ================================

export interface LocaleConfig {
  code: string
  name: string
  flag: string
  rtl?: boolean
}

export interface TranslationKeys {
  common: {
    loading: string
    save: string
    cancel: string
    delete: string
    edit: string
    view: string
    search: string
    filter: string
    export: string
    import: string
  }
  dashboard: {
    title: string
    overview: string
    analytics: string
    buildings: string
  }
  buildings: {
    title: string
    add_building: string
    edit_building: string
    building_details: string
  }
  optimization: {
    title: string
    run_optimization: string
    view_results: string
    algorithms: string
  }
}

// ================================
// 🔐 Authentication Types
// ================================

export interface LoginCredentials {
  email: string
  password: string
  remember_me?: boolean
}

export interface RegisterData {
  email: string
  username: string
  full_name: string
  password: string
  confirm_password: string
}

export interface PasswordResetData {
  email: string
}

export interface PasswordChangeData {
  current_password: string
  new_password: string
  confirm_password: string
}

// ================================
// 🔔 Real-time Types
// ================================

export interface RealtimeConfig {
  enabled: boolean
  updateInterval: number
  maxReconnectAttempts: number
  reconnectInterval: number
}

export interface WebSocketConfig {
  url: string
  protocols?: string[]
  options?: {
    heartbeatInterval?: number
    maxReconnectAttempts?: number
    reconnectInterval?: number
  }
}

// ================================
// 📈 Analytics Types
// ================================

export interface AnalyticsEvent {
  name: string
  properties?: Record<string, any>
  timestamp?: string
  user_id?: string
  session_id?: string
}

export interface PerformanceMetrics {
  page_load_time: number
  time_to_interactive: number
  largest_contentful_paint: number
  cumulative_layout_shift: number
  first_input_delay: number
}

// ================================
// 🛠️ Utility Types
// ================================

export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}

export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>

export type OptionalFields<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>

export type ArrayElement<T> = T extends readonly (infer U)[] ? U : never

export type ValueOf<T> = T[keyof T]

export type Prettify<T> = {
  [K in keyof T]: T[K]
} & {}

// Re-export for convenience
export type FC<P = {}> = React.FunctionComponent<P>
export type ComponentType<P = {}> = React.ComponentType<P>

// Module declarations for CSS modules
declare module '*.module.css' {
  const classes: { [key: string]: string }
  export default classes
}

declare module '*.module.scss' {
  const classes: { [key: string]: string }
  export default classes
}

// SVG imports
declare module '*.svg' {
  import React from 'react'
  const SVG: React.VFC<React.SVGProps<SVGSVGElement>>
  export default SVG
}

// Image imports
declare module '*.png'
declare module '*.jpg'
declare module '*.jpeg'
declare module '*.gif'
declare module '*.webp'
declare module '*.avif'
declare module '*.ico'
declare module '*.bmp'

// Web Workers
declare module '*.worker.js' {
  class WebpackWorker extends Worker {
    constructor()
  }
  export default WebpackWorker
}

// JSON imports
declare module '*.json' {
  const value: any
  export default value
}

export {}
