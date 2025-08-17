"""
Database Generator
Generates comprehensive database operations module with SQLite async support.
"""

from typing import Dict, Any
from ..base import BaseGenerator


class DatabaseGenerator(BaseGenerator):
    """
    Generator for database operations module.
    Creates comprehensive database functionality with SQLite and async operations.
    """

    async def generate(self, specifications: Dict) -> str:
        """Generate database module code."""
        
        try:
            # Attempt LLM generation
            prompt = self._create_database_prompt(specifications)
            content = await self._try_llm_generation(prompt, max_tokens=3000, temperature=0.1)
            
            self._update_generation_stats()
            return content
            
        except Exception as e:
            self.logger.warning(f"Database LLM generation failed: {str(e)}, using fallback")
            content = self._use_fallback()
            self._update_generation_stats()
            return content

    def _create_database_prompt(self, specifications: Dict) -> str:
        """Create prompt for database generation."""
        
        return """Generate a comprehensive async SQLite database module for a BotArmy FastAPI application.

Requirements:
1. Use aiosqlite for async database operations
2. Create tables: projects, agents, messages, conflicts, files, events
3. Include comprehensive CRUD operations for all tables
4. Add proper error handling and transaction management
5. Include database initialization and table creation
6. Add statistics and monitoring methods
7. Include event creation for real-time updates
8. Add proper connection management and cleanup
9. Include data validation and foreign key constraints
10. Add batch operations and bulk insert methods
11. Include comprehensive logging and error tracking
12. Add health check and connection status methods

Generate clean, well-documented async Python code with proper exception handling.
"""

    def _generate_fallback(self) -> str:
        """Generate fallback database module."""
        
        return '''"""
Database operations and management for BotArmy application.
Provides comprehensive database functionality using SQLite with async operations.
"""

import sqlite3
import aiosqlite
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

class Database:
    """
    Comprehensive database manager for BotArmy application.
    Handles projects, agents, messages, conflicts, and file storage.
    """

    def __init__(self, database_url: str):
        self.database_url = database_url.replace("sqlite:///", "")
        self.connection = None
        self._stats = {
            "queries_executed": 0,
            "errors": 0,
            "last_error": None
        }

    async def initialize(self):
        """Initialize database and create all required tables"""
        
        try:
            self.connection = await aiosqlite.connect(self.database_url)
            await self.connection.execute("PRAGMA foreign_keys = ON")
            await self._create_tables()
            await self.connection.commit()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            self._stats["errors"] += 1
            self._stats["last_error"] = str(e)
            raise

    async def _create_tables(self):
        """Create all required database tables"""
        
        # Projects table
        await self.connection.execute(\'\'\'
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                requirements TEXT NOT NULL,
                status TEXT DEFAULT \'created\',
                user_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT DEFAULT \'{}\'
            )
        \'\'\')

        # Agents table
        await self.connection.execute(\'\'\'
            CREATE TABLE IF NOT EXISTS agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                agent_type TEXT NOT NULL,
                status TEXT DEFAULT \'idle\',
                progress INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id),
                UNIQUE(project_id, agent_type)
            )
        \'\'\')

        # Messages table
        await self.connection.execute(\'\'\'
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                from_agent TEXT,
                to_agent TEXT,
                content TEXT NOT NULL,
                message_type TEXT DEFAULT \'info\',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        \'\'\')

        # Conflicts table
        await self.connection.execute(\'\'\'
            CREATE TABLE IF NOT EXISTS conflicts (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                description TEXT NOT NULL,
                agents_involved TEXT NOT NULL,
                stage TEXT,
                status TEXT DEFAULT \'pending\',
                resolution TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        \'\'\')

        # Files table
        await self.connection.execute(\'\'\'
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                content TEXT NOT NULL,
                generated_by TEXT,
                file_type TEXT,
                size INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        \'\'\')

        # Events table for real-time updates
        await self.connection.execute(\'\'\'
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT,
                event_type TEXT NOT NULL,
                event_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        \'\'\')

    # Project Operations

    async def create_project(self, requirements: str, user_id: str = None) -> str:
        """Create a new project and return its ID"""
        
        project_id = str(uuid.uuid4())
        
        try:
            await self.connection.execute(
                \'\'\'INSERT INTO projects (id, requirements, user_id) 
                   VALUES (?, ?, ?)\'\'\',
                (project_id, requirements, user_id)
            )
            
            # Initialize agent statuses
            agent_types = ["analyst", "architect", "developer", "tester"]
            for agent_type in agent_types:
                await self.connection.execute(
                    \'\'\'INSERT INTO agents (project_id, agent_type) 
                       VALUES (?, ?)\'\'\',
                    (project_id, agent_type)
                )
            
            await self.connection.commit()
            self._stats["queries_executed"] += len(agent_types) + 1
            
            await self._create_event(project_id, "project_created", {
                "project_id": project_id,
                "requirements": requirements[:100] + "..." if len(requirements) > 100 else requirements
            })
            
            return project_id
            
        except Exception as e:
            await self.connection.rollback()
            logger.error(f"Error creating project: {str(e)}")
            self._stats["errors"] += 1
            self._stats["last_error"] = str(e)
            raise

    async def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project by ID"""
        
        try:
            cursor = await self.connection.execute(
                \'\'\'SELECT * FROM projects WHERE id = ?\'\'\',
                (project_id,)
            )
            row = await cursor.fetchone()
            
            if row:
                return {
                    "id": row[0],
                    "requirements": row[1],
                    "status": row[2],
                    "user_id": row[3],
                    "created_at": row[4],
                    "updated_at": row[5],
                    "metadata": json.loads(row[6]) if row[6] else {}
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting project {project_id}: {str(e)}")
            self._stats["errors"] += 1
            self._stats["last_error"] = str(e)
            return None

    async def update_project_status(self, project_id: str, status: str):
        """Update project status"""
        
        try:
            await self.connection.execute(
                \'\'\'UPDATE projects SET status = ?, updated_at = CURRENT_TIMESTAMP 
                   WHERE id = ?\'\'\',
                (status, project_id)
            )
            await self.connection.commit()
            
            await self._create_event(project_id, "project_status_updated", {
                "project_id": project_id,
                "status": status
            })
            
        except Exception as e:
            logger.error(f"Error updating project status: {str(e)}")
            self._stats["errors"] += 1
            self._stats["last_error"] = str(e)
            raise

    # Event Operations for Real-time Updates

    async def _create_event(self, project_id: str, event_type: str, event_data: Dict[str, Any]):
        """Create an event for real-time updates"""
        
        try:
            await self.connection.execute(
                \'\'\'INSERT INTO events (project_id, event_type, event_data) 
                   VALUES (?, ?, ?)\'\'\',
                (project_id, event_type, json.dumps(event_data))
            )
            await self.connection.commit()
            
        except Exception as e:
            logger.error(f"Error creating event: {str(e)}")
            # Don\'t raise here as events are auxiliary

    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        
        try:
            # Get table counts
            tables = ["projects", "agents", "messages", "conflicts", "files", "events"]
            counts = {}
            
            for table in tables:
                cursor = await self.connection.execute(f"SELECT COUNT(*) FROM {table}")
                row = await cursor.fetchone()
                counts[table] = row[0] if row else 0
            
            return {
                **self._stats,
                "table_counts": counts,
                "database_file": self.database_url
            }
            
        except Exception as e:
            logger.error(f"Error getting database stats: {str(e)}")
            return self._stats

    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self.connection is not None

    async def close(self):
        """Close database connection"""
        if self.connection:
            await self.connection.close()
            self.connection = None
            logger.info("Database connection closed")
'''
