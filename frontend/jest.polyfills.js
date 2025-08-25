// 🏢⚡ Energy Optimizer Pro - Jest Polyfills
// ==========================================

// TextEncoder/TextDecoder polyfill for Node.js environment
const { TextEncoder, TextDecoder } = require('util')

global.TextEncoder = TextEncoder
global.TextDecoder = TextDecoder

// Fetch polyfill
require('whatwg-fetch')

// URL polyfill
const { URL, URLSearchParams } = require('url')
global.URL = URL
global.URLSearchParams = URLSearchParams

// AbortController polyfill
const { AbortController } = require('abortcontroller-polyfill/dist/cjs-ponyfill')
global.AbortController = AbortController

// Performance API polyfill
if (typeof global.performance === 'undefined') {
  global.performance = {
    now: () => Date.now(),
    mark: () => {},
    measure: () => {},
    getEntriesByName: () => [],
    getEntriesByType: () => [],
  }
}

// RequestAnimationFrame polyfill
global.requestAnimationFrame = (callback) => {
  return setTimeout(callback, 16)
}

global.cancelAnimationFrame = (id) => {
  clearTimeout(id)
}

// Canvas API mock for chart testing
global.HTMLCanvasElement.prototype.getContext = jest.fn()

// Mock for crypto.randomUUID (used in some components)
if (typeof global.crypto === 'undefined') {
  global.crypto = {
    randomUUID: () => '12345678-1234-1234-1234-123456789012',
    getRandomValues: (array) => {
      for (let i = 0; i < array.length; i++) {
        array[i] = Math.floor(Math.random() * 256)
      }
      return array
    },
  }
}

// Mock window.location
Object.defineProperty(window, 'location', {
  value: {
    href: 'http://localhost:3000',
    origin: 'http://localhost:3000',
    protocol: 'http:',
    host: 'localhost:3000',
    hostname: 'localhost',
    port: '3000',
    pathname: '/',
    search: '',
    hash: '',
    assign: jest.fn(),
    replace: jest.fn(),
    reload: jest.fn(),
  },
  writable: true,
})

// Mock document.cookie
Object.defineProperty(document, 'cookie', {
  writable: true,
  value: '',
})

// Suppress specific console warnings in tests
const originalConsoleWarn = console.warn
console.warn = (...args) => {
  const message = args[0]
  
  // Suppress React 18 warnings that don't affect functionality
  if (
    typeof message === 'string' && (
      message.includes('Warning: ReactDOM.render is no longer supported') ||
      message.includes('Warning: componentWillReceiveProps') ||
      message.includes('Warning: componentWillMount') ||
      message.includes('validateDOMNesting')
    )
  ) {
    return
  }
  
  originalConsoleWarn.apply(console, args)
}
