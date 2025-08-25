// 🏢⚡ Energy Optimizer Pro - Jest Setup Configuration
// ===================================================

import '@testing-library/jest-dom'
import 'jest-canvas-mock'

// ================================
// 🎭 Global Mocks
// ================================

// Mock Next.js router
jest.mock('next/router', () => ({
  useRouter() {
    return {
      route: '/',
      pathname: '/',
      query: {},
      asPath: '/',
      push: jest.fn(),
      pop: jest.fn(),
      reload: jest.fn(),
      back: jest.fn(),
      prefetch: jest.fn().mockResolvedValue(undefined),
      beforePopState: jest.fn(),
      events: {
        on: jest.fn(),
        off: jest.fn(),
        emit: jest.fn(),
      },
      isFallback: false,
      isLocaleDomain: true,
      isReady: true,
      defaultLocale: 'en',
      domainLocales: [],
      isPreview: false,
    }
  },
}))

// Mock Next.js navigation (App Router)
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      refresh: jest.fn(),
      back: jest.fn(),
      forward: jest.fn(),
      prefetch: jest.fn(),
    }
  },
  useSearchParams() {
    return new URLSearchParams()
  },
  usePathname() {
    return '/'
  },
}))

// Mock Next.js dynamic imports
jest.mock('next/dynamic', () => (fn) => {
  const DynamicComponent = (props) => {
    return fn().then((mod) => mod.default(props))
  }
  DynamicComponent.displayName = 'LoadableComponent'
  return DynamicComponent
})

// Mock Next.js Image component
jest.mock('next/image', () => ({
  __esModule: true,
  default: (props) => {
    // eslint-disable-next-line @next/next/no-img-element
    return <img {...props} alt={props.alt} />
  },
}))

// Mock Next.js Head component
jest.mock('next/head', () => {
  return function Head({ children }) {
    return <>{children}</>
  }
})

// ================================
// 🌐 Web APIs Mocks
// ================================

// Mock IntersectionObserver
global.IntersectionObserver = jest.fn().mockImplementation((callback) => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
  trigger: (entries) => callback(entries),
}))

// Mock ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation((callback) => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
  trigger: (entries) => callback(entries),
}))

// Mock WebSocket
global.WebSocket = jest.fn().mockImplementation(() => ({
  close: jest.fn(),
  send: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  readyState: 1,
  CONNECTING: 0,
  OPEN: 1,
  CLOSING: 2,
  CLOSED: 3,
}))

// Mock fetch API
global.fetch = jest.fn()

// Mock console methods for cleaner test output
const originalError = console.error
const originalWarn = console.warn

beforeAll(() => {
  console.error = (...args) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning: ReactDOM.render is no longer supported')
    ) {
      return
    }
    originalError.call(console, ...args)
  }

  console.warn = (...args) => {
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('componentWillReceiveProps') ||
        args[0].includes('componentWillMount'))
    ) {
      return
    }
    originalWarn.call(console, ...args)
  }
})

afterAll(() => {
  console.error = originalError
  console.warn = originalWarn
})

// ================================
// 📊 Chart Library Mocks
// ================================

// Mock Recharts
jest.mock('recharts', () => ({
  LineChart: ({ children }) => <div data-testid="line-chart">{children}</div>,
  BarChart: ({ children }) => <div data-testid="bar-chart">{children}</div>,
  AreaChart: ({ children }) => <div data-testid="area-chart">{children}</div>,
  PieChart: ({ children }) => <div data-testid="pie-chart">{children}</div>,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  Legend: () => <div data-testid="legend" />,
  Line: () => <div data-testid="line" />,
  Bar: () => <div data-testid="bar" />,
  Area: () => <div data-testid="area" />,
  Pie: () => <div data-testid="pie" />,
  Cell: () => <div data-testid="cell" />,
  ResponsiveContainer: ({ children }) => (
    <div data-testid="responsive-container">{children}</div>
  ),
}))

// ================================
// 🎨 UI Library Mocks
// ================================

// Mock Framer Motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }) => <div {...props}>{children}</div>,
    span: ({ children, ...props }) => <span {...props}>{children}</span>,
    button: ({ children, ...props }) => <button {...props}>{children}</button>,
    img: ({ children, ...props }) => <img {...props} alt="" />,
  },
  AnimatePresence: ({ children }) => <>{children}</>,
  useAnimation: () => ({
    start: jest.fn(),
    stop: jest.fn(),
    set: jest.fn(),
  }),
  useMotionValue: (value) => ({ get: () => value, set: jest.fn() }),
}))

// Mock React Query
jest.mock('@tanstack/react-query', () => ({
  useQuery: jest.fn(),
  useMutation: jest.fn(),
  useQueryClient: jest.fn(),
  QueryClient: jest.fn(),
  QueryClientProvider: ({ children }) => children,
  useInfiniteQuery: jest.fn(),
}))

// ================================
// 🔧 Custom Test Utilities
// ================================

// Custom render function with providers
import { render as rtlRender } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

// Create a custom render function that includes providers
export function renderWithProviders(ui, options = {}) {
  const {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    }),
    ...renderOptions
  } = options

  function Wrapper({ children }) {
    return (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    )
  }

  return rtlRender(ui, { wrapper: Wrapper, ...renderOptions })
}

// Re-export everything
export * from '@testing-library/react'
export { renderWithProviders as render }

// ================================
// 🧪 Custom Matchers
// ================================

// Custom matcher for testing energy data
expect.extend({
  toBeValidEnergyData(received) {
    const pass = (
      typeof received === 'object' &&
      received !== null &&
      typeof received.energy_consumption === 'number' &&
      received.energy_consumption >= 0 &&
      typeof received.timestamp === 'string' &&
      !isNaN(Date.parse(received.timestamp))
    )

    if (pass) {
      return {
        message: () => `expected ${JSON.stringify(received)} not to be valid energy data`,
        pass: true,
      }
    } else {
      return {
        message: () => `expected ${JSON.stringify(received)} to be valid energy data`,
        pass: false,
      }
    }
  },

  toBeValidBuilding(received) {
    const pass = (
      typeof received === 'object' &&
      received !== null &&
      typeof received.id === 'string' &&
      typeof received.name === 'string' &&
      typeof received.type === 'string' &&
      typeof received.size_sqft === 'number' &&
      received.size_sqft > 0
    )

    if (pass) {
      return {
        message: () => `expected ${JSON.stringify(received)} not to be valid building data`,
        pass: true,
      }
    } else {
      return {
        message: () => `expected ${JSON.stringify(received)} to be valid building data`,
        pass: false,
      }
    }
  },
})

// ================================
// 🌍 Environment Variables
// ================================

// Set test environment variables
process.env.NODE_ENV = 'test'
process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000'
process.env.NEXT_PUBLIC_WS_URL = 'ws://localhost:8000'
process.env.NEXT_PUBLIC_ENVIRONMENT = 'test'
process.env.NEXT_PUBLIC_ENABLE_ANALYTICS = 'false'
process.env.NEXT_PUBLIC_ENABLE_NOTIFICATIONS = 'true'
process.env.NEXT_PUBLIC_ENABLE_REALTIME = 'false'

// ================================
// 🔄 Test Lifecycle Hooks
// ================================

// Global setup for all tests
beforeAll(() => {
  // Setup any global test configuration
  global.testStartTime = Date.now()
})

// Global teardown
afterAll(() => {
  // Cleanup any global test resources
  const testDuration = Date.now() - global.testStartTime
  console.log(`\n🧪 Test suite completed in ${testDuration}ms`)
})

// Setup before each test
beforeEach(() => {
  // Clear all mocks before each test
  jest.clearAllMocks()
  
  // Reset fetch mock
  if (global.fetch) {
    global.fetch.mockClear()
  }
  
  // Reset localStorage
  if (global.localStorage) {
    global.localStorage.clear()
  }
  
  // Reset sessionStorage
  if (global.sessionStorage) {
    global.sessionStorage.clear()
  }
})

// Cleanup after each test
afterEach(() => {
  // Cleanup any test-specific resources
  jest.restoreAllMocks()
})

// ================================
// 🎭 Mock Data Factories
// ================================

// Factory for creating mock building data
global.createMockBuilding = (overrides = {}) => ({
  id: 'test-building-1',
  name: 'Test Building',
  address: '123 Test St, Test City',
  type: 'office',
  size_sqft: 50000,
  floors: 10,
  year_built: 2020,
  occupancy: 100,
  efficiency_score: 0.85,
  is_active: true,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  ...overrides,
})

// Factory for creating mock energy data
global.createMockEnergyData = (overrides = {}) => ({
  id: 'test-energy-1',
  building_id: 'test-building-1',
  timestamp: new Date().toISOString(),
  energy_consumption: 245.7,
  temperature: 22.5,
  humidity: 45.0,
  occupancy: 75.0,
  cost: 36.86,
  power_factor: 0.92,
  demand_kw: 180.5,
  created_at: new Date().toISOString(),
  ...overrides,
})

// Factory for creating mock user data
global.createMockUser = (overrides = {}) => ({
  id: 'test-user-1',
  email: 'test@energy-optimizer.com',
  username: 'testuser',
  full_name: 'Test User',
  role: 'analyst',
  is_active: true,
  created_at: '2024-01-01T00:00:00Z',
  last_login: new Date().toISOString(),
  ...overrides,
})

// Factory for creating mock optimization job
global.createMockOptimizationJob = (overrides = {}) => ({
  id: 'test-job-1',
  building_id: 'test-building-1',
  algorithm: 'xgboost',
  status: 'completed',
  energy_savings_percent: 25.5,
  cost_savings_annual: 15000,
  carbon_reduction_tons: 8.7,
  confidence_score: 0.94,
  recommendations: [
    'Optimize HVAC scheduling',
    'Implement smart lighting controls',
    'Upgrade to high-efficiency equipment',
  ],
  created_at: '2024-01-01T00:00:00Z',
  completed_at: '2024-01-01T00:05:00Z',
  ...overrides,
})

// ================================
// 🌐 API Mock Helpers
// ================================

// Helper to mock successful API responses
global.mockApiSuccess = (data) => {
  global.fetch.mockResolvedValueOnce({
    ok: true,
    status: 200,
    json: jest.fn().mockResolvedValueOnce({
      data,
      status: 'success',
      timestamp: new Date().toISOString(),
    }),
  })
}

// Helper to mock API errors
global.mockApiError = (message = 'API Error', status = 500) => {
  global.fetch.mockResolvedValueOnce({
    ok: false,
    status,
    json: jest.fn().mockResolvedValueOnce({
      detail: message,
      status: 'error',
      timestamp: new Date().toISOString(),
    }),
  })
}

// Helper to mock network errors
global.mockNetworkError = () => {
  global.fetch.mockRejectedValueOnce(new Error('Network Error'))
}

// ================================
// 🔄 Test State Management
// ================================

// Mock Zustand store
jest.mock('zustand', () => ({
  create: jest.fn((createState) => {
    let state
    const setState = jest.fn((partial) => {
      state = { ...state, ...partial }
    })
    const getState = jest.fn(() => state)
    const subscribe = jest.fn()
    const destroy = jest.fn()
    
    state = createState(setState, getState, {
      setState,
      getState,
      subscribe,
      destroy,
    })
    
    return {
      ...state,
      setState,
      getState,
      subscribe,
      destroy,
    }
  }),
}))

// ================================
// 🎨 Style and Animation Mocks
// ================================

// Mock CSS modules
jest.mock('*.module.css', () => ({}))
jest.mock('*.module.scss', () => ({}))

// Mock GSAP animations (if used)
jest.mock('gsap', () => ({
  to: jest.fn(),
  from: jest.fn(),
  set: jest.fn(),
  timeline: jest.fn(() => ({
    to: jest.fn(),
    from: jest.fn(),
    set: jest.fn(),
  })),
  registerPlugin: jest.fn(),
}))

// ================================
// 📱 Device and Media Mocks
// ================================

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // Deprecated
    removeListener: jest.fn(), // Deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
})

// Mock window.scroll methods
Object.defineProperty(window, 'scrollTo', {
  writable: true,
  value: jest.fn(),
})

Object.defineProperty(window, 'scrollBy', {
  writable: true,
  value: jest.fn(),
})

// Mock clipboard API
Object.defineProperty(navigator, 'clipboard', {
  writable: true,
  value: {
    writeText: jest.fn().mockResolvedValue(undefined),
    readText: jest.fn().mockResolvedValue(''),
  },
})

// ================================
// 🕒 Date and Time Mocks
// ================================

// Mock Date.now for consistent timestamps in tests
const MOCK_DATE = new Date('2024-08-24T12:00:00Z')
global.Date.now = jest.fn(() => MOCK_DATE.getTime())

// ================================
// 🔐 Authentication Mocks
// ================================

// Mock authentication context
global.mockAuthenticatedUser = (user = null) => {
  const mockUser = user || global.createMockUser()
  
  jest.doMock('../context/AuthContext', () => ({
    useAuth: () => ({
      user: mockUser,
      isAuthenticated: !!mockUser,
      login: jest.fn(),
      logout: jest.fn(),
      loading: false,
    }),
    AuthProvider: ({ children }) => children,
  }))
  
  return mockUser
}

// Mock unauthenticated state
global.mockUnauthenticatedUser = () => {
  jest.doMock('../context/AuthContext', () => ({
    useAuth: () => ({
      user: null,
      isAuthenticated: false,
      login: jest.fn(),
      logout: jest.fn(),
      loading: false,
    }),
    AuthProvider: ({ children }) => children,
  }))
}

// ================================
// 📊 Performance Testing Helpers
// ================================

// Helper to measure component render time
global.measureRenderTime = async (renderFn) => {
  const start = performance.now()
  const result = await renderFn()
  const end = performance.now()
  
  return {
    result,
    renderTime: end - start,
  }
}

// Helper to test memory usage
global.measureMemoryUsage = () => {
  if (performance.memory) {
    return {
      used: performance.memory.usedJSHeapSize,
      total: performance.memory.totalJSHeapSize,
      limit: performance.memory.jsHeapSizeLimit,
    }
  }
  return null
}

// ================================
// 🔄 Async Testing Helpers
// ================================

// Helper to wait for async operations
global.waitForAsync = (timeout = 1000) => {
  return new Promise(resolve => setTimeout(resolve, timeout))
}

// Helper for testing async hooks
global.waitForNextUpdate = async () => {
  await new Promise(resolve => setTimeout(resolve, 0))
}

// ================================
// 🌐 Internationalization Mocks
// ================================

// Mock next-i18next (if used in future)
jest.mock('next-i18next', () => ({
  useTranslation: () => ({
    t: (key) => key,
    i18n: {
      language: 'en',
      changeLanguage: jest.fn(),
    },
  }),
  Trans: ({ children }) => children,
}))

// ================================
// 📱 PWA Mocks
// ================================

// Mock service worker registration
Object.defineProperty(navigator, 'serviceWorker', {
  writable: true,
  value: {
    register: jest.fn().mockResolvedValue({}),
    ready: Promise.resolve({}),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
  },
})

// ================================
// 🎯 Test Configuration Overrides
// ================================

// Increase timeout for integration tests
jest.setTimeout(30000)

// Custom global test configuration
global.testConfig = {
  defaultTimeout: 5000,
  slowTestThreshold: 1000,
  enablePerformanceTracking: process.env.TRACK_PERFORMANCE === 'true',
  enableMemoryTracking: process.env.TRACK_MEMORY === 'true',
}

// ================================
// 🐛 Error Handling
// ================================

// Custom error handler for unhandled rejections in tests
process.on('unhandledRejection', (error) => {
  console.error('Unhandled promise rejection in test:', error)
  // Don't fail tests on unhandled rejections unless explicitly configured
  if (process.env.FAIL_ON_UNHANDLED_REJECTION === 'true') {
    process.exit(1)
  }
})

// ================================
// 📊 Test Reporting Helpers
// ================================

// Helper to create test reports
global.createTestReport = (testName, results) => {
  const report = {
    testName,
    timestamp: new Date().toISOString(),
    results,
    performance: global.testConfig.enablePerformanceTracking ? {
      renderTime: 0, // Would be populated by actual measurements
    } : null,
    memory: global.testConfig.enableMemoryTracking ? global.measureMemoryUsage() : null,
  }
  
  return report
}

// ================================
// 🚀 Final Setup
// ================================

// Log test setup completion
console.log('🧪 Jest setup completed for Energy Optimizer Pro')
console.log(`📊 Test environment: ${process.env.NODE_ENV}`)
console.log(`⚙️  Performance tracking: ${global.testConfig.enablePerformanceTracking}`)
console.log(`💾 Memory tracking: ${global.testConfig.enableMemoryTracking}`)
