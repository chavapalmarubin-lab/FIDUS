"""
AI Strategy Advisor Service
Uses Claude Sonnet 4.5 for intelligent trading strategy analysis
"""
import os
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class AIStrategyAdvisor:
    """AI-powered trading strategy advisor using Claude Sonnet 4.5"""
    
    def __init__(self, db):
        self.db = db
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        self.model_provider = "anthropic"
        self.model_name = "claude-sonnet-4-5-20250929"
        self._chat_instances = {}
        
    def _get_system_prompt(self) -> str:
        """Generate the system prompt for the AI advisor"""
        return """You are an expert AI Trading Strategy Advisor for FIDUS Investment Platform. 
You have deep expertise in:
- Quantitative trading analysis
- Risk-adjusted performance metrics (Sharpe ratio, Sortino ratio, Calmar ratio)
- Portfolio optimization and capital allocation
- Technical analysis and market dynamics

Your role is to:
1. Analyze trading strategies and provide actionable insights
2. Recommend optimal capital allocation based on risk/return profiles
3. Identify high-performing strategies and explain why they succeed
4. Flag concerning risk patterns and suggest mitigation strategies
5. Answer questions about specific managers, funds, and performance metrics

Communication style:
- Be concise but thorough
- Use specific numbers and percentages from the data
- Provide clear reasoning for recommendations
- Use professional financial terminology
- Format responses with clear sections when appropriate

IMPORTANT: Base all analysis on the actual data provided. Do not make up numbers or statistics."""

    async def _get_chat_instance(self, session_id: str):
        """Get or create a chat instance for the session"""
        from emergentintegrations.llm.chat import LlmChat
        
        if session_id not in self._chat_instances:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=session_id,
                system_message=self._get_system_prompt()
            ).with_model(self.model_provider, self.model_name)
            self._chat_instances[session_id] = chat
            
        return self._chat_instances[session_id]
    
    async def _get_managers_data(self, period_days: int = 30) -> Dict[str, Any]:
        """Fetch current managers data for context"""
        try:
            from services.trading_analytics_service import TradingAnalyticsService
            service = TradingAnalyticsService(self.db)
            return await service.get_managers_ranking(period_days)
        except Exception as e:
            logger.error(f"Error fetching managers data: {e}")
            return {"managers": [], "error": str(e)}
    
    async def _get_historical_data(self, account: int, days: int = 90) -> Dict[str, Any]:
        """Fetch historical trading data for deeper analysis"""
        try:
            # Get deal history for the account
            deals = await self.db.mt5_deals.find({
                "account": account
            }).sort("time", -1).limit(500).to_list(length=500)
            
            # Get account history
            account_history = await self.db.mt5_accounts.find({
                "account": account
            }).sort("last_sync", -1).limit(days).to_list(length=days)
            
            return {
                "deals_count": len(deals),
                "history_points": len(account_history),
                "deals_summary": self._summarize_deals(deals) if deals else None
            }
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return {"error": str(e)}
    
    def _summarize_deals(self, deals: List[Dict]) -> Dict[str, Any]:
        """Summarize deal history for context"""
        if not deals:
            return {}
            
        total_profit = sum(d.get("profit", 0) for d in deals)
        winning_deals = [d for d in deals if d.get("profit", 0) > 0]
        losing_deals = [d for d in deals if d.get("profit", 0) < 0]
        
        return {
            "total_deals": len(deals),
            "winning_deals": len(winning_deals),
            "losing_deals": len(losing_deals),
            "total_profit": round(total_profit, 2),
            "avg_win": round(sum(d.get("profit", 0) for d in winning_deals) / len(winning_deals), 2) if winning_deals else 0,
            "avg_loss": round(sum(d.get("profit", 0) for d in losing_deals) / len(losing_deals), 2) if losing_deals else 0
        }
    
    def _format_managers_context(self, managers_data: Dict[str, Any]) -> str:
        """Format managers data as context for the AI"""
        managers = managers_data.get("managers", [])
        if not managers:
            return "No manager data available."
            
        context = f"""
CURRENT PORTFOLIO DATA (as of {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}):

SUMMARY:
- Total Managers: {len(managers)}
- Total P&L: ${managers_data.get('total_pnl', 0):,.2f}
- Average Return: {managers_data.get('average_return', 0):.2f}%
- Best Performer: {managers_data.get('best_performer', 'N/A')}
- Worst Performer: {managers_data.get('worst_performer', 'N/A')}

INDIVIDUAL STRATEGY DETAILS:
"""
        for i, m in enumerate(managers, 1):
            context += f"""
{i}. {m.get('manager_name', 'Unknown')} (Account #{m.get('account', 'N/A')})
   - Fund: {m.get('fund', 'N/A')}
   - Initial Allocation: ${m.get('initial_allocation', 0):,.2f}
   - Current Equity: ${m.get('current_equity', 0):,.2f}
   - Total P&L: ${m.get('total_pnl', 0):,.2f}
   - Return: {m.get('return_percentage', 0):.2f}%
   - Sharpe Ratio: {m.get('sharpe_ratio', 0):.2f}
   - Sortino Ratio: {m.get('sortino_ratio', 0):.2f}
   - Win Rate: {m.get('win_rate', 0):.2f}%
   - Profit Factor: {m.get('profit_factor', 0):.2f}
   - Max Drawdown: {m.get('max_drawdown_pct', 0):.2f}%
   - Total Trades: {m.get('total_trades', 0)}
"""
        return context
    
    async def generate_automated_insights(self, period_days: int = 30) -> Dict[str, Any]:
        """Generate automated insights about the portfolio"""
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            
            managers_data = await self._get_managers_data(period_days)
            context = self._format_managers_context(managers_data)
            
            # Create a one-off chat for insights
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"insights_{datetime.now().timestamp()}",
                system_message=self._get_system_prompt()
            ).with_model(self.model_provider, self.model_name)
            
            prompt = f"""
{context}

Based on this data, provide a concise executive summary with:

1. **Portfolio Health Score** (1-10) with brief explanation
2. **Top Performer Spotlight** - Why is the best strategy succeeding?
3. **Risk Alerts** - Any concerning patterns that need attention?
4. **Key Insight** - One actionable recommendation for the portfolio

Keep the response concise but data-driven. Use specific numbers from the data above.
"""
            
            message = UserMessage(text=prompt)
            response = await chat.send_message(message)
            
            return {
                "success": True,
                "insights": response,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "period_days": period_days
            }
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return {
                "success": False,
                "error": str(e),
                "insights": None
            }
    
    async def generate_allocation_recommendations(self, 
                                                   total_capital: float,
                                                   risk_tolerance: str = "moderate",
                                                   period_days: int = 30) -> Dict[str, Any]:
        """Generate AI-powered allocation recommendations"""
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage
            
            managers_data = await self._get_managers_data(period_days)
            context = self._format_managers_context(managers_data)
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"allocation_{datetime.now().timestamp()}",
                system_message=self._get_system_prompt()
            ).with_model(self.model_provider, self.model_name)
            
            prompt = f"""
{context}

ALLOCATION REQUEST:
- Total Capital to Allocate: ${total_capital:,.2f}
- Risk Tolerance: {risk_tolerance.upper()}
- Analysis Period: Last {period_days} days

Based on the performance data above, provide an OPTIMAL CAPITAL ALLOCATION recommendation.

Consider:
1. Risk-adjusted returns (Sharpe ratio, Sortino ratio)
2. Maximum drawdown history
3. Consistency of returns
4. Diversification across funds

Provide your recommendation in this format:

**RECOMMENDED ALLOCATION:**
| Strategy | Allocation % | Amount | Reasoning |
|----------|-------------|--------|-----------|
| [Name]   | X%          | $X     | Brief reason |

**ALLOCATION RATIONALE:**
[2-3 sentences explaining the overall strategy]

**RISK CONSIDERATIONS:**
[Key risks to monitor]

Use specific numbers and be decisive in your recommendations.
"""
            
            message = UserMessage(text=prompt)
            response = await chat.send_message(message)
            
            return {
                "success": True,
                "recommendations": response,
                "total_capital": total_capital,
                "risk_tolerance": risk_tolerance,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating allocation recommendations: {e}")
            return {
                "success": False,
                "error": str(e),
                "recommendations": None
            }
    
    async def chat(self, 
                   session_id: str, 
                   user_message: str,
                   include_data_context: bool = True,
                   period_days: int = 30) -> Dict[str, Any]:
        """Handle chat messages with the AI advisor"""
        try:
            from emergentintegrations.llm.chat import UserMessage
            
            chat = await self._get_chat_instance(session_id)
            
            # Build message with optional data context
            full_message = user_message
            if include_data_context:
                managers_data = await self._get_managers_data(period_days)
                context = self._format_managers_context(managers_data)
                full_message = f"""
CURRENT DATA CONTEXT:
{context}

USER QUESTION:
{user_message}
"""
            
            message = UserMessage(text=full_message)
            response = await chat.send_message(message)
            
            # Store message in database for persistence
            await self._store_chat_message(session_id, user_message, response)
            
            return {
                "success": True,
                "response": response,
                "session_id": session_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": None
            }
    
    async def _store_chat_message(self, session_id: str, user_message: str, ai_response: str):
        """Store chat messages in database for persistence"""
        try:
            await self.db.ai_advisor_chats.insert_one({
                "session_id": session_id,
                "user_message": user_message,
                "ai_response": ai_response,
                "timestamp": datetime.now(timezone.utc),
                "model": f"{self.model_provider}/{self.model_name}"
            })
        except Exception as e:
            logger.error(f"Error storing chat message: {e}")
    
    async def get_chat_history(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve chat history for a session"""
        try:
            messages = await self.db.ai_advisor_chats.find({
                "session_id": session_id
            }).sort("timestamp", -1).limit(limit).to_list(length=limit)
            
            # Convert ObjectId and datetime for JSON serialization
            for msg in messages:
                msg["_id"] = str(msg["_id"])
                if msg.get("timestamp"):
                    msg["timestamp"] = msg["timestamp"].isoformat()
            
            return list(reversed(messages))  # Return in chronological order
            
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            return []
    
    def clear_session(self, session_id: str):
        """Clear a chat session from memory"""
        if session_id in self._chat_instances:
            del self._chat_instances[session_id]
