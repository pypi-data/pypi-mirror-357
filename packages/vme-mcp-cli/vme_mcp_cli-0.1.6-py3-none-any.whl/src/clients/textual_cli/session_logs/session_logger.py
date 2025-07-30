"""
Session Logger for VME Chat Client
Comprehensive logging of conversation flow, tool usage, and user intent analysis
"""

import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class MessageType(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    ERROR = "error"

class ToolStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    NOT_FOUND = "not_found"

@dataclass
class ToolCallMetrics:
    """Metrics for individual tool calls"""
    tool_name: str
    arguments: Dict[str, Any]
    status: ToolStatus
    execution_time_ms: float
    result_size_bytes: int
    error_message: Optional[str] = None
    parallel_group_id: Optional[str] = None  # For tracking parallel executions

@dataclass
class MessageEntry:
    """Individual message in conversation"""
    timestamp: str
    message_type: MessageType
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    tool_calls: List[ToolCallMetrics] = field(default_factory=list)
    response_time_ms: Optional[float] = None
    tts_enabled: bool = False
    tts_text: Optional[str] = None

@dataclass
class IntentAnalysis:
    """Analysis of user intent vs tool capabilities"""
    user_message: str
    inferred_intent: str
    available_tools: List[str]
    called_tools: List[str]
    missing_tools: List[str]  # Tools that would have been helpful but don't exist
    irrelevant_tools: List[str]  # Tools called but not helpful for intent
    success_score: float  # 0-1 score of how well tools matched intent

@dataclass
class SessionMetadata:
    """Session-level metadata"""
    session_id: str
    start_time: str
    end_time: Optional[str] = None
    client_version: str = "1.0.0"
    audio_enabled: bool = False
    audio_mode: Optional[str] = None
    llm_provider: str = "unknown"
    total_messages: int = 0
    total_tool_calls: int = 0
    total_errors: int = 0
    session_duration_ms: Optional[float] = None

@dataclass
class SessionLog:
    """Complete session log structure"""
    metadata: SessionMetadata
    messages: List[MessageEntry] = field(default_factory=list)
    intent_analysis: List[IntentAnalysis] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)

class SessionLogger:
    """Manages session logging and analysis"""
    
    def __init__(self, log_dir: str = "session_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Initialize current session
        self.session_id = str(uuid.uuid4())
        self.session_start = time.time()
        
        self.current_session = SessionLog(
            metadata=SessionMetadata(
                session_id=self.session_id,
                start_time=datetime.now(timezone.utc).isoformat()
            )
        )
        
        # Track current conversation context
        self.current_parallel_group = None
        self.pending_tool_calls = {}
        
        logger.info(f"📝 Session logger initialized: {self.session_id}")
    
    def set_session_config(self, audio_enabled: bool, audio_mode: str, llm_provider: str):
        """Update session metadata with configuration"""
        self.current_session.metadata.audio_enabled = audio_enabled
        self.current_session.metadata.audio_mode = audio_mode
        self.current_session.metadata.llm_provider = llm_provider
    
    def log_user_message(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """Log user message and return message ID"""
        message_id = str(uuid.uuid4())
        
        entry = MessageEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            message_type=MessageType.USER,
            content=content,
            metadata=metadata or {}
        )
        
        self.current_session.messages.append(entry)
        self.current_session.metadata.total_messages += 1
        
        logger.debug(f"📝 Logged user message: {content[:50]}...")
        return message_id
    
    def log_assistant_message(self, content: str, response_time_ms: float, 
                            tts_enabled: bool = False, tts_text: str = None,
                            metadata: Dict[str, Any] = None) -> str:
        """Log assistant response with performance metrics"""
        message_id = str(uuid.uuid4())
        
        entry = MessageEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            message_type=MessageType.ASSISTANT,
            content=content,
            response_time_ms=response_time_ms,
            tts_enabled=tts_enabled,
            tts_text=tts_text,
            metadata=metadata or {}
        )
        
        self.current_session.messages.append(entry)
        self.current_session.metadata.total_messages += 1
        
        logger.debug(f"📝 Logged assistant message: {content[:50]}... (took {response_time_ms:.0f}ms)")
        return message_id
    
    def start_tool_call_group(self, tool_calls: List[Dict[str, Any]]) -> str:
        """Start tracking a group of parallel tool calls"""
        group_id = str(uuid.uuid4())
        self.current_parallel_group = group_id
        
        # Initialize tracking for each tool call
        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            call_id = tool_call.get("id", str(uuid.uuid4()))
            
            self.pending_tool_calls[call_id] = {
                "tool_name": tool_name,
                "arguments": tool_call.get("arguments", {}),
                "start_time": time.time(),
                "group_id": group_id
            }
        
        logger.debug(f"📝 Started tool call group: {group_id} with {len(tool_calls)} tools")
        return group_id
    
    def log_tool_call_result(self, tool_call_id: str, tool_name: str, 
                           status: ToolStatus, result: Any = None, 
                           error_message: str = None) -> str:
        """Log individual tool call completion"""
        
        # Get pending call info
        pending = self.pending_tool_calls.pop(tool_call_id, {})
        execution_time = (time.time() - pending.get("start_time", time.time())) * 1000
        
        # Calculate result size
        result_size = 0
        if result:
            try:
                result_size = len(str(result).encode('utf-8'))
            except:
                result_size = 0
        
        metrics = ToolCallMetrics(
            tool_name=tool_name,
            arguments=pending.get("arguments", {}),
            status=status,
            execution_time_ms=execution_time,
            result_size_bytes=result_size,
            error_message=error_message,
            parallel_group_id=pending.get("group_id")
        )
        
        # Add to the last message (should be assistant message that initiated tools)
        if self.current_session.messages:
            self.current_session.messages[-1].tool_calls.append(metrics)
        
        self.current_session.metadata.total_tool_calls += 1
        if status != ToolStatus.SUCCESS:
            self.current_session.metadata.total_errors += 1
        
        logger.debug(f"📝 Logged tool call: {tool_name} -> {status.value} ({execution_time:.0f}ms)")
        return tool_call_id
    
    def log_intent_analysis(self, user_message: str, available_tools: List[str], 
                          called_tools: List[str], inferred_intent: str = None):
        """Analyze and log user intent vs tool capabilities"""
        
        # Basic intent analysis (can be enhanced with ML later)
        if not inferred_intent:
            inferred_intent = self._infer_intent(user_message)
        
        # Identify potentially missing tools
        missing_tools = self._identify_missing_tools(user_message, available_tools)
        
        # Identify irrelevant tools that were called
        irrelevant_tools = self._identify_irrelevant_tools(user_message, called_tools)
        
        # Calculate success score
        success_score = self._calculate_success_score(
            user_message, called_tools, missing_tools, irrelevant_tools
        )
        
        analysis = IntentAnalysis(
            user_message=user_message,
            inferred_intent=inferred_intent,
            available_tools=available_tools,
            called_tools=called_tools,
            missing_tools=missing_tools,
            irrelevant_tools=irrelevant_tools,
            success_score=success_score
        )
        
        self.current_session.intent_analysis.append(analysis)
        logger.debug(f"📝 Intent analysis: {inferred_intent} (score: {success_score:.2f})")
    
    def log_error(self, error_message: str, error_type: str = "general", 
                  metadata: Dict[str, Any] = None):
        """Log error events"""
        entry = MessageEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            message_type=MessageType.ERROR,
            content=error_message,
            metadata={
                "error_type": error_type,
                **(metadata or {})
            }
        )
        
        self.current_session.messages.append(entry)
        self.current_session.metadata.total_errors += 1
        
        logger.debug(f"📝 Logged error: {error_type} - {error_message}")
    
    def finalize_session(self) -> str:
        """Finalize and save session log"""
        session_duration = (time.time() - self.session_start) * 1000
        
        self.current_session.metadata.end_time = datetime.now(timezone.utc).isoformat()
        self.current_session.metadata.session_duration_ms = session_duration
        
        # Calculate performance metrics
        self._calculate_performance_metrics()
        
        # Save to file
        log_file = self.log_dir / f"session_{self.session_id}.json"
        try:
            # Convert dataclass to dict with enum handling
            session_dict = self._serialize_session()
            with open(log_file, 'w') as f:
                json.dump(session_dict, f, indent=2)
            
            logger.info(f"📝 Session log saved: {log_file}")
            return str(log_file)
            
        except Exception as e:
            logger.error(f"❌ Failed to save session log: {e}")
            return None
    
    def _infer_intent(self, user_message: str) -> str:
        """Basic intent inference (placeholder for ML enhancement)"""
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ["list", "show", "get", "what"]):
            return "information_retrieval"
        elif any(word in message_lower for word in ["create", "make", "add", "new"]):
            return "resource_creation"
        elif any(word in message_lower for word in ["delete", "remove", "stop", "terminate"]):
            return "resource_deletion"
        elif any(word in message_lower for word in ["update", "modify", "change", "edit"]):
            return "resource_modification"
        elif any(word in message_lower for word in ["help", "how", "explain"]):
            return "help_and_guidance"
        else:
            return "general_inquiry"
    
    def _identify_missing_tools(self, user_message: str, available_tools: List[str]) -> List[str]:
        """Identify tools that might be missing for user's intent"""
        # This is a placeholder - can be enhanced with tool capability mapping
        missing = []
        
        message_lower = user_message.lower()
        if "backup" in message_lower and not any("backup" in tool.lower() for tool in available_tools):
            missing.append("backup_management_tools")
        
        if "monitor" in message_lower and not any("monitor" in tool.lower() for tool in available_tools):
            missing.append("monitoring_tools")
        
        return missing
    
    def _identify_irrelevant_tools(self, user_message: str, called_tools: List[str]) -> List[str]:
        """Identify tools that were called but seem irrelevant"""
        # Placeholder for more sophisticated analysis
        return []
    
    def _calculate_success_score(self, user_message: str, called_tools: List[str], 
                               missing_tools: List[str], irrelevant_tools: List[str]) -> float:
        """Calculate how well tools matched user intent (0-1 score)"""
        if not called_tools and not missing_tools:
            return 1.0  # Perfect match - no tools needed
        
        if not called_tools and missing_tools:
            return 0.0  # No tools called but some were needed
        
        # Basic scoring logic
        score = 1.0
        score -= len(missing_tools) * 0.3  # Penalty for missing tools
        score -= len(irrelevant_tools) * 0.2  # Penalty for irrelevant tools
        
        return max(0.0, min(1.0, score))
    
    def _calculate_performance_metrics(self):
        """Calculate session-wide performance metrics"""
        messages = self.current_session.messages
        
        # Response time statistics
        response_times = [m.response_time_ms for m in messages if m.response_time_ms is not None]
        if response_times:
            self.current_session.performance_metrics.update({
                "avg_response_time_ms": sum(response_times) / len(response_times),
                "max_response_time_ms": max(response_times),
                "min_response_time_ms": min(response_times)
            })
        
        # Tool call statistics
        all_tool_calls = []
        for message in messages:
            all_tool_calls.extend(message.tool_calls)
        
        if all_tool_calls:
            tool_times = [tc.execution_time_ms for tc in all_tool_calls]
            success_rate = len([tc for tc in all_tool_calls if tc.status == ToolStatus.SUCCESS]) / len(all_tool_calls)
            
            self.current_session.performance_metrics.update({
                "avg_tool_execution_ms": sum(tool_times) / len(tool_times),
                "tool_success_rate": success_rate,
                "parallel_groups": len(set(tc.parallel_group_id for tc in all_tool_calls if tc.parallel_group_id))
            })
        
        # Intent analysis summary
        if self.current_session.intent_analysis:
            avg_success_score = sum(ia.success_score for ia in self.current_session.intent_analysis) / len(self.current_session.intent_analysis)
            self.current_session.performance_metrics["avg_intent_success_score"] = avg_success_score
    
    def _serialize_session(self) -> dict:
        """Convert session to JSON-serializable dict"""
        def convert_enum(obj):
            if isinstance(obj, Enum):
                return obj.value
            elif isinstance(obj, dict):
                return {k: convert_enum(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_enum(item) for item in obj]
            else:
                return obj
        
        # Convert to dict first
        session_dict = asdict(self.current_session)
        
        # Convert all enums to their values
        return convert_enum(session_dict)