"""
Hull-Style Risk Engine Service
Implements position sizing and risk controls based on John C. Hull principles

Key Features:
- Maximum lot sizing per instrument based on stop-loss and risk budget
- Margin constraint calculations for 200:1 leverage
- Risk Control composite scoring
- Trade breach detection and alerting
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import math

logger = logging.getLogger(__name__)

# ============================================================================
# DEFAULT INSTRUMENT SPECIFICATIONS
# Used when MongoDB collection doesn't have the instrument
# ============================================================================
DEFAULT_INSTRUMENT_SPECS = {
    "XAUUSD": {
        "symbol": "XAUUSD",
        "name": "Gold",
        "contract_size": 100,  # 100 oz per lot
        "pip_size": 0.01,
        "pip_value_per_lot": 1.0,  # $1 per 0.01 move per lot
        "value_per_unit_move_per_lot": 100,  # $100 per $1 move per lot
        "lot_step": 0.01,
        "min_lot": 0.01,
        "max_lot": 100.0,
        "typical_spread": 0.30,
        "default_stop_distance": 10.0,  # $10 default stop
        "atr_multiplier": 1.5
    },
    "EURUSD": {
        "symbol": "EURUSD",
        "name": "Euro/US Dollar",
        "contract_size": 100000,
        "pip_size": 0.0001,
        "pip_value_per_lot": 10.0,  # $10 per pip per lot
        "value_per_unit_move_per_lot": 100000,
        "lot_step": 0.01,
        "min_lot": 0.01,
        "max_lot": 100.0,
        "typical_spread": 1.0,  # pips
        "default_stop_distance": 0.0050,  # 50 pips
        "atr_multiplier": 1.5
    },
    "GBPUSD": {
        "symbol": "GBPUSD",
        "name": "British Pound/US Dollar",
        "contract_size": 100000,
        "pip_size": 0.0001,
        "pip_value_per_lot": 10.0,
        "value_per_unit_move_per_lot": 100000,
        "lot_step": 0.01,
        "min_lot": 0.01,
        "max_lot": 100.0,
        "typical_spread": 1.2,
        "default_stop_distance": 0.0060,
        "atr_multiplier": 1.5
    },
    "USDJPY": {
        "symbol": "USDJPY",
        "name": "US Dollar/Japanese Yen",
        "contract_size": 100000,
        "pip_size": 0.01,
        "pip_value_per_lot": 6.67,  # Approx at 150 rate
        "value_per_unit_move_per_lot": 667,
        "lot_step": 0.01,
        "min_lot": 0.01,
        "max_lot": 100.0,
        "typical_spread": 1.0,
        "default_stop_distance": 0.50,  # 50 pips
        "atr_multiplier": 1.5
    },
    "US30": {
        "symbol": "US30",
        "name": "Dow Jones Industrial Average",
        "contract_size": 1,
        "pip_size": 1.0,
        "pip_value_per_lot": 1.0,  # $1 per point per lot
        "value_per_unit_move_per_lot": 1.0,
        "lot_step": 0.1,
        "min_lot": 0.1,
        "max_lot": 50.0,
        "typical_spread": 3.0,
        "default_stop_distance": 100,  # 100 points
        "atr_multiplier": 1.0
    },
    "NAS100": {
        "symbol": "NAS100",
        "name": "NASDAQ 100",
        "contract_size": 1,
        "pip_size": 0.1,
        "pip_value_per_lot": 0.1,
        "value_per_unit_move_per_lot": 1.0,
        "lot_step": 0.1,
        "min_lot": 0.1,
        "max_lot": 50.0,
        "typical_spread": 2.0,
        "default_stop_distance": 50,
        "atr_multiplier": 1.0
    },
    "DE40": {
        "symbol": "DE40",
        "name": "DAX 40",
        "contract_size": 1,
        "pip_size": 0.1,
        "pip_value_per_lot": 1.0,
        "value_per_unit_move_per_lot": 1.0,
        "lot_step": 0.1,
        "min_lot": 0.1,
        "max_lot": 50.0,
        "typical_spread": 2.0,
        "default_stop_distance": 50,
        "atr_multiplier": 1.0
    },
    "BTCUSD": {
        "symbol": "BTCUSD",
        "name": "Bitcoin/US Dollar",
        "contract_size": 1,
        "pip_size": 1.0,
        "pip_value_per_lot": 1.0,
        "value_per_unit_move_per_lot": 1.0,
        "lot_step": 0.01,
        "min_lot": 0.01,
        "max_lot": 10.0,
        "typical_spread": 50,
        "default_stop_distance": 1000,
        "atr_multiplier": 2.0
    }
}

# ============================================================================
# FIDUS RISK POLICY DEFAULTS (Hull-style discipline)
# These are platform defaults, overrideable per strategy/account
# ============================================================================

DEFAULT_RISK_POLICY = {
    # A) Loss limits (Hull-style "survival first")
    "max_risk_per_trade_pct": 1.0,      # 1% of equity (range 0.25-2.0%)
    "max_intraday_loss_pct": 3.0,       # 3% daily stop (range 1.0-5.0%)
    "max_weekly_loss_pct": 6.0,         # 6% weekly (range 3.0-10.0%)
    "max_monthly_drawdown_pct": 10.0,   # 10% monthly DD (range 6.0-15.0%)
    
    # B) Margin / leverage controls (secondary constraint)
    "leverage": 200,                     # 200:1 static
    "max_margin_usage_pct": 25.0,       # 25% of equity (range 10-35%)
    "max_single_instrument_notional_x": 10,  # Max 10x equity per symbol (range 5-15x)
    "max_total_portfolio_notional_x": 20,    # Max 20x equity total (range 10-30x)
    
    # C) Time risk (FIDUS = intraday only)
    "allow_overnight": False,           # No overnight exposure
    "force_flat_time_utc": "21:50",     # 16:50 NY time = 21:50 UTC (10 min before rollover)
    
    # Allowed ranges for UI validation
    "ranges": {
        "max_risk_per_trade_pct": [0.25, 2.0],
        "max_intraday_loss_pct": [1.0, 5.0],
        "max_weekly_loss_pct": [3.0, 10.0],
        "max_monthly_drawdown_pct": [6.0, 15.0],
        "max_margin_usage_pct": [10.0, 35.0],
        "max_single_instrument_notional_x": [5, 15],
        "max_total_portfolio_notional_x": [10, 30]
    }
}

# ATR multipliers by asset class for stop proxy estimation
ATR_MULTIPLIERS = {
    "FX_MAJOR": 0.75,       # FX majors like EURUSD, GBPUSD
    "FX_CROSS": 1.00,       # FX crosses like AUDCAD (more volatile)
    "Metals": 0.60,         # Gold - volatile but tighter intraday management
    "INDEX_CFD": 0.80,      # Indices like US30, DE40
    "CRYPTO": 2.00          # Crypto pairs (very volatile)
}

# Risk Control Score penalty weights (deterministic formula)
# Start at 100, subtract penalties, clamp to 0-100
RISK_SCORE_PENALTIES = {
    "lot_breach_per_trade": 6,       # -6 per breach (cap -30)
    "lot_breach_cap": 30,
    "risk_per_trade_breach": 8,      # -8 per breach (cap -40)
    "risk_breach_cap": 40,
    "margin_breach_first_day": 10,   # -10 first day
    "margin_breach_additional": 5,   # -5 each additional (cap -25)
    "margin_breach_cap": 25,
    "daily_loss_breach": 20,         # -20 per day (cap -40)
    "daily_loss_breach_cap": 40,
    "weekly_loss_breach": 25,        # -25 per week (cap -50)
    "weekly_loss_breach_cap": 50,
    "monthly_drawdown_breach": 40,   # -40 one-time
    "overnight_breach": 15,          # -15 per event (cap -45)
    "overnight_breach_cap": 45
}

# Risk score thresholds and labels
RISK_SCORE_LABELS = {
    "strong": {"min": 80, "color": "#10B981", "label": "Strong"},
    "moderate": {"min": 60, "color": "#F59E0B", "label": "Moderate"},
    "weak": {"min": 40, "color": "#F97316", "label": "Weak"},
    "critical": {"min": 0, "color": "#EF4444", "label": "Critical"}
}

# Alert severity thresholds
ALERT_SEVERITY = {
    "critical": {  # Red
        "lot_pct_of_allowed": 150,      # > 150% of max allowed
        "conditions": ["daily_loss_breach", "monthly_drawdown_breach", "overnight_breach"]
    },
    "high": {  # Orange
        "lot_pct_of_allowed_min": 101,  # 101-150% of max allowed
        "lot_pct_of_allowed_max": 150,
        "conditions": ["margin_breach", "risk_per_trade_breach"]
    },
    "medium": {  # Yellow
        "conditions": ["missing_stop_atr_proxy", "concentration_above_60_pct"]
    }
}


class HullRiskEngine:
    """
    Hull-style risk engine implementing position sizing and risk controls
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    # =========================================================================
    # INSTRUMENT SPECS MANAGEMENT
    # =========================================================================
    
    async def get_instrument_specs(self, symbol: str) -> Dict[str, Any]:
        """Get instrument specifications from DB or defaults"""
        try:
            # Try to get from MongoDB first
            specs = await self.db.instrument_specs.find_one({"symbol": symbol.upper()})
            
            if specs:
                specs.pop("_id", None)
                return specs
            
            # Fall back to defaults
            normalized_symbol = symbol.upper()
            if normalized_symbol in DEFAULT_INSTRUMENT_SPECS:
                return DEFAULT_INSTRUMENT_SPECS[normalized_symbol]
            
            # Generic fallback for unknown instruments
            return {
                "symbol": normalized_symbol,
                "name": normalized_symbol,
                "contract_size": 100000,
                "pip_size": 0.0001,
                "pip_value_per_lot": 10.0,
                "value_per_unit_move_per_lot": 100000,
                "lot_step": 0.01,
                "min_lot": 0.01,
                "max_lot": 100.0,
                "typical_spread": 2.0,
                "default_stop_distance": 0.0050,
                "atr_multiplier": 1.5
            }
            
        except Exception as e:
            logger.error(f"Error getting instrument specs for {symbol}: {e}")
            return DEFAULT_INSTRUMENT_SPECS.get(symbol.upper(), DEFAULT_INSTRUMENT_SPECS["EURUSD"])
    
    async def get_all_instrument_specs(self) -> List[Dict[str, Any]]:
        """Get all instrument specifications"""
        try:
            db_specs = await self.db.instrument_specs.find({}).to_list(length=100)
            
            # Merge with defaults
            specs_map = {s["symbol"]: s for s in DEFAULT_INSTRUMENT_SPECS.values()}
            
            for spec in db_specs:
                spec.pop("_id", None)
                specs_map[spec["symbol"]] = spec
            
            return list(specs_map.values())
            
        except Exception as e:
            logger.error(f"Error getting all instrument specs: {e}")
            return list(DEFAULT_INSTRUMENT_SPECS.values())
    
    async def upsert_instrument_specs(self, specs: Dict[str, Any]) -> bool:
        """Create or update instrument specifications"""
        try:
            specs["updated_at"] = datetime.now(timezone.utc)
            await self.db.instrument_specs.update_one(
                {"symbol": specs["symbol"]},
                {"$set": specs},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error upserting instrument specs: {e}")
            return False
    
    # =========================================================================
    # RISK POLICY MANAGEMENT
    # =========================================================================
    
    async def get_risk_policy(self, account: int = None) -> Dict[str, Any]:
        """Get risk policy for an account or global default"""
        try:
            if account:
                policy = await self.db.risk_policies.find_one({"account": account})
                if policy:
                    policy.pop("_id", None)
                    return policy
            
            # Global policy
            global_policy = await self.db.risk_policies.find_one({"account": None, "is_global": True})
            if global_policy:
                global_policy.pop("_id", None)
                return global_policy
            
            return DEFAULT_RISK_POLICY.copy()
            
        except Exception as e:
            logger.error(f"Error getting risk policy: {e}")
            return DEFAULT_RISK_POLICY.copy()
    
    async def update_risk_policy(self, policy: Dict[str, Any], account: int = None) -> bool:
        """Update risk policy for an account or global"""
        try:
            policy["updated_at"] = datetime.now(timezone.utc)
            if account:
                policy["account"] = account
                policy["is_global"] = False
            else:
                policy["account"] = None
                policy["is_global"] = True
            
            await self.db.risk_policies.update_one(
                {"account": account},
                {"$set": policy},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error updating risk policy: {e}")
            return False
    
    # =========================================================================
    # CORE POSITION SIZING CALCULATIONS
    # =========================================================================
    
    def calculate_max_lots(
        self,
        equity: float,
        instrument_specs: Dict[str, Any],
        risk_policy: Dict[str, Any],
        stop_distance: float = None,
        current_price: float = None
    ) -> Dict[str, Any]:
        """
        Calculate maximum allowed lot size based on Hull principles
        
        Args:
            equity: Account equity in USD
            instrument_specs: Instrument specification dict
            risk_policy: Risk policy dict
            stop_distance: Stop loss distance (in price units)
            current_price: Current market price (for notional calculation)
        
        Returns:
            Dict with max_lots_risk, max_lots_margin, max_lots_allowed, and calculation details
        """
        symbol = instrument_specs.get("symbol", "UNKNOWN")
        lot_step = instrument_specs.get("lot_step", 0.01)
        min_lot = instrument_specs.get("min_lot", 0.01)
        max_lot = instrument_specs.get("max_lot", 100.0)
        contract_size = instrument_specs.get("contract_size", 100000)
        value_per_unit = instrument_specs.get("value_per_unit_move_per_lot", 100000)
        
        # Risk parameters
        risk_per_trade_pct = risk_policy.get("max_risk_per_trade_pct", 1.0) / 100
        max_margin_pct = risk_policy.get("max_margin_usage_pct", 25.0) / 100
        leverage = risk_policy.get("leverage", 200)
        
        # Calculate risk budget
        risk_budget = equity * risk_per_trade_pct
        
        # Use default stop if not provided
        if stop_distance is None or stop_distance <= 0:
            stop_distance = instrument_specs.get("default_stop_distance", 0.0050)
            stop_source = "default"
        else:
            stop_source = "provided"
        
        # Calculate max lots based on RISK (stop-based sizing)
        # Loss per lot at stop = stop_distance * value_per_unit_move_per_lot
        if symbol == "XAUUSD":
            # Gold: $1 move = $100 per lot
            loss_per_lot_at_stop = stop_distance * 100
        elif symbol in ["EURUSD", "GBPUSD", "AUDUSD", "NZDUSD"]:
            # Major pairs: pip_value * pips
            pips = stop_distance / instrument_specs.get("pip_size", 0.0001)
            loss_per_lot_at_stop = pips * instrument_specs.get("pip_value_per_lot", 10)
        elif symbol == "USDJPY":
            pips = stop_distance / instrument_specs.get("pip_size", 0.01)
            loss_per_lot_at_stop = pips * instrument_specs.get("pip_value_per_lot", 6.67)
        elif symbol in ["US30", "NAS100", "DE40"]:
            # Indices: points * $1 per point
            loss_per_lot_at_stop = stop_distance * instrument_specs.get("pip_value_per_lot", 1.0)
        elif symbol == "BTCUSD":
            loss_per_lot_at_stop = stop_distance * 1.0
        else:
            # Generic calculation
            loss_per_lot_at_stop = stop_distance * value_per_unit
        
        # Max lots based on risk
        if loss_per_lot_at_stop > 0:
            max_lots_risk = risk_budget / loss_per_lot_at_stop
        else:
            max_lots_risk = max_lot
        
        # Calculate max lots based on MARGIN
        # Notional per lot = contract_size * price (or contract_size for indices)
        if current_price and current_price > 0:
            notional_per_lot = contract_size * current_price
        else:
            # Estimate based on typical values
            if symbol == "XAUUSD":
                notional_per_lot = 100 * 2000  # 100 oz * $2000
            elif symbol in ["EURUSD", "GBPUSD"]:
                notional_per_lot = 100000 * 1.0  # Standard lot
            elif symbol in ["US30"]:
                notional_per_lot = 1 * 40000  # ~$40k index
            else:
                notional_per_lot = contract_size
        
        margin_per_lot = notional_per_lot / leverage
        max_margin_allowed = equity * max_margin_pct
        
        if margin_per_lot > 0:
            max_lots_margin = max_margin_allowed / margin_per_lot
        else:
            max_lots_margin = max_lot
        
        # Final max lots = min(risk, margin) capped at instrument max
        max_lots_allowed = min(max_lots_risk, max_lots_margin, max_lot)
        
        # Floor to lot step
        max_lots_allowed = self._floor_to_step(max_lots_allowed, lot_step)
        max_lots_allowed = max(min_lot, max_lots_allowed)
        
        # Determine binding constraint
        if max_lots_risk <= max_lots_margin:
            binding_constraint = "RISK"
        else:
            binding_constraint = "MARGIN"
        
        return {
            "symbol": symbol,
            "equity": equity,
            "risk_budget": round(risk_budget, 2),
            "risk_per_trade_pct": risk_per_trade_pct * 100,
            "stop_distance": stop_distance,
            "stop_source": stop_source,
            "loss_per_lot_at_stop": round(loss_per_lot_at_stop, 2),
            "max_lots_risk": round(self._floor_to_step(max_lots_risk, lot_step), 2),
            "leverage": leverage,
            "margin_per_lot": round(margin_per_lot, 2),
            "max_margin_allowed": round(max_margin_allowed, 2),
            "max_lots_margin": round(self._floor_to_step(max_lots_margin, lot_step), 2),
            "max_lots_allowed": round(max_lots_allowed, 2),
            "binding_constraint": binding_constraint,
            "lot_step": lot_step,
            "min_lot": min_lot,
            "max_lot": max_lot
        }
    
    def _floor_to_step(self, value: float, step: float) -> float:
        """Floor value to nearest step"""
        if step <= 0:
            return value
        return math.floor(value / step) * step
    
    # =========================================================================
    # RISK CONTROL COMPOSITE SCORE (DETERMINISTIC PENALTY-BASED)
    # Formula: Start at 100, subtract penalties for breaches, clamp to 0-100
    # =========================================================================
    
    async def calculate_risk_control_score(
        self,
        account: int,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate composite Risk Control score (0-100) using deterministic penalty system
        
        Penalty deductions:
        - Lot breach: -6 each (cap -30)
        - Risk-per-trade breach: -8 each (cap -40)
        - Margin breach: -10 first day, -5 additional (cap -25)
        - Daily loss breach: -20 each (cap -40)
        - Weekly loss breach: -25 each (cap -50)
        - Monthly drawdown breach: -40 one-time
        - Overnight breach: -15 each (cap -45)
        
        Labels:
        - 80-100: Strong
        - 60-79: Moderate
        - 40-59: Weak
        - 0-39: Critical
        """
        try:
            risk_policy = await self.get_risk_policy(account)
            
            # Get account info
            account_info = await self.db.mt5_accounts.find_one({"account": account})
            if not account_info:
                return self._empty_risk_score("Account not found")
            
            equity = account_info.get("equity", 0)
            initial_allocation = account_info.get("initial_allocation", equity)
            
            # Get deals for the period
            start_date = datetime.now(timezone.utc) - timedelta(days=period_days)
            deals = await self.db.mt5_deals.find({
                "account": account,
                "time": {"$gte": start_date}
            }).to_list(length=1000)
            
            # ===== Calculate breaches and penalties =====
            score = 100  # Start at 100
            breach_details = []
            
            # 1) Lot breach penalties
            lot_breaches = await self._count_lot_breaches(deals, equity, risk_policy)
            lot_penalty = min(lot_breaches * RISK_SCORE_PENALTIES["lot_breach_per_trade"], 
                             RISK_SCORE_PENALTIES["lot_breach_cap"])
            score -= lot_penalty
            if lot_breaches > 0:
                breach_details.append(f"Lot breaches: {lot_breaches} (-{lot_penalty})")
            
            # 2) Risk-per-trade breach penalties
            risk_breaches = self._count_risk_breaches(deals, initial_allocation, risk_policy)
            risk_penalty = min(risk_breaches * RISK_SCORE_PENALTIES["risk_per_trade_breach"],
                              RISK_SCORE_PENALTIES["risk_breach_cap"])
            score -= risk_penalty
            if risk_breaches > 0:
                breach_details.append(f"Risk breaches: {risk_breaches} (-{risk_penalty})")
            
            # 3) Margin breach penalties
            margin_breach_days = self._count_margin_breach_days(account_info, risk_policy)
            if margin_breach_days > 0:
                margin_penalty = RISK_SCORE_PENALTIES["margin_breach_first_day"]
                if margin_breach_days > 1:
                    margin_penalty += (margin_breach_days - 1) * RISK_SCORE_PENALTIES["margin_breach_additional"]
                margin_penalty = min(margin_penalty, RISK_SCORE_PENALTIES["margin_breach_cap"])
                score -= margin_penalty
                breach_details.append(f"Margin breaches: {margin_breach_days} days (-{margin_penalty})")
            
            # 4) Daily loss breach penalties (from account history if available)
            daily_breaches = self._count_daily_loss_breaches(account_info, deals, risk_policy)
            daily_penalty = min(daily_breaches * RISK_SCORE_PENALTIES["daily_loss_breach"],
                               RISK_SCORE_PENALTIES["daily_loss_breach_cap"])
            score -= daily_penalty
            if daily_breaches > 0:
                breach_details.append(f"Daily loss breaches: {daily_breaches} (-{daily_penalty})")
            
            # 5) Drawdown / Monthly breach check
            current_dd_pct = 0
            if initial_allocation > 0:
                current_dd_pct = max(0, ((initial_allocation - equity) / initial_allocation) * 100)
            
            max_monthly_dd = risk_policy.get("max_monthly_drawdown_pct", 10.0)
            if current_dd_pct > max_monthly_dd:
                score -= RISK_SCORE_PENALTIES["monthly_drawdown_breach"]
                breach_details.append(f"Monthly DD breach: {current_dd_pct:.1f}% > {max_monthly_dd}% (-40)")
            
            # 6) Overnight breach penalties (if we track overnight positions)
            overnight_breaches = self._count_overnight_breaches(deals, risk_policy)
            overnight_penalty = min(overnight_breaches * RISK_SCORE_PENALTIES["overnight_breach"],
                                   RISK_SCORE_PENALTIES["overnight_breach_cap"])
            score -= overnight_penalty
            if overnight_breaches > 0:
                breach_details.append(f"Overnight breaches: {overnight_breaches} (-{overnight_penalty})")
            
            # Clamp score to 0-100
            composite_score = max(0, min(100, score))
            
            # Determine label based on thresholds
            if composite_score >= RISK_SCORE_LABELS["strong"]["min"]:
                label = RISK_SCORE_LABELS["strong"]["label"]
                color = RISK_SCORE_LABELS["strong"]["color"]
            elif composite_score >= RISK_SCORE_LABELS["moderate"]["min"]:
                label = RISK_SCORE_LABELS["moderate"]["label"]
                color = RISK_SCORE_LABELS["moderate"]["color"]
            elif composite_score >= RISK_SCORE_LABELS["weak"]["min"]:
                label = RISK_SCORE_LABELS["weak"]["label"]
                color = RISK_SCORE_LABELS["weak"]["color"]
            else:
                label = RISK_SCORE_LABELS["critical"]["label"]
                color = RISK_SCORE_LABELS["critical"]["color"]
            
            # Also compute the older component metrics for backward compatibility
            risk_compliance = await self._calculate_risk_per_trade_compliance(
                deals, initial_allocation, risk_policy
            )
            margin_compliance = self._calculate_margin_compliance(account_info, risk_policy)
            drawdown_compliance = self._calculate_drawdown_compliance(
                account_info, initial_allocation, risk_policy
            )
            position_compliance = await self._calculate_position_size_compliance(
                deals, equity, risk_policy
            )
            
            return {
                "account": account,
                "composite_score": round(composite_score, 1),
                "label": label,
                "color": color,
                "breach_summary": breach_details,
                "total_penalty_points": round(100 - composite_score, 1),
                "components": {
                    "risk_per_trade": risk_compliance,
                    "margin_usage": margin_compliance,
                    "drawdown": drawdown_compliance,
                    "position_size": position_compliance
                },
                "period_days": period_days,
                "total_trades": len(deals),
                "calculated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk control score: {e}")
            return self._empty_risk_score(str(e))
    
    def _empty_risk_score(self, error: str = None) -> Dict[str, Any]:
        """Return empty risk score structure"""
        return {
            "composite_score": 0,
            "label": "Unknown",
            "color": "#64748B",
            "components": {},
            "error": error
        }
    
    async def _calculate_risk_per_trade_compliance(
        self,
        deals: List[Dict],
        equity: float,
        risk_policy: Dict
    ) -> Dict[str, Any]:
        """Calculate % of trades that respected max risk per trade"""
        if not deals or equity <= 0:
            return {"score": 50, "detail": "Insufficient data", "compliant_pct": 0}
        
        max_risk_pct = risk_policy.get("max_risk_per_trade_pct", 1.0)
        max_loss_per_trade = equity * (max_risk_pct / 100)
        
        compliant_trades = 0
        total_trades = 0
        
        for deal in deals:
            profit = deal.get("profit", 0)
            if profit < 0:  # Only count losing trades
                total_trades += 1
                if abs(profit) <= max_loss_per_trade * 1.5:  # 50% tolerance
                    compliant_trades += 1
        
        if total_trades == 0:
            return {"score": 100, "detail": "No losing trades", "compliant_pct": 100}
        
        compliant_pct = (compliant_trades / total_trades) * 100
        score = min(100, compliant_pct)
        
        return {
            "score": round(score, 1),
            "detail": f"{compliant_trades}/{total_trades} trades compliant",
            "compliant_pct": round(compliant_pct, 1)
        }
    
    # =========================================================================
    # BREACH COUNTING METHODS (for deterministic scoring)
    # =========================================================================
    
    async def _count_lot_breaches(
        self,
        deals: List[Dict],
        equity: float,
        risk_policy: Dict
    ) -> int:
        """Count trades where lot size exceeded MaxLotsAllowed"""
        if not deals or equity <= 0:
            return 0
        
        breaches = 0
        for deal in deals:
            symbol = deal.get("symbol", "")
            volume = deal.get("volume", 0)
            
            if not symbol or volume <= 0:
                continue
            
            specs = await self.get_instrument_specs(symbol)
            max_calc = self.calculate_max_lots(equity, specs, risk_policy)
            
            if volume > max_calc["max_lots_allowed"]:
                breaches += 1
        
        return breaches
    
    def _count_risk_breaches(
        self,
        deals: List[Dict],
        equity: float,
        risk_policy: Dict
    ) -> int:
        """Count trades where risk at stop exceeded RiskBudget"""
        if not deals or equity <= 0:
            return 0
        
        max_risk_pct = risk_policy.get("max_risk_per_trade_pct", 1.0)
        max_loss_per_trade = equity * (max_risk_pct / 100)
        
        breaches = 0
        for deal in deals:
            profit = deal.get("profit", 0)
            # Count losses that exceeded the risk budget
            if profit < 0 and abs(profit) > max_loss_per_trade:
                breaches += 1
        
        return breaches
    
    def _count_margin_breach_days(
        self,
        account_info: Dict,
        risk_policy: Dict
    ) -> int:
        """Count days margin usage exceeded threshold (simplified - current state only)"""
        equity = account_info.get("equity", 0)
        margin = account_info.get("margin", 0)
        
        if equity <= 0:
            return 0
        
        max_margin_pct = risk_policy.get("max_margin_usage_pct", 25.0)
        current_usage_pct = (margin / equity) * 100
        
        # For now, return 1 if currently in breach, 0 otherwise
        # In production, this would query historical margin snapshots
        return 1 if current_usage_pct > max_margin_pct else 0
    
    def _count_daily_loss_breaches(
        self,
        account_info: Dict,
        deals: List[Dict],
        risk_policy: Dict
    ) -> int:
        """Count days where daily loss exceeded threshold"""
        if not deals:
            return 0
        
        max_intraday_loss_pct = risk_policy.get("max_intraday_loss_pct", 3.0)
        equity = account_info.get("equity", 0)
        initial_allocation = account_info.get("initial_allocation", equity)
        
        if initial_allocation <= 0:
            return 0
        
        max_daily_loss = initial_allocation * (max_intraday_loss_pct / 100)
        
        # Group deals by date and sum P&L
        from collections import defaultdict
        daily_pnl = defaultdict(float)
        
        for deal in deals:
            deal_time = deal.get("time")
            if deal_time:
                if isinstance(deal_time, str):
                    try:
                        deal_time = datetime.fromisoformat(deal_time.replace('Z', '+00:00'))
                    except:
                        continue
                date_key = deal_time.strftime("%Y-%m-%d")
                daily_pnl[date_key] += deal.get("profit", 0)
        
        # Count days with breach
        breaches = 0
        for date_key, pnl in daily_pnl.items():
            if pnl < -max_daily_loss:
                breaches += 1
        
        return breaches
    
    def _count_overnight_breaches(
        self,
        deals: List[Dict],
        risk_policy: Dict
    ) -> int:
        """Count overnight position breaches (positions held past force-flat time)"""
        if risk_policy.get("allow_overnight", True):
            return 0  # Overnight allowed, no breaches
        
        # For now, return 0 - would need position history to detect overnight holds
        # In production, this would check position open/close times against force_flat_time
        return 0
    
    def _calculate_margin_compliance(
        self,
        account_info: Dict,
        risk_policy: Dict
    ) -> Dict[str, Any]:
        """Calculate margin usage compliance"""
        equity = account_info.get("equity", 0)
        margin = account_info.get("margin", 0)
        
        if equity <= 0:
            return {"score": 50, "detail": "No equity data", "current_usage_pct": 0}
        
        max_margin_pct = risk_policy.get("max_margin_usage_pct", 25.0)
        current_usage_pct = (margin / equity) * 100 if equity > 0 else 0
        
        if current_usage_pct <= max_margin_pct:
            score = 100
        elif current_usage_pct <= max_margin_pct * 1.5:
            score = 70
        else:
            score = max(0, 100 - (current_usage_pct - max_margin_pct) * 2)
        
        return {
            "score": round(score, 1),
            "detail": f"Current: {current_usage_pct:.1f}% (max: {max_margin_pct}%)",
            "current_usage_pct": round(current_usage_pct, 1),
            "max_allowed_pct": max_margin_pct
        }
    
    def _calculate_drawdown_compliance(
        self,
        account_info: Dict,
        initial_allocation: float,
        risk_policy: Dict
    ) -> Dict[str, Any]:
        """Calculate drawdown compliance"""
        equity = account_info.get("equity", 0)
        # Note: max_drawdown_pct from account_info could be used for historical analysis
        _ = account_info.get("max_drawdown_pct", 0)  # Reserved for future use
        
        # Calculate current drawdown from peak
        if initial_allocation > 0:
            current_dd_pct = max(0, ((initial_allocation - equity) / initial_allocation) * 100)
        else:
            current_dd_pct = 0
        
        max_intraday_loss_pct = risk_policy.get("max_intraday_loss_pct", 3.0)
        
        # Score based on drawdown relative to limit
        if current_dd_pct <= max_intraday_loss_pct:
            score = 100
        elif current_dd_pct <= max_intraday_loss_pct * 2:
            score = 60
        elif current_dd_pct <= max_intraday_loss_pct * 3:
            score = 30
        else:
            score = 0
        
        return {
            "score": round(score, 1),
            "detail": f"Current DD: {current_dd_pct:.1f}% (max: {max_intraday_loss_pct}%)",
            "current_drawdown_pct": round(current_dd_pct, 1),
            "max_allowed_pct": max_intraday_loss_pct
        }
    
    async def _calculate_position_size_compliance(
        self,
        deals: List[Dict],
        equity: float,
        risk_policy: Dict
    ) -> Dict[str, Any]:
        """Calculate position size compliance"""
        if not deals:
            return {"score": 100, "detail": "No trades to evaluate", "breaches": 0}
        
        breaches = 0
        total_evaluated = 0
        breach_details = []
        
        for deal in deals:
            symbol = deal.get("symbol", "")
            volume = deal.get("volume", 0)
            
            if not symbol or volume <= 0:
                continue
            
            total_evaluated += 1
            
            # Get instrument specs and calculate max allowed
            specs = await self.get_instrument_specs(symbol)
            max_calc = self.calculate_max_lots(equity, specs, risk_policy)
            
            if volume > max_calc["max_lots_allowed"] * 1.5:  # 50% tolerance
                breaches += 1
                breach_details.append({
                    "symbol": symbol,
                    "traded": volume,
                    "allowed": max_calc["max_lots_allowed"]
                })
        
        if total_evaluated == 0:
            return {"score": 100, "detail": "No trades to evaluate", "breaches": 0}
        
        compliance_pct = ((total_evaluated - breaches) / total_evaluated) * 100
        score = min(100, compliance_pct)
        
        return {
            "score": round(score, 1),
            "detail": f"{breaches} breaches in {total_evaluated} trades",
            "breaches": breaches,
            "breach_details": breach_details[:5]  # Top 5
        }
    
    # =========================================================================
    # RISK ANALYSIS FOR STRATEGY/ACCOUNT
    # =========================================================================
    
    async def get_strategy_risk_analysis(
        self,
        account: int,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get comprehensive risk analysis for a strategy/account
        """
        try:
            # Get account info
            account_info = await self.db.mt5_accounts.find_one({"account": account})
            if not account_info:
                return {"error": f"Account {account} not found"}
            
            equity = account_info.get("equity", 0)
            risk_policy = await self.get_risk_policy(account)
            
            # Get deals for symbol analysis
            start_date = datetime.now(timezone.utc) - timedelta(days=period_days)
            deals = await self.db.mt5_deals.find({
                "account": account,
                "time": {"$gte": start_date}
            }).to_list(length=1000)
            
            # Analyze symbols traded
            symbol_analysis = {}
            for deal in deals:
                symbol = deal.get("symbol", "")
                if not symbol:
                    continue
                
                if symbol not in symbol_analysis:
                    symbol_analysis[symbol] = {
                        "trades": 0,
                        "total_volume": 0,
                        "max_volume": 0,
                        "total_pnl": 0,
                        "stop_distances": []
                    }
                
                symbol_analysis[symbol]["trades"] += 1
                volume = deal.get("volume", 0)
                symbol_analysis[symbol]["total_volume"] += volume
                symbol_analysis[symbol]["max_volume"] = max(symbol_analysis[symbol]["max_volume"], volume)
                symbol_analysis[symbol]["total_pnl"] += deal.get("profit", 0)
                
                # Try to extract stop distance (if available)
                sl = deal.get("sl", 0)
                price = deal.get("price", 0)
                if sl > 0 and price > 0:
                    symbol_analysis[symbol]["stop_distances"].append(abs(price - sl))
            
            # Calculate risk limits for each symbol
            instruments_analysis = []
            breaches = []
            
            for symbol, data in symbol_analysis.items():
                specs = await self.get_instrument_specs(symbol)
                
                # Calculate average stop distance
                if data["stop_distances"]:
                    avg_stop = sum(data["stop_distances"]) / len(data["stop_distances"])
                    stop_source = "historical"
                else:
                    avg_stop = specs.get("default_stop_distance", 0)
                    stop_source = "default"
                
                # Calculate max lots
                max_calc = self.calculate_max_lots(equity, specs, risk_policy, avg_stop)
                
                # Check for breaches
                is_breach = data["max_volume"] > max_calc["max_lots_allowed"]
                
                analysis = {
                    "symbol": symbol,
                    "trades": data["trades"],
                    "avg_stop_distance": round(avg_stop, 5),
                    "stop_source": stop_source,
                    "max_lots_allowed": max_calc["max_lots_allowed"],
                    "max_lots_observed": round(data["max_volume"], 2),
                    "binding_constraint": max_calc["binding_constraint"],
                    "is_breach": is_breach,
                    "total_pnl": round(data["total_pnl"], 2)
                }
                
                instruments_analysis.append(analysis)
                
                if is_breach:
                    breaches.append({
                        "type": "LOT_SIZE_BREACH",
                        "symbol": symbol,
                        "traded": data["max_volume"],
                        "allowed": max_calc["max_lots_allowed"],
                        "message": f"Traded {data['max_volume']:.2f} lots {symbol}, allowed {max_calc['max_lots_allowed']:.2f}"
                    })
            
            # Get risk control score
            risk_score = await self.calculate_risk_control_score(account, period_days)
            
            return {
                "account": account,
                "manager_name": account_info.get("manager_name", f"Account {account}"),
                "equity": equity,
                "leverage": risk_policy.get("leverage", 200),
                "risk_policy": {
                    "max_risk_per_trade_pct": risk_policy.get("max_risk_per_trade_pct", 1.0),
                    "max_intraday_loss_pct": risk_policy.get("max_intraday_loss_pct", 3.0),
                    "max_margin_usage_pct": risk_policy.get("max_margin_usage_pct", 25.0)
                },
                "risk_control_score": risk_score,
                "instruments": sorted(instruments_analysis, key=lambda x: x["trades"], reverse=True),
                "breaches": breaches,
                "total_breaches": len(breaches),
                "period_days": period_days,
                "analyzed_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting strategy risk analysis: {e}")
            return {"error": str(e)}
    
    # =========================================================================
    # DETERMINISTIC NARRATIVE GENERATION
    # =========================================================================
    
    def generate_risk_profile_narrative(
        self,
        managers_data: List[Dict],
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Generate deterministic narrative analysis for risk profile
        No AI hallucination - pure template-based rules
        """
        if not managers_data:
            return self._empty_narrative("No manager data available")
        
        # Calculate aggregate metrics
        total_trades = sum(m.get("total_trades", 0) for m in managers_data)
        avg_sharpe = sum(m.get("sharpe_ratio", 0) for m in managers_data) / len(managers_data)
        # avg_sortino calculated but referenced in Sortino-specific sections if added later
        _ = sum(m.get("sortino_ratio", 0) for m in managers_data) / len(managers_data)  # Reserved for Sortino analysis
        avg_win_rate = sum(m.get("win_rate", 0) for m in managers_data) / len(managers_data)
        avg_profit_factor = sum(m.get("profit_factor", 0) for m in managers_data) / len(managers_data)
        avg_return = sum(m.get("return_percentage", 0) for m in managers_data) / len(managers_data)
        avg_drawdown = sum(abs(m.get("max_drawdown_pct", 0)) for m in managers_data) / len(managers_data)
        
        # Build narrative sections
        executive_read = []
        metric_interpretations = []
        red_flags = []
        actionable_fixes = []
        confidence_notes = []
        
        # ===== CONFIDENCE CHECK =====
        if total_trades == 0:
            confidence_notes.append("⚠️ LOW CONFIDENCE: No trades recorded in this period. All metrics are default/undefined values.")
            executive_read.append("Trading activity has been zero or not recorded. Metrics cannot be reliably interpreted.")
        elif total_trades < 20:
            confidence_notes.append(f"⚠️ LIMITED DATA: Only {total_trades} trades recorded. Statistical significance is low.")
        
        # ===== SHARPE RATIO =====
        if total_trades == 0:
            metric_interpretations.append({
                "metric": "Sharpe Ratio",
                "value": f"{avg_sharpe:.2f}",
                "interpretation": "Cannot evaluate - no trading activity recorded."
            })
        elif avg_sharpe >= 1.5:
            metric_interpretations.append({
                "metric": "Sharpe Ratio",
                "value": f"{avg_sharpe:.2f}",
                "interpretation": "Excellent risk-adjusted returns. The portfolio is generating strong returns relative to volatility."
            })
        elif avg_sharpe >= 1.0:
            metric_interpretations.append({
                "metric": "Sharpe Ratio",
                "value": f"{avg_sharpe:.2f}",
                "interpretation": "Good risk-adjusted performance. Returns adequately compensate for the risk taken."
            })
        elif avg_sharpe >= 0.5:
            metric_interpretations.append({
                "metric": "Sharpe Ratio",
                "value": f"{avg_sharpe:.2f}",
                "interpretation": "Moderate performance. Consider reviewing strategies with lower contribution."
            })
        elif avg_sharpe > 0:
            metric_interpretations.append({
                "metric": "Sharpe Ratio",
                "value": f"{avg_sharpe:.2f}",
                "interpretation": "Below-average risk-adjusted returns. Volatility is not being adequately rewarded."
            })
            red_flags.append("Sharpe Ratio below 0.5 indicates poor risk-adjusted returns")
        else:
            metric_interpretations.append({
                "metric": "Sharpe Ratio",
                "value": f"{avg_sharpe:.2f}",
                "interpretation": "Negative Sharpe indicates returns have been consistently negative or highly volatile."
            })
            red_flags.append("CRITICAL: Negative Sharpe Ratio - returns are negative on risk-adjusted basis")
            actionable_fixes.append("Review all strategies for systematic issues; consider reducing exposure")
        
        # ===== WIN RATE =====
        if avg_win_rate == 0 and total_trades == 0:
            metric_interpretations.append({
                "metric": "Win Rate",
                "value": "0.00%",
                "interpretation": "No trades recorded - win rate cannot be calculated."
            })
        elif avg_win_rate == 0 and total_trades > 0:
            metric_interpretations.append({
                "metric": "Win Rate",
                "value": "0.00%",
                "interpretation": "CRITICAL: All recorded trades were losses. Immediate strategy review required."
            })
            red_flags.append("0% Win Rate with recorded trades indicates systematic failure or data issue")
            actionable_fixes.append("Verify trade data integrity; if accurate, halt trading for strategy review")
        elif avg_win_rate < 40:
            metric_interpretations.append({
                "metric": "Win Rate",
                "value": f"{avg_win_rate:.1f}%",
                "interpretation": "Low win rate. Profitability depends on high reward-to-risk ratio per trade."
            })
            if avg_profit_factor < 1.5:
                red_flags.append(f"Low win rate ({avg_win_rate:.1f}%) combined with low profit factor is concerning")
        elif avg_win_rate >= 60:
            metric_interpretations.append({
                "metric": "Win Rate",
                "value": f"{avg_win_rate:.1f}%",
                "interpretation": "Strong win rate indicates consistent trade selection accuracy."
            })
        else:
            metric_interpretations.append({
                "metric": "Win Rate",
                "value": f"{avg_win_rate:.1f}%",
                "interpretation": "Average win rate. System viability depends on risk management quality."
            })
        
        # ===== PROFIT FACTOR =====
        if avg_profit_factor == 0 or total_trades == 0:
            metric_interpretations.append({
                "metric": "Profit Factor",
                "value": f"{avg_profit_factor:.2f}",
                "interpretation": "Cannot evaluate - insufficient trade data."
            })
        elif avg_profit_factor < 1.0:
            metric_interpretations.append({
                "metric": "Profit Factor",
                "value": f"{avg_profit_factor:.2f}",
                "interpretation": "LOSING SYSTEM: Gross losses exceed gross profits. Not sustainable."
            })
            red_flags.append(f"Profit Factor {avg_profit_factor:.2f} < 1.0 means the system is losing money")
            actionable_fixes.append("Reduce position sizes immediately; conduct full strategy audit")
        elif avg_profit_factor < 1.5:
            metric_interpretations.append({
                "metric": "Profit Factor",
                "value": f"{avg_profit_factor:.2f}",
                "interpretation": "Marginally profitable but vulnerable to drawdowns. Thin edge."
            })
        elif avg_profit_factor >= 2.0:
            metric_interpretations.append({
                "metric": "Profit Factor",
                "value": f"{avg_profit_factor:.2f}",
                "interpretation": "Strong profit factor indicates robust edge with healthy profit-to-loss ratio."
            })
        else:
            metric_interpretations.append({
                "metric": "Profit Factor",
                "value": f"{avg_profit_factor:.2f}",
                "interpretation": "Acceptable profit factor. System has positive expectancy."
            })
        
        # ===== DRAWDOWN / RISK CONTROL =====
        risk_control_score = max(0, 100 - avg_drawdown * 3)
        
        if avg_drawdown > 30:
            metric_interpretations.append({
                "metric": "Risk Control",
                "value": f"{risk_control_score:.0f}/100",
                "interpretation": f"CRITICAL: Max drawdown of {avg_drawdown:.1f}% indicates severe risk management failure."
            })
            red_flags.append(f"Drawdown exceeds 30% ({avg_drawdown:.1f}%) - capital preservation at risk")
            actionable_fixes.append("Implement strict position size limits immediately")
            actionable_fixes.append("Review and enforce daily loss limits")
        elif avg_drawdown > 20:
            metric_interpretations.append({
                "metric": "Risk Control",
                "value": f"{risk_control_score:.0f}/100",
                "interpretation": f"Elevated drawdown of {avg_drawdown:.1f}%. Risk management needs attention."
            })
            red_flags.append(f"Drawdown above 20% ({avg_drawdown:.1f}%) is concerning")
        elif avg_drawdown > 10:
            metric_interpretations.append({
                "metric": "Risk Control",
                "value": f"{risk_control_score:.0f}/100",
                "interpretation": f"Moderate drawdown of {avg_drawdown:.1f}%. Within acceptable range for active trading."
            })
        else:
            metric_interpretations.append({
                "metric": "Risk Control",
                "value": f"{risk_control_score:.0f}/100",
                "interpretation": f"Strong risk control with drawdown limited to {avg_drawdown:.1f}%."
            })
        
        # ===== EXECUTIVE SUMMARY =====
        if total_trades == 0:
            executive_read = [
                "No trading activity recorded in this period.",
                "All performance metrics are undefined or default values.",
                "Unable to assess strategy effectiveness without trade data."
            ]
        else:
            if avg_return >= 0 and avg_sharpe >= 0.5 and avg_profit_factor >= 1.0:
                executive_read.append(f"Portfolio is performing positively with {avg_return:.1f}% return over {period_days} days.")
            elif avg_return < 0:
                executive_read.append(f"Portfolio is in drawdown with {avg_return:.1f}% loss over {period_days} days.")
            
            if len(red_flags) == 0:
                executive_read.append("No critical risk flags detected. Risk parameters are within acceptable bounds.")
            elif len(red_flags) <= 2:
                executive_read.append(f"{len(red_flags)} risk concern(s) identified requiring attention.")
            else:
                executive_read.append(f"ALERT: {len(red_flags)} risk flags detected. Immediate review recommended.")
        
        return {
            "period_days": period_days,
            "total_trades": total_trades,
            "executive_read": executive_read,
            "metric_interpretations": metric_interpretations,
            "red_flags": red_flags,
            "actionable_fixes": actionable_fixes,
            "confidence_notes": confidence_notes,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    def _empty_narrative(self, reason: str) -> Dict[str, Any]:
        """Return empty narrative structure"""
        return {
            "executive_read": [reason],
            "metric_interpretations": [],
            "red_flags": [],
            "actionable_fixes": [],
            "confidence_notes": ["Unable to generate analysis"],
            "error": reason
        }
