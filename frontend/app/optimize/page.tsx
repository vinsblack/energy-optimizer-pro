'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useQuery, useMutation } from 'react-query'
import DashboardLayout from '@/components/layout/DashboardLayout'
import MetricCard, { MetricGrid } from '@/components/ui/MetricCard'
import EnergyChart from '@/components/charts/EnergyChart'
import LoadingSpinner, { LoadingOverlay, LoadingButton } from '@/components/ui/LoadingSpinner'
import StatusIndicator from '@/components/ui/StatusIndicator'
import { apiService, handleApiError, OptimizationRequest } from '@/lib/api'
import { toast } from 'react-hot-toast'
import {
  Brain,
  Zap,
  TrendingUp,
  DollarSign,
  Settings,
  Play,
  CheckCircle,
  AlertCircle,
  BarChart3,
  Lightbulb,
  Target,
  Clock,
  Award,
  ArrowRight,
  Info
} from 'lucide-react'

interface OptimizationState {
  isRunning: boolean
  progress: number
  currentStep: string
  result: any
}

export default function OptimizePage() {
  const [selectedAlgorithm, setSelectedAlgorithm] = useState('xgboost')
  const [optimizationParams, setOptimizationParams] = useState({
    startDate: '2024-08-01',
    endDate: '2024-08-24',
    buildingType: 'commercial',
    floorArea: 2500,
    optimizationGoals: ['cost_reduction', 'energy_efficiency']
  })
  const [optimizationState, setOptimizationState] = useState<OptimizationState>({
    isRunning: false,
    progress: 0,
    currentStep: '',
    result: null
  })

  // Fetch available algorithms
  const { data: algorithmsData, isLoading: algorithmsLoading } = useQuery(
    'algorithms',
    () => apiService.getAlgorithms()
  )

  // Optimization mutation
  const optimizationMutation = useMutation(
    (request: OptimizationRequest) => apiService.runOptimization(request),
    {
      onMutate: () => {
        setOptimizationState({
          isRunning: true,
          progress: 0,
          currentStep: 'Preparing data...',
          result: null
        })
      },
      onSuccess: (data) => {
        setOptimizationState({
          isRunning: false,
          progress: 100,
          currentStep: 'Completed',
          result: data
        })
        toast.success(`Optimization completed! ${data.savings_percent.toFixed(1)}% savings identified`)
      },
      onError: (error) => {
        setOptimizationState(prev => ({
          ...prev,
          isRunning: false
        }))
        toast.error(handleApiError(error))
      }
    }
  )

  // Simulate progress for better UX
  useEffect(() => {
    if (optimizationState.isRunning && optimizationState.progress < 90) {
      const steps = [
        'Preparing data...',
        'Feature engineering...',
        'Training ML model...',
        'Validating predictions...',
        'Generating recommendations...',
        'Finalizing results...'
      ]
      
      const timer = setTimeout(() => {
        const newProgress = Math.min(optimizationState.progress + Math.random() * 15, 90)
        const stepIndex = Math.floor((newProgress / 100) * steps.length)
        
        setOptimizationState(prev => ({
          ...prev,
          progress: newProgress,
          currentStep: steps[stepIndex] || steps[steps.length - 1]
        }))
      }, 1000 + Math.random() * 2000)

      return () => clearTimeout(timer)
    }
  }, [optimizationState.isRunning, optimizationState.progress])

  const handleOptimize = () => {
    const request: OptimizationRequest = {
      algorithm: selectedAlgorithm,
      start_date: optimizationParams.startDate,
      end_date: optimizationParams.endDate,
      building_config: {
        building_type: optimizationParams.buildingType,
        floor_area: optimizationParams.floorArea,
        building_age: 10,
        insulation_level: 0.75,
        hvac_efficiency: 0.8,
        occupancy_max: 100,
        location: 'Rome, IT',
        renewable_energy: false,
        smart_systems: false
      },
      optimization_goals: optimizationParams.optimizationGoals
    }

    optimizationMutation.mutate(request)
  }

  const selectedAlgorithmInfo = algorithmsData?.available_algorithms?.find(
    alg => alg.name === selectedAlgorithm
  )

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
                AI Optimization Engine
              </h1>
              <p className="text-gray-600 mt-2">
                Use advanced machine learning algorithms to optimize energy consumption
              </p>
            </div>
            
            <div className="flex items-center space-x-3">
              <StatusIndicator 
                status="online" 
                label="ML Engine Ready"
                showIcon 
              />
              <button className="btn-secondary btn-sm">
                <Settings className="w-4 h-4 mr-2" />
                Advanced Settings
              </button>
            </div>
          </div>
        </motion.div>

        {!optimizationState.result ? (
          <>
            {/* Configuration Section */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Main Configuration */}
              <div className="lg:col-span-2 space-y-6">
                {/* Algorithm Selection */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.1 }}
                >
                  <div className="card">
                    <h3 className="text-xl font-bold text-gray-900 mb-6">
                      Select ML Algorithm
                    </h3>
                    
                    {algorithmsLoading ? (
                      <div className="text-center py-8">
                        <LoadingSpinner size="lg" text="Loading algorithms..." />
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {algorithmsData?.available_algorithms?.map((algorithm) => (
                          <div
                            key={algorithm.name}
                            className={`p-4 border rounded-xl cursor-pointer transition-all duration-200 ${
                              selectedAlgorithm === algorithm.name
                                ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-500 ring-opacity-20'
                                : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
                            }`}
                            onClick={() => setSelectedAlgorithm(algorithm.name)}
                          >
                            <div className="flex items-center justify-between mb-2">
                              <h4 className="font-semibold text-gray-900">
                                {algorithm.display_name}
                              </h4>
                              {selectedAlgorithm === algorithm.name && (
                                <CheckCircle className="w-5 h-5 text-blue-600" />
                              )}
                            </div>
                            
                            <p className="text-sm text-gray-600 mb-3">
                              {algorithm.description}
                            </p>
                            
                            <div className="space-y-1 text-xs">
                              <div className="flex justify-between">
                                <span className="text-gray-500">Accuracy:</span>
                                <span className="font-medium text-green-600">
                                  {algorithm.typical_accuracy}
                                </span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-500">Speed:</span>
                                <span className="font-medium">
                                  {algorithm.training_time}
                                </span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </motion.div>

                {/* Parameters */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.2 }}
                >
                  <div className="card">
                    <h3 className="text-xl font-bold text-gray-900 mb-6">
                      Optimization Parameters
                    </h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Start Date
                        </label>
                        <input
                          type="date"
                          value={optimizationParams.startDate}
                          onChange={(e) => setOptimizationParams(prev => ({
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
                          value={optimizationParams.endDate}
                          onChange={(e) => setOptimizationParams(prev => ({
                            ...prev,
                            endDate: e.target.value
                          }))}
                          className="input"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Building Type
                        </label>
                        <select
                          value={optimizationParams.buildingType}
                          onChange={(e) => setOptimizationParams(prev => ({
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

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Floor Area (m²)
                        </label>
                        <input
                          type="number"
                          value={optimizationParams.floorArea}
                          onChange={(e) => setOptimizationParams(prev => ({
                            ...prev,
                            floorArea: parseInt(e.target.value)
                          }))}
                          min="100"
                          step="100"
                          className="input"
                        />
                      </div>
                    </div>

                    {/* Optimization Goals */}
                    <div className="mt-6">
                      <label className="block text-sm font-medium text-gray-700 mb-4">
                        Optimization Goals
                      </label>
                      <div className="grid grid-cols-2 gap-4">
                        {[
                          { id: 'cost_reduction', label: 'Cost Reduction', icon: DollarSign },
                          { id: 'energy_efficiency', label: 'Energy Efficiency', icon: Zap },
                          { id: 'carbon_footprint', label: 'Carbon Footprint', icon: Target },
                          { id: 'peak_shaving', label: 'Peak Shaving', icon: BarChart3 }
                        ].map(({ id, label, icon: Icon }) => (
                          <label key={id} className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                            <input
                              type="checkbox"
                              checked={optimizationParams.optimizationGoals.includes(id)}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  setOptimizationParams(prev => ({
                                    ...prev,
                                    optimizationGoals: [...prev.optimizationGoals, id]
                                  }))
                                } else {
                                  setOptimizationParams(prev => ({
                                    ...prev,
                                    optimizationGoals: prev.optimizationGoals.filter(g => g !== id)
                                  }))
                                }
                              }}
                              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                            />
                            <Icon className="w-5 h-5 text-gray-600" />
                            <span className="text-sm font-medium text-gray-900">
                              {label}
                            </span>
                          </label>
                        ))}
                      </div>
                    </div>
                  </div>
                </motion.div>
              </div>

              {/* Algorithm Info Sidebar */}
              <div className="space-y-6">
                {selectedAlgorithmInfo && (
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5 }}
                  >
                    <div className="card">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">
                        {selectedAlgorithmInfo.display_name}
                      </h3>
                      
                      <p className="text-sm text-gray-600 mb-4">
                        {selectedAlgorithmInfo.description}
                      </p>

                      <div className="space-y-3">
                        <div>
                          <h4 className="text-sm font-medium text-green-700 mb-1">
                            Advantages
                          </h4>
                          <ul className="text-xs text-gray-600 space-y-1">
                            {selectedAlgorithmInfo.pros.map((pro, index) => (
                              <li key={index}>• {pro}</li>
                            ))}
                          </ul>
                        </div>

                        <div>
                          <h4 className="text-sm font-medium text-orange-700 mb-1">
                            Considerations
                          </h4>
                          <ul className="text-xs text-gray-600 space-y-1">
                            {selectedAlgorithmInfo.cons.map((con, index) => (
                              <li key={index}>• {con}</li>
                            ))}
                          </ul>
                        </div>

                        <div className="pt-3 border-t border-gray-200">
                          <h4 className="text-sm font-medium text-gray-900 mb-2">
                            Performance Metrics
                          </h4>
                          <div className="space-y-2">
                            <div className="flex justify-between text-xs">
                              <span className="text-gray-600">Accuracy:</span>
                              <span className="font-medium">{selectedAlgorithmInfo.typical_accuracy}</span>
                            </div>
                            <div className="flex justify-between text-xs">
                              <span className="text-gray-600">Training Speed:</span>
                              <span className="font-medium">{selectedAlgorithmInfo.training_time}</span>
                            </div>
                            <div className="flex justify-between text-xs">
                              <span className="text-gray-600">Memory Usage:</span>
                              <span className="font-medium">{selectedAlgorithmInfo.memory_usage}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}

                {/* Quick Tips */}
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: 0.1 }}
                >
                  <div className="card">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      <Lightbulb className="w-5 h-5 inline mr-2 text-yellow-500" />
                      Optimization Tips
                    </h3>
                    
                    <div className="space-y-3 text-sm text-gray-600">
                      <div className="flex items-start space-x-2">
                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span>Use at least 7 days of data for reliable results</span>
                      </div>
                      <div className="flex items-start space-x-2">
                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span>XGBoost typically provides the highest accuracy</span>
                      </div>
                      <div className="flex items-start space-x-2">
                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span>Include multiple optimization goals for better insights</span>
                      </div>
                      <div className="flex items-start space-x-2">
                        <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span>Review recommendations before implementation</span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              </div>
            </div>

            {/* Run Optimization Button */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
            >
              <div className="card text-center">
                <div className="max-w-2xl mx-auto">
                  <Brain className="w-16 h-16 text-blue-600 mx-auto mb-4" />
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">
                    Ready to Optimize?
                  </h3>
                  <p className="text-gray-600 mb-6">
                    Our AI will analyze your energy consumption patterns and provide 
                    actionable recommendations to reduce costs and improve efficiency.
                  </p>
                  
                  <LoadingButton
                    onClick={handleOptimize}
                    loading={optimizationState.isRunning}
                    disabled={optimizationParams.optimizationGoals.length === 0}
                    className="btn-primary btn-lg px-8 py-4"
                  >
                    <Play className="w-6 h-6 mr-3" />
                    Start AI Optimization
                  </LoadingButton>
                </div>
              </div>
            </motion.div>
          </>
        ) : (
          /* Results Section */
          <OptimizationResults result={optimizationState.result} />
        )}

        {/* Loading Overlay */}
        <LoadingOverlay 
          show={optimizationState.isRunning}
        >
          <div className="text-center">
            <div className="relative">
              <div className="w-24 h-24 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center mb-6">
                <Brain className="w-12 h-12 text-white" />
              </div>
              <div className="absolute inset-0 rounded-full border-4 border-blue-200">
                <div 
                  className="h-full rounded-full bg-gradient-to-r from-blue-600 to-purple-600 transition-all duration-500"
                  style={{ width: `${optimizationState.progress}%` }}
                />
              </div>
            </div>
            
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              AI Optimization in Progress
            </h3>
            <p className="text-gray-600 mb-4">
              {optimizationState.currentStep}
            </p>
            <div className="text-sm text-gray-500">
              {Math.round(optimizationState.progress)}% Complete
            </div>
          </div>
        </LoadingOverlay>
      </div>
    </DashboardLayout>
  )
}

// Results Component
function OptimizationResults({ result }: { result: any }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="space-y-8"
    >
      {/* Success Header */}
      <div className="card gradient-success text-white">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center mb-2">
              <Award className="w-8 h-8 mr-3" />
              <h2 className="text-2xl font-bold">Optimization Complete!</h2>
            </div>
            <p className="text-white/90">
              AI analysis identified {result.savings_percent.toFixed(1)}% energy savings potential
            </p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold mb-1">
              €{Math.round(result.cost_savings_eur).toLocaleString()}
            </div>
            <div className="text-white/90 text-sm">
              Annual savings potential
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <MetricGrid columns={4}>
        <MetricCard
          icon={<Brain className="w-8 h-8 text-blue-600" />}
          title="Model Accuracy"
          value={`${(result.accuracy * 100).toFixed(1)}%`}
          trend="positive"
          subtitle="R² Score"
        />
        <MetricCard
          icon={<TrendingUp className="w-8 h-8 text-green-600" />}
          title="Energy Savings"
          value={`${result.savings_percent.toFixed(1)}%`}
          trend="positive"
          subtitle="Consumption Reduction"
        />
        <MetricCard
          icon={<DollarSign className="w-8 h-8 text-emerald-600" />}
          title="Cost Savings"
          value={`€${Math.round(result.cost_savings_eur).toLocaleString()}`}
          trend="positive"
          subtitle="Annual Estimate"
        />
        <MetricCard
          icon={<Clock className="w-8 h-8 text-orange-600" />}
          title="Processing Time"
          value={`${result.processing_time.toFixed(1)}s`}
          subtitle="Analysis Duration"
        />
      </MetricGrid>

      {/* Detailed Results */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Predictions Chart */}
        <div className="card">
          <h3 className="text-xl font-bold text-gray-900 mb-6">
            Energy Predictions vs Actual
          </h3>
          <div className="h-64 flex items-center justify-center text-gray-500">
            Chart visualization would go here
          </div>
        </div>

        {/* Recommendations */}
        <div className="card">
          <h3 className="text-xl font-bold text-gray-900 mb-6">
            AI Recommendations
          </h3>
          <div className="space-y-4">
            {result.suggestions.map((category: any, index: number) => (
              <div key={index}>
                <h4 className="font-semibold text-gray-900 mb-2">
                  {category.category?.replace('_', ' ').toUpperCase()}
                </h4>
                <div className="space-y-2">
                  {category.suggestions?.map((suggestion: any, suggIndex: number) => (
                    <div key={suggIndex} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                      <ArrowRight className="w-4 h-4 text-blue-600 mt-1 flex-shrink-0" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {suggestion.action}
                        </p>
                        <p className="text-xs text-green-600 mt-1">
                          Estimated savings: {suggestion.estimated_savings_percent}%
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Next Steps
            </h3>
            <p className="text-gray-600 text-sm mt-1">
              Review recommendations and export your optimization report
            </p>
          </div>
          
          <div className="flex space-x-3">
            <button className="btn-secondary">
              <BarChart3 className="w-4 h-4 mr-2" />
              View Report
            </button>
            <button className="btn-primary">
              <Play className="w-4 h-4 mr-2" />
              Run New Optimization
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
