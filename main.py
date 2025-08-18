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
    # Create test project on startup
    try:
        existing = db.get_project('proj_49583')
        if not existing:
            logger.info("Creating test project...")
            db.create_project_with_id('proj_49583', 'Test Project', 'A test project for development')
            
            # Add some sample data for testing
            db.add_message(
                project_id='proj_49583',
                from_agent='system',
                to_agent='analyst', 
                message_type='info',
                content={'text': 'System initialized successfully'},
                confidence=1.0
            )
            
            # Add some sample messages to populate the chat
            db.add_message(
                project_id='proj_49583',
                from_agent='analyst',
                to_agent='architect', 
                message_type='handoff',
                content={'text': 'Requirements analysis complete', 'analysis': 'Sample analysis data'},
                confidence=0.9
            )
            
            db.add_message(
                project_id='proj_49583',
                from_agent='architect',
                to_agent='developer', 
                message_type='handoff',
                content={'text': 'Architecture design ready', 'design': 'Sample design data'},
                confidence=0.8
            )
            
            # Add a sample task/action for the action queue
            conn = sqlite3.connect(db.db_path)
            conn.execute(
                '''
                INSERT INTO actions (id, project_id, title, description, priority, options)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (str(uuid.uuid4()), 'proj_49583', 
                  'Review Architecture Design', 
                  'Please review the proposed system architecture and provide feedback.',
                  'high', 
                  json.dumps(['Approve', 'Request Changes', 'Reject']))
            )
            conn.commit()
            conn.close()
            
            logger.info("Test project created successfully with sample data")
    except Exception as e:
        logger.error(f"Failed to create test project: {str(e)}")
    
    # Start the background task
    task = asyncio.create_task(process_message_queue())
    yield
    # Clean up the background task
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.info("Background task cancelled successfully.")

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

# Set some initial status for the real agents
agents["analyst"].status = 'idle'
agents["analyst"].current_task = 'Waiting for new requirements'
agents["architect"].status = 'working'
agents["architect"].current_task = 'Reviewing system architecture'

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
    try:
        project_id = db.create_project(request.name, request.requirements)

        # Start analysis in background
        background_tasks.add_task(start_agent_workflow, project_id,
                                  request.requirements)

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


@app.get("/api/events")
async def stream_global_events():
    """Global SSE endpoint for real-time updates"""
    async def generate():
        yield f"data: {json.dumps({'type': 'connected', 'timestamp': datetime.utcnow().isoformat()})}

"
        
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
                yield f"data: {json.dumps(agent_statuses)}

"
                
                # Send recent task updates
                try:
                    tasks_response = await get_global_tasks()
                    if tasks_response["tasks"]:
                        task_update = {
                            'type': 'new_task',
                            'payload': tasks_response["tasks"][:1],  # Send latest task
                            'timestamp': datetime.utcnow().isoformat()
                        }
                        yield f"data: {json.dumps(task_update)}

"
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


# Background task to run agent workflow
async def start_agent_workflow(project_id: str, requirements: str):
    """Start the agent workflow for a project"""
    try:
        logger.info(f"Starting workflow for project {project_id}")

        # Send initial message to analyst
        message_id = db.add_message(project_id=project_id,
                                    from_agent="system",
                                    to_agent="analyst",
                                    message_type="start_analysis",
                                    content={"requirements": requirements},
                                    confidence=1.0)

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
                            db.update_message_status(message["id"],
                                                     "completed")
                        else:
                            db.update_message_status(message["id"], "error")
                            logger.error(
                                f"Agent {to_agent} failed: {result.get('message', 'Unknown error')}"
                            )

                    except Exception as e:
                        logger.error(
                            f"Error processing message {message['id']}: {str(e)}"
                        )
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
