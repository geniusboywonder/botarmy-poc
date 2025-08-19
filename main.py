import os
import asyncio
import json
import sqlite3
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

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - handles startup and shutdown"""
    # Create test project on startup without triggering agent processing
    try:
        existing = db.get_project('proj_49583')
        if not existing:
            logger.info("Creating test project...")
            db.create_project_with_id('proj_49583', 'Test Project', 'A test project for development')
            
            # Add a sample task/action for the action queue (non-processed)
            conn = sqlite3.connect(db.db_path)
            conn.execute(
                '''
                INSERT INTO actions (id, project_id, title, description, priority, options)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (str(uuid.uuid4()), 'proj_49583', 
                  'Welcome Task', 
                  'This is a sample task to demonstrate the interface. Use chat with @agent mentions to interact.',
                  'low', 
                  json.dumps(['Acknowledge', 'Dismiss'])))
            )
            conn.commit()
            conn.close()
            
            logger.info("Test project created successfully with sample data")
    except Exception as e:
        logger.error(f"Failed to create test project: {str(e)}")
    
    # Test OpenAI connection without using quota
    try:
        if os.getenv("OPENAI_API_KEY"):
            logger.info("OpenAI API key detected - Ready for agent interactions")
        else:
            logger.warning("No OpenAI API key found - Agents will not function")
    except Exception as e:
        logger.error(f"OpenAI connection test failed: {str(e)}")
    
    # No automatic background processing - agents only work when called via chat
    yield
    # Cleanup (nothing to cancel since no background tasks)

# Initialize components
app = FastAPI(title="BotArmy POC", version="1.0.0", lifespan=lifespan)
db = DatabaseManager()
llm_client = LLMClient(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize agents with mock implementations for missing agents
class MockAgent:
    def __init__(self, agent_id, llm_client, db):
        self.id = agent_id
        self.llm_client = llm_client
        self.db = db
        # Give some variety to the mock agents
        if agent_id == "developer":
            self.status = 'working'
            self.current_task = 'Implementing user authentication system'
        else:  # tester
            self.status = 'idle' 
            self.current_task = None
        
    async def process_message(self, message):
        # Mock implementation
        return {"status": "complete", "message": f"Mock {self.id} processed message"}

# Initialize agents
agents = {
    "analyst": AnalystAgent(llm_client, db),
    "architect": ArchitectAgent(llm_client, db),
    "developer": MockAgent("developer", llm_client, db),
    "tester": MockAgent("tester", llm_client, db),
}

# Set all agents to idle status initially - no auto-processing
agents["analyst"].status = 'idle'
agents["analyst"].current_task = 'Ready for instructions'
agents["architect"].status = 'idle'
agents["architect"].current_task = 'Ready for instructions'

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
async def create_project(request: ProjectCreateRequest,
                         background_tasks: BackgroundTasks):
    """Create new project without triggering automatic agent processing"""
    try:
        project_id = db.create_project(request.name, request.requirements)

        # Do NOT start automatic analysis - agents only respond to chat commands
        logger.info(f"Project {project_id} created. Use chat with @agent mentions to interact.")

        return {"project_id": project_id, "status": "created", "message": "Use chat with @agent mentions to interact"}

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
    cursor = conn.execute(
        '''
        SELECT * FROM messages WHERE project_id = ?
        ORDER BY timestamp DESC LIMIT ?
    ''', (project_id, limit))

    messages = []
    for row in cursor.fetchall():
        messages.append({
            'id': row[0],
            'from_agent': row[2],
            'to_agent': row[3],
            'message_type': row[4],
            'content': json.loads(row[5]),
            'status': row[6],
            'confidence': row[7],
            'timestamp': row[8]
        })

    conn.close()
    return {"messages": messages}


# Get pending actions for human intervention
@app.get("/api/projects/{project_id}/actions")
async def get_actions(project_id: str):
    conn = sqlite3.connect(db.db_path)
    cursor = conn.execute(
        '''
        SELECT * FROM actions WHERE project_id = ? AND status = 'pending'
        ORDER BY created_at DESC
    ''', (project_id, ))

    actions = []
    for row in cursor.fetchall():
        actions.append({
            'id': row[0],
            'title': row[2],
            'description': row[3],
            'priority': row[4],
            'options': json.loads(row[6]) if row[6] else [],
            'created_at': row[8]
        })

    conn.close()
    return {"actions": actions}


# Submit human action response
@app.post("/api/actions/respond")
async def respond_to_action(request: ActionResponseRequest):
    conn = sqlite3.connect(db.db_path)

    conn.execute(
        '''
        UPDATE actions SET status = 'resolved', response = ?, resolved_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (request.response, request.action_id))

    conn.commit()
    conn.close()

    return {"status": "resolved"}


# Global API Endpoints for Frontend Integration
@app.get("/api/agents")
async def get_agents():
    """Get all agent statuses - Global endpoint for frontend"""
    try:
        return {
            "agents": [
                {
                    "id": agent_id,
                    "role": agent_id.title(),
                    "status": getattr(agent, 'status', 'idle'),
                    "current_task": getattr(agent, 'current_task', None),
                    "queue": {
                        "todo": 0,
                        "inProgress": 1 if getattr(agent, 'status', 'idle') == 'working' else 0,
                        "done": 0,
                        "failed": 0
                    },
                    "expanded": False,
                    "chat": [],
                    "handoff": None
                }
                for agent_id, agent in agents.items()
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching agents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks")  
async def get_global_tasks():
    """Get tasks across all projects - Global endpoint for frontend"""
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.execute(
            '''SELECT id, project_id, title, description, priority, created_at 
               FROM actions WHERE status = 'pending'
               ORDER BY 
                 CASE priority 
                   WHEN 'high' THEN 1 
                   WHEN 'medium' THEN 2 
                   ELSE 3 
                 END, created_at ASC 
               LIMIT 50'''
        )
        
        tasks = []
        for row in cursor.fetchall():
            tasks.append({
                'id': row[0],
                'project_id': row[1], 
                'title': row[2],
                'description': row[3],
                'priority': row[4],
                'created_at': row[5],
                'options': ['Approve', 'Reject', 'Modify']  # Default options
            })
        
        conn.close()
        return {"tasks": tasks}
        
    except Exception as e:
        logger.error(f"Error fetching tasks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/artifacts")
async def get_global_artifacts():
    """Get artifacts across all projects - Global endpoint for frontend"""
    try:
        # For now, return empty structure - will be populated as agents create artifacts
        return {
            "artifacts": {
                "requirements": [],
                "design": [],
                "development": [],
                "testing": [],
                "deployment": [],
                "maintenance": []
            }
        }
    except Exception as e:
        logger.error(f"Error fetching artifacts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/messages")
async def get_global_messages():
    """Get recent messages across all projects - Global endpoint for frontend"""
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.execute(
            '''SELECT id, project_id, from_agent, to_agent, message_type, content, status, timestamp 
               FROM messages 
               ORDER BY timestamp DESC LIMIT 100'''
        )
        
        messages = []
        for row in cursor.fetchall():
            try:
                content = json.loads(row[5]) if row[5] else {}
            except (json.JSONDecodeError, TypeError):
                content = {"text": str(row[5])}
                
            messages.append({
                'id': row[0],
                'project_id': row[1],
                'from_agent': row[2],
                'to_agent': row[3],
                'message_type': row[4],
                'content': content,
                'status': row[6],
                'timestamp': row[7]
            })
        
        conn.close()
        return {"messages": messages}
        
    except Exception as e:
        logger.error(f"Error fetching messages: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/logs")
async def get_global_logs():
    """Get system logs - Global endpoint for frontend"""
    try:
        # For now, redirect to messages as logs
        messages_response = await get_global_messages()
        
        # Convert messages to log format
        logs = []
        for msg in messages_response["messages"]:
            log_type = "info"
            if msg.get("message_type") == "error":
                log_type = "error"
            elif msg.get("message_type") in ["handoff", "escalation"]:
                log_type = "handoff"
            elif msg.get("status") == "completed":
                log_type = "success"
                
            logs.append({
                "id": msg["id"],
                "text": f"{msg['from_agent']} → {msg['to_agent']}: {msg.get('content', {}).get('text', msg['message_type'])}",
                "type": log_type,
                "timestamp": msg["timestamp"]
            })
            
        return {"logs": logs}
        
    except Exception as e:
        logger.error(f"Error fetching logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Pydantic models for chat functionality
class ChatMessageRequest(BaseModel):
    content: str
    message_type: str
    target_agent: Optional[str] = None
    mentioned_agents: List[str] = []
    project_id: str = 'proj_49583'  # Default project


class AgentActionRequest(BaseModel):
    agent_id: str
    action: str  # pause, resume, stop


# Chat system state
chat_history = []
pending_permissions = {}  # Store pending permission requests


# Chat API endpoints
@app.post("/api/chat/send")
async def send_chat_message(request: ChatMessageRequest):
    """Send message to agents via chat interface with @mention support"""
    try:
        message_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Add user message to chat history
        user_message = {
            'id': message_id,
            'type': request.message_type,
            'content': request.content,
            'timestamp': timestamp,
            'fromAgent': 'human',
            'targetAgent': request.target_agent,
            'mentionedAgents': request.mentioned_agents
        }
        chat_history.append(user_message)
        
        # Store in database
        conn = sqlite3.connect(db.db_path)
        conn.execute(
            '''
            INSERT INTO messages (id, project_id, from_agent, to_agent, message_type, content, status, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            message_id,
            request.project_id,
            'human',
            request.target_agent or 'system',
            request.message_type,
            json.dumps({'text': request.content, 'mentions': request.mentioned_agents}),
            'sent',
            timestamp
        ))
        conn.commit()
        conn.close()
        
        # If agents are mentioned, process the message
        if request.target_agent and request.target_agent in agents:
            agent = agents[request.target_agent]
            
            # Check if agent is paused
            if getattr(agent, 'status', 'idle') == 'paused':
                response_message = {
                    'id': str(uuid.uuid4()),
                    'type': 'agent_response',
                    'content': f'Agent @{request.target_agent} is currently paused. Use the resume button to continue.',
                    'timestamp': datetime.utcnow().isoformat(),
                    'fromAgent': request.target_agent,
                    'targetAgent': 'human'
                }
                chat_history.append(response_message)
                return {'status': 'delivered', 'agent_paused': True, 'message_id': message_id}
            
            # For now, create mock agent responses to demonstrate the system
            agent_response = await create_mock_agent_response(request.target_agent, request.content)
            
            response_message = {
                'id': str(uuid.uuid4()),
                'type': 'agent_response',
                'content': agent_response['content'],
                'timestamp': datetime.utcnow().isoformat(),
                'fromAgent': request.target_agent,
                'targetAgent': 'human'
            }
            chat_history.append(response_message)
            
            # Update agent status
            if hasattr(agent, 'status'):
                agent.status = 'working'
                agent.current_task = f'Processing: {request.content[:50]}...'
        
        return {'status': 'delivered', 'message_id': message_id}
        
    except Exception as e:
        logger.error(f'Error sending chat message: {str(e)}')
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat/history")
async def get_chat_history():
    """Get chat message history"""
    return {'messages': chat_history}


@app.post("/api/agents/action")
async def agent_action(request: AgentActionRequest):
    """Pause/Resume/Stop agent"""
    try:
        if request.agent_id not in agents:
            raise HTTPException(status_code=404, detail='Agent not found')
        
        agent = agents[request.agent_id]
        
        if request.action == 'pause':
            agent.status = 'paused'
            agent.current_task = 'Paused by user'
            message = f'Agent @{request.agent_id} has been paused'
        elif request.action == 'resume':
            agent.status = 'idle'
            agent.current_task = 'Ready for instructions'
            message = f'Agent @{request.agent_id} has been resumed'
        elif request.action == 'stop':
            agent.status = 'idle'
            agent.current_task = None
            message = f'Agent @{request.agent_id} has been stopped'
        else:
            raise HTTPException(status_code=400, detail='Invalid action')
        
        # Add system message to chat
        system_message = {
            'id': str(uuid.uuid4()),
            'type': 'system',
            'content': message,
            'timestamp': datetime.utcnow().isoformat(),
            'fromAgent': 'system',
            'targetAgent': 'human'
        }
        chat_history.append(system_message)
        
        return {'status': 'success', 'message': message}
        
    except Exception as e:
        logger.error(f'Error performing agent action: {str(e)}')
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/permissions/respond")
async def respond_to_permission(request_id: str, response: str):
    """Respond to agent permission request"""
    try:
        if request_id not in pending_permissions:
            raise HTTPException(status_code=404, detail='Permission request not found')
        
        permission_request = pending_permissions[request_id]
        
        # Create response message
        response_message = {
            'id': str(uuid.uuid4()),
            'type': 'system',
            'content': f'Permission {response.lower()} for {permission_request["agent_id"]} request: {permission_request["action"]}',
            'timestamp': datetime.utcnow().isoformat(),
            'fromAgent': 'system',
            'targetAgent': 'human'
        }
        chat_history.append(response_message)
        
        # Remove from pending
        del pending_permissions[request_id]
        
        return {'status': 'success', 'response': response}
        
    except Exception as e:
        logger.error(f'Error responding to permission: {str(e)}')
        raise HTTPException(status_code=500, detail=str(e))


async def create_mock_agent_response(agent_id: str, user_message: str) -> Dict:
    """Create mock agent responses to demonstrate the system"""
    responses = {
        'analyst': {
            'analyze': 'I\'ll analyze the requirements. May I proceed to review the project scope and create a detailed analysis report?',
            'default': 'I\'m ready to analyze requirements, user stories, and project scope. What would you like me to examine?'
        },
        'architect': {
            'design': 'I\'ll create the system architecture. Should I start with the high-level design and component breakdown?',
            'default': 'I can help with system design, architecture patterns, and technical specifications. What do you need?'
        },
        'developer': {
            'implement': 'I\'m ready to start coding. Should I begin with the core functionality or would you like me to focus on a specific module?',
            'default': 'I can write code, implement features, and handle development tasks. What should I work on?'
        },
        'tester': {
            'test': 'I\'ll create comprehensive tests. Should I start with unit tests or would you prefer integration testing first?',
            'default': 'I can create test cases, run quality checks, and validate functionality. How can I help?'
        }
    }
    
    agent_responses = responses.get(agent_id, {'default': f'Agent {agent_id} received your message.'})
    
    # Simple keyword matching for response selection
    user_lower = user_message.lower()
    for keyword, response in agent_responses.items():
        if keyword != 'default' and keyword in user_lower:
            return {'content': response, 'requires_permission': True}
    
    return {'content': agent_responses['default'], 'requires_permission': False}


@app.get("/api/events")
async def stream_global_events():
    """Global SSE endpoint for real-time updates"""
    async def generate():
        yield f"data: {json.dumps({'type': 'connected', 'timestamp': datetime.utcnow().isoformat()})}\n\n"
        
        while True:
            try:
                # Send agent status updates
                agent_statuses = {
                    'type': 'agent_update',
                    'payload': {
                        agent_id: {
                            'id': agent_id,
                            'status': getattr(agent, 'status', 'idle'),
                            'current_task': getattr(agent, 'current_task', None)
                        }
                        for agent_id, agent in agents.items()
                    },
                    'timestamp': datetime.utcnow().isoformat()
                }
                yield f"data: {json.dumps(agent_statuses)}\n\n"
                
                # Send recent task updates
                try:
                    tasks_response = await get_global_tasks()
                    if tasks_response["tasks"]:
                        task_update = {
                            'type': 'new_task',
                            'payload': tasks_response["tasks"][:1],  # Send latest task
                            'timestamp': datetime.utcnow().isoformat()
                        }
                        yield f"data: {json.dumps(task_update)}\n\n"
                except:
                    pass  # Skip if no tasks
                
                await asyncio.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Global SSE error: {str(e)}")
                break
    
    return StreamingResponse(generate(), media_type="text/plain")


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
                cursor = conn.execute(
                    '''
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
                cursor = conn.execute(
                    '''
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
                        }
                        for agent_id, agent in agents.items()
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


# Disabled automatic workflow - agents only respond to manual chat commands
# Original function renamed to start_agent_workflow_disabled
async def start_agent_workflow_disabled(project_id: str, requirements: str):
    """DISABLED: Original auto-workflow function - agents only respond to chat now"""
    logger.info(f"Auto-workflow disabled for project {project_id}. Use chat with @agent mentions instead.")
    # No automatic processing - function exists for compatibility but does nothing


# Disabled automatic message queue processing 
# Original function renamed to process_message_queue_disabled
async def process_message_queue_disabled():
    """DISABLED: Original message queue processor - replaced with manual chat system"""
    logger.info("Automatic message queue processing disabled. Use chat interface instead.")
    # No automatic processing - function exists for compatibility but does nothing


# Serve static files (React app)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
