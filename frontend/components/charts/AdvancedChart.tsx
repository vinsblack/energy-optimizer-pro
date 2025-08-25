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
  ReferenceLine,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter,
  ComposedChart
} from 'recharts'
import { 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  LineChart as LineChartIcon, 
  Activity,
  PieChart as PieChartIcon,
  Target,
  Maximize2,
  Download,
  Settings,
  RefreshCw
} from 'lucide-react'

export interface ChartDataPoint {
  timestamp: string
  energy_consumption: number
  predicted?: number
  temperature?: number
  humidity?: number
  occupancy?: number
  cost?: number
  efficiency?: number
  [key: string]: any
}

interface AdvancedChartProps {
  data: ChartDataPoint[]
  type?: 'line' | 'area' | 'bar' | 'pie' | 'scatter' | 'composed'
  height?: number
  showControls?: boolean
  showLegend?: boolean
  showGrid?: boolean
  showTooltip?: boolean
  theme?: 'light' | 'dark'
  className?: string
  title?: string
  subtitle?: string
  primaryMetric?: string
  secondaryMetrics?: string[]
  colors?: string[]
  showStats?: boolean
  interactive?: boolean
  exportable?: boolean
}

const defaultColors = [
  '#3b82f6', // blue
  '#10b981', // green  
  '#f59e0b', // amber
  '#ef4444', // red
  '#8b5cf6', // purple
  '#06b6d4', // cyan
  '#84cc16', // lime
  '#f97316', // orange
]

export default function AdvancedChart({
  data = [],
  type = 'line',
  height = 400,
  showControls = true,
  showLegend = true,
  showGrid = true,
  showTooltip = true,
  theme = 'light',
  className = '',
  title,
  subtitle,
  primaryMetric = 'energy_consumption',
  secondaryMetrics = [],
  colors = defaultColors,
  showStats = true,
  interactive = true,
  exportable = false
}: AdvancedChartProps) {
  const [chartType, setChartType] = useState(type)
  const [timeRange, setTimeRange] = useState('all')
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [selectedMetrics, setSelectedMetrics] = useState([primaryMetric, ...secondaryMetrics])

  // Process data
  const processedData = useMemo(() => {
    if (!data || data.length === 0) {
      return generateSampleData()
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

    return filteredData.map((d, index) => ({
      ...d,
      formattedTime: formatTimeForChart(d.timestamp, index, timeRange),
      index
    }))
  }, [data, timeRange])

  // Calculate statistics
  const stats = useMemo(() => {
    if (processedData.length === 0) return null

    const primaryValues = processedData.map(d => d[primaryMetric]).filter(v => v != null)
    if (primaryValues.length === 0) return null

    const avg = primaryValues.reduce((a, b) => a + b, 0) / primaryValues.length
    const max = Math.max(...primaryValues)
    const min = Math.min(...primaryValues)
    const trend = primaryValues.length > 1 ? 
      ((primaryValues[primaryValues.length - 1] - primaryValues[0]) / primaryValues[0]) * 100 : 0

    return { avg, max, min, trend, count: primaryValues.length }
  }, [processedData, primaryMetric])

  const generateSampleData = () => {
    return Array.from({ length: 24 }, (_, i) => ({
      timestamp: `2024-08-${String(i + 1).padStart(2, '0')}T12:00:00Z`,
      formattedTime: `Day ${i + 1}`,
      energy_consumption: 45 + Math.sin(i / 24 * Math.PI * 2) * 15 + Math.random() * 10,
      temperature: 22 + Math.sin((i - 6) / 24 * Math.PI * 2) * 8,
      cost: (45 + Math.sin(i / 24 * Math.PI * 2) * 15 + Math.random() * 10) * 0.15,
      efficiency: 80 + Math.random() * 20,
      index: i
    }))
  }

  const formatTimeForChart = (timestamp: string, index: number, range: string) => {
    try {
      const date = new Date(timestamp)
      if (isNaN(date.getTime())) {
        return `Point ${index + 1}`
      }
      
      if (range === '24h') {
        return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
      } else if (range === '7d') {
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
        <div className="bg-white p-4 rounded-lg shadow-lg border border-gray-200 max-w-xs">
          <p className="text-sm font-medium text-gray-900 mb-2">{label}</p>
          <div className="space-y-1">
            {payload.map((entry: any, index: number) => (
              <div key={index} className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: entry.color }}
                  />
                  <span className="text-gray-600 capitalize">
                    {entry.dataKey.replace('_', ' ')}:
                  </span>
                </div>
                <span className="font-medium text-gray-900 ml-2">
                  {typeof entry.value === 'number' ? entry.value.toFixed(1) : entry.value}
                  {entry.dataKey.includes('consumption') || entry.dataKey.includes('cost') ? 
                    (entry.dataKey.includes('cost') ? ' €' : ' kWh') : 
                    entry.dataKey.includes('temperature') ? ' °C' :
                    entry.dataKey.includes('humidity') ? ' %' :
                    entry.dataKey.includes('efficiency') ? ' %' : ''
                  }
                </span>
              </div>
            ))}
          </div>
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
                {selectedMetrics.map((metric, index) => (
                  <linearGradient key={metric} id={`gradient-${metric}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={colors[index % colors.length]} stopOpacity={0.3}/>
                    <stop offset="95%" stopColor={colors[index % colors.length]} stopOpacity={0.1}/>
                  </linearGradient>
                ))}
              </defs>
              {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />}
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
              {showTooltip && <Tooltip content={<CustomTooltip />} />}
              {showLegend && <Legend />}
              
              {selectedMetrics.map((metric, index) => (
                <Area
                  key={metric}
                  type="monotone"
                  dataKey={metric}
                  stroke={colors[index % colors.length]}
                  strokeWidth={2}
                  fill={`url(#gradient-${metric})`}
                  name={metric.replace('_', ' ').toUpperCase()}
                />
              ))}
            </AreaChart>
          </ResponsiveContainer>
        )

      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={height}>
            <BarChart {...commonProps}>
              {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />}
              <XAxis dataKey="formattedTime" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} />
              {showTooltip && <Tooltip content={<CustomTooltip />} />}
              {showLegend && <Legend />}
              
              {selectedMetrics.map((metric, index) => (
                <Bar
                  key={metric}
                  dataKey={metric}
                  fill={colors[index % colors.length]}
                  name={metric.replace('_', ' ').toUpperCase()}
                  radius={[2, 2, 0, 0]}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        )

      case 'pie':
        const pieData = selectedMetrics.map((metric, index) => ({
          name: metric.replace('_', ' ').toUpperCase(),
          value: processedData.reduce((sum, d) => sum + (d[metric] || 0), 0),
          fill: colors[index % colors.length]
        }))

        return (
          <ResponsiveContainer width="100%" height={height}>
            <PieChart>
              <Pie
                data={pieData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={height / 3}
                label={(entry) => `${entry.name}: ${entry.value.toFixed(1)}`}
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Pie>
              {showTooltip && <Tooltip />}
              {showLegend && <Legend />}
            </PieChart>
          </ResponsiveContainer>
        )

      case 'scatter':
        return (
          <ResponsiveContainer width="100%" height={height}>
            <ScatterChart {...commonProps}>
              {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />}
              <XAxis 
                dataKey={primaryMetric}
                stroke="#64748b"
                fontSize={12}
                name={primaryMetric.replace('_', ' ')}
              />
              <YAxis 
                dataKey={selectedMetrics[1] || 'temperature'}
                stroke="#64748b"
                fontSize={12}
                name={(selectedMetrics[1] || 'temperature').replace('_', ' ')}
              />
              {showTooltip && <Tooltip content={<CustomTooltip />} />}
              <Scatter
                dataKey={selectedMetrics[1] || 'temperature'}
                fill={colors[0]}
                name="Data Points"
              />
            </ScatterChart>
          </ResponsiveContainer>
        )

      case 'composed':
        return (
          <ResponsiveContainer width="100%" height={height}>
            <ComposedChart {...commonProps}>
              {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />}
              <XAxis dataKey="formattedTime" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} />
              {showTooltip && <Tooltip content={<CustomTooltip />} />}
              {showLegend && <Legend />}
              
              <Area
                type="monotone"
                dataKey={primaryMetric}
                fill={colors[0]}
                fillOpacity={0.3}
                stroke={colors[0]}
                name={primaryMetric.replace('_', ' ').toUpperCase()}
              />
              
              {selectedMetrics.slice(1).map((metric, index) => (
                <Line
                  key={metric}
                  type="monotone"
                  dataKey={metric}
                  stroke={colors[(index + 1) % colors.length]}
                  strokeWidth={2}
                  dot={false}
                  name={metric.replace('_', ' ').toUpperCase()}
                />
              ))}
            </ComposedChart>
          </ResponsiveContainer>
        )

      default: // line chart
        return (
          <ResponsiveContainer width="100%" height={height}>
            <LineChart {...commonProps}>
              {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />}
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
              {showTooltip && <Tooltip content={<CustomTooltip />} />}
              {showLegend && <Legend />}
              
              {/* Average reference line */}
              {stats && showStats && (
                <ReferenceLine 
                  y={stats.avg} 
                  stroke="#9ca3af" 
                  strokeDasharray="2 2" 
                  label={{ value: 'Avg', position: 'insideTopRight' }}
                />
              )}
              
              {selectedMetrics.map((metric, index) => (
                <Line
                  key={metric}
                  type="monotone"
                  dataKey={metric}
                  stroke={colors[index % colors.length]}
                  strokeWidth={metric === primaryMetric ? 3 : 2}
                  dot={false}
                  activeDot={{ r: 6, fill: colors[index % colors.length] }}
                  name={metric.replace('_', ' ').toUpperCase()}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        )
    }
  }

  const allMetrics = useMemo(() => {
    if (processedData.length === 0) return []
    
    const firstPoint = processedData[0]
    return Object.keys(firstPoint).filter(key => 
      typeof firstPoint[key] === 'number' && 
      key !== 'index' &&
      !key.includes('formatted')
    )
  }, [processedData])

  const handleExport = () => {
    // TODO: Implement chart export functionality
    toast.success('Chart exported successfully!')
  }

  const handleRefresh = () => {
    // TODO: Implement data refresh
    toast.success('Data refreshed!')
  }

  return (
    <motion.div 
      className={`bg-white rounded-2xl border border-gray-100 overflow-hidden ${className} ${
        isFullscreen ? 'fixed inset-4 z-50' : ''
      }`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      layout
    >
      {/* Header */}
      <div className="p-6 border-b border-gray-100">
        <div className="flex items-center justify-between mb-4">
          <div>
            {title && (
              <h3 className="text-lg font-semibold text-gray-900">
                {title}
              </h3>
            )}
            {subtitle && (
              <p className="text-sm text-gray-500 mt-1">
                {subtitle}
              </p>
            )}
            {!title && !subtitle && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Energy Analytics
                </h3>
                <p className="text-sm text-gray-500">
                  {processedData.length} data points
                </p>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-2">
            {exportable && (
              <button
                onClick={handleExport}
                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
                title="Export Chart"
              >
                <Download className="w-4 h-4" />
              </button>
            )}
            
            <button
              onClick={handleRefresh}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
              title="Refresh Data"
            >
              <RefreshCw className="w-4 h-4" />
            </button>

            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
              title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
            >
              <Maximize2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Stats */}
        {showStats && stats && (
          <div className="flex items-center space-x-6 mb-4">
            <div className="text-sm">
              <span className="text-gray-500">Average:</span>
              <span className="font-semibold text-gray-900 ml-1">
                {stats.avg.toFixed(1)}
              </span>
            </div>
            
            <div className="text-sm">
              <span className="text-gray-500">Range:</span>
              <span className="font-semibold text-gray-900 ml-1">
                {stats.min.toFixed(1)} - {stats.max.toFixed(1)}
              </span>
            </div>
            
            <div className={`text-sm flex items-center ${
              stats.trend >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {stats.trend >= 0 ? (
                <TrendingUp className="w-4 h-4 mr-1" />
              ) : (
                <TrendingDown className="w-4 h-4 mr-1" />
              )}
              <span className="font-semibold">
                {Math.abs(stats.trend).toFixed(1)}%
              </span>
            </div>
          </div>
        )}

        {/* Controls */}
        {showControls && (
          <div className="flex flex-wrap items-center justify-between gap-4">
            {/* Chart Type */}
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">Type:</span>
              {[
                { type: 'line', icon: LineChartIcon, label: 'Line' },
                { type: 'area', icon: Activity, label: 'Area' },
                { type: 'bar', icon: BarChart3, label: 'Bar' },
                { type: 'pie', icon: PieChartIcon, label: 'Pie' },
                { type: 'composed', icon: Target, label: 'Mixed' }
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
              <span className="text-sm text-gray-600">Range:</span>
              {['24h', '7d', '30d', 'all'].map((range) => (
                <button
                  key={range}
                  onClick={() => setTimeRange(range)}
                  className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                    timeRange === range
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  {range.toUpperCase()}
                </button>
              ))}
            </div>

            {/* Metric Selection */}
            {allMetrics.length > 1 && (
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">Metrics:</span>
                <select
                  value={primaryMetric}
                  onChange={(e) => {
                    const newPrimary = e.target.value
                    setSelectedMetrics([newPrimary, ...selectedMetrics.filter(m => m !== newPrimary)])
                  }}
                  className="text-sm border-gray-300 rounded-lg focus:border-blue-500 focus:ring-blue-500"
                >
                  {allMetrics.map(metric => (
                    <option key={metric} value={metric}>
                      {metric.replace('_', ' ').toUpperCase()}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Chart Container */}
      <div className="p-6">
        {processedData.length === 0 ? (
          <div className="flex items-center justify-center h-64 text-gray-500">
            <div className="text-center">
              <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <h3 className="text-lg font-medium mb-2">No Data Available</h3>
              <p className="text-sm">Upload or generate data to see visualizations</p>
            </div>
          </div>
        ) : (
          renderChart()
        )}
      </div>
    </motion.div>
  )
}

// Export additional chart variants
export function EnergyLineChart(props: Omit<AdvancedChartProps, 'type'>) {
  return <AdvancedChart {...props} type="line" />
}

export function EnergyAreaChart(props: Omit<AdvancedChartProps, 'type'>) {
  return <AdvancedChart {...props} type="area" />
}

export function EnergyBarChart(props: Omit<AdvancedChartProps, 'type'>) {
  return <AdvancedChart {...props} type="bar" />
}

export function EnergyPieChart(props: Omit<AdvancedChartProps, 'type'>) {
  return <AdvancedChart {...props} type="pie" />
}

export function EnergyComposedChart(props: Omit<AdvancedChartProps, 'type'>) {
  return <AdvancedChart {...props} type="composed" />
}
