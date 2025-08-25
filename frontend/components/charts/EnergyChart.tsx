'use client'

import { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts'
import { TrendingUp, TrendingDown, BarChart3, LineChart as LineChartIcon, Activity } from 'lucide-react'

interface EnergyDataPoint {
  timestamp: string
  energy_consumption: number
  temperature?: number
  humidity?: number
  occupancy?: number
  hour?: number
  day_of_week?: number
  [key: string]: any
}

interface EnergyChartProps {
  data?: EnergyDataPoint[]
  type?: 'line' | 'area' | 'bar'
  showControls?: boolean
  height?: number
  className?: string
}

export default function EnergyChart({
  data = [],
  type = 'line',
  showControls = true,
  height = 400,
  className = ''
}: EnergyChartProps) {
  const [chartType, setChartType] = useState(type)
  const [timeRange, setTimeRange] = useState('all')
  const [showPrediction, setShowPrediction] = useState(false)

  // Process and filter data
  const processedData = useMemo(() => {
    if (!data || data.length === 0) {
      // Return sample data if no data provided
      return Array.from({ length: 24 }, (_, i) => ({
        timestamp: `${i.toString().padStart(2, '0')}:00`,
        energy_consumption: 45 + Math.sin(i / 24 * Math.PI * 2) * 15 + Math.random() * 10,
        temperature: 22 + Math.sin((i - 6) / 24 * Math.PI * 2) * 8,
        hour: i
      }))
    }

    let filteredData = [...data]

    // Apply time range filter
    if (timeRange !== 'all') {
      const now = new Date()
      const hoursBack = timeRange === '24h' ? 24 : timeRange === '7d' ? 168 : timeRange === '30d' ? 720 : 0
      
      if (hoursBack > 0) {
        const cutoff = new Date(now.getTime() - hoursBack * 60 * 60 * 1000)
        filteredData = data.filter(d => new Date(d.timestamp) >= cutoff)
      }
    }

    // Format data for recharts
    return filteredData.map((d, index) => ({
      ...d,
      formattedTime: formatTimeForChart(d.timestamp, index),
      predicted: showPrediction ? d.energy_consumption + (Math.random() - 0.5) * 5 : undefined
    }))
  }, [data, timeRange, showPrediction])

  // Calculate statistics
  const stats = useMemo(() => {
    if (processedData.length === 0) return null

    const values = processedData.map(d => d.energy_consumption)
    const avg = values.reduce((a, b) => a + b, 0) / values.length
    const max = Math.max(...values)
    const min = Math.min(...values)
    const trend = values.length > 1 ? values[values.length - 1] - values[0] : 0

    return { avg, max, min, trend }
  }, [processedData])

  const formatTimeForChart = (timestamp: string, index: number) => {
    try {
      const date = new Date(timestamp)
      if (isNaN(date.getTime())) {
        return `Point ${index + 1}`
      }
      
      if (timeRange === '24h') {
        return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
      } else if (timeRange === '7d') {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      }
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    } catch (error) {
      return `Point ${index + 1}`
    }
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
          <p className="text-sm font-medium text-gray-900 mb-2">{label}</p>
          {payload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center space-x-2 text-sm">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-gray-600">{entry.dataKey}:</span>
              <span className="font-medium text-gray-900">
                {entry.value?.toFixed(1)} kWh
              </span>
            </div>
          ))}
        </div>
      )
    }
    return null
  }

  const renderChart = () => {
    const commonProps = {
      data: processedData,
      height,
      margin: { top: 20, right: 30, left: 20, bottom: 5 }
    }

    switch (chartType) {
      case 'area':
        return (
          <ResponsiveContainer width="100%" height={height}>
            <AreaChart {...commonProps}>
              <defs>
                <linearGradient id="energyGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis 
                dataKey="formattedTime" 
                stroke="#64748b"
                fontSize={12}
                axisLine={false}
                tickLine={false}
              />
              <YAxis 
                stroke="#64748b"
                fontSize={12}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="energy_consumption"
                stroke="#3b82f6"
                strokeWidth={2}
                fill="url(#energyGradient)"
                name="Energy Consumption"
              />
              {showPrediction && (
                <Area
                  type="monotone"
                  dataKey="predicted"
                  stroke="#10b981"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  fill="none"
                  name="Predicted"
                />
              )}
            </AreaChart>
          </ResponsiveContainer>
        )

      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={height}>
            <BarChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis 
                dataKey="formattedTime" 
                stroke="#64748b"
                fontSize={12}
                axisLine={false}
                tickLine={false}
              />
              <YAxis 
                stroke="#64748b"
                fontSize={12}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar
                dataKey="energy_consumption"
                fill="#3b82f6"
                name="Energy Consumption"
                radius={[2, 2, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        )

      default:
        return (
          <ResponsiveContainer width="100%" height={height}>
            <LineChart {...commonProps}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis 
                dataKey="formattedTime" 
                stroke="#64748b"
                fontSize={12}
                axisLine={false}
                tickLine={false}
              />
              <YAxis 
                stroke="#64748b"
                fontSize={12}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip content={<CustomTooltip />} />
              
              {/* Average reference line */}
              {stats && (
                <ReferenceLine 
                  y={stats.avg} 
                  stroke="#9ca3af" 
                  strokeDasharray="2 2" 
                  label={{ value: 'Avg', position: 'insideTopRight' }}
                />
              )}
              
              <Line
                type="monotone"
                dataKey="energy_consumption"
                stroke="#3b82f6"
                strokeWidth={3}
                dot={false}
                activeDot={{ r: 6, fill: '#3b82f6' }}
                name="Energy Consumption"
              />
              
              {showPrediction && (
                <Line
                  type="monotone"
                  dataKey="predicted"
                  stroke="#10b981"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={false}
                  name="Predicted"
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        )
    }
  }

  if (!data && processedData.length === 0) {
    return (
      <div className={`bg-white rounded-2xl p-6 border border-gray-100 ${className}`}>
        <div className="text-center text-gray-500">
          <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <h3 className="text-lg font-medium mb-2">No Energy Data</h3>
          <p className="text-sm">Upload or generate data to see energy consumption analytics</p>
        </div>
      </div>
    )
  }

  return (
    <motion.div 
      className={`bg-white rounded-2xl border border-gray-100 ${className}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Header */}
      {showControls && (
        <div className="p-6 border-b border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                Energy Consumption
              </h3>
              <p className="text-sm text-gray-500">
                {processedData.length} data points
              </p>
            </div>

            {/* Stats */}
            {stats && (
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <div className="text-sm text-gray-500">Average</div>
                  <div className="font-semibold text-gray-900">
                    {stats.avg.toFixed(1)} kWh
                  </div>
                </div>
                
                <div className="text-right">
                  <div className="text-sm text-gray-500">Trend</div>
                  <div className={`font-semibold flex items-center ${
                    stats.trend >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {stats.trend >= 0 ? (
                      <TrendingUp className="w-4 h-4 mr-1" />
                    ) : (
                      <TrendingDown className="w-4 h-4 mr-1" />
                    )}
                    {Math.abs(stats.trend).toFixed(1)}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Controls */}
          <div className="flex flex-wrap items-center justify-between gap-4">
            {/* Chart Type */}
            <div className="flex items-center space-x-2">
              {[
                { type: 'line', icon: LineChartIcon, label: 'Line' },
                { type: 'area', icon: Activity, label: 'Area' },
                { type: 'bar', icon: BarChart3, label: 'Bar' }
              ].map(({ type: t, icon: Icon, label }) => (
                <button
                  key={t}
                  onClick={() => setChartType(t as any)}
                  className={`p-2 rounded-lg transition-colors ${
                    chartType === t
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-400 hover:text-gray-600 hover:bg-gray-50'
                  }`}
                  title={label}
                >
                  <Icon className="w-4 h-4" />
                </button>
              ))}
            </div>

            {/* Time Range */}
            <div className="flex items-center space-x-2">
              {[
                { value: '24h', label: '24H' },
                { value: '7d', label: '7D' },
                { value: '30d', label: '30D' },
                { value: 'all', label: 'All' }
              ].map(({ value, label }) => (
                <button
                  key={value}
                  onClick={() => setTimeRange(value)}
                  className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                    timeRange === value
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>

            {/* Prediction Toggle */}
            <label className="flex items-center space-x-2 text-sm">
              <input
                type="checkbox"
                checked={showPrediction}
                onChange={(e) => setShowPrediction(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-gray-600">Show Prediction</span>
            </label>
          </div>
        </div>
      )}

      {/* Chart */}
      <div className="p-6">
        {renderChart()}
      </div>
    </motion.div>
  )
}

// Compact chart for smaller spaces
interface CompactEnergyChartProps {
  data: EnergyDataPoint[]
  height?: number
  showValue?: boolean
}

export function CompactEnergyChart({ 
  data, 
  height = 200, 
  showValue = true 
}: CompactEnergyChartProps) {
  const processedData = data.slice(-12) // Show last 12 points

  const currentValue = data.length > 0 ? data[data.length - 1].energy_consumption : 0
  const previousValue = data.length > 1 ? data[data.length - 2].energy_consumption : 0
  const change = ((currentValue - previousValue) / previousValue * 100)

  return (
    <div className="bg-white rounded-lg p-4 border border-gray-100">
      {showValue && (
        <div className="flex items-center justify-between mb-3">
          <div>
            <div className="text-2xl font-bold text-gray-900">
              {currentValue.toFixed(1)} kWh
            </div>
            <div className="text-sm text-gray-500">Current Usage</div>
          </div>
          
          <div className={`text-sm font-medium ${
            change >= 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            {change >= 0 ? '+' : ''}{change.toFixed(1)}%
          </div>
        </div>
      )}

      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={processedData}>
          <defs>
            <linearGradient id="compactGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
            </linearGradient>
          </defs>
          <Area
            type="monotone"
            dataKey="energy_consumption"
            stroke="#3b82f6"
            strokeWidth={2}
            fill="url(#compactGradient)"
            dot={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
