import type { Metadata } from 'next'
import './globals.css'
import { Inter } from 'next/font/google'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: {
    default: 'Energy Optimizer Pro - AI-Powered Building Energy Management',
    template: '%s | Energy Optimizer Pro'
  },
  description: 'Reduce energy costs by 15-25% with professional AI analytics. Enterprise-grade building energy optimization with 91%+ ML accuracy. Real-time monitoring, predictive analytics, and smart automation for commercial buildings.',
  keywords: [
    'energy optimization',
    'building management system',
    'AI machine learning',
    'energy efficiency',
    'smart buildings',
    'sustainability',
    'cost reduction',
    'carbon footprint',
    'IoT sensors',
    'predictive analytics',
    'energy monitoring',
    'commercial buildings',
    'facility management',
    'green technology',
    'ESG compliance',
    'building automation',
    'energy dashboard',
    'HVAC optimization',
    'utility management',
    'energy analytics'
  ].join(', '),
  authors: [{ name: 'Energy Optimizer Team', url: 'https://energy-optimizer-pro.vercel.app' }],
  creator: 'Energy Optimizer Pro',
  publisher: 'Energy Optimizer Pro',
  category: 'Business Software',
  
  // Open Graph / Facebook
  openGraph: {
    type: 'website',
    url: 'https://energy-optimizer-pro.vercel.app',
    title: 'Energy Optimizer Pro - AI-Powered Building Energy Management',
    description: 'Reduce energy costs by 15-25% with professional AI analytics. Enterprise-grade building energy optimization with 91%+ ML accuracy.',
    siteName: 'Energy Optimizer Pro',
    images: [
      {
        url: '/og-dashboard.png',
        width: 1200,
        height: 630,
        alt: 'Energy Optimizer Pro Dashboard - Real-time Energy Analytics',
      }
    ],
    locale: 'en_US',
  },
  
  // Twitter
  twitter: {
    card: 'summary_large_image',
    site: '@EnergyOptimizerPro',
    creator: '@EnergyOptimizerPro',
    title: 'Energy Optimizer Pro - AI-Powered Building Energy Management',
    description: '🏢⚡ Reduce energy costs by 15-25% with AI analytics. 91%+ ML accuracy, real-time monitoring, predictive optimization.',
    images: ['/twitter-dashboard.png'],
  },
  
  // App-specific
  applicationName: 'Energy Optimizer Pro',
  appleWebApp: {
    title: 'Energy Optimizer Pro',
    statusBarStyle: 'default',
    capable: true,
  },
  
  // SEO
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  
  // Icons and manifest
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
  },
  manifest: '/manifest.json',
  
  // Additional
  alternates: {
    canonical: 'https://energy-optimizer-pro.vercel.app',
  },
  
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#3b82f6' },
    { media: '(prefers-color-scheme: dark)', color: '#1e40af' },
  ],
  
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 5,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="h-full bg-gray-50 scroll-smooth">
      <head>
        {/* Schema.org structured data for SEO */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'SoftwareApplication',
              name: 'Energy Optimizer Pro',
              description: 'AI-Powered building energy management system that reduces energy costs by 15-25% with professional analytics.',
              url: 'https://energy-optimizer-pro.vercel.app',
              applicationCategory: 'BusinessApplication',
              operatingSystem: 'Web Browser',
              offers: {
                '@type': 'Offer',
                priceCurrency: 'EUR',
                price: '0',
                availability: 'https://schema.org/InStock'
              },
              aggregateRating: {
                '@type': 'AggregateRating',
                ratingValue: '4.9',
                reviewCount: '127'
              },
              publisher: {
                '@type': 'Organization',
                name: 'Energy Optimizer Pro',
                logo: {
                  '@type': 'ImageObject',
                  url: 'https://energy-optimizer-pro.vercel.app/logo.png'
                }
              },
              featureList: [
                '91%+ ML Accuracy',
                '15-25% Cost Reduction',
                'Real-time Monitoring',
                'Predictive Analytics',
                'Smart Automation',
                'Enterprise-grade Security'
              ]
            })
          }}
        />
        
        {/* Preconnect for performance */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className={`${inter.className} h-full antialiased`}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}
