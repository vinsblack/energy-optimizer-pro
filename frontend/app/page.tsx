'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import DashboardLayout from '@/components/layout/DashboardLayout'
import MetricCard from '@/components/ui/MetricCard'
import EnergyChart from '@/components/charts/EnergyChart'
import QuickActions from '@/components/ui/QuickActions'
import StatusIndicator from '@/components/ui/StatusIndicator'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { useQuery } from 'react-query'
import { apiService } from '@/lib/api'
import { 
  Zap, 
  TrendingDown, 
  Building, 
  Cpu, 
  BarChart3,
  ArrowRight,
  Play,
  Settings,
  Database,
  Brain
} from 'lucide-react'

export default function HomePage() {
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d')
  
  // Fetch system health
  const { data: healthData, isLoading: isHealthLoading } = useQuery(
    'system-health',
    () => apiService.getHealth(),
    {
      refetchInterval: 30000, // Refresh every 30 seconds
    }
  )

  // Fetch demo data for charts
  const { data: demoData, isLoading: isDemoLoading } = useQuery(
    'demo-data',
    () => apiService.generateSampleData('2024-08-17', '2024-08-24', 'commercial', 2500),
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
    }
  )

  const systemStatus = healthData?.status === 'healthy' ? 'online' : 'offline'
  const systemAccuracy = healthData?.performance_metrics?.test_accuracy ? 
    (healthData.performance_metrics.test_accuracy * 100).toFixed(1) + '%' : 'N/A'

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Hero Section */}
        <motion.div 
          className="gradient-modern rounded-3xl p-8 text-white relative overflow-hidden"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="relative z-10">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="heading-1 mb-4">
                  Energy Optimizer Pro
                </h1>
                <p className="text-xl text-white/90 mb-6 max-w-2xl">
                  AI-Powered building energy optimization with 91%+ ML accuracy. 
                  Reduce energy costs by 15-25% with professional analytics.
                </p>
                
                <div className="flex items-center space-x-4">
                  <StatusIndicator 
                    status={systemStatus}
                    label="System Status"
                  />
                  <span className="text-white/80">•</span>
                  <span className="text-white/90 font-medium">
                    {systemAccuracy} Accuracy
                  </span>
                  <span className="text-white/80">•</span>
                  <span className="text-white/90 font-medium">
                    v2.0 Professional
                  </span>
                </div>
              </div>
              
              <div className="hidden lg:block">
                <div className="relative">
                  <div className="w-32 h-32 rounded-full bg-white/10 backdrop-blur-sm flex items-center justify-center">
                    <Zap className="w-16 h-16 text-white" />
                  </div>
                  <div className="absolute -top-2 -right-2 w-8 h-8 bg-green-400 rounded-full flex items-center justify-center">
                    <span className="text-xs font-bold text-white">AI</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Background Pattern */}
          <div className="absolute inset-0 opacity-10">
            <div className="absolute top-10 left-10 w-20 h-20 border border-white rounded-full"></div>
            <div className="absolute top-32 right-20 w-16 h-16 border border-white rounded-full"></div>
            <div className="absolute bottom-20 left-32 w-12 h-12 border border-white rounded-full"></div>
          </div>
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <QuickActions />
        </motion.div>

        {/* Key Metrics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <h2 className="heading-3 mb-6">System Overview</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              icon={<Brain className="w-8 h-8 text-blue-600" />}
              title="ML Accuracy"
              value={isHealthLoading ? 'Loading...' : systemAccuracy}
              change={systemAccuracy !== 'N/A' ? '+2.3%' : undefined}
              trend="positive"
              subtitle="Model Performance"
            />
            
            <MetricCard
              icon={<TrendingDown className="w-8 h-8 text-green-600" />}
              title="Avg. Savings"
              value="22.5%"
              change="+1.2%"
              trend="positive"
              subtitle="Energy Cost Reduction"
            />
            
            <MetricCard
              icon={<Building className="w-8 h-8 text-purple-600" />}
              title="Buildings"
              value="1,247"
              change="+45"
              trend="positive"
              subtitle="Analyzed This Month"
            />
            
            <MetricCard
              icon={<Cpu className="w-8 h-8 text-orange-600" />}
              title="Processing"
              value={healthData?.performance_metrics?.test_processing_time_ms ? 
                `${Math.round(healthData.performance_metrics.test_processing_time_ms)}ms` : '350ms'}
              change="-15ms"
              trend="positive"
              subtitle="Analysis Speed"
            />
          </div>
        </motion.div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Energy Analytics Chart */}
          <motion.div 
            className="lg:col-span-2"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <div className="card">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-gray-900">
                  Energy Consumption Analytics
                </h3>
                
                <div className="flex items-center space-x-2">
                  {['24h', '7d', '30d', '90d'].map((period) => (
                    <button
                      key={period}
                      onClick={() => setSelectedTimeRange(period)}
                      className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                        selectedTimeRange === period
                          ? 'bg-blue-100 text-blue-700'
                          : 'text-gray-600 hover:text-gray-900'
                      }`}
                    >
                      {period}
                    </button>
                  ))}
                </div>
              </div>
              
              {isDemoLoading ? (
                <div className="flex items-center justify-center h-64">
                  <LoadingSpinner size="lg" />
                </div>
              ) : (
                <EnergyChart data={demoData?.data} />
              )}
            </div>
          </motion.div>

          {/* System Status & Recent Activity */}
          <motion.div 
            className="space-y-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            {/* System Status */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                System Health
              </h3>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">API Status</span>
                  <StatusIndicator status={systemStatus} />
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">ML Models</span>
                  <StatusIndicator status="online" />
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Data Pipeline</span>
                  <StatusIndicator status="online" />
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Analytics</span>
                  <StatusIndicator status="online" />
                </div>
              </div>
              
              {healthData?.performance_metrics && (
                <div className="mt-4 pt-4 border-t border-gray-100">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">
                    Performance Metrics
                  </h4>
                  <div className="text-xs text-gray-600 space-y-1">
                    <div>Data Points: {healthData.performance_metrics.test_data_points?.toLocaleString()}</div>
                    <div>Features: {healthData.performance_metrics.features_generated}</div>
                    <div>Response Time: {Math.round(healthData.performance_metrics.test_processing_time_ms)}ms</div>
                  </div>
                </div>
              )}
            </div>

            {/* Quick Analysis */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Quick Analysis
              </h3>
              
              <div className="space-y-3">
                <Link href="/analyze" className="block">
                  <div className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                        <BarChart3 className="w-4 h-4 text-blue-600" />
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          New Analysis
                        </div>
                        <div className="text-xs text-gray-500">
                          Upload or generate data
                        </div>
                      </div>
                    </div>
                    <ArrowRight className="w-4 h-4 text-gray-400" />
                  </div>
                </Link>
                
                <Link href="/optimize" className="block">
                  <div className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                        <Play className="w-4 h-4 text-green-600" />
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          Run Optimization
                        </div>
                        <div className="text-xs text-gray-500">
                          AI-powered analysis
                        </div>
                      </div>
                    </div>
                    <ArrowRight className="w-4 h-4 text-gray-400" />
                  </div>
                </Link>
                
                <Link href="/settings" className="block">
                  <div className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
                        <Settings className="w-4 h-4 text-gray-600" />
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          Configuration
                        </div>
                        <div className="text-xs text-gray-500">
                          System settings
                        </div>
                      </div>
                    </div>
                    <ArrowRight className="w-4 h-4 text-gray-400" />
                  </div>
                </Link>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          <div className="card">
            <h3 className="text-xl font-bold text-gray-900 mb-6">
              Recent Activity
            </h3>
            
            <div className="space-y-4">
              {[
                {
                  icon: <Database className="w-5 h-5 text-blue-600" />,
                  title: 'Commercial Building Analysis Complete',
                  description: 'Building XYZ-789 • 23.5% savings identified',
                  time: '2 minutes ago',
                  status: 'success'
                },
                {
                  icon: <Brain className="w-5 h-5 text-green-600" />,
                  title: 'ML Model Training Complete',
                  description: 'XGBoost model • 94.2% accuracy achieved',
                  time: '15 minutes ago', 
                  status: 'success'
                },
                {
                  icon: <BarChart3 className="w-5 h-5 text-purple-600" />,
                  title: 'Energy Report Generated',
                  description: 'Monthly analytics for 15 buildings',
                  time: '1 hour ago',
                  status: 'info'
                },
                {
                  icon: <Building className="w-5 h-5 text-orange-600" />,
                  title: 'New Building Registered',
                  description: 'Residential complex • 850 units',
                  time: '3 hours ago',
                  status: 'info'
                }
              ].map((activity, index) => (
                <div key={index} className="flex items-start space-x-4 p-4 rounded-xl hover:bg-gray-50 transition-colors">
                  <div className="flex-shrink-0 mt-1">
                    {activity.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-medium text-gray-900">
                        {activity.title}
                      </h4>
                      <span className="text-xs text-gray-500">
                        {activity.time}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      {activity.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-6 pt-4 border-t border-gray-100">
              <Link 
                href="/activity" 
                className="text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors"
              >
                View all activity →
              </Link>
            </div>
          </div>
        </motion.div>
      </div>
    </DashboardLayout>
  )
}
