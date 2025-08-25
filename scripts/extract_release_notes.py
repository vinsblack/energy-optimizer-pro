#!/usr/bin/env python3
"""
Extract release notes from CHANGELOG.md or generate them from git commits.
"""
import re
import subprocess
import sys
from pathlib import Path

def get_latest_tag():
    """Get the latest git tag."""
    try:
        result = subprocess.run(['git', 'describe', '--tags', '--abbrev=0'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def get_commits_since_last_tag():
    """Get commits since last tag."""
    last_tag = get_latest_tag()
    
    if last_tag:
        cmd = ['git', 'log', f'{last_tag}..HEAD', '--oneline']
    else:
        cmd = ['git', 'log', '--oneline']
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    except subprocess.CalledProcessError:
        return []

def extract_from_changelog():
    """Extract release notes from CHANGELOG.md."""
    changelog_path = Path('CHANGELOG.md')
    
    if not changelog_path.exists():
        return None
    
    with open(changelog_path, 'r') as f:
        content = f.read()
    
    # Look for the first version section
    version_pattern = r'## \[?([^\]]+)\]?.*?\n(.*?)(?=\n## |\nâ|\Z)'
    match = re.search(version_pattern, content, re.DOTALL)
    
    if match:
        version = match.group(1)
        notes = match.group(2).strip()
        return f"## Release {version}\n\n{notes}"
    
    return None

def generate_from_commits():
    """Generate release notes from git commits."""
    commits = get_commits_since_last_tag()
    
    if not commits:
        return "## Release Notes\n\nNo changes since last release."
    
    # Categorize commits
    features = []
    fixes = []
    docs = []
    other = []
    
    for commit in commits:
        commit_lower = commit.lower()
        
        if any(keyword in commit_lower for keyword in ['feat:', 'feature:', 'add:', 'new:']):
            features.append(commit)
        elif any(keyword in commit_lower for keyword in ['fix:', 'bug:', 'patch:']):
            fixes.append(commit)
        elif any(keyword in commit_lower for keyword in ['doc:', 'docs:', 'readme:']):
            docs.append(commit)
        else:
            other.append(commit)
    
    # Build release notes
    notes = ["## Release Notes", ""]
    
    if features:
        notes.append("### ✨ New Features")
        for commit in features:
            notes.append(f"- {commit}")
        notes.append("")
    
    if fixes:
        notes.append("### 🐛 Bug Fixes")
        for commit in fixes:
            notes.append(f"- {commit}")
        notes.append("")
    
    if docs:
        notes.append("### 📚 Documentation")
        for commit in docs:
            notes.append(f"- {commit}")
        notes.append("")
    
    if other:
        notes.append("### 🔧 Other Changes")
        for commit in other[:10]:  # Limit to avoid too long
            notes.append(f"- {commit}")
        if len(other) > 10:
            notes.append(f"- ... and {len(other) - 10} more commits")
        notes.append("")
    
    notes.append("### 📈 Metrics")
    notes.append(f"- Total commits: {len(commits)}")
    notes.append(f"- New features: {len(features)}")
    notes.append(f"- Bug fixes: {len(fixes)}")
    
    return "\n".join(notes)

def main():
    """Main function to extract or generate release notes."""
    # Try to extract from CHANGELOG first
    release_notes = extract_from_changelog()
    
    # If no CHANGELOG, generate from commits
    if not release_notes:
        release_notes = generate_from_commits()
    
    # Add standard footer
    release_notes += "\n\n---\n\n"
    release_notes += "### 🚀 Quick Start\n\n"
    release_notes += "```bash\n"
    release_notes += "# Install\n"
    release_notes += "pip install building-energy-optimizer[all]\n\n"
    release_notes += "# Quick demo\n"
    release_notes += "beo demo\n\n"
    release_notes += "# Start services\n"
    release_notes += "beo api &\n"
    release_notes += "beo dashboard\n"
    release_notes += "```\n\n"
    release_notes += "### 📚 Documentation\n\n"
    release_notes += "- [API Documentation](https://your-username.github.io/building-energy-optimizer/api/)\n"
    release_notes += "- [User Guide](https://your-username.github.io/building-energy-optimizer/)\n"
    release_notes += "- [Examples](https://github.com/your-username/building-energy-optimizer/tree/main/examples)\n\n"
    release_notes += "### 🐛 Issues\n\n"
    release_notes += "Report bugs and request features at: [GitHub Issues](https://github.com/your-username/building-energy-optimizer/issues)\n"
    
    print(release_notes)

if __name__ == "__main__":
    main()
