"""
File management utilities for generated code organization.
"""

import os
import json
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
import zipfile
from datetime import datetime

class FileManager:
    """Manages file operations for generated code."""
    
    def __init__(self, base_path: str, logger):
        self.base_path = Path(base_path)
        self.logger = logger
        self.project_files = {}
        
        # Ensure base directory exists
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    async def create_project_structure(self, project_id: str, architecture: Dict) -> Dict[str, str]:
        """Create directory structure for a project."""
        
        project_path = self.base_path / project_id
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Create standard directories
        directories = [
            "backend",
            "frontend/src/components",
            "frontend/src/context", 
            "frontend/src/utils",
            "database",
            "tests",
            "docs",
            "config"
        ]
        
        created_dirs = {}
        
        for dir_path in directories:
            full_path = project_path / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            created_dirs[dir_path] = str(full_path)
            self.logger.info(f"Created directory: {full_path}")
        
        # Add architecture-specific directories
        if architecture.get("components"):
            for component in architecture["components"]:
                comp_dir = project_path / "backend" / component.lower()
                comp_dir.mkdir(parents=True, exist_ok=True)
                created_dirs[f"backend/{component.lower()}"] = str(comp_dir)
        
        return created_dirs
    
    async def save_generated_file(self, project_id: str, relative_path: str, content: str,
                                 generator_type: str = "developer") -> Dict[str, Any]:
        """Save a generated file to the project structure."""
        
        project_path = self.base_path / project_id
        file_path = project_path / relative_path
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file content
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            file_info = {
                "path": str(file_path),
                "relative_path": relative_path,
                "size": len(content.encode('utf-8')),
                "generated_by": generator_type,
                "created_at": datetime.utcnow().isoformat(),
                "type": self._get_file_type(relative_path)
            }
            
            # Track file in project registry
            if project_id not in self.project_files:
                self.project_files[project_id] = []
            self.project_files[project_id].append(file_info)
            
            self.logger.info(f"Saved file: {file_path}")
            return file_info
            
        except Exception as e:
            self.logger.error(f"Failed to save file {file_path}: {str(e)}")
            raise
    
    async def save_file_batch(self, project_id: str, files: Dict[str, str],
                            generator_type: str = "developer") -> List[Dict[str, Any]]:
        """Save multiple files in batch."""
        
        saved_files = []
        
        for relative_path, content in files.items():
            try:
                file_info = await self.save_generated_file(
                    project_id, relative_path, content, generator_type
                )
                saved_files.append(file_info)
            except Exception as e:
                self.logger.error(f"Failed to save file {relative_path}: {str(e)}")
                # Continue with other files
        
        return saved_files
    
    async def read_project_file(self, project_id: str, relative_path: str) -> Optional[str]:
        """Read a file from the project."""
        
        project_path = self.base_path / project_id
        file_path = project_path / relative_path
        
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                self.logger.warning(f"File not found: {file_path}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to read file {file_path}: {str(e)}")
            return None
    
    async def list_project_files(self, project_id: str) -> List[Dict[str, Any]]:
        """List all files in a project."""
        
        project_path = self.base_path / project_id
        
        if not project_path.exists():
            return []
        
        files = []
        for file_path in project_path.rglob('*'):
            if file_path.is_file():
                relative_path = str(file_path.relative_to(project_path))
                
                try:
                    stat = file_path.stat()
                    files.append({
                        "path": str(file_path),
                        "relative_path": relative_path,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "type": self._get_file_type(relative_path)
                    })
                except Exception as e:
                    self.logger.warning(f"Failed to stat file {file_path}: {str(e)}")
        
        return files
    
    async def create_project_archive(self, project_id: str) -> str:
        """Create a ZIP archive of the entire project."""
        
        project_path = self.base_path / project_id
        
        if not project_path.exists():
            raise FileNotFoundError(f"Project {project_id} not found")
        
        # Create temporary zip file
        temp_dir = tempfile.mkdtemp()
        zip_path = Path(temp_dir) / f"{project_id}.zip"
        
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in project_path.rglob('*'):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(project_path)
                        zipf.write(file_path, relative_path)
            
            self.logger.info(f"Created project archive: {zip_path}")
            return str(zip_path)
            
        except Exception as e:
            self.logger.error(f"Failed to create archive: {str(e)}")
            # Clean up temp file
            if zip_path.exists():
                zip_path.unlink()
            raise
    
    async def apply_file_template(self, template_name: str, variables: Dict[str, Any]) -> str:
        """Apply variables to a file template."""
        
        template_path = self.base_path.parent / "templates" / f"{template_name}.template"
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template {template_name} not found")
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Simple variable substitution
            for key, value in variables.items():
                placeholder = "{{" + key + "}}"
                template_content = template_content.replace(placeholder, str(value))
            
            return template_content
            
        except Exception as e:
            self.logger.error(f"Failed to apply template {template_name}: {str(e)}")
            raise
    
    async def validate_file_structure(self, project_id: str, expected_structure: Dict) -> Dict[str, Any]:
        """Validate that project has expected file structure."""
        
        project_path = self.base_path / project_id
        results = {
            "valid": True,
            "missing_files": [],
            "unexpected_files": [],
            "structure_score": 0
        }
        
        if not project_path.exists():
            results["valid"] = False
            results["missing_files"] = list(expected_structure.keys())
            return results
        
        # Check for expected files
        for expected_file in expected_structure.get("required_files", []):
            file_path = project_path / expected_file
            if not file_path.exists():
                results["missing_files"].append(expected_file)
                results["valid"] = False
        
        # Check for expected directories
        for expected_dir in expected_structure.get("required_directories", []):
            dir_path = project_path / expected_dir
            if not dir_path.exists() or not dir_path.is_dir():
                results["missing_files"].append(f"{expected_dir}/ (directory)")
                results["valid"] = False
        
        # Calculate structure score
        expected_count = len(expected_structure.get("required_files", [])) + \
                        len(expected_structure.get("required_directories", []))
        missing_count = len(results["missing_files"])
        
        if expected_count > 0:
            results["structure_score"] = ((expected_count - missing_count) / expected_count) * 100
        else:
            results["structure_score"] = 100
        
        return results
    
    def _get_file_type(self, file_path: str) -> str:
        """Determine file type from extension."""
        
        path = Path(file_path)
        extension = path.suffix.lower()
        
        type_mapping = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'react',
            '.ts': 'typescript',
            '.tsx': 'react-typescript',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.md': 'markdown',
            '.txt': 'text',
            '.sql': 'sql',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.toml': 'toml',
            '.env': 'environment'
        }
        
        return type_mapping.get(extension, 'unknown')
    
    async def backup_project(self, project_id: str) -> str:
        """Create a backup of the project."""
        
        project_path = self.base_path / project_id
        backup_dir = self.base_path / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"{project_id}_{timestamp}"
        
        try:
            shutil.copytree(project_path, backup_path)
            self.logger.info(f"Created backup: {backup_path}")
            return str(backup_path)
        except Exception as e:
            self.logger.error(f"Failed to create backup: {str(e)}")
            raise
    
    async def restore_project(self, project_id: str, backup_path: str) -> bool:
        """Restore a project from backup."""
        
        project_path = self.base_path / project_id
        backup_source = Path(backup_path)
        
        if not backup_source.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")
        
        try:
            # Remove existing project
            if project_path.exists():
                shutil.rmtree(project_path)
            
            # Restore from backup
            shutil.copytree(backup_source, project_path)
            self.logger.info(f"Restored project from: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore project: {str(e)}")
            return False
    
    async def cleanup_old_projects(self, days_old: int = 30) -> int:
        """Clean up projects older than specified days."""
        
        cutoff_time = datetime.utcnow().timestamp() - (days_old * 24 * 3600)
        cleaned_count = 0
        
        for project_dir in self.base_path.iterdir():
            if project_dir.is_dir() and project_dir.name != "backups":
                try:
                    if project_dir.stat().st_mtime < cutoff_time:
                        shutil.rmtree(project_dir)
                        cleaned_count += 1
                        self.logger.info(f"Cleaned up old project: {project_dir}")
                except Exception as e:
                    self.logger.warning(f"Failed to clean up {project_dir}: {str(e)}")
        
        return cleaned_count
    
    def get_project_stats(self, project_id: str) -> Dict[str, Any]:
        """Get statistics about a project."""
        
        project_path = self.base_path / project_id
        
        if not project_path.exists():
            return {"exists": False}
        
        stats = {
            "exists": True,
            "total_files": 0,
            "total_size": 0,
            "file_types": {},
            "directory_count": 0
        }
        
        for item in project_path.rglob('*'):
            if item.is_file():
                stats["total_files"] += 1
                stats["total_size"] += item.stat().st_size
                
                file_type = self._get_file_type(item.name)
                stats["file_types"][file_type] = stats["file_types"].get(file_type, 0) + 1
                
            elif item.is_dir():
                stats["directory_count"] += 1
        
        return stats
