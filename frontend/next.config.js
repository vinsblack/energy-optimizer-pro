/** @type {import('next').NextConfig} */

const path = require('path')

// Bundle analyzer for performance optimization
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})

// PWA configuration
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  runtimeCaching: [
    {
      urlPattern: /^https?.*/,
      handler: 'NetworkFirst',
      options: {
        cacheName: 'offlineCache',
        expiration: {
          maxEntries: 200,
        },
      },
    },
  ],
  disable: process.env.NODE_ENV === 'development',
})

const nextConfig = {
  // ================================
  // 🚀 Performance Optimizations
  // ================================
  
  // Experimental features disabled for demo
  experimental: {
    serverComponentsExternalPackages: ['@prisma/client'],
  },

  // Compiler optimizations
  compiler: {
    // Remove console logs in production
    removeConsole: process.env.NODE_ENV === 'production' ? {
      exclude: ['error', 'warn'],
    } : false,
  },

  // SWC minification
  swcMinify: true,

  // Image optimization
  images: {
    domains: [
      'localhost',
      'energy-optimizer.com',
      'staging.energy-optimizer.com',
      'via.placeholder.com',
      'images.unsplash.com',
      'cdn.energy-optimizer.com',
    ],
    formats: ['image/webp', 'image/avif'],
    minimumCacheTTL: 60,
    dangerouslyAllowSVG: true,
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
  },

  // ================================
  // 📡 API & Networking
  // ================================
  
  // Custom headers for security
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()',
          },
        ],
      },
      {
        source: '/api/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'no-cache, no-store, must-revalidate',
          },
        ],
      },
    ]
  },

  // API rewrites for backend proxy
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/:path*`,
      },
      {
        source: '/ws',
        destination: `${apiUrl}/ws`,
      },
    ]
  },

  // Redirects for better UX
  async redirects() {
    return [
      {
        source: '/dashboard',
        destination: '/',
        permanent: false,
      },
      {
        source: '/docs',
        destination: '/api/docs',
        permanent: false,
      },
    ]
  },

  // ================================
  // 🗂️ File & Asset Handling
  // ================================
  
  // Static file serving
  trailingSlash: false,
  
  // Asset optimization
  generateEtags: true,
  compress: true,
  
  // Build output configuration
  output: 'standalone',
  distDir: '.next',
  
  // Environment variables
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
    BUILD_TIME: new Date().toISOString(),
    BUILD_VERSION: process.env.npm_package_version || '1.0.0',
  },

  // Public runtime config (available in browser)
  publicRuntimeConfig: {
    APP_NAME: process.env.NEXT_PUBLIC_APP_NAME || 'Energy Optimizer Pro',
    APP_VERSION: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',
    ENVIRONMENT: process.env.NEXT_PUBLIC_ENVIRONMENT || 'development',
  },

  // Server runtime config (server-side only)
  serverRuntimeConfig: {
    SECRET_API_KEY: process.env.SECRET_API_KEY,
  },

  // ================================
  // 📦 Module Resolution & Webpack
  // ================================
  
  // Custom webpack configuration
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Alias configuration
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname),
      '@/components': path.resolve(__dirname, 'components'),
      '@/lib': path.resolve(__dirname, 'lib'),
      '@/styles': path.resolve(__dirname, 'styles'),
      '@/types': path.resolve(__dirname, 'types'),
      '@/utils': path.resolve(__dirname, 'utils'),
      '@/hooks': path.resolve(__dirname, 'hooks'),
      '@/store': path.resolve(__dirname, 'store'),
    }

    // Optimize bundle size
    if (!dev && !isServer) {
      config.optimization = {
        ...config.optimization,
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            vendor: {
              test: /[\\/]node_modules[\\/]/,
              name: 'vendors',
              chunks: 'all',
            },
            recharts: {
              test: /[\\/]node_modules[\\/]recharts[\\/]/,
              name: 'recharts',
              chunks: 'all',
            },
            common: {
              name: 'common',
              minChunks: 2,
              chunks: 'all',
              enforce: true,
            },
          },
        },
      }
    }

    // Handle worker files
    config.module.rules.push({
      test: /\.worker\.js$/,
      use: { loader: 'worker-loader' },
    })

    // Handle SVG imports
    config.module.rules.push({
      test: /\.svg$/,
      use: ['@svgr/webpack'],
    })

    // Bundle analyzer
    if (process.env.ANALYZE === 'true') {
      const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin
      config.plugins.push(
        new BundleAnalyzerPlugin({
          analyzerMode: 'static',
          openAnalyzer: false,
          reportFilename: isServer ? '../analyze/server.html' : './analyze/client.html',
        })
      )
    }

    return config
  },

  // ================================
  // 🎯 Performance & Caching
  // ================================
  
  // Disable x-powered-by header
  poweredByHeader: false,
  
  // Generate standalone output for Docker
  output: process.env.NODE_ENV === 'production' ? 'standalone' : undefined,
  
  // Custom page extensions
  pageExtensions: ['ts', 'tsx', 'js', 'jsx', 'md', 'mdx'],
  
  // React strict mode
  reactStrictMode: true,
  
  // ESLint during builds
  eslint: {
    dirs: ['app', 'pages', 'components', 'lib', 'utils'],
    ignoreDuringBuilds: false,
  },

  // TypeScript configuration
  typescript: {
    ignoreBuildErrors: false,
    tsconfigPath: './tsconfig.json',
  },

  // ================================
  // 🌍 Internationalization (Future)
  // ================================
  
  // i18n: {
  //   locales: ['en', 'it', 'es', 'de', 'fr'],
  //   defaultLocale: 'en',
  //   localeDetection: true,
  // },

  // ================================
  // 🔧 Development Experience
  // ================================
  
  // Source maps in development
  productionBrowserSourceMaps: false,
  
  // Optimize fonts
  optimizeFonts: true,
  
  // Custom build directory
  generateBuildId: async () => {
    // Use git commit hash as build ID
    const { execSync } = require('child_process')
    try {
      return execSync('git rev-parse HEAD').toString().trim()
    } catch {
      return null
    }
  },

  // ================================
  // 📊 Analytics & Monitoring
  // ================================
  
  // Webpack dev middleware configuration moved to server config

  // ================================
  // 🛡️ Security Configuration
  // ================================
  // (Headers configured above in main headers function)
}

// Apply plugins based on environment
let configWithPlugins = nextConfig

// Apply PWA in production
if (process.env.NODE_ENV === 'production') {
  configWithPlugins = withPWA(configWithPlugins)
}

// Apply bundle analyzer if enabled
if (process.env.ANALYZE === 'true') {
  configWithPlugins = withBundleAnalyzer(configWithPlugins)
}

module.exports = configWithPlugins
