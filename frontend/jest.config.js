// 🏢⚡ Energy Optimizer Pro - Jest Testing Configuration
// =====================================================

const nextJest = require('next/jest')

const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files
  dir: './',
})

// Custom Jest configuration
const customJestConfig = {
  // ================================
  // 🎯 Basic Configuration
  // ================================
  displayName: 'Energy Optimizer Pro Frontend',
  testEnvironment: 'jsdom',
  clearMocks: true,
  collectCoverage: true,
  coverageDirectory: 'coverage',
  verbose: true,

  // ================================
  // 📁 File Patterns
  // ================================
  testMatch: [
    '<rootDir>/**/__tests__/**/*.(ts|tsx|js)',
    '<rootDir>/**/?(*.)(test|spec).(ts|tsx|js)',
  ],
  testPathIgnorePatterns: [
    '<rootDir>/.next/',
    '<rootDir>/node_modules/',
    '<rootDir>/e2e/',
    '<rootDir>/coverage/',
    '<rootDir>/out/',
  ],

  // ================================
  // 📊 Coverage Configuration
  // ================================
  collectCoverageFrom: [
    'components/**/*.{ts,tsx}',
    'lib/**/*.{ts,tsx}',
    'utils/**/*.{ts,tsx}',
    'hooks/**/*.{ts,tsx}',
    'store/**/*.{ts,tsx}',
    'app/**/*.{ts,tsx}',
    'pages/**/*.{ts,tsx}',
    '!**/*.d.ts',
    '!**/*.stories.{ts,tsx}',
    '!**/node_modules/**',
    '!**/.next/**',
    '!**/coverage/**',
  ],
  coverageReporters: [
    'text',
    'html',
    'lcov',
    'json-summary',
    'cobertura',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
    './components/': {
      branches: 85,
      functions: 85,
      lines: 85,
      statements: 85,
    },
    './lib/': {
      branches: 90,
      functions: 90,
      lines: 90,
      statements: 90,
    },
  },

  // ================================
  // 🔧 Module Resolution
  // ================================
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/$1',
    '^@/components/(.*)$': '<rootDir>/components/$1',
    '^@/lib/(.*)$': '<rootDir>/lib/$1',
    '^@/utils/(.*)$': '<rootDir>/utils/$1',
    '^@/hooks/(.*)$': '<rootDir>/hooks/$1',
    '^@/store/(.*)$': '<rootDir>/store/$1',
    '^@/types/(.*)$': '<rootDir>/types/$1',
    '^@/styles/(.*)$': '<rootDir>/styles/$1',
    '^@/constants/(.*)$': '<rootDir>/constants/$1',
    '^@/config/(.*)$': '<rootDir>/config/$1',
    
    // Handle CSS modules
    '\\.module\\.(css|sass|scss)$': 'identity-obj-proxy',
    
    // Handle static assets
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '\\.(jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$': '<rootDir>/__mocks__/fileMock.js',
  },

  // ================================
  // 🛠️ Transform Configuration
  // ================================
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': ['babel-jest', { presets: ['next/babel'] }],
  },
  transformIgnorePatterns: [
    '/node_modules/',
    '^.+\\.module\\.(css|sass|scss)$',
  ],

  // ================================
  // ⚙️ Setup and Environment
  // ================================
  setupFilesAfterEnv: [
    '<rootDir>/jest.setup.js'
  ],
  testEnvironmentOptions: {
    url: 'http://localhost:3000',
  },

  // ================================
  // 🌐 Global Configuration
  // ================================
  globals: {
    'ts-jest': {
      tsconfig: {
        jsx: 'react-jsx',
      },
    },
  },

  // ================================
  // 📊 Reporters
  // ================================
  reporters: [
    'default',
    [
      'jest-html-reporters',
      {
        publicPath: './coverage/html-report',
        filename: 'jest-report.html',
        openReport: false,
        expand: true,
      },
    ],
    [
      'jest-junit',
      {
        outputDirectory: './coverage',
        outputName: 'junit.xml',
        usePathForSuiteName: true,
      },
    ],
  ],

  // ================================
  // ⏱️ Performance Configuration
  // ================================
  maxWorkers: '50%',
  watchPathIgnorePatterns: [
    '<rootDir>/.next/',
    '<rootDir>/node_modules/',
    '<rootDir>/coverage/',
  ],

  // ================================
  // 🎭 Mock Configuration
  // ================================
  moduleFileExtensions: [
    'ts',
    'tsx',
    'js',
    'jsx',
    'json',
    'node',
  ],

  // ================================
  // 🧪 Custom Test Environment
  // ================================
  testEnvironmentOptions: {
    customExportConditions: [''],
  },

  // ================================
  // 🔄 Watch Configuration
  // ================================
  watchPlugins: [
    'jest-watch-typeahead/filename',
    'jest-watch-typeahead/testname',
  ],

  // ================================
  // ⚡ Performance Optimizations
  // ================================
  cache: true,
  cacheDirectory: '<rootDir>/.jest-cache',
  
  // Bail on first test failure in CI
  bail: process.env.CI ? 1 : 0,
  
  // Force exit to avoid hanging tests
  forceExit: process.env.CI ? true : false,
  
  // Detect open handles in CI
  detectOpenHandles: process.env.CI ? true : false,

  // ================================
  // 🎯 Project-Specific Setup
  // ================================
  
  // Setup files that run before each test file
  setupFiles: [
    '<rootDir>/jest.polyfills.js'
  ],

  // ================================
  // 📝 Custom Matchers
  // ================================
  // Add custom Jest matchers
  // setupFilesAfterEnv includes our custom matchers

  // ================================
  // 🎨 Snapshot Configuration
  // ================================
  snapshotSerializers: [
    'enzyme-to-json/serializer'
  ],

  // ================================
  // 🔍 Error Handling
  // ================================
  errorOnDeprecated: true,
  notify: false,
  notifyMode: 'failure-change',

  // ================================
  // 📊 Test Results Processing
  // ================================
  passWithNoTests: true,
  restoreMocks: true,
  resetMocks: false,
  resetModules: false,

  // ================================
  // 🌍 Global Test Variables
  // ================================
  globals: {
    __DEV__: true,
    __TEST__: true,
    __VERSION__: process.env.npm_package_version || '1.0.0',
  },
}

// ================================
// 🎯 Environment-Specific Configs
// ================================

// CI-specific configuration
if (process.env.CI) {
  customJestConfig.reporters = [
    'default',
    ['jest-junit', {
      outputDirectory: './coverage',
      outputName: 'junit.xml',
    }],
  ]
  customJestConfig.coverageReporters = ['text', 'lcov', 'cobertura']
  customJestConfig.maxWorkers = 2
  customJestConfig.bail = 1
}

// Debug mode configuration
if (process.env.DEBUG_TESTS) {
  customJestConfig.verbose = true
  customJestConfig.detectOpenHandles = true
  customJestConfig.forceExit = false
}

// Coverage mode
if (process.env.COVERAGE) {
  customJestConfig.collectCoverage = true
  customJestConfig.coverageReporters = ['text', 'html', 'lcov']
}

// Create and export the Jest configuration
module.exports = createJestConfig(customJestConfig)
