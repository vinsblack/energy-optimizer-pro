'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import DashboardLayout from '@/components/layout/DashboardLayout'
import { Input, Select, Checkbox, FormGroup } from '@/components/forms/FormComponents'
import LoadingButton from '@/components/ui/LoadingSpinner'
import StatusIndicator from '@/components/ui/StatusIndicator'
import { toast } from 'react-hot-toast'
import {
  Settings,
  User,
  Bell,
  Shield,
  Database,
  Cpu,
  Palette,
  Globe,
  Save,
  RotateCcw,
  Download,
  Upload,
  Key,
  Mail,
  Smartphone,
  Monitor,
  Sun,
  Moon,
  Zap,
  Building,
  DollarSign,
  Languages
} from 'lucide-react'

interface SettingsTab {
  id: string
  label: string
  icon: React.ReactNode
  description: string
}

const settingsTabs: SettingsTab[] = [
  {
    id: 'profile',
    label: 'Profile',
    icon: <User className="w-5 h-5" />,
    description: 'Personal information and preferences'
  },
  {
    id: 'notifications',
    label: 'Notifications',
    icon: <Bell className="w-5 h-5" />,
    description: 'Alert and notification preferences'
  },
  {
    id: 'system',
    label: 'System',
    icon: <Cpu className="w-5 h-5" />,
    description: 'System configuration and performance'
  },
  {
    id: 'security',
    label: 'Security',
    icon: <Shield className="w-5 h-5" />,
    description: 'Security settings and access control'
  },
  {
    id: 'api',
    label: 'API',
    icon: <Database className="w-5 h-5" />,
    description: 'API configuration and endpoints'
  },
  {
    id: 'appearance',
    label: 'Appearance',
    icon: <Palette className="w-5 h-5" />,
    description: 'Theme and display preferences'
  }
]

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('profile')
  const [isSaving, setIsSaving] = useState(false)
  const [hasChanges, setHasChanges] = useState(false)

  // Settings state
  const [settings, setSettings] = useState({
    // Profile
    profile: {
      firstName: 'Admin',
      lastName: 'User',
      email: 'admin@energyoptimizer.com',
      phone: '+39 123 456 7890',
      company: 'Energy Optimizer Pro',
      role: 'Energy Analyst',
      timezone: 'Europe/Rome',
      language: 'en'
    },
    
    // Notifications
    notifications: {
      emailAlerts: true,
      smsAlerts: false,
      browserNotifications: true,
      weeklyReports: true,
      systemAlerts: true,
      optimizationCompleted: true,
      thresholdAlerts: true,
      maintenanceAlerts: true
    },
    
    // System
    system: {
      defaultAlgorithm: 'xgboost',
      maxConcurrentJobs: 5,
      dataRetentionDays: 365,
      autoOptimization: false,
      cachingEnabled: true,
      analyticsEnabled: true,
      debugMode: false,
      performanceMode: 'balanced'
    },
    
    // Security
    security: {
      twoFactorEnabled: false,
      sessionTimeout: 8,
      passwordExpiry: 90,
      loginNotifications: true,
      apiKeyRotation: true,
      auditLogging: true,
      ipWhitelist: ''
    },
    
    // API
    api: {
      baseUrl: 'http://localhost:8000',
      timeout: 30,
      retryAttempts: 3,
      rateLimit: 100,
      enableCaching: true,
      compressionEnabled: true,
      apiKey: '••••••••••••••••'
    },
    
    // Appearance
    appearance: {
      theme: 'light',
      primaryColor: 'blue',
      compactMode: false,
      animations: true,
      reducedMotion: false,
      fontSize: 'medium',
      sidebarExpanded: true
    }
  })

  const handleSave = async () => {
    setIsSaving(true)
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      toast.success('Settings saved successfully!')
      setHasChanges(false)
    } catch (error) {
      toast.error('Failed to save settings')
    } finally {
      setIsSaving(false)
    }
  }

  const handleReset = () => {
    // Reset to defaults
    toast.success('Settings reset to defaults')
    setHasChanges(false)
  }

  const updateSetting = (section: string, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section as keyof typeof prev],
        [key]: value
      }
    }))
    setHasChanges(true)
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'profile':
        return <ProfileSettings settings={settings.profile} updateSetting={(key, value) => updateSetting('profile', key, value)} />
      case 'notifications':
        return <NotificationSettings settings={settings.notifications} updateSetting={(key, value) => updateSetting('notifications', key, value)} />
      case 'system':
        return <SystemSettings settings={settings.system} updateSetting={(key, value) => updateSetting('system', key, value)} />
      case 'security':
        return <SecuritySettings settings={settings.security} updateSetting={(key, value) => updateSetting('security', key, value)} />
      case 'api':
        return <ApiSettings settings={settings.api} updateSetting={(key, value) => updateSetting('api', key, value)} />
      case 'appearance':
        return <AppearanceSettings settings={settings.appearance} updateSetting={(key, value) => updateSetting('appearance', key, value)} />
      default:
        return null
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
                Settings
              </h1>
              <p className="text-gray-600 mt-2">
                Configure your Energy Optimizer Pro preferences and system settings
              </p>
            </div>
            
            <div className="flex space-x-3">
              <button 
                onClick={handleReset}
                className="btn-secondary"
                disabled={!hasChanges}
              >
                <RotateCcw className="w-4 h-4 mr-2" />
                Reset
              </button>
              
              <LoadingButton
                onClick={handleSave}
                loading={isSaving}
                disabled={!hasChanges}
                className="btn-primary"
              >
                <Save className="w-4 h-4 mr-2" />
                Save Changes
              </LoadingButton>
            </div>
          </div>
        </motion.div>

        {/* Settings Interface */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar Navigation */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <div className="card">
              <nav className="space-y-1">
                {settingsTabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-start space-x-3 px-3 py-3 text-left rounded-lg transition-all duration-200 ${
                      activeTab === tab.id
                        ? 'bg-blue-50 text-blue-700 border-r-4 border-blue-700'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <div className={`flex-shrink-0 ${activeTab === tab.id ? 'text-blue-600' : 'text-gray-400'}`}>
                      {tab.icon}
                    </div>
                    <div>
                      <div className="font-medium">
                        {tab.label}
                      </div>
                      <div className="text-xs text-gray-500 mt-0.5">
                        {tab.description}
                      </div>
                    </div>
                  </button>
                ))}
              </nav>
            </div>
          </motion.div>

          {/* Settings Content */}
          <motion.div
            className="lg:col-span-3"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <div className="card">
              {renderTabContent()}
            </div>
          </motion.div>
        </div>
      </div>
    </DashboardLayout>
  )
}

// Profile Settings Component
function ProfileSettings({ settings, updateSetting }: any) {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">Profile Settings</h2>
        <p className="text-gray-600">Manage your personal information and preferences</p>
      </div>

      <FormGroup title="Personal Information">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Input
            label="First Name"
            value={settings.firstName}
            onChange={(e) => updateSetting('firstName', e.target.value)}
            icon={<User />}
          />
          <Input
            label="Last Name"
            value={settings.lastName}
            onChange={(e) => updateSetting('lastName', e.target.value)}
            icon={<User />}
          />
          <Input
            label="Email Address"
            type="email"
            value={settings.email}
            onChange={(e) => updateSetting('email', e.target.value)}
            icon={<Mail />}
          />
          <Input
            label="Phone Number"
            type="tel"
            value={settings.phone}
            onChange={(e) => updateSetting('phone', e.target.value)}
            icon={<Smartphone />}
          />
        </div>
      </FormGroup>

      <FormGroup title="Organization">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Input
            label="Company"
            value={settings.company}
            onChange={(e) => updateSetting('company', e.target.value)}
            icon={<Building />}
          />
          <Input
            label="Role"
            value={settings.role}
            onChange={(e) => updateSetting('role', e.target.value)}
            icon={<User />}
          />
        </div>
      </FormGroup>

      <FormGroup title="Localization">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Select
            label="Timezone"
            value={settings.timezone}
            onChange={(e) => updateSetting('timezone', e.target.value)}
            icon={<Globe />}
            options={[
              { value: 'Europe/Rome', label: 'Europe/Rome (GMT+1)' },
              { value: 'Europe/London', label: 'Europe/London (GMT+0)' },
              { value: 'America/New_York', label: 'America/New_York (GMT-5)' },
              { value: 'Asia/Tokyo', label: 'Asia/Tokyo (GMT+9)' }
            ]}
          />
          <Select
            label="Language"
            value={settings.language}
            onChange={(e) => updateSetting('language', e.target.value)}
            icon={<Languages />}
            options={[
              { value: 'en', label: 'English' },
              { value: 'it', label: 'Italiano' },
              { value: 'es', label: 'Español' },
              { value: 'fr', label: 'Français' }
            ]}
          />
        </div>
      </FormGroup>
    </div>
  )
}

// Notification Settings Component
function NotificationSettings({ settings, updateSetting }: any) {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">Notification Settings</h2>
        <p className="text-gray-600">Control how and when you receive notifications</p>
      </div>

      <FormGroup title="Delivery Methods">
        <div className="space-y-4">
          <Checkbox
            label="Email Notifications"
            description="Receive notifications via email"
            checked={settings.emailAlerts}
            onChange={(e) => updateSetting('emailAlerts', e.target.checked)}
          />
          <Checkbox
            label="SMS Notifications"
            description="Receive critical alerts via SMS"
            checked={settings.smsAlerts}
            onChange={(e) => updateSetting('smsAlerts', e.target.checked)}
          />
          <Checkbox
            label="Browser Notifications"
            description="Show notifications in your browser"
            checked={settings.browserNotifications}
            onChange={(e) => updateSetting('browserNotifications', e.target.checked)}
          />
        </div>
      </FormGroup>

      <FormGroup title="Notification Types">
        <div className="space-y-4">
          <Checkbox
            label="Weekly Reports"
            description="Receive weekly energy performance summaries"
            checked={settings.weeklyReports}
            onChange={(e) => updateSetting('weeklyReports', e.target.checked)}
          />
          <Checkbox
            label="System Alerts"
            description="Get notified about system status changes"
            checked={settings.systemAlerts}
            onChange={(e) => updateSetting('systemAlerts', e.target.checked)}
          />
          <Checkbox
            label="Optimization Completed"
            description="Notifications when ML optimization jobs finish"
            checked={settings.optimizationCompleted}
            onChange={(e) => updateSetting('optimizationCompleted', e.target.checked)}
          />
          <Checkbox
            label="Threshold Alerts"
            description="Alerts when energy consumption exceeds thresholds"
            checked={settings.thresholdAlerts}
            onChange={(e) => updateSetting('thresholdAlerts', e.target.checked)}
          />
          <Checkbox
            label="Maintenance Alerts"
            description="Notifications for scheduled maintenance"
            checked={settings.maintenanceAlerts}
            onChange={(e) => updateSetting('maintenanceAlerts', e.target.checked)}
          />
        </div>
      </FormGroup>
    </div>
  )
}

// System Settings Component
function SystemSettings({ settings, updateSetting }: any) {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">System Settings</h2>
        <p className="text-gray-600">Configure system behavior and performance</p>
      </div>

      <FormGroup title="ML Configuration">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Select
            label="Default Algorithm"
            value={settings.defaultAlgorithm}
            onChange={(e) => updateSetting('defaultAlgorithm', e.target.value)}
            icon={<Cpu />}
            options={[
              { value: 'xgboost', label: 'XGBoost (Recommended)' },
              { value: 'lightgbm', label: 'LightGBM (Fast)' },
              { value: 'random_forest', label: 'Random Forest (Robust)' }
            ]}
          />
          <Input
            label="Max Concurrent Jobs"
            type="number"
            value={settings.maxConcurrentJobs}
            onChange={(e) => updateSetting('maxConcurrentJobs', parseInt(e.target.value))}
            min="1"
            max="10"
            icon={<Zap />}
          />
        </div>
      </FormGroup>

      <FormGroup title="Data Management">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Input
            label="Data Retention (Days)"
            type="number"
            value={settings.dataRetentionDays}
            onChange={(e) => updateSetting('dataRetentionDays', parseInt(e.target.value))}
            min="30"
            max="3650"
            icon={<Database />}
            hint="How long to keep historical data"
          />
          <Select
            label="Performance Mode"
            value={settings.performanceMode}
            onChange={(e) => updateSetting('performanceMode', e.target.value)}
            icon={<Monitor />}
            options={[
              { value: 'high_performance', label: 'High Performance' },
              { value: 'balanced', label: 'Balanced' },
              { value: 'power_saving', label: 'Power Saving' }
            ]}
          />
        </div>
      </FormGroup>

      <FormGroup title="System Features">
        <div className="space-y-4">
          <Checkbox
            label="Auto Optimization"
            description="Automatically run optimization when new data is available"
            checked={settings.autoOptimization}
            onChange={(e) => updateSetting('autoOptimization', e.target.checked)}
          />
          <Checkbox
            label="Enable Caching"
            description="Cache results for faster performance"
            checked={settings.cachingEnabled}
            onChange={(e) => updateSetting('cachingEnabled', e.target.checked)}
          />
          <Checkbox
            label="Analytics Tracking"
            description="Enable usage analytics for system improvement"
            checked={settings.analyticsEnabled}
            onChange={(e) => updateSetting('analyticsEnabled', e.target.checked)}
          />
          <Checkbox
            label="Debug Mode"
            description="Enable detailed logging for troubleshooting"
            checked={settings.debugMode}
            onChange={(e) => updateSetting('debugMode', e.target.checked)}
          />
        </div>
      </FormGroup>
    </div>
  )
}

// Security Settings Component
function SecuritySettings({ settings, updateSetting }: any) {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">Security Settings</h2>
        <p className="text-gray-600">Manage security and access control settings</p>
      </div>

      <FormGroup title="Authentication">
        <div className="space-y-4">
          <Checkbox
            label="Two-Factor Authentication"
            description="Add an extra layer of security to your account"
            checked={settings.twoFactorEnabled}
            onChange={(e) => updateSetting('twoFactorEnabled', e.target.checked)}
          />
          <Checkbox
            label="Login Notifications"
            description="Get notified when someone logs into your account"
            checked={settings.loginNotifications}
            onChange={(e) => updateSetting('loginNotifications', e.target.checked)}
          />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
          <Input
            label="Session Timeout (Hours)"
            type="number"
            value={settings.sessionTimeout}
            onChange={(e) => updateSetting('sessionTimeout', parseInt(e.target.value))}
            min="1"
            max="24"
            icon={<Clock />}
          />
          <Input
            label="Password Expiry (Days)"
            type="number"
            value={settings.passwordExpiry}
            onChange={(e) => updateSetting('passwordExpiry', parseInt(e.target.value))}
            min="30"
            max="365"
            icon={<Key />}
          />
        </div>
      </FormGroup>

      <FormGroup title="API Security">
        <div className="space-y-4">
          <Checkbox
            label="API Key Auto-Rotation"
            description="Automatically rotate API keys for enhanced security"
            checked={settings.apiKeyRotation}
            onChange={(e) => updateSetting('apiKeyRotation', e.target.checked)}
          />
          <Checkbox
            label="Audit Logging"
            description="Log all API calls and system actions"
            checked={settings.auditLogging}
            onChange={(e) => updateSetting('auditLogging', e.target.checked)}
          />
        </div>
        
        <Input
          label="IP Whitelist"
          value={settings.ipWhitelist}
          onChange={(e) => updateSetting('ipWhitelist', e.target.value)}
          placeholder="192.168.1.0/24, 10.0.0.0/8"
          hint="Comma-separated IP ranges (leave empty to allow all)"
          icon={<Shield />}
        />
      </FormGroup>
    </div>
  )
}

// API Settings Component
function ApiSettings({ settings, updateSetting }: any) {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">API Configuration</h2>
        <p className="text-gray-600">Configure API endpoints and connection settings</p>
      </div>

      <FormGroup title="Connection Settings">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Input
            label="API Base URL"
            value={settings.baseUrl}
            onChange={(e) => updateSetting('baseUrl', e.target.value)}
            icon={<Globe />}
            hint="Backend API endpoint URL"
          />
          <Input
            label="Request Timeout (seconds)"
            type="number"
            value={settings.timeout}
            onChange={(e) => updateSetting('timeout', parseInt(e.target.value))}
            min="5"
            max="300"
            icon={<Clock />}
          />
          <Input
            label="Retry Attempts"
            type="number"
            value={settings.retryAttempts}
            onChange={(e) => updateSetting('retryAttempts', parseInt(e.target.value))}
            min="0"
            max="10"
            icon={<RotateCcw />}
          />
          <Input
            label="Rate Limit (requests/hour)"
            type="number"
            value={settings.rateLimit}
            onChange={(e) => updateSetting('rateLimit', parseInt(e.target.value))}
            min="10"
            max="10000"
            icon={<Zap />}
          />
        </div>
      </FormGroup>

      <FormGroup title="Performance">
        <div className="space-y-4">
          <Checkbox
            label="Enable Caching"
            description="Cache API responses for better performance"
            checked={settings.enableCaching}
            onChange={(e) => updateSetting('enableCaching', e.target.checked)}
          />
          <Checkbox
            label="Compression"
            description="Enable gzip compression for API responses"
            checked={settings.compressionEnabled}
            onChange={(e) => updateSetting('compressionEnabled', e.target.checked)}
          />
        </div>
      </FormGroup>

      <FormGroup title="API Key Management">
        <div className="space-y-4">
          <Input
            label="Current API Key"
            value={settings.apiKey}
            readOnly
            icon={<Key />}
            rightIcon={
              <button className="text-blue-600 hover:text-blue-700">
                <Eye className="w-4 h-4" />
              </button>
            }
          />
          <div className="flex space-x-3">
            <button className="btn-secondary">
              <Key className="w-4 h-4 mr-2" />
              Generate New Key
            </button>
            <button className="btn-secondary">
              <Download className="w-4 h-4 mr-2" />
              Download Key
            </button>
          </div>
        </div>
      </FormGroup>
    </div>
  )
}

// Appearance Settings Component
function AppearanceSettings({ settings, updateSetting }: any) {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-2">Appearance Settings</h2>
        <p className="text-gray-600">Customize the look and feel of your dashboard</p>
      </div>

      <FormGroup title="Theme">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { value: 'light', label: 'Light', icon: <Sun className="w-5 h-5" /> },
            { value: 'dark', label: 'Dark', icon: <Moon className="w-5 h-5" /> },
            { value: 'auto', label: 'Auto', icon: <Monitor className="w-5 h-5" /> }
          ].map((theme) => (
            <div
              key={theme.value}
              className={`p-4 border rounded-xl cursor-pointer transition-all duration-200 ${
                settings.theme === theme.value
                  ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-500 ring-opacity-20'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => updateSetting('theme', theme.value)}
            >
              <div className="flex items-center justify-center mb-2">
                {theme.icon}
              </div>
              <div className="text-center font-medium text-gray-900">
                {theme.label}
              </div>
            </div>
          ))}
        </div>
      </FormGroup>

      <FormGroup title="Layout">
        <div className="space-y-4">
          <Checkbox
            label="Compact Mode"
            description="Use a more compact layout to fit more content"
            checked={settings.compactMode}
            onChange={(e) => updateSetting('compactMode', e.target.checked)}
          />
          <Checkbox
            label="Expanded Sidebar"
            description="Keep the sidebar expanded by default"
            checked={settings.sidebarExpanded}
            onChange={(e) => updateSetting('sidebarExpanded', e.target.checked)}
          />
        </div>
      </FormGroup>

      <FormGroup title="Accessibility">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Select
            label="Font Size"
            value={settings.fontSize}
            onChange={(e) => updateSetting('fontSize', e.target.value)}
            options={[
              { value: 'small', label: 'Small' },
              { value: 'medium', label: 'Medium' },
              { value: 'large', label: 'Large' }
            ]}
          />
          <div className="space-y-4">
            <Checkbox
              label="Enable Animations"
              description="Show smooth transitions and animations"
              checked={settings.animations}
              onChange={(e) => updateSetting('animations', e.target.checked)}
            />
            <Checkbox
              label="Reduced Motion"
              description="Minimize motion for accessibility"
              checked={settings.reducedMotion}
              onChange={(e) => updateSetting('reducedMotion', e.target.checked)}
            />
          </div>
        </div>
      </FormGroup>
    </div>
  )
}
