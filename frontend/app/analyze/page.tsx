'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useQuery, useMutation } from 'react-query'
import DashboardLayout from '@/components/layout/DashboardLayout'
import MetricCard, { MetricGrid } from '@/components/ui/MetricCard'
import EnergyChart from '@/components/charts/EnergyChart'
import LoadingSpinner, { LoadingOverlay, LoadingButton } from '@/components/ui/LoadingSpinner'
import { apiService, handleApiError } from '@/lib/api'
import { toast } from 'react-hot-toast'
import {
  Upload,
  Play,
  Database,
  Calendar,
  Building,
  TrendingUp,
  Zap,
  BarChart3,
  FileText,
  Download,
  Settings,
  Info
} from 'lucide-react'

interface DataGenerationParams {
  startDate: string
  endDate: string
  buildingType: string
  floorArea: number
  includeWeather: boolean
  includeOccupancy: boolean
  noiseLevel: number
}

export default function AnalyzePage() {
  const [activeTab, setActiveTab] = useState<'generate' | 'upload'>('generate')
  const [analysisData, setAnalysisData] = useState<any>(null)
  const [generationParams, setGenerationParams] = useState<DataGenerationParams>({
    startDate: '2024-08-01',
    endDate: '2024-08-24',
    buildingType: 'commercial',
    floorArea: 2500,
    includeWeather: true,
    includeOccupancy: true,
    noiseLevel: 0.1
  })

  // Get building types for form
  const { data: buildingTypes } = useQuery(
    'building-types',
    () => apiService.getBuildingTypes()
  )

  // Data generation mutation
  const generateDataMutation = useMutation(
    (params: DataGenerationParams) => 
      apiService.generateSampleData(
        params.startDate,
        params.endDate,
        params.buildingType,
        params.floorArea
      ),
    {
      onSuccess: (data) => {
        setAnalysisData(data)
        toast.success(`Generated ${data.data_points} data points successfully!`)
      },
      onError: (error) => {
        toast.error(handleApiError(error))
      }
    }
  )

  const handleGenerateData = () => {
    generateDataMutation.mutate(generationParams)
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (file.type !== 'text/csv') {
      toast.error('Please upload a CSV file')
      return
    }

    try {
      const formData = new FormData()
      formData.append('file', file)
      
      // TODO: Implement file upload API endpoint
      toast.success('File uploaded successfully!')
    } catch (error) {
      toast.error('Failed to upload file')
    }
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
                Data Analysis
              </h1>
              <p className="text-gray-600 mt-2">
                Generate sample data or upload your energy consumption data for analysis
              </p>
            </div>
            
            <div className="flex items-center space-x-3">
              <button className="btn-secondary btn-sm">
                <FileText className="w-4 h-4 mr-2" />
                Documentation
              </button>
              <button className="btn-primary btn-sm">
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </button>
            </div>
          </div>
        </motion.div>

        {/* Tab Navigation */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {[
                { id: 'generate', label: 'Generate Data', icon: Database },
                { id: 'upload', label: 'Upload Data', icon: Upload }
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
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {activeTab === 'generate' ? (
              <motion.div
                key="generate"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.4 }}
              >
                {/* Data Generation Form */}
                <div className="card">
                  <h3 className="text-xl font-bold text-gray-900 mb-6">
                    Generate Sample Data
                  </h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Date Range */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Start Date
                      </label>
                      <input
                        type="date"
                        value={generationParams.startDate}
                        onChange={(e) => setGenerationParams(prev => ({
                          ...prev,
                          startDate: e.target.value
                        }))}
                        className="input"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        End Date
                      </label>
                      <input
                        type="date"
                        value={generationParams.endDate}
                        onChange={(e) => setGenerationParams(prev => ({
                          ...prev,
                          endDate: e.target.value
                        }))}
                        className="input"
                      />
                    </div>

                    {/* Building Type */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Building Type
                      </label>
                      <select
                        value={generationParams.buildingType}
                        onChange={(e) => setGenerationParams(prev => ({
                          ...prev,
                          buildingType: e.target.value
                        }))}
                        className="select"
                      >
                        <option value="commercial">Commercial</option>
                        <option value="residential">Residential</option>
                        <option value="industrial">Industrial</option>
                      </select>
                    </div>

                    {/* Floor Area */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Floor Area (m²)
                      </label>
                      <input
                        type="number"
                        value={generationParams.floorArea}
                        onChange={(e) => setGenerationParams(prev => ({
                          ...prev,
                          floorArea: parseInt(e.target.value)
                        }))}
                        min="100"
                        step="100"
                        className="input"
                      />
                    </div>
                  </div>

                  {/* Advanced Options */}
                  <div className="mt-6 pt-6 border-t border-gray-200">
                    <h4 className="text-sm font-medium text-gray-900 mb-4">
                      Advanced Options
                    </h4>
                    
                    <div className="space-y-4">
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          checked={generationParams.includeWeather}
                          onChange={(e) => setGenerationParams(prev => ({
                            ...prev,
                            includeWeather: e.target.checked
                          }))}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span className="ml-2 text-sm text-gray-700">
                          Include weather data
                        </span>
                      </label>

                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          checked={generationParams.includeOccupancy}
                          onChange={(e) => setGenerationParams(prev => ({
                            ...prev,
                            includeOccupancy: e.target.checked
                          }))}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span className="ml-2 text-sm text-gray-700">
                          Include occupancy patterns
                        </span>
                      </label>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Noise Level: {generationParams.noiseLevel}
                        </label>
                        <input
                          type="range"
                          min="0"
                          max="0.5"
                          step="0.05"
                          value={generationParams.noiseLevel}
                          onChange={(e) => setGenerationParams(prev => ({
                            ...prev,
                            noiseLevel: parseFloat(e.target.value)
                          }))}
                          className="w-full"
                        />
                        <div className="flex justify-between text-xs text-gray-500 mt-1">
                          <span>Clean</span>
                          <span>Realistic</span>
                          <span>Noisy</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Generate Button */}
                  <div className="mt-6">
                    <LoadingButton
                      onClick={handleGenerateData}
                      loading={generateDataMutation.isLoading}
                      className="btn-primary btn-lg w-full md:w-auto"
                    >
                      <Play className="w-5 h-5 mr-2" />
                      Generate Data
                    </LoadingButton>
                  </div>
                </div>
              </motion.div>
            ) : (
              <motion.div
                key="upload"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.4 }}
              >
                {/* File Upload */}
                <div className="card">
                  <h3 className="text-xl font-bold text-gray-900 mb-6">
                    Upload Energy Data
                  </h3>
                  
                  <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-gray-400 transition-colors">
                    <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h4 className="text-lg font-medium text-gray-900 mb-2">
                      Drop your CSV file here
                    </h4>
                    <p className="text-gray-600 mb-4">
                      or click to browse your files
                    </p>
                    
                    <input
                      type="file"
                      accept=".csv"
                      onChange={handleFileUpload}
                      className="hidden"
                      id="file-upload"
                    />
                    <label
                      htmlFor="file-upload"
                      className="btn-primary cursor-pointer inline-flex items-center"
                    >
                      <Upload className="w-4 h-4 mr-2" />
                      Choose File
                    </label>
                  </div>

                  <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <div className="flex items-start">
                      <Info className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
                      <div>
                        <h4 className="text-sm font-medium text-blue-900 mb-2">
                          CSV Format Requirements
                        </h4>
                        <ul className="text-sm text-blue-700 space-y-1">
                          <li>• <code>timestamp</code>: Date/time in ISO format</li>
                          <li>• <code>energy_consumption</code>: Energy usage in kWh</li>
                          <li>• Optional: temperature, humidity, occupancy</li>
                          <li>• Maximum file size: 10MB</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Data Preview */}
            {analysisData && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                <EnergyChart 
                  data={analysisData.data}
                  height={400}
                  showControls={true}
                />
              </motion.div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Stats */}
            {analysisData ? (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5 }}
              >
                <div className="card">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Data Statistics
                  </h3>
                  
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Data Points</span>
                      <span className="font-medium text-gray-900">
                        {analysisData.data_points.toLocaleString()}
                      </span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Features</span>
                      <span className="font-medium text-gray-900">
                        {analysisData.features.length}
                      </span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Avg Consumption</span>
                      <span className="font-medium text-gray-900">
                        {analysisData.statistics.avg_consumption.toFixed(1)} kWh
                      </span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Peak Consumption</span>
                      <span className="font-medium text-gray-900">
                        {analysisData.statistics.max_consumption.toFixed(1)} kWh
                      </span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Total Consumption</span>
                      <span className="font-medium text-gray-900">
                        {(analysisData.statistics.total_consumption / 1000).toFixed(1)} MWh
                      </span>
                    </div>
                  </div>

                  <div className="mt-6 pt-4 border-t border-gray-100">
                    <button className="btn-primary w-full">
                      <Download className="w-4 h-4 mr-2" />
                      Export Data
                    </button>
                  </div>
                </div>
              </motion.div>
            ) : (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5 }}
              >
                <div className="card">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Getting Started
                  </h3>
                  
                  <div className="space-y-4">
                    <div className="flex items-start space-x-3">
                      <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-xs font-bold text-blue-600">1</span>
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-gray-900">
                          Generate or Upload Data
                        </h4>
                        <p className="text-xs text-gray-600 mt-1">
                          Create sample data or upload your CSV file
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-start space-x-3">
                      <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-xs font-bold text-blue-600">2</span>
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-gray-900">
                          Review Analytics
                        </h4>
                        <p className="text-xs text-gray-600 mt-1">
                          Analyze patterns and consumption trends
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-start space-x-3">
                      <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-xs font-bold text-blue-600">3</span>
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-gray-900">
                          Run Optimization
                        </h4>
                        <p className="text-xs text-gray-600 mt-1">
                          Use ML algorithms to find savings
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Building Types Info */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
            >
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Building Types
                </h3>
                
                <div className="space-y-3">
                  {buildingTypes?.building_types?.map((type, index) => (
                    <div key={type.type} className="p-3 bg-gray-50 rounded-lg">
                      <h4 className="text-sm font-medium text-gray-900">
                        {type.display_name}
                      </h4>
                      <p className="text-xs text-gray-600 mt-1">
                        {type.typical_consumption}
                      </p>
                      <p className="text-xs text-green-600 mt-1">
                        {type.optimization_potential} savings potential
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          </div>
        </div>

        {/* Loading Overlay */}
        <LoadingOverlay 
          show={generateDataMutation.isLoading}
          text="Generating energy data..."
        />
      </div>
    </DashboardLayout>
  )
}
