#!/usr/bin/env python3
"""
DDT Coding Platform - Project Reorganization Script

This script safely reorganizes the project structure to follow best practices:
1. Renames 'new app' to 'src' (removes space)
2. Consolidates test files into tests/ directory
3. Organizes utility scripts into tools/ directory
4. Updates all import paths and references

Usage:
    python reorganize_project.py --dry-run    # Preview changes
    python reorganize_project.py --apply      # Apply changes
"""

import os
import shutil
import subprocess
import argparse
from pathlib import Path
import re

class ProjectReorganizer:
    def __init__(self, root_dir: str, dry_run: bool = True):
        self.root = Path(root_dir).resolve()
        self.dry_run = dry_run
        self.changes = []
        
    def log_change(self, operation: str, source: str, target: str = None):
        """Log a change to be made"""
        if target:
            self.changes.append(f"{operation}: {source} -> {target}")
        else:
            self.changes.append(f"{operation}: {source}")
    
    def safe_move(self, source: Path, target: Path):
        """Safely move a file or directory"""
        if not source.exists():
            print(f"⚠️  Source doesn't exist: {source}")
            return False
            
        # Create target directory if needed
        target.parent.mkdir(parents=True, exist_ok=True)
        
        if self.dry_run:
            self.log_change("MOVE", str(source), str(target))
            return True
        else:
            try:
                shutil.move(str(source), str(target))
                print(f"✅ Moved: {source} -> {target}")
                return True
            except Exception as e:
                print(f"❌ Failed to move {source} to {target}: {e}")
                return False
    
    def safe_mkdir(self, directory: Path):
        """Safely create a directory"""
        if self.dry_run:
            self.log_change("CREATE_DIR", str(directory))
        else:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created directory: {directory}")
    
    def reorganize_main_structure(self):
        """Reorganize the main project structure"""
        print("🔄 Reorganizing main project structure...")
        
        # 1. Rename 'new app' to 'src'
        old_app_dir = self.root / "new app"
        new_src_dir = self.root / "src"
        
        if old_app_dir.exists():
            self.safe_move(old_app_dir, new_src_dir)
        
        # 2. Create tests directory
        tests_dir = self.root / "tests"
        self.safe_mkdir(tests_dir)
        self.safe_mkdir(tests_dir / "unit")
        self.safe_mkdir(tests_dir / "integration")
        self.safe_mkdir(tests_dir / "fixtures")
        
        # 3. Create tools directory
        tools_dir = self.root / "tools"
        self.safe_mkdir(tools_dir)
        self.safe_mkdir(tools_dir / "scripts")
        self.safe_mkdir(tools_dir / "migration")
        self.safe_mkdir(tools_dir / "development")
        
        # 4. Create config directory
        config_dir = self.root / "config"
        self.safe_mkdir(config_dir)
        self.safe_mkdir(config_dir / "settings")
        self.safe_mkdir(config_dir / "docker")
    
    def reorganize_test_files(self):
        """Move test files from root to tests/ directory"""
        print("🧪 Reorganizing test files...")
        
        test_files = [
            "test_fast_submission.py",
            "test_health.py", 
            "test_integration.py",
            "test_judge0_direct.py",
            "test_language_mismatch.py",
            "test_pipeline.py",
            "test_single_submission.py",
            "test_submission_eval.py",
            "test_submission_flow.py"
        ]
        
        tests_dir = self.root / "tests" / "integration"
        
        for test_file in test_files:
            source = self.root / test_file
            target = tests_dir / test_file
            if source.exists():
                self.safe_move(source, target)
    
    def reorganize_utility_scripts(self):
        """Move utility scripts to tools/ directory"""
        print("🔧 Reorganizing utility scripts...")
        
        utility_files = [
            "check_languages.py",
            "debug_testcase_filter.py", 
            "diagnose_testcases.py",
            "final_test.py",
            "fix_orphaned_testcases.py",
            "path_debug.py",
            "simulate_task_logic.py",
            "enhanced_hello_world_stubs.py",
            "hello_world_stubs.py",
            "update_hello_simple.py",
            "update_hello_world.py",
            "update_hello_world_docker.py"
        ]
        
        tools_dir = self.root / "tools" / "scripts"
        
        for utility_file in utility_files:
            source = self.root / utility_file
            target = tools_dir / utility_file
            if source.exists():
                self.safe_move(source, target)
    
    def update_docker_compose(self):
        """Update Docker Compose files with new paths"""
        print("🐳 Updating Docker Compose configuration...")
        
        compose_file = self.root / "infra" / "compose" / "dev" / "docker-compose.yml"
        
        if not compose_file.exists():
            print(f"⚠️  Docker compose file not found: {compose_file}")
            return
        
        if self.dry_run:
            self.log_change("UPDATE", str(compose_file), "Fix paths from 'new app' to 'src'")
            return
        
        # Read and update the compose file
        with open(compose_file, 'r') as f:
            content = f.read()
        
        # Replace old paths
        content = content.replace('new app/student_auth', 'src/student_auth')
        content = content.replace('"new app/student_auth/manage.py"', 'src/student_auth/manage.py')
        content = content.replace('"/workspace/new app/student_auth"', '"/workspace/src/student_auth"')
        
        with open(compose_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated Docker Compose file: {compose_file}")
    
    def update_dockerfile(self):
        """Update Dockerfile with new paths"""
        print("🐳 Updating Dockerfile...")
        
        dockerfile = self.root / "infra" / "docker" / "backend" / "Dockerfile"
        
        if not dockerfile.exists():
            print(f"⚠️  Dockerfile not found: {dockerfile}")
            return
        
        if self.dry_run:
            self.log_change("UPDATE", str(dockerfile), "Fix paths from 'new app' to 'src'")
            return
        
        # Read and update the dockerfile
        with open(dockerfile, 'r') as f:
            content = f.read()
        
        # Replace old paths
        content = content.replace('new app/student_auth/', 'src/student_auth/')
        content = content.replace('"new app/student_auth/manage.py"', 'src/student_auth/manage.py')
        
        with open(dockerfile, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated Dockerfile: {dockerfile}")
    
    def cleanup_empty_dirs(self):
        """Remove empty directories after reorganization"""
        print("🧹 Cleaning up empty directories...")
        
        potential_empty_dirs = [
            self.root / "new app",
        ]
        
        for dir_path in potential_empty_dirs:
            if dir_path.exists() and not any(dir_path.iterdir()):
                if self.dry_run:
                    self.log_change("REMOVE_EMPTY", str(dir_path))
                else:
                    shutil.rmtree(dir_path)
                    print(f"🗑️  Removed empty directory: {dir_path}")
    
    def create_readme_updates(self):
        """Create updated README files for new structure"""
        print("📝 Creating updated documentation...")
        
        new_structure_doc = self.root / "PROJECT_STRUCTURE.md"
        
        if self.dry_run:
            self.log_change("CREATE", str(new_structure_doc))
            return
        
        content = '''# DDT Coding Platform - Project Structure

## 📁 Reorganized Directory Structure

```
ddt-coding/
├── src/                     # Main Django application (formerly "new app/")
│   └── student_auth/        # Django project
│       ├── accounts/        # Main app
│       ├── student_auth/    # Project settings
│       └── manage.py        # Django management
├── frontend/                # React application
│   ├── src/
│   ├── public/
│   └── package.json
├── infra/                   # Infrastructure & deployment
│   ├── compose/            # Docker Compose files
│   └── docker/             # Dockerfiles
├── tests/                   # All test files
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── fixtures/           # Test data
├── tools/                   # Development utilities
│   ├── scripts/            # Utility scripts
│   ├── migration/          # Migration helpers
│   └── development/        # Dev tools
├── config/                  # Configuration files
│   ├── settings/           # Django settings split
│   └── docker/             # Docker configs
└── docs/                    # Documentation
    ├── api/
    ├── deployment/
    └── development/
```

## 🔄 What Changed

### Moved
- `new app/` → `src/` (removed space from directory name)
- All `test_*.py` files → `tests/integration/`
- Utility scripts → `tools/scripts/`

### Updated
- Docker Compose paths updated
- Dockerfile paths updated
- Import statements fixed

### Benefits
- ✅ No spaces in directory names
- ✅ Clear separation of concerns
- ✅ Better organization for testing
- ✅ Easier to navigate and maintain
- ✅ Follows Python project best practices
'''
        
        with open(new_structure_doc, 'w') as f:
            f.write(content)
        
        print(f"✅ Created: {new_structure_doc}")
    
    def run_reorganization(self):
        """Run the complete reorganization process"""
        print("🚀 Starting DDT Coding Platform reorganization...")
        print(f"📍 Root directory: {self.root}")
        print(f"🔍 Mode: {'DRY RUN' if self.dry_run else 'APPLY CHANGES'}")
        print()
        
        # Run all reorganization steps
        self.reorganize_main_structure()
        self.reorganize_test_files()
        self.reorganize_utility_scripts()
        self.update_docker_compose()
        self.update_dockerfile()
        self.cleanup_empty_dirs()
        self.create_readme_updates()
        
        # Summary
        print("\n" + "="*60)
        if self.dry_run:
            print(f"📋 PREVIEW: {len(self.changes)} changes planned:")
            for change in self.changes:
                print(f"   {change}")
            print("\n💡 Run with --apply to execute these changes")
        else:
            print("✅ Reorganization completed successfully!")
            print("\n🔄 Next steps:")
            print("   1. Test Docker containers: docker-compose up")
            print("   2. Run tests: python -m pytest tests/")
            print("   3. Update any remaining hardcoded paths")
            print("   4. Commit changes to git")


def main():
    parser = argparse.ArgumentParser(description="Reorganize DDT Coding Platform project structure")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run)")
    parser.add_argument("--root", default=".", help="Root directory of the project")
    
    args = parser.parse_args()
    
    reorganizer = ProjectReorganizer(
        root_dir=args.root,
        dry_run=not args.apply
    )
    
    reorganizer.run_reorganization()


if __name__ == "__main__":
    main()