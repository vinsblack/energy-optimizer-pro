'use client'

import { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import DashboardLayout from '@/components/layout/DashboardLayout'
import MetricCard, { MetricGrid } from '@/components/ui/MetricCard'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import StatusIndicator from '@/components/ui/StatusIndicator'
import {
  FileText,
  Download,
  Plus,
  Filter,
  Calendar,
  TrendingUp,
  TrendingDown,
  BarChart3,
  PieChart,
  DollarSign,
  Zap,
  Building,
  Clock,
  Share,
  Eye,
  Edit,
  Trash2,
  ExternalLink,
  Star,
  Users,
  Target
} from 'lucide-react'

interface Report {
  id: string
  title: string
  description: string
  type: 'energy_analysis' | 'cost_optimization' | 'sustainability' | 'performance'
  status: 'draft' | 'published' | 'archived'
  generatedAt: string
  author: string
  buildings: string[]
  metrics: {
    totalSavings: number
    energyReduction: number
    costSavings: number
    carbonReduction: number
  }
  views: number
  starred: boolean
  size: string
  format: 'pdf' | 'excel' | 'html'
}

// Mock data
const mockReports: Report[] = [
  {
    id: '1',
    title: 'Q3 2024 Energy Performance Report',
    description: 'Comprehensive analysis of energy consumption across all commercial buildings',
    type: 'energy_analysis',
    status: 'published',
    generatedAt: '2024-08-20T10:30:00Z',
    author: 'Energy Analyst',
    buildings: ['HQ Building', 'Tech Campus', 'Office Complex A'],
    metrics: {
      totalSavings: 24.5,
      energyReduction: 1250,
      costSavings: 45000,
      carbonReduction: 2.3
    },
    views: 127,
    starred: true,
    size: '2.4 MB',
    format: 'pdf'
  },
  {
    id: '2',
    title: 'Cost Optimization Analysis - August 2024',
    description: 'ML-driven cost reduction recommendations and ROI analysis',
    type: 'cost_optimization',
    status: 'published',
    generatedAt: '2024-08-18T14:15:00Z',
    author: 'AI System',
    buildings: ['Manufacturing Plant A', 'Warehouse District'],
    metrics: {
      totalSavings: 18.7,
      energyReduction: 890,
      costSavings: 28000,
      carbonReduction: 1.8
    },
    views: 89,
    starred: false,
    size: '1.8 MB',
    format: 'excel'
  },
  {
    id: '3',
    title: 'Sustainability Impact Report',
    description: 'Carbon footprint analysis and environmental impact assessment',
    type: 'sustainability',
    status: 'draft',
    generatedAt: '2024-08-22T09:45:00Z',
    author: 'Sustainability Team',
    buildings: ['Residential Complex B', 'Corporate HQ'],
    metrics: {
      totalSavings: 31.2,
      energyReduction: 2100,
      costSavings: 62000,
      carbonReduction: 4.1
    },
    views: 23,
    starred: true,
    size: '3.1 MB',
    format: 'html'
  },
  {
    id: '4',
    title: 'Performance Benchmarking Study',
    description: 'Comparative analysis against industry standards and best practices',
    type: 'performance',
    status: 'published',
    generatedAt: '2024-08-15T16:20:00Z',
    author: 'Performance Team',
    buildings: ['All Buildings'],
    metrics: {
      totalSavings: 22.1,
      energyReduction: 1650,
      costSavings: 38000,
      carbonReduction: 2.9
    },
    views: 156,
    starred: false,
    size: '4.2 MB',
    format: 'pdf'
  }
]

export default function ReportsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState<'all' | Report['type']>('all')
  const [filterStatus, setFilterStatus] = useState<'all' | Report['status']>('all')
  const [sortBy, setSortBy] = useState<'date' | 'views' | 'title' | 'savings'>('date')
  const [selectedReports, setSelectedReports] = useState<string[]>([])
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')

  // Filter and sort reports
  const filteredReports = useMemo(() => {
    let filtered = mockReports.filter(report => {
      const matchesSearch = report.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          report.description.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesType = filterType === 'all' || report.type === filterType
      const matchesStatus = filterStatus === 'all' || report.status === filterStatus
      
      return matchesSearch && matchesType && matchesStatus
    })

    // Sort reports
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'views':
          return b.views - a.views
        case 'title':
          return a.title.localeCompare(b.title)
        case 'savings':
          return b.metrics.totalSavings - a.metrics.totalSavings
        default:
          return new Date(b.generatedAt).getTime() - new Date(a.generatedAt).getTime()
      }
    })

    return filtered
  }, [searchTerm, filterType, filterStatus, sortBy])

  const getReportTypeConfig = (type: Report['type']) => {
    switch (type) {
      case 'energy_analysis':
        return {
          color: 'text-blue-700 bg-blue-100',
          icon: <Zap className="w-4 h-4" />,
          label: 'Energy Analysis'
        }
      case 'cost_optimization':
        return {
          color: 'text-green-700 bg-green-100',
          icon: <DollarSign className="w-4 h-4" />,
          label: 'Cost Optimization'
        }
      case 'sustainability':
        return {
          color: 'text-emerald-700 bg-emerald-100',
          icon: <Target className="w-4 h-4" />,
          label: 'Sustainability'
        }
      case 'performance':
        return {
          color: 'text-purple-700 bg-purple-100',
          icon: <BarChart3 className="w-4 h-4" />,
          label: 'Performance'
        }
      default:
        return {
          color: 'text-gray-700 bg-gray-100',
          icon: <FileText className="w-4 h-4" />,
          label: 'Report'
        }
    }
  }

  const getStatusConfig = (status: Report['status']) => {
    switch (status) {
      case 'published':
        return { color: 'text-green-600', label: 'Published', dot: 'bg-green-500' }
      case 'draft':
        return { color: 'text-yellow-600', label: 'Draft', dot: 'bg-yellow-500' }
      case 'archived':
        return { color: 'text-gray-600', label: 'Archived', dot: 'bg-gray-500' }
      default:
        return { color: 'text-gray-600', label: 'Unknown', dot: 'bg-gray-500' }
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const totalMetrics = useMemo(() => {
    return filteredReports.reduce((acc, report) => ({
      totalSavings: acc.totalSavings + report.metrics.totalSavings,
      energyReduction: acc.energyReduction + report.metrics.energyReduction,
      costSavings: acc.costSavings + report.metrics.costSavings,
      carbonReduction: acc.carbonReduction + report.metrics.carbonReduction
    }), { totalSavings: 0, energyReduction: 0, costSavings: 0, carbonReduction: 0 })
  }, [filteredReports])

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="heading-2 text-gray-900">
                Analytics Reports
              </h1>
              <p className="text-gray-600 mt-2">
                Generate, view, and manage comprehensive energy optimization reports
              </p>
            </div>
            
            <div className="flex space-x-3">
              <button className="btn-secondary">
                <Filter className="w-5 h-5 mr-2" />
                Advanced Filters
              </button>
              <button className="btn-primary">
                <Plus className="w-5 h-5 mr-2" />
                Generate Report
              </button>
            </div>
          </div>
        </motion.div>

        {/* Summary Metrics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <MetricGrid columns={4}>
            <MetricCard
              icon={<FileText className="w-8 h-8 text-blue-600" />}
              title="Total Reports"
              value={filteredReports.length.toString()}
              subtitle="Available Reports"
            />
            <MetricCard
              icon={<TrendingUp className="w-8 h-8 text-green-600" />}
              title="Avg Savings"
              value={`${(totalMetrics.totalSavings / filteredReports.length || 0).toFixed(1)}%`}
              trend="positive"
              subtitle="Energy Reduction"
            />
            <MetricCard
              icon={<DollarSign className="w-8 h-8 text-emerald-600" />}
              title="Total Savings"
              value={`€${Math.round(totalMetrics.costSavings / 1000)}K`}
              trend="positive"
              subtitle="Cost Reduction"
            />
            <MetricCard
              icon={<Target className="w-8 h-8 text-purple-600" />}
              title="Carbon Reduced"
              value={`${totalMetrics.carbonReduction.toFixed(1)}T`}
              trend="positive"
              subtitle="CO₂ Equivalent"
            />
          </MetricGrid>
        </motion.div>

        {/* Filters & Controls */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <div className="card">
            <div className="flex flex-wrap items-center justify-between gap-4">
              {/* Search */}
              <div className="relative flex-1 max-w-md">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <FileText className="w-4 h-4 text-gray-400" />
                </div>
                <input
                  type="text"
                  placeholder="Search reports..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 input"
                />
              </div>

              {/* Filters */}
              <div className="flex items-center space-x-4">
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value as any)}
                  className="select"
                >
                  <option value="all">All Types</option>
                  <option value="energy_analysis">Energy Analysis</option>
                  <option value="cost_optimization">Cost Optimization</option>
                  <option value="sustainability">Sustainability</option>
                  <option value="performance">Performance</option>
                </select>

                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value as any)}
                  className="select"
                >
                  <option value="all">All Status</option>
                  <option value="published">Published</option>
                  <option value="draft">Draft</option>
                  <option value="archived">Archived</option>
                </select>

                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="select"
                >
                  <option value="date">Sort by Date</option>
                  <option value="views">Sort by Views</option>
                  <option value="title">Sort by Title</option>
                  <option value="savings">Sort by Savings</option>
                </select>

                {/* View Mode Toggle */}
                <div className="flex bg-gray-100 rounded-lg p-1">
                  <button
                    onClick={() => setViewMode('grid')}
                    className={`p-2 rounded ${viewMode === 'grid' ? 'bg-white shadow-sm' : ''}`}
                  >
                    <BarChart3 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setViewMode('list')}
                    className={`p-2 rounded ${viewMode === 'list' ? 'bg-white shadow-sm' : ''}`}
                  >
                    <FileText className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Reports Grid/List */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          {viewMode === 'grid' ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              <AnimatePresence mode="popLayout">
                {filteredReports.map((report, index) => (
                  <ReportCard key={report.id} report={report} index={index} />
                ))}
              </AnimatePresence>
            </div>
          ) : (
            <div className="card">
              <ReportsList reports={filteredReports} />
            </div>
          )}
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Quick Report Generation
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                {
                  title: 'Energy Analysis',
                  description: 'Consumption patterns and trends',
                  icon: <Zap className="w-6 h-6 text-blue-600" />,
                  color: 'bg-blue-50 hover:bg-blue-100'
                },
                {
                  title: 'Cost Report',
                  description: 'Financial impact and savings',
                  icon: <DollarSign className="w-6 h-6 text-green-600" />,
                  color: 'bg-green-50 hover:bg-green-100'
                },
                {
                  title: 'Sustainability',
                  description: 'Carbon footprint analysis',
                  icon: <Target className="w-6 h-6 text-emerald-600" />,
                  color: 'bg-emerald-50 hover:bg-emerald-100'
                },
                {
                  title: 'Performance',
                  description: 'Efficiency benchmarking',
                  icon: <BarChart3 className="w-6 h-6 text-purple-600" />,
                  color: 'bg-purple-50 hover:bg-purple-100'
                }
              ].map((template, index) => (
                <motion.button
                  key={template.title}
                  className={`p-4 rounded-xl border border-gray-200 text-left transition-all duration-200 ${template.color}`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                >
                  <div className="flex items-center justify-between mb-3">
                    {template.icon}
                    <Plus className="w-4 h-4 text-gray-400" />
                  </div>
                  <h4 className="font-semibold text-gray-900 mb-1">
                    {template.title}
                  </h4>
                  <p className="text-xs text-gray-600">
                    {template.description}
                  </p>
                </motion.button>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </DashboardLayout>
  )
}

// Report Card Component
function ReportCard({ report, index }: { report: Report; index: number }) {
  const typeConfig = getReportTypeConfig(report.type)
  const statusConfig = getStatusConfig(report.status)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 20 }}
      transition={{ duration: 0.3, delay: index * 0.1 }}
      className="card-hover group cursor-pointer"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${typeConfig.color}`}>
              {typeConfig.icon}
              <span className="ml-1">{typeConfig.label}</span>
            </span>
            
            <div className={`flex items-center text-xs ${statusConfig.color}`}>
              <div className={`w-2 h-2 rounded-full ${statusConfig.dot} mr-1`} />
              {statusConfig.label}
            </div>
          </div>
          
          <h3 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
            {report.title}
          </h3>
          <p className="text-sm text-gray-600 mt-1 line-clamp-2">
            {report.description}
          </p>
        </div>
        
        <div className="flex items-center space-x-1">
          {report.starred && (
            <Star className="w-4 h-4 text-yellow-500 fill-current" />
          )}
          <button className="p-1 hover:bg-gray-100 rounded opacity-0 group-hover:opacity-100 transition-opacity">
            <Trash2 className="w-4 h-4 text-gray-400 hover:text-red-500" />
          </button>
        </div>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-lg font-bold text-green-600">
            {report.metrics.totalSavings.toFixed(1)}%
          </div>
          <div className="text-xs text-gray-600">Energy Savings</div>
        </div>
        
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-lg font-bold text-blue-600">
            €{Math.round(report.metrics.costSavings / 1000)}K
          </div>
          <div className="text-xs text-gray-600">Cost Savings</div>
        </div>
      </div>

      {/* Buildings */}
      <div className="mb-4">
        <div className="flex items-center text-sm text-gray-600 mb-2">
          <Building className="w-4 h-4 mr-1" />
          <span>{report.buildings.length} Building{report.buildings.length > 1 ? 's' : ''}</span>
        </div>
        <div className="flex flex-wrap gap-1">
          {report.buildings.slice(0, 2).map((building, i) => (
            <span key={i} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
              {building}
            </span>
          ))}
          {report.buildings.length > 2 && (
            <span className="text-xs text-gray-500 px-2 py-1">
              +{report.buildings.length - 2} more
            </span>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between text-sm text-gray-500 pt-4 border-t border-gray-100">
        <div className="flex items-center space-x-4">
          <div className="flex items-center">
            <Clock className="w-4 h-4 mr-1" />
            {formatDate(report.generatedAt)}
          </div>
          <div className="flex items-center">
            <Eye className="w-4 h-4 mr-1" />
            {report.views}
          </div>
        </div>
        
        <div className="flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <button className="p-1 hover:bg-gray-100 rounded">
            <Eye className="w-4 h-4 text-gray-600" />
          </button>
          <button className="p-1 hover:bg-gray-100 rounded">
            <Download className="w-4 h-4 text-gray-600" />
          </button>
          <button className="p-1 hover:bg-gray-100 rounded">
            <Share className="w-4 h-4 text-gray-600" />
          </button>
        </div>
      </div>
    </motion.div>
  )
}

// Reports List Component
function ReportsList({ reports }: { reports: Report[] }) {
  return (
    <div className="overflow-hidden">
      <table className="w-full">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Report
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Type
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Savings
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Generated
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {reports.map((report, index) => {
            const typeConfig = getReportTypeConfig(report.type)
            const statusConfig = getStatusConfig(report.status)
            
            return (
              <motion.tr
                key={report.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                className="hover:bg-gray-50 transition-colors"
              >
                <td className="px-6 py-4">
                  <div className="flex items-center">
                    {report.starred && (
                      <Star className="w-4 h-4 text-yellow-500 fill-current mr-2" />
                    )}
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {report.title}
                      </div>
                      <div className="text-sm text-gray-500">
                        {report.author} • {report.views} views
                      </div>
                    </div>
                  </div>
                </td>
                
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${typeConfig.color}`}>
                    {typeConfig.icon}
                    <span className="ml-1">{typeConfig.label}</span>
                  </span>
                </td>
                
                <td className="px-6 py-4">
                  <div className={`flex items-center text-sm ${statusConfig.color}`}>
                    <div className={`w-2 h-2 rounded-full ${statusConfig.dot} mr-2`} />
                    {statusConfig.label}
                  </div>
                </td>
                
                <td className="px-6 py-4">
                  <div className="text-sm">
                    <div className="font-medium text-green-600">
                      {report.metrics.totalSavings.toFixed(1)}%
                    </div>
                    <div className="text-gray-500">
                      €{Math.round(report.metrics.costSavings / 1000)}K
                    </div>
                  </div>
                </td>
                
                <td className="px-6 py-4 text-sm text-gray-500">
                  {formatDate(report.generatedAt)}
                </td>
                
                <td className="px-6 py-4">
                  <div className="flex items-center space-x-2">
                    <button className="p-1 hover:bg-gray-100 rounded">
                      <Eye className="w-4 h-4 text-gray-600" />
                    </button>
                    <button className="p-1 hover:bg-gray-100 rounded">
                      <Download className="w-4 h-4 text-gray-600" />
                    </button>
                    <button className="p-1 hover:bg-gray-100 rounded">
                      <Edit className="w-4 h-4 text-gray-600" />
                    </button>
                    <button className="p-1 hover:bg-gray-100 rounded">
                      <ExternalLink className="w-4 h-4 text-gray-600" />
                    </button>
                  </div>
                </td>
              </motion.tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

// Utility functions
function getReportTypeConfig(type: Report['type']) {
  switch (type) {
    case 'energy_analysis':
      return {
        color: 'text-blue-700 bg-blue-100',
        icon: <Zap className="w-4 h-4" />,
        label: 'Energy Analysis'
      }
    case 'cost_optimization':
      return {
        color: 'text-green-700 bg-green-100',
        icon: <DollarSign className="w-4 h-4" />,
        label: 'Cost Optimization'
      }
    case 'sustainability':
      return {
        color: 'text-emerald-700 bg-emerald-100',
        icon: <Target className="w-4 h-4" />,
        label: 'Sustainability'
      }
    case 'performance':
      return {
        color: 'text-purple-700 bg-purple-100',
        icon: <BarChart3 className="w-4 h-4" />,
        label: 'Performance'
      }
    default:
      return {
        color: 'text-gray-700 bg-gray-100',
        icon: <FileText className="w-4 h-4" />,
        label: 'Report'
      }
  }
}

function getStatusConfig(status: Report['status']) {
  switch (status) {
    case 'published':
      return { color: 'text-green-600', label: 'Published', dot: 'bg-green-500' }
    case 'draft':
      return { color: 'text-yellow-600', label: 'Draft', dot: 'bg-yellow-500' }
    case 'archived':
      return { color: 'text-gray-600', label: 'Archived', dot: 'bg-gray-500' }
    default:
      return { color: 'text-gray-600', label: 'Unknown', dot: 'bg-gray-500' }
  }
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
