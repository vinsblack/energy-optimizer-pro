'use client'

import { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import DashboardLayout from '@/components/layout/DashboardLayout'
import StatusIndicator from '@/components/ui/StatusIndicator'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { CompactEnergyChart } from '@/components/charts/EnergyChart'
import {
  Building,
  Plus,
  Search,
  Filter,
  MapPin,
  Users,
  Zap,
  TrendingUp,
  TrendingDown,
  Calendar,
  MoreVertical,
  Edit,
  Trash2,
  Eye,
  AlertTriangle,
  CheckCircle
} from 'lucide-react'

interface BuildingData {
  id: string
  name: string
  type: 'commercial' | 'residential' | 'industrial'
  location: string
  floorArea: number
  occupancy: number
  maxOccupancy: number
  energyConsumption: number
  monthlyConsumption: number[]
  efficiency: number
  lastOptimized: string
  status: 'online' | 'offline' | 'warning'
  savings: number
  alerts: number
}

// Mock data
const mockBuildings: BuildingData[] = [
  {
    id: '1',
    name: 'Corporate Headquarters',
    type: 'commercial',
    location: 'Rome, Italy',
    floorArea: 15000,
    occupancy: 450,
    maxOccupancy: 500,
    energyConsumption: 2847.5,
    monthlyConsumption: [2400, 2200, 2100, 1950, 1800, 1750, 1900, 2100, 2300, 2600, 2800, 2850],
    efficiency: 87.5,
    lastOptimized: '2 days ago',
    status: 'online',
    savings: 23.4,
    alerts: 0
  },
  {
    id: '2',
    name: 'Manufacturing Plant A',
    type: 'industrial',
    location: 'Milan, Italy',
    floorArea: 25000,
    occupancy: 180,
    maxOccupancy: 200,
    energyConsumption: 5240.8,
    monthlyConsumption: [5100, 4950, 4800, 4600, 4400, 4350, 4500, 4700, 4900, 5200, 5400, 5250],
    efficiency: 78.2,
    lastOptimized: '1 week ago',
    status: 'warning',
    savings: 18.7,
    alerts: 2
  },
  {
    id: '3',
    name: 'Residential Complex B',
    type: 'residential',
    location: 'Naples, Italy',
    floorArea: 8500,
    occupancy: 140,
    maxOccupancy: 150,
    energyConsumption: 1650.3,
    monthlyConsumption: [1700, 1600, 1500, 1400, 1300, 1250, 1350, 1450, 1550, 1650, 1750, 1650],
    efficiency: 92.1,
    lastOptimized: '3 days ago',
    status: 'online',
    savings: 28.9,
    alerts: 0
  },
  {
    id: '4',
    name: 'Tech Campus',
    type: 'commercial',
    location: 'Florence, Italy',
    floorArea: 12000,
    occupancy: 320,
    maxOccupancy: 400,
    energyConsumption: 2156.7,
    monthlyConsumption: [2100, 1950, 1800, 1650, 1500, 1450, 1600, 1800, 2000, 2200, 2300, 2150],
    efficiency: 83.4,
    lastOptimized: '5 days ago',
    status: 'online',
    savings: 21.2,
    alerts: 1
  },
  {
    id: '5',
    name: 'Warehouse District',
    type: 'industrial',
    location: 'Turin, Italy',
    floorArea: 18000,
    occupancy: 85,
    maxOccupancy: 100,
    energyConsumption: 3420.1,
    monthlyConsumption: [3300, 3200, 3100, 2950, 2800, 2750, 2900, 3100, 3250, 3400, 3500, 3420],
    efficiency: 74.8,
    lastOptimized: '2 weeks ago',
    status: 'offline',
    savings: 15.3,
    alerts: 3
  }
]

export default function BuildingsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState<'all' | 'commercial' | 'residential' | 'industrial'>('all')
  const [filterStatus, setFilterStatus] = useState<'all' | 'online' | 'offline' | 'warning'>('all')
  const [sortBy, setSortBy] = useState<'name' | 'consumption' | 'efficiency' | 'savings'>('name')
  const [selectedBuilding, setSelectedBuilding] = useState<BuildingData | null>(null)
  const [showDetails, setShowDetails] = useState(false)

  // Filter and sort buildings
  const filteredBuildings = useMemo(() => {
    let filtered = mockBuildings.filter(building => {
      const matchesSearch = building.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          building.location.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesType = filterType === 'all' || building.type === filterType
      const matchesStatus = filterStatus === 'all' || building.status === filterStatus
      
      return matchesSearch && matchesType && matchesStatus
    })

    // Sort buildings
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'consumption':
          return b.energyConsumption - a.energyConsumption
        case 'efficiency':
          return b.efficiency - a.efficiency
        case 'savings':
          return b.savings - a.savings
        default:
          return a.name.localeCompare(b.name)
      }
    })

    return filtered
  }, [searchTerm, filterType, filterStatus, sortBy])

  const getBuildingTypeColor = (type: string) => {
    switch (type) {
      case 'commercial':
        return 'text-blue-700 bg-blue-100'
      case 'residential':
        return 'text-green-700 bg-green-100'
      case 'industrial':
        return 'text-purple-700 bg-purple-100'
      default:
        return 'text-gray-700 bg-gray-100'
    }
  }

  const getEfficiencyColor = (efficiency: number) => {
    if (efficiency >= 85) return 'text-green-600'
    if (efficiency >= 75) return 'text-yellow-600'
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
                Building Management
              </h1>
              <p className="text-gray-600 mt-2">
                Monitor and manage your building portfolio energy performance
              </p>
            </div>
            
            <button className="btn-primary">
              <Plus className="w-5 h-5 mr-2" />
              Add Building
            </button>
          </div>
        </motion.div>

        {/* Stats Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="card text-center">
              <Building className="w-8 h-8 text-blue-600 mx-auto mb-3" />
              <div className="text-2xl font-bold text-gray-900 mb-1">
                {mockBuildings.length}
              </div>
              <div className="text-sm text-gray-600">Total Buildings</div>
            </div>
            
            <div className="card text-center">
              <Zap className="w-8 h-8 text-green-600 mx-auto mb-3" />
              <div className="text-2xl font-bold text-gray-900 mb-1">
                {mockBuildings.reduce((sum, b) => sum + b.energyConsumption, 0).toFixed(0)}
              </div>
              <div className="text-sm text-gray-600">Total kWh</div>
            </div>
            
            <div className="card text-center">
              <TrendingUp className="w-8 h-8 text-emerald-600 mx-auto mb-3" />
              <div className="text-2xl font-bold text-gray-900 mb-1">
                {(mockBuildings.reduce((sum, b) => sum + b.savings, 0) / mockBuildings.length).toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600">Avg Savings</div>
            </div>
            
            <div className="card text-center">
              <AlertTriangle className="w-8 h-8 text-orange-600 mx-auto mb-3" />
              <div className="text-2xl font-bold text-gray-900 mb-1">
                {mockBuildings.reduce((sum, b) => sum + b.alerts, 0)}
              </div>
              <div className="text-sm text-gray-600">Active Alerts</div>
            </div>
          </div>
        </motion.div>

        {/* Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <div className="card">
            <div className="flex flex-wrap items-center justify-between gap-4">
              {/* Search */}
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search buildings..."
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
                  <option value="commercial">Commercial</option>
                  <option value="residential">Residential</option>
                  <option value="industrial">Industrial</option>
                </select>

                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value as any)}
                  className="select"
                >
                  <option value="all">All Status</option>
                  <option value="online">Online</option>
                  <option value="warning">Warning</option>
                  <option value="offline">Offline</option>
                </select>

                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="select"
                >
                  <option value="name">Sort by Name</option>
                  <option value="consumption">Sort by Consumption</option>
                  <option value="efficiency">Sort by Efficiency</option>
                  <option value="savings">Sort by Savings</option>
                </select>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Buildings Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            <AnimatePresence mode="popLayout">
              {filteredBuildings.map((building, index) => (
                <motion.div
                  key={building.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  className="card-hover cursor-pointer"
                  onClick={() => {
                    setSelectedBuilding(building)
                    setShowDetails(true)
                  }}
                >
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 mb-1">
                        {building.name}
                      </h3>
                      <div className="flex items-center text-sm text-gray-500">
                        <MapPin className="w-4 h-4 mr-1" />
                        {building.location}
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <StatusIndicator status={building.status} showLabel={false} />
                      <button 
                        className="p-1 hover:bg-gray-100 rounded"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <MoreVertical className="w-4 h-4 text-gray-400" />
                      </button>
                    </div>
                  </div>

                  {/* Building Type */}
                  <div className="mb-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getBuildingTypeColor(building.type)}`}>
                      {building.type.charAt(0).toUpperCase() + building.type.slice(1)}
                    </span>
                  </div>

                  {/* Metrics */}
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <div className="text-sm text-gray-500">Energy Usage</div>
                      <div className="text-xl font-bold text-gray-900">
                        {building.energyConsumption.toLocaleString()}
                      </div>
                      <div className="text-xs text-gray-500">kWh/month</div>
                    </div>
                    
                    <div>
                      <div className="text-sm text-gray-500">Efficiency</div>
                      <div className={`text-xl font-bold ${getEfficiencyColor(building.efficiency)}`}>
                        {building.efficiency}%
                      </div>
                      <div className="text-xs text-gray-500">Performance</div>
                    </div>
                  </div>

                  {/* Mini Chart */}
                  <div className="mb-4">
                    <CompactEnergyChart 
                      data={building.monthlyConsumption.map((consumption, index) => ({
                        timestamp: `Month ${index + 1}`,
                        energy_consumption: consumption
                      }))}
                      height={60}
                      showValue={false}
                    />
                  </div>

                  {/* Footer */}
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center text-gray-500">
                      <Users className="w-4 h-4 mr-1" />
                      {building.occupancy}/{building.maxOccupancy}
                    </div>
                    
                    <div className={`font-medium ${building.savings > 20 ? 'text-green-600' : building.savings > 15 ? 'text-yellow-600' : 'text-red-600'}`}>
                      {building.savings > 0 ? '+' : ''}{building.savings}% savings
                    </div>
                  </div>

                  {/* Alerts */}
                  {building.alerts > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <div className="flex items-center text-sm text-orange-600">
                        <AlertTriangle className="w-4 h-4 mr-1" />
                        {building.alerts} alert{building.alerts > 1 ? 's' : ''}
                      </div>
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </motion.div>

        {/* Building Details Modal */}
        <AnimatePresence>
          {showDetails && selectedBuilding && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
              onClick={() => setShowDetails(false)}
            >
              <motion.div
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.95, opacity: 0 }}
                className="bg-white rounded-2xl p-6 max-w-4xl max-h-[90vh] overflow-y-auto m-4"
                onClick={(e) => e.stopPropagation()}
              >
                <BuildingDetailsModal 
                  building={selectedBuilding}
                  onClose={() => setShowDetails(false)}
                />
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </DashboardLayout>
  )
}

// Building Details Modal Component
function BuildingDetailsModal({ 
  building, 
  onClose 
}: { 
  building: BuildingData
  onClose: () => void 
}) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            {building.name}
          </h2>
          <div className="flex items-center mt-2 space-x-4">
            <div className="flex items-center text-gray-600">
              <MapPin className="w-4 h-4 mr-1" />
              {building.location}
            </div>
            <StatusIndicator status={building.status} showIcon />
          </div>
        </div>
        
        <div className="flex space-x-2">
          <button className="btn-secondary btn-sm">
            <Edit className="w-4 h-4 mr-2" />
            Edit
          </button>
          <button 
            onClick={onClose}
            className="btn-secondary btn-sm"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 rounded-lg p-4 text-center">
          <Building className="w-8 h-8 text-blue-600 mx-auto mb-2" />
          <div className="text-2xl font-bold text-gray-900">
            {building.floorArea.toLocaleString()}
          </div>
          <div className="text-sm text-gray-600">Floor Area (m²)</div>
        </div>

        <div className="bg-green-50 rounded-lg p-4 text-center">
          <Users className="w-8 h-8 text-green-600 mx-auto mb-2" />
          <div className="text-2xl font-bold text-gray-900">
            {building.occupancy}/{building.maxOccupancy}
          </div>
          <div className="text-sm text-gray-600">Occupancy</div>
        </div>

        <div className="bg-purple-50 rounded-lg p-4 text-center">
          <Zap className="w-8 h-8 text-purple-600 mx-auto mb-2" />
          <div className="text-2xl font-bold text-gray-900">
            {building.energyConsumption.toLocaleString()}
          </div>
          <div className="text-sm text-gray-600">kWh/month</div>
        </div>

        <div className="bg-emerald-50 rounded-lg p-4 text-center">
          <TrendingUp className="w-8 h-8 text-emerald-600 mx-auto mb-2" />
          <div className="text-2xl font-bold text-gray-900">
            {building.savings}%
          </div>
          <div className="text-sm text-gray-600">Savings</div>
        </div>
      </div>

      {/* Energy Chart */}
      <div className="bg-white border border-gray-200 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Monthly Energy Consumption
        </h3>
        <CompactEnergyChart 
          data={building.monthlyConsumption.map((consumption, index) => ({
            timestamp: `Month ${index + 1}`,
            energy_consumption: consumption
          }))}
          height={200}
        />
      </div>

      {/* Additional Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">
            Building Information
          </h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Type:</span>
              <span className="font-medium capitalize">{building.type}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Efficiency Rating:</span>
              <span className={`font-medium ${getEfficiencyColor(building.efficiency)}`}>
                {building.efficiency}%
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Last Optimized:</span>
              <span className="font-medium">{building.lastOptimized}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Active Alerts:</span>
              <span className={`font-medium ${building.alerts > 0 ? 'text-orange-600' : 'text-green-600'}`}>
                {building.alerts}
              </span>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">
            Quick Actions
          </h3>
          <div className="space-y-2">
            <button className="w-full btn-primary justify-start">
              <Play className="w-4 h-4 mr-2" />
              Run Optimization
            </button>
            <button className="w-full btn-secondary justify-start">
              <Eye className="w-4 h-4 mr-2" />
              View Analytics
            </button>
            <button className="w-full btn-secondary justify-start">
              <Calendar className="w-4 h-4 mr-2" />
              Schedule Maintenance
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

function getEfficiencyColor(efficiency: number): string {
  if (efficiency >= 85) return 'text-green-600'
  if (efficiency >= 75) return 'text-yellow-600'
  return 'text-red-600'
}
