"""
AI协作会话管理器

维护AI协作的历史上下文和会话状态。
解决痛点：增量迭代时需要重复传递相同信息
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from .context_generator import ProjectContextGenerator


@dataclass
class SessionMessage:
    """会话消息"""
    timestamp: str
    role: str  # 'user', 'ai', 'system'
    content: str
    message_type: str  # 'chat', 'code', 'decision', 'requirement'
    metadata: Dict[str, Any] = None


@dataclass
class SessionDecision:
    """会话决策记录"""
    decision_id: str
    timestamp: str
    topic: str
    decision: str
    rationale: str
    impact: List[str]


@dataclass
class SessionContext:
    """会话上下文"""
    session_id: str
    created_at: str
    updated_at: str
    project_name: str
    current_focus: str
    messages: List[SessionMessage]
    decisions: List[SessionDecision]
    code_changes: List[Dict[str, Any]]
    ai_instructions: str


class AISessionManager:
    """
    AI协作会话管理器
    
    功能：
    - 维护对话历史和上下文
    - 记录重要的设计决策
    - 跟踪代码变更历史
    - 生成增量上下文摘要
    - 避免重复传递相同信息
    """
    
    def __init__(self, project_path: Path = None):
        self.project_path = project_path or Path.cwd()
        self.sessions_dir = self.project_path / ".aiculture" / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        self.context_generator = ProjectContextGenerator(project_path)
        self.current_session: Optional[SessionContext] = None
        
    def start_session(self, focus_topic: str = None) -> str:
        """开始新的AI协作会话"""
        
        session_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        # 获取项目上下文
        project_context = self.context_generator.generate_context()
        
        # 生成AI协作指导
        ai_instructions = self._generate_session_instructions(project_context, focus_topic)
        
        self.current_session = SessionContext(
            session_id=session_id,
            created_at=timestamp,
            updated_at=timestamp,
            project_name=project_context.name,
            current_focus=focus_topic or "通用开发",
            messages=[],
            decisions=[],
            code_changes=[],
            ai_instructions=ai_instructions
        )
        
        # 添加系统消息
        self.add_message(
            role="system",
            content=f"开始AI协作会话，专注于: {self.current_session.current_focus}",
            message_type="chat"
        )
        
        self._save_session()
        return session_id
    
    def load_session(self, session_id: str) -> bool:
        """加载现有会话"""
        session_file = self.sessions_dir / f"{session_id}.json"
        
        if not session_file.exists():
            return False
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 重构消息和决策对象
            messages = [SessionMessage(**msg) for msg in data['messages']]
            decisions = [SessionDecision(**dec) for dec in data['decisions']]
            
            self.current_session = SessionContext(
                session_id=data['session_id'],
                created_at=data['created_at'],
                updated_at=data['updated_at'],
                project_name=data['project_name'],
                current_focus=data['current_focus'],
                messages=messages,
                decisions=decisions,
                code_changes=data['code_changes'],
                ai_instructions=data['ai_instructions']
            )
            
            return True
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"加载会话失败: {e}")
            return False
    
    def add_message(self, role: str, content: str, message_type: str = "chat", 
                   metadata: Dict[str, Any] = None) -> None:
        """添加会话消息"""
        if not self.current_session:
            raise ValueError("没有活跃的会话，请先调用 start_session() 或 load_session()")
        
        message = SessionMessage(
            timestamp=datetime.now().isoformat(),
            role=role,
            content=content,
            message_type=message_type,
            metadata=metadata or {}
        )
        
        self.current_session.messages.append(message)
        self.current_session.updated_at = datetime.now().isoformat()
        self._save_session()
    
    def record_decision(self, topic: str, decision: str, rationale: str, 
                       impact: List[str] = None) -> str:
        """记录重要决策"""
        if not self.current_session:
            raise ValueError("没有活跃的会话")
        
        decision_id = str(uuid.uuid4())[:8]
        
        session_decision = SessionDecision(
            decision_id=decision_id,
            timestamp=datetime.now().isoformat(),
            topic=topic,
            decision=decision,
            rationale=rationale,
            impact=impact or []
        )
        
        self.current_session.decisions.append(session_decision)
        
        # 同时添加为消息
        self.add_message(
            role="system",
            content=f"决策记录: {topic} - {decision}",
            message_type="decision",
            metadata={
                "decision_id": decision_id,
                "rationale": rationale,
                "impact": impact
            }
        )
        
        return decision_id
    
    def record_code_change(self, file_path: str, change_type: str, 
                          description: str, diff: str = None) -> None:
        """记录代码变更"""
        if not self.current_session:
            raise ValueError("没有活跃的会话")
        
        change_record = {
            "timestamp": datetime.now().isoformat(),
            "file_path": file_path,
            "change_type": change_type,  # 'create', 'modify', 'delete'
            "description": description,
            "diff": diff
        }
        
        self.current_session.code_changes.append(change_record)
        
        # 同时添加为消息
        self.add_message(
            role="system",
            content=f"代码变更: {change_type} {file_path} - {description}",
            message_type="code",
            metadata=change_record
        )
    
    def generate_session_summary(self) -> str:
        """生成会话摘要"""
        if not self.current_session:
            return "没有活跃的会话"
        
        session = self.current_session
        
        # 统计信息
        total_messages = len(session.messages)
        user_messages = len([m for m in session.messages if m.role == "user"])
        ai_messages = len([m for m in session.messages if m.role == "ai"])
        decisions_count = len(session.decisions)
        code_changes_count = len(session.code_changes)
        
        # 最近的活动
        recent_messages = session.messages[-5:] if session.messages else []
        
        summary = f"""# 🤖 AI协作会话摘要

**会话ID**: {session.session_id}
**项目**: {session.project_name}
**专注领域**: {session.current_focus}
**创建时间**: {session.created_at}
**最后更新**: {session.updated_at}

## 📊 会话统计
- 总消息数: {total_messages}
- 用户消息: {user_messages}
- AI回复: {ai_messages}
- 决策记录: {decisions_count}
- 代码变更: {code_changes_count}

## 🎯 重要决策
"""
        
        if session.decisions:
            for decision in session.decisions[-3:]:  # 最近3个决策
                summary += f"""
**{decision.topic}** ({decision.timestamp[:10]})
- 决策: {decision.decision}
- 原因: {decision.rationale}
"""
        else:
            summary += "暂无记录的决策\n"
        
        summary += "\n## 💻 代码变更历史\n"
        
        if session.code_changes:
            for change in session.code_changes[-5:]:  # 最近5个变更
                summary += f"- **{change['change_type']}** `{change['file_path']}`: {change['description']}\n"
        else:
            summary += "暂无代码变更记录\n"
        
        summary += f"\n## 🤖 当前AI指导原则\n{session.ai_instructions}\n"
        
        summary += "\n## 📝 最近对话\n"
        
        for message in recent_messages:
            role_icon = {"user": "👤", "ai": "🤖", "system": "⚙️"}.get(message.role, "❓")
            timestamp = message.timestamp[:16].replace('T', ' ')
            summary += f"**{role_icon} {timestamp}**: {message.content[:100]}...\n"
        
        return summary
    
    def generate_incremental_context(self, since_timestamp: str = None) -> str:
        """生成增量上下文（只包含新的信息）"""
        if not self.current_session:
            return ""
        
        cutoff_time = since_timestamp or self.current_session.created_at
        
        # 获取时间戳之后的消息
        new_messages = [
            msg for msg in self.current_session.messages 
            if msg.timestamp > cutoff_time
        ]
        
        # 获取时间戳之后的决策
        new_decisions = [
            dec for dec in self.current_session.decisions
            if dec.timestamp > cutoff_time
        ]
        
        # 获取时间戳之后的代码变更
        new_changes = [
            change for change in self.current_session.code_changes
            if change['timestamp'] > cutoff_time
        ]
        
        if not new_messages and not new_decisions and not new_changes:
            return "📝 没有新的上下文信息"
        
        context = f"# 📈 增量上下文更新\n\n"
        context += f"**更新时间**: {datetime.now().isoformat()}\n"
        context += f"**基准时间**: {cutoff_time}\n\n"
        
        if new_decisions:
            context += "## 🎯 新决策\n"
            for decision in new_decisions:
                context += f"- **{decision.topic}**: {decision.decision}\n"
            context += "\n"
        
        if new_changes:
            context += "## 💻 新代码变更\n"
            for change in new_changes:
                context += f"- **{change['change_type']}** `{change['file_path']}`: {change['description']}\n"
            context += "\n"
        
        if new_messages:
            context += "## 💬 新对话内容\n"
            for message in new_messages:
                if message.message_type == "chat":
                    role_icon = {"user": "👤", "ai": "🤖"}.get(message.role, "❓")
                    context += f"{role_icon} {message.content}\n\n"
        
        return context
    
    def get_ai_context_prompt(self) -> str:
        """获取适合发送给AI的完整上下文提示词"""
        if not self.current_session:
            return "没有活跃的会话上下文"
        
        prompt = f"""# 🤖 AI协作上下文

你好！我们正在进行AI协作开发。以下是当前会话的完整上下文信息：

## 基本信息
- **项目**: {self.current_session.project_name}
- **当前专注**: {self.current_session.current_focus}
- **会话时长**: {len(self.current_session.messages)} 条消息

## 协作指导原则
{self.current_session.ai_instructions}

## 重要决策历史
"""
        
        if self.current_session.decisions:
            for decision in self.current_session.decisions[-3:]:
                prompt += f"- **{decision.topic}**: {decision.decision} (原因: {decision.rationale})\n"
        else:
            prompt += "暂无重要决策记录\n"
        
        prompt += "\n## 最近代码变更\n"
        
        if self.current_session.code_changes:
            for change in self.current_session.code_changes[-3:]:
                prompt += f"- {change['change_type']} `{change['file_path']}`: {change['description']}\n"
        else:
            prompt += "暂无代码变更\n"
        
        prompt += f"\n## 请注意\n"
        prompt += f"- 请基于以上上下文继续我们的协作\n"
        prompt += f"- 重要决策请提醒我记录到会话中\n"
        prompt += f"- 代码变更完成后请提醒我更新会话历史\n"
        prompt += f"- 保持与项目现有风格和决策的一致性\n"
        
        return prompt
    
    def list_sessions(self) -> List[Dict[str, str]]:
        """列出所有会话"""
        sessions = []
        
        for session_file in self.sessions_dir.glob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                sessions.append({
                    "session_id": data['session_id'],
                    "project_name": data['project_name'],
                    "current_focus": data['current_focus'],
                    "created_at": data['created_at'],
                    "updated_at": data['updated_at'],
                    "message_count": len(data['messages']),
                    "decision_count": len(data['decisions'])
                })
                
            except (json.JSONDecodeError, KeyError):
                continue
        
        # 按更新时间排序
        sessions.sort(key=lambda x: x['updated_at'], reverse=True)
        return sessions
    
    def _generate_session_instructions(self, project_context, focus_topic: str = None) -> str:
        """生成会话特定的AI指导原则"""
        
        base_instructions = project_context.ai_instructions
        
        focus_instructions = ""
        if focus_topic:
            focus_instructions = f"\n\n## 当前专注领域: {focus_topic}\n"
            
            focus_guides = {
                "重构": "- 优先保持功能不变的情况下改进代码结构\n- 每次重构后确保测试通过\n- 关注代码复杂度和可读性",
                "新功能": "- 先理解需求再开始编码\n- 遵循项目现有的架构模式\n- 编写相应的测试用例",
                "bug修复": "- 先重现问题再修复\n- 找到根本原因而不是症状\n- 添加测试防止回归",
                "性能优化": "- 先测量再优化\n- 关注瓶颈点而不是过早优化\n- 保持代码可读性",
                "文档": "- 文档要与代码同步更新\n- 重点说明设计决策和为什么\n- 提供实际的使用示例"
            }
            
            for topic, guide in focus_guides.items():
                if topic in focus_topic:
                    focus_instructions += guide + "\n"
        
        session_instructions = f"""## AI协作会话指导原则

{base_instructions}

## 会话管理
- 重要的设计决策请提醒用户记录到会话历史中
- 代码变更完成后建议更新会话记录
- 保持与之前讨论决策的一致性
- 如果需要推翻之前的决策，请明确说明原因

{focus_instructions}

## 协作风格
- 先理解用户的意图和上下文
- 提供具体可操作的建议
- 解释重要的设计选择
- 在不确定时主动询问澄清
"""
        
        return session_instructions
    
    def _save_session(self) -> None:
        """保存会话到文件"""
        if not self.current_session:
            return
        
        session_file = self.sessions_dir / f"{self.current_session.session_id}.json"
        
        # 转换为可序列化的字典
        data = asdict(self.current_session)
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_session_status(self) -> Dict[str, Any]:
        """获取当前会话状态"""
        if not self.current_session:
            return {"status": "no_active_session"}
        
        session = self.current_session
        
        return {
            "status": "active",
            "session_id": session.session_id,
            "project_name": session.project_name,
            "current_focus": session.current_focus,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "message_count": len(session.messages),
            "decision_count": len(session.decisions),
            "code_change_count": len(session.code_changes),
            "duration": self._calculate_session_duration()
        }
    
    def _calculate_session_duration(self) -> str:
        """计算会话持续时间"""
        if not self.current_session:
            return "0分钟"
        
        from datetime import datetime
        
        start_time = datetime.fromisoformat(self.current_session.created_at)
        current_time = datetime.now()
        
        duration = current_time - start_time
        
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        
        if duration.days > 0:
            return f"{duration.days}天{hours}小时"
        elif hours > 0:
            return f"{hours}小时{minutes}分钟"
        else:
            return f"{minutes}分钟" 