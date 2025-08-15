import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional


class DatabaseManager:

    def __init__(self, db_path: str = "data/botarmy.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)

        # Messages table for agent communication
        conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                from_agent TEXT NOT NULL,
                to_agent TEXT,
                message_type TEXT NOT NULL,
                content TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                confidence REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                thread_id TEXT,
                attempt_number INTEGER DEFAULT 1
            )
        ''')

        # Projects table for project specifications
        conn.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                requirements TEXT NOT NULL,
                spec TEXT,
                status TEXT DEFAULT 'active',
                version INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Actions table for human interventions
        conn.execute('''
            CREATE TABLE IF NOT EXISTS actions (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                options TEXT,
                response TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                resolved_at DATETIME
            )
        ''')

        conn.commit()
        conn.close()

    def add_message(self,
                    project_id: str,
                    from_agent: str,
                    to_agent: str,
                    message_type: str,
                    content: dict,
                    confidence: float = None) -> str:
        """Add new message to queue"""
        message_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)

        conn.execute(
            '''
            INSERT INTO messages (id, project_id, from_agent, to_agent, message_type, content, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (message_id, project_id, from_agent, to_agent, message_type,
              json.dumps(content), confidence))

        conn.commit()
        conn.close()
        return message_id

    def get_pending_messages(self, agent_id: str = None) -> List[Dict]:
        """Get pending messages for agent or all pending messages"""
        conn = sqlite3.connect(self.db_path)

        if agent_id:
            cursor = conn.execute(
                '''
                SELECT * FROM messages WHERE to_agent = ? AND status = 'pending'
                ORDER BY timestamp ASC
            ''', (agent_id, ))
        else:
            cursor = conn.execute('''
                SELECT * FROM messages WHERE status = 'pending'
                ORDER BY timestamp ASC
            ''')

        messages = []
        for row in cursor.fetchall():
            messages.append({
                'id': row[0],
                'project_id': row[1],
                'from_agent': row[2],
                'to_agent': row[3],
                'message_type': row[4],
                'content': json.loads(row[5]),
                'status': row[6],
                'confidence': row[7],
                'timestamp': row[8]
            })

        conn.close()
        return messages

    def update_message_status(self, message_id: str, status: str):
        """Update message status"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('UPDATE messages SET status = ? WHERE id = ?',
                     (status, message_id))
        conn.commit()
        conn.close()

    def create_project(self, name: str, requirements: str) -> str:
        """Create new project"""
        project_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)

        conn.execute(
            '''
            INSERT INTO projects (id, name, requirements)
            VALUES (?, ?, ?)
        ''', (project_id, name, requirements))

        conn.commit()
        conn.close()
        return project_id

    def get_project(self, project_id: str) -> Dict:
        """Get project details"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('SELECT * FROM projects WHERE id = ?',
                              (project_id, ))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row[0],
                'name': row[1],
                'requirements': row[2],
                'spec': json.loads(row[3]) if row[3] else {},
                'status': row[4],
                'version': row[5],
                'created_at': row[6],
                'updated_at': row[7]
            }
        return None
