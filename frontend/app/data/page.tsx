'use client'

import { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useDropzone } from 'react-dropzone'
import DashboardLayout from '@/components/layout/DashboardLayout'
import MetricCard, { MetricGrid } from '@/components/ui/MetricCard'
import LoadingSpinner, { LoadingButton } from '@/components/ui/LoadingSpinner'
import StatusIndicator from '@/components/ui/StatusIndicator'
import { toast } from 'react-hot-toast'
import {
  Database,
  Upload,
  Download,
  FileText,
  Trash2,
  Eye,
  Edit,
  Filter,
  Calendar,
  BarChart3,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Clock,
  HardDrive,
  Zap,
  Building,
  RefreshCw,
  Search,
  Plus,
  Settings,
  Share,
  Archive
} from 'lucide-react'

interface Dataset {
  id: string
  name: string
  description: string
  source: 'uploaded' | 'generated' | 'imported'
  format: 'csv' | 'excel' | 'json'
  size: number
  records: number
  columns: string[]
  createdAt: string
  lastModified: string
  status: 'processing' | 'ready' | 'error'
  buildings: string[]
  dateRange: {
    start: string
    end: string
  }
  quality: {
    score: number
    issues: string[]
    completeness: number
  }
}

// Mock datasets
const mockDatasets: Dataset[] = [
  {
    id: '1',
    name: 'Corporate HQ Energy Data - Q3 2024',
    description: 'Complete energy consumption data for corporate headquarters',
    source: 'uploaded',
    format: 'csv',
    size: 2400000, // 2.4MB
    records: 8760,
    columns: ['timestamp', 'energy_consumption', 'temperature', 'humidity', 'occupancy'],
    createdAt: '2024-08-20T10:30:00Z',
    lastModified: '2024-08-22T14:15:00Z',
    status: 'ready',
    buildings: ['Corporate HQ'],
    dateRange: {
      start: '2024-07-01',
      end: '2024-09-30'
    },
    quality: {
      score: 92,
      issues: ['2 missing values'],
      completeness: 99.8
    }
  },
  {
    id: '2',
    name: 'Manufacturing Plants Dataset',
    description: 'Multi-building industrial energy consumption data',
    source: 'generated',
    format: 'csv',
    size: 5600000, // 5.6MB
    records: 17520,
    columns: ['timestamp', 'energy_consumption', 'production_rate', 'ambient_temp', 'machine_load'],
    createdAt: '2024-08-18T09:15:00Z',
    lastModified: '2024-08-21T11:30:00Z',
    status: 'ready',
    buildings: ['Plant A', 'Plant B', 'Warehouse'],
    dateRange: {
      start: '2024-06-01',
      end: '2024-08-31'
    },
    quality: {
      score: 88,
      issues: ['15 outliers detected', '1 data gap'],
      completeness: 97.2
    }
  },
  {
    id: '3',
    name: 'Smart Building IoT Stream',
    description: 'Real-time sensor data from smart building systems',
    source: 'imported',
    format: 'json',
    size: 890000, // 890KB
    records: 4320,
    columns: ['timestamp', 'sensor_id', 'energy_consumption', 'room_temp', 'motion_detected'],
    createdAt: '2024-08-22T16:45:00Z',
    lastModified: '2024-08-23T08:20:00Z',
    status: 'processing',
    buildings: ['Smart Campus'],
    dateRange: {
      start: '2024-08-20',
      end: '2024-08-23'
    },
    quality: {
      score: 0,
      issues: [],
      completeness: 0
    }
  }
]

export default function DataPage() {
  const [activeTab, setActiveTab] = useState<'overview' | 'upload' | 'manage'>('overview')
  const [selectedDatasets, setSelectedDatasets] = useState<string[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [filterSource, setFilterSource] = useState<'all' | Dataset['source']>('all')
  const [filterStatus, setFilterStatus] = useState<'all' | Dataset['status']>('all')

  // Dropzone configuration
  const onDrop = useCallback((acceptedFiles: File[]) => {
    acceptedFiles.forEach((file) => {
      if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
        toast.success(`Processing ${file.name}...`)
        // TODO: Implement file upload
      } else {
        toast.error(`${file.name} is not a supported format`)
      }
    })
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/json': ['.json']
    },
    maxSize: 50 * 1024 * 1024, // 50MB
    maxFiles: 5
  })

  const filteredDatasets = mockDatasets.filter(dataset => {
    const matchesSearch = dataset.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         dataset.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesSource = filterSource === 'all' || dataset.source === filterSource
    const matchesStatus = filterStatus === 'all' || dataset.status === filterStatus
    
    return matchesSearch && matchesSource && matchesStatus
  })

  const totalSize = mockDatasets.reduce((sum, ds) => sum + ds.size, 0)
  const totalRecords = mockDatasets.reduce((sum, ds) => sum + ds.records, 0)
  const avgQuality = mockDatasets.reduce((sum, ds) => sum + ds.quality.score, 0) / mockDatasets.length

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
  }

  const getSourceConfig = (source: Dataset['source']) => {
    switch (source) {
      case 'uploaded':
        return { color: 'text-blue-700 bg-blue-100', label: 'Uploaded' }
      case 'generated':
        return { color: 'text-green-700 bg-green-100', label: 'Generated' }
      case 'imported':
        return { color: 'text-purple-700 bg-purple-100', label: 'Imported' }
      default:
        return { color: 'text-gray-700 bg-gray-100', label: 'Unknown' }
    }
  }

  const getStatusConfig = (status: Dataset['status']) => {
    switch (status) {
      case 'ready':
        return { color: 'text-green-600', icon: <CheckCircle className="w-4 h-4" /> }
      case 'processing':
        return { color: 'text-blue-600', icon: <RefreshCw className="w-4 h-4 animate-spin" /> }
      case 'error':
        return { color: 'text-red-600', icon: <AlertCircle className="w-4 h-4" /> }
      default:
        return { color: 'text-gray-600', icon: <Clock className="w-4 h-4" /> }
    }
  }

  const getQualityColor = (score: number) => {
    if (score >= 90) return 'text-green-600'
    if (score >= 75) return 'text-yellow-600'
    return 'text-red-600'
  }

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
                Data Management
              </h1>
              <p className="text-gray-600 mt-2">
                Upload, manage, and analyze your energy consumption datasets
              </p>
            </div>
            
            <div className="flex space-x-3">
              <button className="btn-secondary">
                <Settings className="w-4 h-4 mr-2" />
                Data Settings
              </button>
              <button className="btn-primary">
                <Plus className="w-4 h-4 mr-2" />
                New Dataset
              </button>
            </div>
          </div>
        </motion.div>

        {/* Overview Metrics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <MetricGrid columns={4}>
            <MetricCard
              icon={<Database className="w-8 h-8 text-blue-600" />}
              title="Total Datasets"
              value={mockDatasets.length.toString()}
              subtitle="Available Datasets"
            />
            <MetricCard
              icon={<HardDrive className="w-8 h-8 text-purple-600" />}
              title="Storage Used"
              value={formatFileSize(totalSize)}
              subtitle="Data Storage"
            />
            <MetricCard
              icon={<BarChart3 className="w-8 h-8 text-green-600" />}
              title="Total Records"
              value={totalRecords.toLocaleString()}
              subtitle="Data Points"
            />
            <MetricCard
              icon={<TrendingUp className="w-8 h-8 text-emerald-600" />}
              title="Avg Quality"
              value={`${avgQuality.toFixed(1)}%`}
              trend="positive"
              subtitle="Data Quality Score"
            />
          </MetricGrid>
        </motion.div>

        {/* Tab Navigation */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {[
                { id: 'overview', label: 'Overview', icon: BarChart3 },
                { id: 'upload', label: 'Upload Data', icon: Upload },
                { id: 'manage', label: 'Manage Datasets', icon: Database }
              ].map(({ id, label, icon: Icon }) => (
                <button
                  key={id}
                  onClick={() => setActiveTab(id as any)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span>{label}</span>
                </button>
              ))}
            </nav>
          </div>
        </motion.div>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          {activeTab === 'overview' && (
            <motion.div
              key="overview"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.4 }}
              className="space-y-6"
            >
              {/* Recent Datasets */}
              <div className="card">
                <h3 className="text-xl font-bold text-gray-900 mb-6">
                  Recent Datasets
                </h3>
                
                <div className="space-y-4">
                  {mockDatasets.slice(0, 3).map((dataset, index) => (
                    <div key={dataset.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className="p-2 bg-white rounded-lg">
                          <FileText className="w-6 h-6 text-blue-600" />
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">
                            {dataset.name}
                          </h4>
                          <div className="text-sm text-gray-500">
                            {dataset.records.toLocaleString()} records • {formatFileSize(dataset.size)}
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-3">
                        <StatusIndicator status={dataset.status === 'ready' ? 'online' : dataset.status === 'processing' ? 'warning' : 'offline'} />
                        <button className="btn-secondary btn-sm">
                          <Eye className="w-4 h-4 mr-1" />
                          View
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Data Quality Overview */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="card">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Data Quality Overview
                  </h3>
                  
                  <div className="space-y-4">
                    {mockDatasets.map((dataset) => (
                      <div key={dataset.id} className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="text-sm font-medium text-gray-900">
                            {dataset.name}
                          </div>
                          <div className="flex items-center mt-1">
                            <div className="flex-1 bg-gray-200 rounded-full h-2 mr-3">
                              <div
                                className={`h-2 rounded-full ${
                                  dataset.quality.score >= 90 ? 'bg-green-500' :
                                  dataset.quality.score >= 75 ? 'bg-yellow-500' : 'bg-red-500'
                                }`}
                                style={{ width: `${dataset.quality.score}%` }}
                              />
                            </div>
                            <span className={`text-sm font-medium ${getQualityColor(dataset.quality.score)}`}>
                              {dataset.quality.score}%
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="card">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Storage Analytics
                  </h3>
                  
                  <div className="space-y-4">
                    <div className="text-center">
                      <div className="relative w-32 h-32 mx-auto mb-4">
                        <svg className="w-32 h-32 transform -rotate-90">
                          <circle
                            cx="64"
                            cy="64"
                            r="56"
                            stroke="#e5e7eb"
                            strokeWidth="8"
                            fill="transparent"
                          />
                          <circle
                            cx="64"
                            cy="64"
                            r="56"
                            stroke="#3b82f6"
                            strokeWidth="8"
                            fill="transparent"
                            strokeDasharray={`${2 * Math.PI * 56}`}
                            strokeDashoffset={`${2 * Math.PI * 56 * (1 - 0.34)}`}
                            className="transition-all duration-300"
                          />
                        </svg>
                        <div className="absolute inset-0 flex items-center justify-center">
                          <div className="text-center">
                            <div className="text-2xl font-bold text-gray-900">34%</div>
                            <div className="text-xs text-gray-500">Used</div>
                          </div>
                        </div>
                      </div>
                      
                      <div className="text-sm text-gray-600">
                        {formatFileSize(totalSize)} of 25 GB used
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'upload' && (
            <motion.div
              key="upload"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.4 }}
              className="space-y-6"
            >
              {/* Upload Zone */}
              <div className="card">
                <h3 className="text-xl font-bold text-gray-900 mb-6">
                  Upload Energy Data
                </h3>
                
                <div
                  {...getRootProps()}
                  className={`border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-200 cursor-pointer ${
                    isDragActive
                      ? 'border-blue-400 bg-blue-50'
                      : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
                  }`}
                >
                  <input {...getInputProps()} />
                  
                  <div className="space-y-4">
                    <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                      <Upload className="w-8 h-8 text-blue-600" />
                    </div>
                    
                    <div>
                      <h4 className="text-lg font-semibold text-gray-900">
                        {isDragActive ? 'Drop files here' : 'Drag & drop your files'}
                      </h4>
                      <p className="text-gray-600 mt-2">
                        or <span className="text-blue-600 font-medium">browse to choose files</span>
                      </p>
                    </div>
                    
                    <div className="text-sm text-gray-500">
                      Supports CSV, Excel, JSON • Max 50MB per file
                    </div>
                  </div>
                </div>

                {/* Upload Requirements */}
                <div className="mt-6 p-6 bg-blue-50 rounded-xl border border-blue-200">
                  <h4 className="text-sm font-medium text-blue-900 mb-3">
                    Data Format Requirements
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-800">
                    <div>
                      <strong>Required Columns:</strong>
                      <ul className="mt-1 space-y-1 text-blue-700">
                        <li>• <code>timestamp</code> (ISO 8601 format)</li>
                        <li>• <code>energy_consumption</code> (kWh)</li>
                      </ul>
                    </div>
                    <div>
                      <strong>Optional Columns:</strong>
                      <ul className="mt-1 space-y-1 text-blue-700">
                        <li>• <code>temperature</code> (°C)</li>
                        <li>• <code>humidity</code> (%)</li>
                        <li>• <code>occupancy</code> (count)</li>
                        <li>• <code>building_id</code> (identifier)</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'manage' && (
            <motion.div
              key="manage"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.4 }}
              className="space-y-6"
            >
              {/* Filters */}
              <div className="card">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  {/* Search */}
                  <div className="relative flex-1 max-w-md">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Search datasets..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10 input"
                    />
                  </div>

                  {/* Filters */}
                  <div className="flex items-center space-x-4">
                    <select
                      value={filterSource}
                      onChange={(e) => setFilterSource(e.target.value as any)}
                      className="select"
                    >
                      <option value="all">All Sources</option>
                      <option value="uploaded">Uploaded</option>
                      <option value="generated">Generated</option>
                      <option value="imported">Imported</option>
                    </select>

                    <select
                      value={filterStatus}
                      onChange={(e) => setFilterStatus(e.target.value as any)}
                      className="select"
                    >
                      <option value="all">All Status</option>
                      <option value="ready">Ready</option>
                      <option value="processing">Processing</option>
                      <option value="error">Error</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Datasets List */}
              <div className="space-y-4">
                {filteredDatasets.map((dataset, index) => {
                  const sourceConfig = getSourceConfig(dataset.source)
                  const statusConfig = getStatusConfig(dataset.status)
                  
                  return (
                    <motion.div
                      key={dataset.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                      className="card-hover"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-4 flex-1">
                          <div className="p-3 bg-gray-50 rounded-lg">
                            <FileText className="w-6 h-6 text-blue-600" />
                          </div>
                          
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center space-x-3 mb-2">
                              <h3 className="font-semibold text-gray-900 truncate">
                                {dataset.name}
                              </h3>
                              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${sourceConfig.color}`}>
                                {sourceConfig.label}
                              </span>
                              <div className={`flex items-center space-x-1 ${statusConfig.color}`}>
                                {statusConfig.icon}
                                <span className="text-xs capitalize">{dataset.status}</span>
                              </div>
                            </div>
                            
                            <p className="text-sm text-gray-600 mb-3">
                              {dataset.description}
                            </p>
                            
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                              <div>
                                <span className="text-gray-500">Records:</span>
                                <span className="font-medium text-gray-900 ml-1">
                                  {dataset.records.toLocaleString()}
                                </span>
                              </div>
                              <div>
                                <span className="text-gray-500">Size:</span>
                                <span className="font-medium text-gray-900 ml-1">
                                  {formatFileSize(dataset.size)}
                                </span>
                              </div>
                              <div>
                                <span className="text-gray-500">Quality:</span>
                                <span className={`font-medium ml-1 ${getQualityColor(dataset.quality.score)}`}>
                                  {dataset.quality.score}%
                                </span>
                              </div>
                              <div>
                                <span className="text-gray-500">Modified:</span>
                                <span className="font-medium text-gray-900 ml-1">
                                  {new Date(dataset.lastModified).toLocaleDateString()}
                                </span>
                              </div>
                            </div>

                            {/* Quality Issues */}
                            {dataset.quality.issues.length > 0 && (
                              <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded-lg">
                                <div className="flex items-center">
                                  <AlertCircle className="w-4 h-4 text-yellow-600 mr-2" />
                                  <span className="text-sm text-yellow-800">
                                    {dataset.quality.issues.join(', ')}
                                  </span>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                            <Eye className="w-4 h-4 text-gray-600" />
                          </button>
                          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                            <Download className="w-4 h-4 text-gray-600" />
                          </button>
                          <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                            <Edit className="w-4 h-4 text-gray-600" />
                          </button>
                          <button className="p-2 hover:bg-red-50 rounded-lg transition-colors group">
                            <Trash2 className="w-4 h-4 text-gray-600 group-hover:text-red-600" />
                          </button>
                        </div>
                      </div>
                    </motion.div>
                  )
                })}
              </div>
            </motion.div>
          )}

          {activeTab === 'upload' && (
            <motion.div
              key="upload"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.4 }}
            >
              <DataUploadSection />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </DashboardLayout>
  )
}

// Data Upload Section Component
function DataUploadSection() {
  const [uploadMethod, setUploadMethod] = useState<'file' | 'api' | 'database'>('file')

  return (
    <div className="space-y-6">
      {/* Upload Method Selection */}
      <div className="card">
        <h3 className="text-xl font-bold text-gray-900 mb-6">
          Choose Upload Method
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            {
              id: 'file',
              title: 'File Upload',
              description: 'Upload CSV, Excel, or JSON files',
              icon: <Upload className="w-6 h-6" />,
              color: 'bg-blue-50 border-blue-200 text-blue-700'
            },
            {
              id: 'api',
              title: 'API Import',
              description: 'Connect to external APIs',
              icon: <Database className="w-6 h-6" />,
              color: 'bg-green-50 border-green-200 text-green-700'
            },
            {
              id: 'database',
              title: 'Database Import',
              description: 'Import from SQL databases',
              icon: <HardDrive className="w-6 h-6" />,
              color: 'bg-purple-50 border-purple-200 text-purple-700'
            }
          ].map((method) => (
            <button
              key={method.id}
              onClick={() => setUploadMethod(method.id as any)}
              className={`p-6 border-2 rounded-xl text-left transition-all duration-200 ${
                uploadMethod === method.id
                  ? method.color + ' ring-2 ring-opacity-20'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                {method.icon}
                {uploadMethod === method.id && (
                  <CheckCircle className="w-5 h-5 text-current" />
                )}
              </div>
              <h4 className="font-semibold text-gray-900 mb-1">
                {method.title}
              </h4>
              <p className="text-sm text-gray-600">
                {method.description}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Upload Interface */}
      {uploadMethod === 'file' && <FileUploadInterface />}
      {uploadMethod === 'api' && <ApiImportInterface />}
      {uploadMethod === 'database' && <DatabaseImportInterface />}
    </div>
  )
}

// File Upload Interface
function FileUploadInterface() {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    // Handle file upload logic
    toast.success(`Processing ${acceptedFiles.length} file(s)...`)
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/json': ['.json']
    }
  })

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        File Upload
      </h3>
      
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 cursor-pointer ${
          isDragActive
            ? 'border-blue-400 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h4 className="text-lg font-medium text-gray-900 mb-2">
          {isDragActive ? 'Drop files here' : 'Upload your energy data files'}
        </h4>
        <p className="text-gray-600">
          Drag and drop files or click to browse
        </p>
      </div>
    </div>
  )
}

// API Import Interface  
function ApiImportInterface() {
  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        API Import
      </h3>
      <p className="text-gray-600 mb-6">
        Connect to external APIs to import energy data automatically
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Input
          label="API Endpoint URL"
          placeholder="https://api.example.com/energy-data"
          icon={<Globe />}
        />
        <Input
          label="API Key"
          type="password"
          placeholder="Enter your API key"
          icon={<Key />}
        />
      </div>
      
      <div className="mt-6">
        <button className="btn-primary">
          <Database className="w-4 h-4 mr-2" />
          Test Connection
        </button>
      </div>
    </div>
  )
}

// Database Import Interface
function DatabaseImportInterface() {
  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Database Import
      </h3>
      <p className="text-gray-600 mb-6">
        Import data directly from SQL databases
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Select
          label="Database Type"
          options={[
            { value: 'postgresql', label: 'PostgreSQL' },
            { value: 'mysql', label: 'MySQL' },
            { value: 'sqlite', label: 'SQLite' },
            { value: 'oracle', label: 'Oracle' }
          ]}
          icon={<HardDrive />}
        />
        <Input
          label="Connection String"
          placeholder="postgresql://user:pass@host:port/db"
          icon={<Database />}
        />
      </div>
      
      <div className="mt-6">
        <button className="btn-primary">
          <HardDrive className="w-4 h-4 mr-2" />
          Connect Database
        </button>
      </div>
    </div>
  )
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
}

function getQualityColor(score: number): string {
  if (score >= 90) return 'text-green-600'
  if (score >= 75) return 'text-yellow-600'
  return 'text-red-600'
}
