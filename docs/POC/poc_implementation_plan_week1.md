# BotArmy POC Implementation Plan

## Executive Summary

This document provides detailed implementation instructions for the BotArmy POC, designed for completion by Developer, Tester, and DevOps roles. The POC uses a simplified architecture focused on rapid delivery using Replit as the single platform for development, hosting, and deployment.

**Target Timeline**: 3 weeks (21 days)
**Platform**: Replit (free tier)
**Architecture**: FastAPI backend + React frontend + SQLite database + SSE real-time updates

## Prerequisites

### Required Accounts and Access
- **Replit Account**: Free tier (upgrade to Hacker plan $7/month if needed for always-on)
- **OpenAI API Key**: Free tier with GPT-4o-mini access
- **GitHub Account**: For version control and backup

### Required Skills
- **Developer**: Python (FastAPI), JavaScript (React), SQL (SQLite)
- **Tester**: Manual testing, basic automation with Python/JavaScript
- **DevOps**: Replit deployment, environment configuration, monitoring

## Week 1: Foundation Setup (Days 1-7)

### Day 1-2: Project Setup and Core Backend

**Developer Tasks:**

1. **Initialize Replit Project**
```bash
# Create new Replit with Python template
# Name: botarmy-poc
# Template: Python
```

2. **Set up project structure**
```
botarmy-poc/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── database.py         # SQLite operations
├── agents.py           # Agent implementations
├── llm_client.py       # OpenAI API client
├── static/             # React build output
├── src/                # React source files
├── data/               # SQLite database and logs
├── tests/              # Test files
└── .replit             # Replit configuration
```

3. **Install dependencies** (requirements.txt)
```txt
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
openai==1.3.0
sqlite3
aiofiles==23.2.1
jinja2==3.1.2
python-json-logger==2.0.7
pytest==7.4.3
httpx==0.25.2
```

4. **Create database schema** (database.py)
```python
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
    
    def add_message(self, project_id: str, from_agent: str, to_agent: str, 
                   message_type: str, content: dict, confidence: float = None) -> str:
        """Add new message to queue"""
        message_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        
        conn.execute('''
            INSERT INTO messages (id, project_id, from_agent, to_agent, message_type, content, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (message_id, project_id, from_agent, to_agent, message_type, json.dumps(content), confidence))
        
        conn.commit()
        conn.close()
        return message_id
    
    def get_pending_messages(self, agent_id: str = None) -> List[Dict]:
        """Get pending messages for agent or all pending messages"""
        conn = sqlite3.connect(self.db_path)
        
        if agent_id:
            cursor = conn.execute('''
                SELECT * FROM messages WHERE to_agent = ? AND status = 'pending'
                ORDER BY timestamp ASC
            ''', (agent_id,))
        else:
            cursor = conn.execute('''
                SELECT * FROM messages WHERE status = 'pending'
                ORDER BY timestamp ASC
            ''')
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'id': row[0], 'project_id': row[1], 'from_agent': row[2],
                'to_agent': row[3], 'message_type': row[4], 'content': json.loads(row[5]),
                'status': row[6], 'confidence': row[7], 'timestamp': row[8]
            })
        
        conn.close()
        return messages
    
    def update_message_status(self, message_id: str, status: str):
        """Update message status"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('UPDATE messages SET status = ? WHERE id = ?', (status, message_id))
        conn.commit()
        conn.close()
    
    def create_project(self, name: str, requirements: str) -> str:
        """Create new project"""
        project_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        
        conn.execute('''
            INSERT INTO projects (id, name, requirements)
            VALUES (?, ?, ?)
        ''', (project_id, name, requirements))
        
        conn.commit()
        conn.close()
        return project_id
    
    def get_project(self, project_id: str) -> Dict:
        """Get project details"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0], 'name': row[1], 'requirements': row[2],
                'spec': json.loads(row[3]) if row[3] else {}, 'status': row[4],
                'version': row[5], 'created_at': row[6], 'updated_at': row[7]
            }
        return None
```

5. **Create LLM client** (llm_client.py)
```python
import asyncio
import json
from typing import Dict, Optional
from openai import AsyncOpenAI
import logging

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"
        self.max_retries = 3
        self.base_delay = 1.0
    
    async def generate_response(self, prompt: str, system_prompt: str = None, 
                              temperature: float = 0.3, max_tokens: int = 2000) -> Dict:
        """Generate response from LLM with retry logic"""
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        for attempt in range(self.max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                content = response.choices[0].message.content
                usage = response.usage
                
                return {
                    "content": content,
                    "tokens_used": usage.total_tokens,
                    "success": True
                }
                
            except Exception as e:
                logger.warning(f"LLM API attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt)  # Exponential backoff
                    await asyncio.sleep(delay)
                else:
                    return {
                        "content": f"LLM API failed after {self.max_retries} attempts: {str(e)}",
                        "tokens_used": 0,
                        "success": False,
                        "error": str(e)
                    }
    
    async def extract_json(self, text: str, schema_description: str) -> Dict:
        """Extract structured JSON from text response"""
        prompt = f"""
        Extract the following information from the text and return as valid JSON:
        Schema: {schema_description}
        
        Text: {text}
        
        Return only valid JSON, no other text:
        """
        
        response = await self.generate_response(prompt, temperature=0.1)
        
        if not response["success"]:
            return {"error": response["error"]}
        
        try:
            return json.loads(response["content"])
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON response: {str(e)}"}
```

**DevOps Tasks:**

1. **Configure Replit environment**
```bash
# .replit file
modules = ["python-3.11"]

[nix]
channel = "stable-23.05"

[deployment]
run = ["python", "main.py"]
deploymentTarget = "cloudrun"

[[ports]]
localPort = 8000
externalPort = 80
```

2. **Set up environment variables**
```bash
# In Replit Secrets tab
OPENAI_API_KEY=your_openai_api_key_here
ENVIRONMENT=development
LOG_LEVEL=INFO
```

3. **Create data directory**
```bash
mkdir -p data/logs
touch data/botarmy.db
```

### Day 3-4: Core Agent Implementation

**Developer Tasks:**

1. **Create base agent class** (agents.py)
```python
import asyncio
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from database import DatabaseManager
from llm_client import LLMClient
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self, agent_id: str, llm_client: LLMClient, db: DatabaseManager):
        self.agent_id = agent_id
        self.llm_client = llm_client
        self.db = db
        self.status = "idle"
        self.current_task = None
        self.max_attempts = 3
        self.confidence_threshold = 0.7
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return system prompt for this agent"""
        pass
    
    @abstractmethod
    async def process_message(self, message: Dict) -> Dict:
        """Process incoming message and return response"""
        pass
    
    async def send_message(self, project_id: str, to_agent: str, message_type: str, 
                          content: Dict, confidence: float = None):
        """Send message to another agent"""
        message_id = self.db.add_message(
            project_id=project_id,
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type=message_type,
            content=content,
            confidence=confidence
        )
        logger.info(f"{self.agent_id} sent message {message_id} to {to_agent}")
        return message_id
    
    async def escalate_to_human(self, project_id: str, issue: str, options: List[Dict]):
        """Escalate decision to human"""
        conn = sqlite3.connect(self.db.db_path)
        action_id = str(uuid.uuid4())
        
        conn.execute('''
            INSERT INTO actions (id, project_id, title, description, priority, options)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (action_id, project_id, f"{self.agent_id} needs decision", 
              issue, "high", json.dumps(options)))
        
        conn.commit()
        conn.close()
        return action_id
    
    def update_status(self, status: str, task: str = None):
        """Update agent status"""
        self.status = status
        self.current_task = task
        logger.info(f"{self.agent_id} status: {status} - {task}")

class AnalystAgent(BaseAgent):
    def __init__(self, llm_client: LLMClient, db: DatabaseManager):
        super().__init__("analyst", llm_client, db)
    
    def get_system_prompt(self) -> str:
        return """You are a Business Analyst AI responsible for analyzing requirements and creating user stories.
        
        Your tasks:
        1. Analyze user requirements for clarity and completeness
        2. Create detailed user stories with acceptance criteria
        3. Identify potential risks and constraints
        4. Generate success metrics
        
        Always respond with structured JSON containing:
        - analysis: Your analysis of the requirements
        - user_stories: Array of user stories with acceptance criteria
        - risks: Identified risks and mitigation strategies
        - success_metrics: Measurable success criteria
        - confidence: Your confidence score (0.0 to 1.0)
        - next_steps: What should happen next
        
        Be concise but thorough. Ask for clarification if requirements are unclear."""
    
    async def process_message(self, message: Dict) -> Dict:
        """Process requirements and create analysis"""
        self.update_status("thinking", "Analyzing requirements")
        
        content = message["content"]
        project_id = message["project_id"]
        
        if message["message_type"] == "start_analysis":
            requirements = content.get("requirements", "")
            
            prompt = f"""
            Analyze these product requirements and create a comprehensive analysis:
            
            Requirements: {requirements}
            
            Create user stories, identify risks, and suggest success metrics.
            Respond with JSON only.
            """
            
            response = await self.llm_client.generate_response(
                prompt=prompt,
                system_prompt=self.get_system_prompt(),
                temperature=0.3
            )
            
            if response["success"]:
                try:
                    analysis = json.loads(response["content"])
                    confidence = analysis.get("confidence", 0.8)
                    
                    # Send to architect
                    await self.send_message(
                        project_id=project_id,
                        to_agent="architect",
                        message_type="handoff",
                        content=analysis,
                        confidence=confidence
                    )
                    
                    self.update_status("idle", "Analysis complete")
                    
                    return {
                        "status": "complete",
                        "analysis": analysis,
                        "tokens_used": response["tokens_used"]
                    }
                    
                except json.JSONDecodeError:
                    self.update_status("error", "Invalid JSON response from LLM")
                    return {"status": "error", "message": "Invalid analysis format"}
            else:
                self.update_status("error", f"LLM error: {response['error']}")
                return {"status": "error", "message": response["error"]}

class ArchitectAgent(BaseAgent):
    def __init__(self, llm_client: LLMClient, db: DatabaseManager):
        super().__init__("architect", llm_client, db)
    
    def get_system_prompt(self) -> str:
        return """You are a Software Architect AI responsible for creating technical designs.
        
        Your tasks:
        1. Review business analysis and user stories
        2. Create system architecture and component design
        3. Select appropriate technology stack
        4. Design API specifications and data models
        5. Plan deployment and infrastructure
        
        Always respond with structured JSON containing:
        - architecture: High-level system design
        - components: List of components with responsibilities
        - tech_stack: Selected technologies with justification
        - api_design: API endpoints and data models
        - deployment_plan: Infrastructure and deployment strategy
        - confidence: Your confidence score (0.0 to 1.0)
        - concerns: Any technical concerns or trade-offs
        
        Focus on simple, maintainable solutions for POC development."""
    
    async def process_message(self, message: Dict) -> Dict:
        """Process analysis and create architecture"""
        self.update_status("thinking", "Creating architecture")
        
        content = message["content"]
        project_id = message["project_id"]
        
        if message["message_type"] == "handoff":
            analysis = content
            
            prompt = f"""
            Based on this business analysis, create a technical architecture:
            
            Analysis: {json.dumps(analysis, indent=2)}
            
            Design a simple, maintainable architecture suitable for a POC.
            Focus on React frontend, FastAPI backend, and SQLite database.
            Respond with JSON only.
            """
            
            response = await self.llm_client.generate_response(
                prompt=prompt,
                system_prompt=self.get_system_prompt(),
                temperature=0.2
            )
            
            if response["success"]:
                try:
                    architecture = json.loads(response["content"])
                    confidence = architecture.get("confidence", 0.8)
                    
                    # Send to developer
                    await self.send_message(
                        project_id=project_id,
                        to_agent="developer",
                        message_type="handoff",
                        content={
                            "analysis": analysis,
                            "architecture": architecture
                        },
                        confidence=confidence
                    )
                    
                    self.update_status("idle", "Architecture complete")
                    
                    return {
                        "status": "complete",
                        "architecture": architecture,
                        "tokens_used": response["tokens_used"]
                    }
                    
                except json.JSONDecodeError:
                    self.update_status("error", "Invalid JSON response from LLM")
                    return {"status": "error", "message": "Invalid architecture format"}
            else:
                self.update_status("error", f"LLM error: {response['error']}")
                return {"status": "error", "message": response["error"]}

# Additional agent classes (DeveloperAgent, TesterAgent) follow similar pattern...
```

2. **Create main FastAPI application** (main.py - Part 1)
```python
import os
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

# Local imports
from database import DatabaseManager
from llm_client import LLMClient
from agents import AnalystAgent, ArchitectAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
app = FastAPI(title="BotArmy POC", version="1.0.0")
db = DatabaseManager()
llm_client = LLMClient(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize agents
agents = {
    "analyst": AnalystAgent(llm_client, db),
    "architect": ArchitectAgent(llm_client, db),
    # Add more agents as implemented
}

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests
class ProjectCreateRequest(BaseModel):
    name: str
    requirements: str

class ActionResponseRequest(BaseModel):
    action_id: str
    response: str

# Global state for SSE connections
sse_connections = {}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Create new project
@app.post("/api/projects")
async def create_project(request: ProjectCreateRequest, background_tasks: BackgroundTasks):
    try:
        project_id = db.create_project(request.name, request.requirements)
        
        # Start analysis in background
        background_tasks.add_task(start_agent_workflow, project_id, request.requirements)
        
        return {"project_id": project_id, "status": "created"}
    
    except Exception as e:
        logger.error(f"Failed to create project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Get project details
@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project

# Get project messages
@app.get("/api/projects/{project_id}/messages")
async def get_messages(project_id: str, limit: int = 50):
    conn = sqlite3.connect(db.db_path)
    cursor = conn.execute('''
        SELECT * FROM messages WHERE project_id = ?
        ORDER BY timestamp DESC LIMIT ?
    ''', (project_id, limit))
    
    messages = []
    for row in cursor.fetchall():
        messages.append({
            'id': row[0], 'from_agent': row[2], 'to_agent': row[3],
            'message_type': row[4], 'content': json.loads(row[5]),
            'status': row[6], 'confidence': row[7], 'timestamp': row[8]
        })
    
    conn.close()
    return {"messages": messages}

# Get pending actions for human intervention
@app.get("/api/projects/{project_id}/actions")
async def get_actions(project_id: str):
    conn = sqlite3.connect(db.db_path)
    cursor = conn.execute('''
        SELECT * FROM actions WHERE project_id = ? AND status = 'pending'
        ORDER BY created_at DESC
    ''', (project_id,))
    
    actions = []
    for row in cursor.fetchall():
        actions.append({
            'id': row[0], 'title': row[2], 'description': row[3],
            'priority': row[4], 'options': json.loads(row[6]) if row[6] else [],
            'created_at': row[8]
        })
    
    conn.close()
    return {"actions": actions}

# Submit human action response
@app.post("/api/actions/respond")
async def respond_to_action(request: ActionResponseRequest):
    conn = sqlite3.connect(db.db_path)
    
    conn.execute('''
        UPDATE actions SET status = 'resolved', response = ?, resolved_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (request.response, request.action_id))
    
    conn.commit()
    conn.close()
    
    return {"status": "resolved"}

# Server-Sent Events endpoint for real-time updates
@app.get("/api/stream/{project_id}")
async def stream_updates(project_id: str):
    async def generate():
        # Send initial connection message
        yield f"data: {json.dumps({'type': 'connected', 'timestamp': datetime.utcnow().isoformat()})}\n\n"
        
        last_check = datetime.utcnow()
        
        while True:
            try:
                # Check for new messages
                conn = sqlite3.connect(db.db_path)
                cursor = conn.execute('''
                    SELECT * FROM messages WHERE project_id = ? AND timestamp > ?
                    ORDER BY timestamp ASC
                ''', (project_id, last_check.isoformat()))
                
                for row in cursor.fetchall():
                    message = {
                        'type': 'message',
                        'id': row[0],
                        'from_agent': row[2],
                        'to_agent': row[3],
                        'message_type': row[4],
                        'content': json.loads(row[5]),
                        'status': row[6],
                        'confidence': row[7],
                        'timestamp': row[8]
                    }
                    yield f"data: {json.dumps(message)}\n\n"
                
                # Check for new actions
                cursor = conn.execute('''
                    SELECT * FROM actions WHERE project_id = ? AND created_at > ?
                    ORDER BY created_at ASC
                ''', (project_id, last_check.isoformat()))
                
                for row in cursor.fetchall():
                    action = {
                        'type': 'action',
                        'id': row[0],
                        'title': row[2],
                        'description': row[3],
                        'priority': row[4],
                        'options': json.loads(row[6]) if row[6] else [],
                        'created_at': row[8]
                    }
                    yield f"data: {json.dumps(action)}\n\n"
                
                conn.close()
                last_check = datetime.utcnow()
                
                # Send agent status updates
                agent_statuses = {
                    'type': 'agent_status',
                    'agents': {
                        agent_id: {
                            'status': agent.status,
                            'current_task': agent.current_task
                        } for agent_id, agent in agents.items()
                    },
                    'timestamp': datetime.utcnow().isoformat()
                }
                yield f"data: {json.dumps(agent_statuses)}\n\n"
                
                await asyncio.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                logger.error(f"SSE error: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                break
    
    return StreamingResponse(generate(), media_type="text/plain")

# Background task to run agent workflow
async def start_agent_workflow(project_id: str, requirements: str):
    """Start the agent workflow for a project"""
    try:
        logger.info(f"Starting workflow for project {project_id}")
        
        # Send initial message to analyst
        message_id = db.add_message(
            project_id=project_id,
            from_agent="system",
            to_agent="analyst",
            message_type="start_analysis",
            content={"requirements": requirements},
            confidence=1.0
        )
        
        # Process messages in a loop
        await process_message_queue()
        
    except Exception as e:
        logger.error(f"Workflow error: {str(e)}")

async def process_message_queue():
    """Process pending messages in the queue"""
    while True:
        try:
            # Get pending messages
            pending_messages = db.get_pending_messages()
            
            if not pending_messages:
                await asyncio.sleep(5)  # Wait before checking again
                continue
            
            for message in pending_messages:
                to_agent = message["to_agent"]
                
                if to_agent in agents:
                    agent = agents[to_agent]
                    
                    # Mark message as processing
                    db.update_message_status(message["id"], "processing")
                    
                    # Process message
                    try:
                        result = await agent.process_message(message)
                        
                        if result["status"] == "complete":
                            db.update_message_status(message["id"], "completed")
                        else:
                            db.update_message_status(message["id"], "error")
                            logger.error(f"Agent {to_agent} failed: {result.get('message', 'Unknown error')}")
                    
                    except Exception as e:
                        logger.error(f"Error processing message {message['id']}: {str(e)}")
                        db.update_message_status(message["id"], "error")
                
                else:
                    logger.warning(f"No agent found for: {to_agent}")
                    db.update_message_status(message["id"], "error")
            
            await asyncio.sleep(1)  # Brief pause between processing cycles
            
        except Exception as e:
            logger.error(f"Message queue processing error: {str(e)}")
            await asyncio.sleep(5)

# Serve static files (React app)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    
    # Start message processing in background
    asyncio.create_task(process_message_queue())
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Tester Tasks:**

1. **Create basic test structure**
```python
# tests/test_database.py
import pytest
import os
import tempfile
from database import DatabaseManager

class TestDatabaseManager:
    def setup_method(self):
        # Create temporary database for testing
        self.db_file = tempfile.NamedTemporaryFile(delete=False)
        self.db = DatabaseManager(self.db_file.name)
    
    def teardown_method(self):
        # Clean up
        os.unlink(self.db_file.name)
    
    def test_create_project(self):
        project_id = self.db.create_project("Test Project", "Test requirements")
        assert project_id is not None
        
        project = self.db.get_project(project_id)
        assert project["name"] == "Test Project"
        assert project["requirements"] == "Test requirements"
    
    def test_add_message(self):
        project_id = self.db.create_project("Test", "Test")
        
        message_id = self.db.add_message(
            project_id=project_id,
            from_agent="analyst",
            to_agent="architect",
            message_type="handoff",
            content={"test": "data"},
            confidence=0.8
        )
        
        messages = self.db.get_pending_messages("architect")
        assert len(messages) == 1
        assert messages[0]["id"] == message_id
        assert messages[0]["confidence"] == 0.8
```

2. **Create API test cases**
```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestAPI:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_create_project(self):
        project_data = {
            "name": "Test Project",
            "requirements": "Build a simple web app"
        }
        
        response = client.post("/api/projects", json=project_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "project_id" in data
        assert data["status"] == "created"
    
    def test_get_project(self):
        # First create a project
        project_data = {
            "name": "Test Project",
            "requirements": "Build a simple web app"
        }
        
        create_response = client.post("/api/projects", json=project_data)
        project_id = create_response.json()["project_id"]
        
        # Then retrieve it
        response = client.get(f"/api/projects/{project_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Test Project"
        assert data["requirements"] == "Build a simple web app"
```

### Day 5-7: Basic Frontend and Integration

**Developer Tasks:**

1. **Create React application structure**
```bash
# Install Node.js dependencies (using Replit package manager)
# In Replit shell:
npm init -y
npm install react react-dom @vitejs/plugin-react vite
npm install @heroicons/react classnames
```

2. **Create Vite configuration** (vite.config.js)
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'static',
    emptyOutDir: true,
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

3. **Create main React components** (src/App.jsx)
```javascript
import React, { useState, useEffect, createContext, useContext } from 'react';
import './App.css';

// Global state context
const AppContext = createContext();

// Main App component
export default function App() {
  const [state, setState] = useState({
    project: null,
    messages: [],
    actions: [],
    agents: {
      analyst: { status: 'idle', current_task: null },
      architect: { status: 'idle', current_task: null },
      developer: { status: 'idle', current_task: null },
      tester: { status: 'idle', current_task: null }
    },
    connected: false
  });

  const updateState = (updates) => {
    setState(prev => ({ ...prev, ...updates }));
  };

  return (
    <AppContext.Provider value={{ ...state, updateState }}>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="container mx-auto px-4 py-8">
          {!state.project ? <ProjectSetup /> : <Dashboard />}
        </main>
      </div>
    </AppContext.Provider>
  );
}

// Header component
function Header() {
  const { project } = useContext(AppContext);
  
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">
            BotArmy POC
          </h1>
          {project && (
            <div className="text-sm text-gray-600">
              Project: <span className="font-medium">{project.name}</span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

// Project setup form
function ProjectSetup() {
  const { updateState } = useContext(AppContext);
  const [formData, setFormData] = useState({
    name: '',
    requirements: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('/api/projects', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const data = await response.json();
        
        // Fetch project details
        const projectResponse = await fetch(`/api/projects/${data.project_id}`);
        const project = await projectResponse.json();
        
        updateState({ project });
        
        // Start SSE connection
        startSSEConnection(data.project_id, updateState);
      } else {
        console.error('Failed to create project');
      }
    } catch (error) {
      console.error('Error creating project:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Create New Project</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Project Name
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter project name..."
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Requirements
            </label>
            <textarea
              value={formData.requirements}
              onChange={(e) => setFormData(prev => ({ ...prev, requirements: e.target.value }))}
              rows={6}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Describe what you want to build..."
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Creating Project...' : 'Create Project'}
          </button>
        </form>
      </div>
    </div>
  );
}

// Main dashboard
function Dashboard() {
  const { project, messages, actions, agents, connected } = useContext(AppContext);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      {/* Agent Status Panel */}
      <div className="lg:col-span-1">
        <AgentStatusPanel agents={agents} connected={connected} />
      </div>
      
      {/* Main Content */}
      <div className="lg:col-span-2">
        <MessagePanel messages={messages} />
      </div>
      
      {/* Action Queue */}
      <div className="lg:col-span-1">
        <ActionPanel actions={actions} />
      </div>
    </div>
  );
}

// Agent status panel
function AgentStatusPanel({ agents, connected }) {
  const getStatusColor = (status) => {
    switch (status) {
      case 'thinking': return 'bg-yellow-100 text-yellow-800';
      case 'waiting': return 'bg-blue-100 text-blue-800';
      case 'error': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'thinking': return '🤔';
      case 'waiting': return '⏳';
      case 'error': return '❌';
      default: return '⚪';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Agent Status</h3>
        <div className={`px-2 py-1 rounded-full text-xs ${connected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
          {connected ? 'Connected' : 'Disconnected'}
        </div>
      </div>
      
      <div className="space-y-3">
        {Object.entries(agents).map(([agentId, agent]) => (
          <div key={agentId} className="border rounded-lg p-3">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium capitalize">{agentId}</span>
              <span className="text-lg">{getStatusIcon(agent.status)}</span>
            </div>
            
            <div className={`px-2 py-1 rounded-full text-xs ${getStatusColor(agent.status)}`}>
              {agent.status}
            </div>
            
            {agent.current_task && (
              <div className="mt-2 text-xs text-gray-600">
                {agent.current_task}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// Message panel
function MessagePanel({ messages }) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-semibold mb-4">Agent Conversations</h3>
      
      <div className="space-y-4 max-h-96 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            No messages yet. Agents will start working once the project is created.
          </div>
        ) : (
          messages.map((message, index) => (
            <MessageBubble key={index} message={message} />
          ))
        )}
      </div>
    </div>
  );
}

// Individual message bubble
function MessageBubble({ message }) {
  const getAgentColor = (agent) => {
    const colors = {
      analyst: 'bg-blue-100 text-blue-800',
      architect: 'bg-green-100 text-green-800',
      developer: 'bg-purple-100 text-purple-800',
      tester: 'bg-orange-100 text-orange-800',
      system: 'bg-gray-100 text-gray-800'
    };
    return colors[agent] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="border rounded-lg p-3">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <span className={`px-2 py-1 rounded-full text-xs ${getAgentColor(message.from_agent)}`}>
            {message.from_agent}
          </span>
          {message.to_agent && (
            <>
              <span className="text-gray-400">→</span>
              <span className={`px-2 py-1 rounded-full text-xs ${getAgentColor(message.to_agent)}`}>
                {message.to_agent}
              </span>
            </>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          {message.confidence && (
            <span className="text-xs text-gray-500">
              {Math.round(message.confidence * 100)}%
            </span>
          )}
          <span className="text-xs text-gray-500">
            {new Date(message.timestamp).toLocaleTimeString()}
          </span>
        </div>
      </div>
      
      <div className="text-sm">
        {typeof message.content === 'string' ? (
          <p>{message.content}</p>
        ) : (
          <details className="cursor-pointer">
            <summary className="font-medium">
              {message.message_type}: {message.content.summary || 'View Details'}
            </summary>
            <pre className="mt-2 text-xs bg-gray-50 p-2 rounded overflow-x-auto">
              {JSON.stringify(message.content, null, 2)}
            </pre>
          </details>
        )}
      </div>
    </div>
  );
}

// Action panel for human interventions
function ActionPanel({ actions }) {
  const { updateState } = useContext(AppContext);

  const handleActionResponse = async (actionId, response) => {
    try {
      await fetch('/api/actions/respond', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action_id: actionId,
          response: response
        }),
      });

      // Remove action from list
      updateState({
        actions: actions.filter(action => action.id !== actionId)
      });
    } catch (error) {
      console.error('Error responding to action:', error);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-semibold mb-4">Action Required</h3>
      
      {actions.length === 0 ? (
        <div className="text-center text-gray-500 py-8">
          No actions required
        </div>
      ) : (
        <div className="space-y-4">
          {actions.map((action) => (
            <ActionItem
              key={action.id}
              action={action}
              onRespond={handleActionResponse}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// Individual action item
function ActionItem({ action, onRespond }) {
  const [selectedOption, setSelectedOption] = useState('');
  const [customResponse, setCustomResponse] = useState('');

  const handleSubmit = () => {
    const response = selectedOption || customResponse;
    if (response.trim()) {
      onRespond(action.id, response);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  return (
    <div className={`border rounded-lg p-4 ${getPriorityColor(action.priority)}`}>
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-medium">{action.title}</h4>
        <span className="text-xs px-2 py-1 rounded-full bg-white bg-opacity-50">
          {action.priority}
        </span>
      </div>
      
      <p className="text-sm mb-3">{action.description}</p>
      
      {action.options && action.options.length > 0 && (
        <div className="mb-3">
          <label className="block text-xs font-medium mb-2">Choose an option:</label>
          <select
            value={selectedOption}
            onChange={(e) => setSelectedOption(e.target.value)}
            className="w-full px-2 py-1 text-sm border rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">Select option...</option>
            {action.options.map((option, index) => (
              <option key={index} value={option.id || option}>
                {option.label || option}
              </option>
            ))}
          </select>
        </div>
      )}
      
      <div className="mb-3">
        <label className="block text-xs font-medium mb-2">Or provide custom response:</label>
        <textarea
          value={customResponse}
          onChange={(e) => setCustomResponse(e.target.value)}
          rows={3}
          className="w-full px-2 py-1 text-sm border rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
          placeholder="Enter your response..."
        />
      </div>
      
      <button
        onClick={handleSubmit}
        disabled={!selectedOption && !customResponse.trim()}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded text-sm hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Submit Response
      </button>
    </div>
  );
}

// Server-Sent Events connection
function startSSEConnection(projectId, updateState) {
  const eventSource = new EventSource(`/api/stream/${projectId}`);
  
  eventSource.onopen = () => {
    updateState({ connected: true });
  };
  
  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'connected':
          updateState({ connected: true });
          break;
          
        case 'message':
          updateState(prevState => ({
            messages: [...prevState.messages, data].slice(-50) // Keep last 50 messages
          }));
          break;
          
        case 'action':
          updateState(prevState => ({
            actions: [...prevState.actions, data]
          }));
          break;
          
        case 'agent_status':
          updateState({ agents: data.agents });
          break;
          
        case 'error':
          console.error('SSE error:', data.message);
          break;
      }
    } catch (error) {
      console.error('Error parsing SSE data:', error);
    }
  };
  
  eventSource.onerror = () => {
    updateState({ connected: false });
    
    // Attempt to reconnect after 5 seconds
    setTimeout(() => {
      startSSEConnection(projectId, updateState);
    }, 5000);
  };
  
  return eventSource;
}
```

4. **Create CSS styles** (src/App.css)
```css
/* Basic Tailwind-like utility classes for styling */
.container {
  max-width: 1200px;
}

.grid {
  display: grid;
}

.grid-cols-1 {
  grid-template-columns: repeat(1, minmax(0, 1fr));
}

.grid-cols-4 {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.col-span-1 {
  grid-column: span 1 / span 1;
}

.col-span-2 {
  grid-column: span 2 / span 2;
}

.gap-6 {
  gap: 1.5rem;
}

.space-y-3 > * + * {
  margin-top: 0.75rem;
}

.space-y-4 > * + * {
  margin-top: 1rem;
}

.space-x-2 > * + * {
  margin-left: 0.5rem;
}

.max-h-96 {
  max-height: 24rem;
}

.overflow-y-auto {
  overflow-y: auto;
}

.overflow-x-auto {
  overflow-x: auto;
}

/* Custom scrollbar for better UX */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Animation for new messages */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-bubble {
  animation: slideIn 0.3s ease-out;
}

/* Status indicator pulse animation */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.status-thinking {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
```

5. **Create HTML template** (static/index.html)
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BotArmy POC</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    /* Custom animations and styles */
    @keyframes slideIn {
      from {
        opacity: 0;
        transform: translateY(10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
    
    .message-bubble {
      animation: slideIn 0.3s ease-out;
    }
    
    @keyframes pulse {
      0%, 100% {
        opacity: 1;
      }
      50% {
        opacity: 0.5;
      }
    }
    
    .status-thinking {
      animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
  </style>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>
```

6. **Create React entry point** (src/main.jsx)
```javascript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

**DevOps Tasks:**

1. **Update Replit configuration**
```bash
# Update .replit file
modules = ["python-3.11", "nodejs-18"]

[nix]
channel = "stable-23.05"

[deployment]
run = ["sh", "-c", "cd /home/runner/botarmy-poc && python main.py"]
deploymentTarget = "cloudrun"

[[ports]]
localPort = 8000
externalPort = 80

[env]
PYTHONPATH = "/home/runner/botarmy-poc"
NODE_ENV = "production"
```

2. **Create startup script** (start.sh)
```bash
#!/bin/bash
echo "Starting BotArmy POC..."

# Check if static files exist, if not build them
if [ ! -d "static" ] || [ ! -f "static/index.html" ]; then
    echo "Building frontend..."
    npm run build
fi

# Start the FastAPI server
echo "Starting backend server..."
python main.py
```

3. **Add build scripts to package.json**
```json
{
  "name": "botarmy-poc-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.0.0",
    "vite": "^4.3.0"
  }
}
```

**Tester Tasks:**

1. **Create end-to-end test scenarios**
```python
# tests/test_integration.py
import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from main import app

class TestIntegration:
    def setup_method(self):
        self.client = TestClient(app)
    
    def test_complete_workflow(self):
        """Test the complete agent workflow"""
        # 1. Create project
        project_data = {
            "name": "Test E-commerce App",
            "requirements": "Build a simple e-commerce web application with user authentication, product catalog, and shopping cart functionality."
        }
        
        response = self.client.post("/api/projects", json=project_data)
        assert response.status_code == 200
        
        project_id = response.json()["project_id"]
        
        # 2. Wait a bit for agents to start processing
        import time
        time.sleep(5)
        
        # 3. Check for messages
        response = self.client.get(f"/api/projects/{project_id}/messages")
        assert response.status_code == 200
        
        messages = response.json()["messages"]
        assert len(messages) > 0
        
        # 4. Check if analyst has produced analysis
        analyst_messages = [m for m in messages if m["from_agent"] == "analyst"]
        assert len(analyst_messages) > 0
        
        # 5. Verify message content structure
        for message in analyst_messages:
            assert "content" in message
            assert message["confidence"] is not None
    
    def test_human_escalation(self):
        """Test human escalation workflow"""
        # This would test scenarios where agents need human input
        # Implementation depends on specific escalation triggers
        pass
    
    def test_error_handling(self):
        """Test error handling scenarios"""
        # Test invalid project creation
        response = self.client.post("/api/projects", json={"name": "", "requirements": ""})
        assert response.status_code == 422  # Validation error
        
        # Test non-existent project
        response = self.client.get("/api/projects/nonexistent")
        assert response.status_code == 404
```

## Week 2: Agent Pipeline Development (Days 8-14)

### Day 8-9: Complete Agent Implementation

**Developer Tasks:**

1. **Complete DeveloperAgent and TesterAgent classes** (Add to agents.py)
```python
class DeveloperAgent(BaseAgent):
    def __init__(self, llm_client: LLMClient, db: DatabaseManager):
        super().__init__("developer", llm_client, db)
    
    def get_system_prompt(self) -> str:
        return """You are a Software Developer AI responsible for implementing code based on architecture specifications.
        
        Your tasks:
        1. Review architecture specifications and technical requirements
        2. Generate functional code modules (frontend, backend, database)
        3. Create API implementations and data models
        4. Write clean, documented, and maintainable code
        5. Ensure code follows best practices and patterns
        
        Always respond with structured JSON containing:
        - implementation_plan: Step-by-step development plan
        - code_modules: Generated code organized by component
        - api_endpoints: Complete API implementation
        - database_schema: Database tables and relationships
        - frontend_components: React components and UI logic
        - confidence: Your confidence score (0.0 to 1.0)
        - testing_notes: Guidelines for testing the implementation
        
        Focus on creating working, deployable code for POC environments."""
    
    async def process_message(self, message: Dict) -> Dict:
        """Process architecture and generate code"""
        self.update_status("thinking", "Generating code implementation")
        
        content = message["content"]
        project_id = message["project_id"]
        
        if message["message_type"] == "handoff":
            analysis = content.get("analysis", {})
            architecture = content.get("architecture", {})
            
            prompt = f"""
            Based on this analysis and architecture, generate a complete code implementation:
            
            Business Analysis: {json.dumps(analysis, indent=2)}
            
            Technical Architecture: {json.dumps(architecture, indent=2)}
            
            Generate working code for all components including:
            - FastAPI backend with all necessary endpoints
            - React frontend with complete UI components
            - SQLite database schema and operations
            - Authentication and authorization (if required)
            - Error handling and validation
            
            Focus on creating deployable, working code suitable for Replit hosting.
            Respond with JSON only.
            """
            
            response = await self.llm_client.generate_response(
                prompt=prompt,
                system_prompt=self.get_system_prompt(),
                temperature=0.1,
                max_tokens=4000
            )
            
            if response["success"]:
                try:
                    implementation = json.loads(response["content"])
                    confidence = implementation.get("confidence", 0.8)
                    
                    # Save generated code to files
                    await self._save_code_artifacts(project_id, implementation)
                    
                    # Send to tester
                    await self.send_message(
                        project_id=project_id,
                        to_agent="tester",
                        message_type="handoff",
                        content={
                            "analysis": analysis,
                            "architecture": architecture,
                            "implementation": implementation
                        },
                        confidence=confidence
                    )
                    
                    self.update_status("idle", "Implementation complete")
                    
                    return {
                        "status": "complete",
                        "implementation": implementation,
                        "tokens_used": response["tokens_used"]
                    }
                    
                except json.JSONDecodeError:
                    self.update_status("error", "Invalid JSON response from LLM")
                    return {"status": "error", "message": "Invalid implementation format"}
            else:
                self.update_status("error", f"LLM error: {response['error']}")
                return {"status": "error", "message": response["error"]}
    
    async def _save_code_artifacts(self, project_id: str, implementation: Dict):
        """Save generated code to files"""
        import os
        import aiofiles
        
        # Create project directory
        project_dir = f"data/generated/{project_id}"
        os.makedirs(project_dir, exist_ok=True)
        