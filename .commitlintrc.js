// 🏢⚡ Energy Optimizer Pro - Commit Message Configuration
// ========================================================

module.exports = {
  extends: ['@commitlint/config-conventional'],
  
  rules: {
    // Type enumeration
    'type-enum': [
      2,
      'always',
      [
        'feat',     // New features
        'fix',      // Bug fixes
        'docs',     // Documentation changes
        'style',    // Code style changes (formatting, etc.)
        'refactor', // Code refactoring
        'perf',     // Performance improvements
        'test',     // Adding or updating tests
        'build',    // Build system changes
        'ci',       // CI/CD changes
        'chore',    // Maintenance tasks
        'revert',   // Reverting changes
        'security', // Security improvements
        'config',   // Configuration changes
        'deps',     // Dependency updates
        'release',  // Release commits
        'hotfix',   // Critical fixes
        'wip',      // Work in progress (avoid in main/develop)
      ],
    ],
    
    // Subject and body rules
    'subject-case': [2, 'always', 'lower-case'],
    'subject-empty': [2, 'never'],
    'subject-max-length': [2, 'always', 72],
    'subject-min-length': [2, 'always', 10],
    'subject-full-stop': [2, 'never', '.'],
    
    // Body rules
    'body-max-line-length': [2, 'always', 100],
    'body-leading-blank': [2, 'always'],
    
    // Footer rules  
    'footer-leading-blank': [2, 'always'],
    'footer-max-line-length': [2, 'always', 100],
    
    // Type and scope rules
    'type-case': [2, 'always', 'lower-case'],
    'type-empty': [2, 'never'],
    'scope-case': [2, 'always', 'lower-case'],
    
    // Header rules
    'header-max-length': [2, 'always', 72],
    'header-min-length': [2, 'always', 15],
  },
  
  // Custom scope enumeration for Energy Optimizer Pro
  rules: {
    'scope-enum': [
      2,
      'always',
      [
        // Frontend scopes
        'frontend',
        'components',
        'ui',
        'dashboard',
        'charts',
        'auth',
        'routing',
        'styles',
        'types',
        'hooks',
        'utils',
        'store',
        
        // Backend scopes
        'backend',
        'api',
        'models',
        'database',
        'auth',
        'ml',
        'optimization',
        'analytics',
        'notifications',
        'websocket',
        'cache',
        
        // Infrastructure scopes
        'docker',
        'nginx',
        'ci',
        'deployment',
        'monitoring',
        'security',
        'performance',
        
        // Documentation scopes
        'docs',
        'readme',
        'api-docs',
        'tutorials',
        
        // Testing scopes
        'tests',
        'e2e',
        'unit',
        'integration',
        'performance',
        
        // Configuration scopes
        'config',
        'env',
        'deps',
        'build',
        
        // Business logic scopes
        'buildings',
        'energy',
        'reports',
        'users',
        'alerts',
      ],
    ],
  },
  
  // Help message for developers
  helpUrl: 'https://github.com/your-username/energy-optimizer-pro/blob/main/docs/commit-conventions.md',
  
  // Custom prompts for interactive commit tools
  prompt: {
    questions: {
      type: {
        description: "Select the type of change that you're committing:",
        enum: {
          feat: {
            description: '✨ A new feature',
            title: 'Features',
            emoji: '✨',
          },
          fix: {
            description: '🐛 A bug fix',
            title: 'Bug Fixes',
            emoji: '🐛',
          },
          docs: {
            description: '📚 Documentation only changes',
            title: 'Documentation',
            emoji: '📚',
          },
          style: {
            description: '💄 Changes that do not affect the meaning of the code',
            title: 'Styles',
            emoji: '💄',
          },
          refactor: {
            description: '♻️ A code change that neither fixes a bug nor adds a feature',
            title: 'Code Refactoring',
            emoji: '♻️',
          },
          perf: {
            description: '⚡ A code change that improves performance',
            title: 'Performance Improvements',
            emoji: '⚡',
          },
          test: {
            description: '🧪 Adding missing tests or correcting existing tests',
            title: 'Tests',
            emoji: '🧪',
          },
          build: {
            description: '🔨 Changes that affect the build system or external dependencies',
            title: 'Builds',
            emoji: '🔨',
          },
          ci: {
            description: '👷 Changes to CI configuration files and scripts',
            title: 'Continuous Integrations',
            emoji: '👷',
          },
          chore: {
            description: '🔧 Other changes that don\'t modify src or test files',
            title: 'Chores',
            emoji: '🔧',
          },
          revert: {
            description: '⏪ Reverts a previous commit',
            title: 'Reverts',
            emoji: '⏪',
          },
          security: {
            description: '🔒 Security improvements and fixes',
            title: 'Security',
            emoji: '🔒',
          },
        },
      },
      scope: {
        description: 'What is the scope of this change (e.g. component, feature, service)?',
      },
      subject: {
        description: 'Write a short, imperative tense description of the change',
      },
      body: {
        description: 'Provide a longer description of the change (optional)',
      },
      isBreaking: {
        description: 'Are there any breaking changes?',
      },
      breakingBody: {
        description: 'A BREAKING CHANGE commit requires a body. Please enter a longer description of the commit itself',
      },
      breaking: {
        description: 'Describe the breaking changes',
      },
      isIssueAffected: {
        description: 'Does this change affect any open issues?',
      },
      issuesBody: {
        description: 'If issues are fixed, the commit requires a body. Please enter a longer description of the commit itself',
      },
      issues: {
        description: 'Add issue references (e.g. "fix #123", "re #123")',
      },
    },
  },
}
