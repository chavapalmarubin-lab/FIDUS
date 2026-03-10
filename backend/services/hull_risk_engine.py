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
# CRITICAL: DRAWDOWN IS THE PARAMOUNT RISK METRIC FOR DAY TRADING WITH LEVERAGE
# - 5% Drawdown = WARNING (Yellow Alert)
# - 10% Drawdown = STOP/CRITICAL (Red Alert - Strategy Review Required)
# ============================================================================

DEFAULT_RISK_POLICY = {
    # A) DRAWDOWN LIMITS - PRIMARY RISK CONTROLS (most important due to leverage)
    "drawdown_warning_pct": 5.0,        # 5% drawdown = WARNING alert
    "drawdown_critical_pct": 10.0,      # 10% drawdown = CRITICAL/STOP - must review strategy
    "max_monthly_drawdown_pct": 10.0,   # 10% monthly DD limit (triggers score penalty)
    
    # B) Loss limits (Hull-style "survival first") - Secondary
    "max_risk_per_trade_pct": 1.0,      # 1% of equity (range 0.25-2.0%)
    "max_intraday_loss_pct": 3.0,       # 3% daily stop (range 1.0-5.0%)
    "max_weekly_loss_pct": 6.0,         # 6% weekly (range 3.0-10.0%)
    
    # C) Margin / leverage controls (secondary constraint)
    "leverage": 200,                     # 200:1 static
    "max_margin_usage_pct": 25.0,       # 25% of equity (range 10-35%)
    "max_single_instrument_notional_x": 10,  # Max 10x equity per symbol (range 5-15x)
    "max_total_portfolio_notional_x": 20,    # Max 20x equity total (range 10-30x)
    
    # D) Time risk (FIDUS = intraday only)
    "allow_overnight": False,           # No overnight exposure
    "force_flat_time_utc": "21:50",     # 16:50 NY time = 21:50 UTC (10 min before rollover)
    
    # Allowed ranges for UI validation
    "ranges": {
        "drawdown_warning_pct": [3.0, 8.0],     # Warning threshold range
        "drawdown_critical_pct": [8.0, 15.0],   # Critical threshold range
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
# ============================================================================
# DRAWDOWN IS PARAMOUNT - Heaviest penalties for drawdown breaches
# ============================================================================
RISK_SCORE_PENALTIES = {
    # DRAWDOWN PENALTIES - PRIMARY (most severe due to leverage risk)
    "drawdown_warning_breach": 30,       # -30 for exceeding 5% drawdown
    "drawdown_critical_breach": 60,      # -60 for exceeding 10% drawdown (automatic CRITICAL)
    "monthly_drawdown_breach": 40,       # -40 for monthly DD breach (legacy)
    
    # SECONDARY PENALTIES - Still important but less weight than drawdown
    "lot_breach_per_trade": 4,           # -4 per breach (cap -20) - reduced from 6
    "lot_breach_cap": 20,
    "risk_per_trade_breach": 5,          # -5 per breach (cap -25) - reduced from 8
    "risk_breach_cap": 25,
    "margin_breach_first_day": 8,        # -8 first day - reduced from 10
    "margin_breach_additional": 4,       # -4 each additional (cap -20)
    "margin_breach_cap": 20,
    "daily_loss_breach": 15,             # -15 per day (cap -30) - reduced from 20
    "daily_loss_breach_cap": 30,
    "weekly_loss_breach": 20,            # -20 per week (cap -40) - reduced from 25
    "weekly_loss_breach_cap": 40,
    "overnight_breach": 10,              # -10 per event (cap -30) - reduced from 15
    "overnight_breach_cap": 30
}

# Risk score thresholds and labels - Adjusted for drawdown focus
# With drawdown as primary: any >10% DD should be Critical
RISK_SCORE_LABELS = {
    "strong": {"min": 80, "color": "#10B981", "label": "Strong"},      # <5% DD, no major breaches
    "moderate": {"min": 60, "color": "#F59E0B", "label": "Moderate"},  # Minor breaches
    "weak": {"min": 40, "color": "#F97316", "label": "Weak"},          # 5-10% DD or multiple breaches
    "critical": {"min": 0, "color": "#EF4444", "label": "Critical"}    # >10% DD - STOP AND REVIEW
}

# DRAWDOWN STATUS LEVELS - For UI display
DRAWDOWN_STATUS = {
    "healthy": {"max_pct": 3.0, "color": "#10B981", "label": "Healthy", "icon": "check-circle"},
    "caution": {"max_pct": 5.0, "color": "#F59E0B", "label": "Caution", "icon": "alert-triangle"},
    "warning": {"max_pct": 10.0, "color": "#F97316", "label": "WARNING", "icon": "alert-circle"},
    "critical": {"max_pct": 100.0, "color": "#EF4444", "label": "CRITICAL - STOP", "icon": "x-circle"}
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

# =============================================================================
# COPY RATIO CONFIGURATION - Social Trading Risk Control
# =============================================================================
# The copy ratio is a powerful real-time risk control mechanism.
# By adjusting the ratio, FIDUS can ensure positions sizes stay within risk limits.
# A ratio of 0.5 means the copied trade will be 50% of the source trade size.

VALID_COPY_RATIOS = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]

# Copy ratio recommendation logic:
# 1. If avg lot size breaches > 20% of allowed: reduce ratio by 0.1-0.2
# 2. If avg lot size breaches > 50% of allowed: reduce ratio by 0.3-0.4
# 3. If avg lot size breaches > 100% of allowed: reduce ratio by 0.5+
# 4. Target: Keep lot sizes within 80-100% of FIDUS max allowed

def get_recommended_copy_ratio(
    current_ratio: float,
    avg_breach_pct: float,
    max_breach_pct: float,
    risk_score: int
) -> dict:
    """
    Calculate the recommended copy ratio based on lot size breaches.
    
    Args:
        current_ratio: Currently configured copy ratio (0.1 to 1.0)
        avg_breach_pct: Average percentage over allowed lot size (e.g., 25 = 25% over)
        max_breach_pct: Maximum breach percentage in the period
        risk_score: Current risk control score (0-100)
        
    Returns:
        Dictionary with recommended ratio and explanation
    """
    recommended = current_ratio
    reasons = []
    urgency = "LOW"
    
    # If no breaches, might be able to increase ratio
    if avg_breach_pct <= 0 and max_breach_pct <= 0:
        if current_ratio < 0.9 and risk_score >= 80:
            # Consider increasing ratio if consistently compliant
            recommended = min(current_ratio + 0.1, 1.0)
            reasons.append("No lot size breaches - ratio can potentially be increased")
            urgency = "INFO"
        else:
            reasons.append("Current ratio is appropriate - no changes needed")
            urgency = "OK"
    
    # Minor breaches (0-20% over): reduce by 0.1
    elif avg_breach_pct <= 20:
        recommended = max(current_ratio - 0.1, 0.1)
        reasons.append(f"Minor lot breaches (avg {avg_breach_pct:.0f}% over limit)")
        urgency = "LOW"
    
    # Moderate breaches (20-50% over): reduce by 0.2
    elif avg_breach_pct <= 50:
        recommended = max(current_ratio - 0.2, 0.1)
        reasons.append(f"Moderate lot breaches (avg {avg_breach_pct:.0f}% over limit)")
        urgency = "MEDIUM"
    
    # Significant breaches (50-100% over): reduce by 0.3
    elif avg_breach_pct <= 100:
        recommended = max(current_ratio - 0.3, 0.1)
        reasons.append(f"Significant lot breaches (avg {avg_breach_pct:.0f}% over limit)")
        urgency = "HIGH"
    
    # Severe breaches (>100% over): reduce by 0.4-0.5
    else:
        reduction = 0.4 if avg_breach_pct <= 150 else 0.5
        recommended = max(current_ratio - reduction, 0.1)
        reasons.append(f"Severe lot breaches (avg {avg_breach_pct:.0f}% over limit) - IMMEDIATE ACTION")
        urgency = "CRITICAL"
    
    # Also check max breach (single worst trade)
    if max_breach_pct > 150 and urgency not in ["HIGH", "CRITICAL"]:
        urgency = "HIGH"
        reasons.append(f"Max single breach was {max_breach_pct:.0f}% over limit")
    
    # Round to nearest valid ratio
    recommended = min(VALID_COPY_RATIOS, key=lambda x: abs(x - recommended))
    
    # Calculate the change from current
    ratio_change = recommended - current_ratio
    
    return {
        "current_ratio": current_ratio,
        "recommended_ratio": recommended,
        "ratio_change": round(ratio_change, 2),
        "reasons": reasons,
        "urgency": urgency,
        "action": "DECREASE" if ratio_change < 0 else ("INCREASE" if ratio_change > 0 else "MAINTAIN")
    }


# =============================================================================
# CUSTOM ACCOUNT POLICY OVERRIDES
# =============================================================================
# Some accounts have specific trading styles that require different rules
# These override the DEFAULT_RISK_POLICY for specific accounts

ACCOUNT_POLICY_OVERRIDES = {
    # JOEL ALVES NASDAQ (Account 2215) - Trades NASDAQ after hours
    # - His strategy intentionally trades after the normal force flat time
    # - Instead of penalizing late trades, we monitor TRADE DURATION
    # - Flag trades that exceed 4 hours (since he should be day trading, just later)
    2215: {
        "account_name": "JOEL ALVES NASDAQ",
        "allow_overnight": True,              # Allow after-hours trading
        "skip_force_flat_penalty": True,      # Don't penalize for trading after 21:50 UTC
        "max_trade_duration_hours": 4,        # Flag trades longer than 4 hours
        "trade_duration_penalty": 10,         # -10 points per trade exceeding duration
        "trade_duration_penalty_cap": 30,     # Cap at -30 points
        "notes": "After-hours NASDAQ trader - monitor duration instead of cutoff time"
    }
}


class HullRiskEngine:
    """
    Hull-style risk engine implementing position sizing and risk controls
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    # =========================================================================
    # DEAL DATA RETRIEVAL - Multi-collection support
    # =========================================================================
    
    async def get_deals_for_account(
        self,
        account: int,
        start_date: datetime = None,
        max_deals: int = 5000,
        allowed_symbols: List[str] = None
    ) -> List[Dict]:
        """
        Get deals for an account from both mt5_deals AND mt5_deals_history collections.
        
        Some accounts (especially demo accounts) store deals in mt5_deals_history,
        while real accounts use mt5_deals. This method checks both and returns
        actual trading deals (excluding deposits/withdrawals).
        
        If no deals are found within the date range, it will retry without the date filter
        to capture historical data.
        
        Returns deals SORTED BY TIME (ascending) for proper FIFO matching.
        
        Args:
            account: MT5 account number
            start_date: Optional start date for filtering
            max_deals: Maximum number of deals to fetch
            allowed_symbols: Optional list of symbols to include (e.g., ["BTCUSD"] for crypto-only analysis)
        """
        try:
            # If allowed_symbols not provided, check account config
            if allowed_symbols is None:
                account_config = await self.db.mt5_accounts.find_one({"account": account})
                if account_config:
                    allowed_symbols = account_config.get("allowed_symbols")
            
            query = {"account": account}
            if start_date:
                query["time"] = {"$gte": start_date}
            
            # Try mt5_deals first (primary collection) - SORT BY TIME
            deals = await self.db.mt5_deals.find(query).sort("time", 1).to_list(length=max_deals)
            
            # If no deals found with date filter, try without date filter
            if not deals and start_date:
                logger.info(f"No deals in mt5_deals for account {account} in date range, trying without date filter...")
                deals = await self.db.mt5_deals.find({"account": account}).sort("time", 1).to_list(length=max_deals)
            
            # If still no deals found, check mt5_deals_history (used by demo accounts)
            if not deals:
                logger.info(f"No deals in mt5_deals for account {account}, checking mt5_deals_history...")
                query_history = {"account": account}
                if start_date:
                    query_history["time"] = {"$gte": start_date}
                deals = await self.db.mt5_deals_history.find(query_history).sort("time", 1).to_list(length=max_deals)
                
                # Try without date filter for history too
                if not deals and start_date:
                    deals = await self.db.mt5_deals_history.find({"account": account}).sort("time", 1).to_list(length=max_deals)
                
                if deals:
                    logger.info(f"Found {len(deals)} deals in mt5_deals_history for account {account}")
            
            # Filter out deposits/withdrawals (type 2 with symbol empty and profit == initial deposit)
            # Keep only actual trading deals with symbols
            trading_deals = []
            for deal in deals:
                symbol = deal.get("symbol", "")
                deal_type = deal.get("type", 0)
                comment = deal.get("comment", "").lower()
                
                # Skip balance operations (deposits/withdrawals)
                if not symbol and deal_type == 2 and ("deposit" in comment or "withdraw" in comment):
                    continue
                
                # Skip deals without a symbol (non-trading operations)
                if not symbol:
                    continue
                
                # Apply allowed_symbols filter if specified
                if allowed_symbols:
                    # Normalize symbol comparison (handle .ecn, etc.)
                    symbol_base = symbol.upper().replace(".ECN", "").replace(".STP", "")
                    if not any(allowed.upper() in symbol_base or symbol_base in allowed.upper() for allowed in allowed_symbols):
                        continue
                
                trading_deals.append(deal)
            
            if allowed_symbols:
                logger.info(f"Account {account}: Found {len(trading_deals)} trading deals (filtered by symbols: {allowed_symbols})")
            else:
                logger.info(f"Account {account}: Found {len(trading_deals)} trading deals (filtered from {len(deals)} total)")
            return trading_deals
            
        except Exception as e:
            logger.error(f"Error getting deals for account {account}: {e}")
            return []
    
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
        """Get all instrument specifications - DB specs take priority over defaults"""
        try:
            # Get ALL DB specs (increased limit to 500)
            db_specs = await self.db.instrument_specs.find({}).to_list(length=500)
            
            # If we have DB specs, use only those (Lucrum specs are our source of truth)
            if db_specs:
                for spec in db_specs:
                    spec.pop("_id", None)
                return db_specs
            
            # Fallback to defaults only if no DB specs exist
            return list(DEFAULT_INSTRUMENT_SPECS.values())
            
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
        """Get risk policy for an account or global default
        
        Policy is merged with DEFAULT_RISK_POLICY to ensure all fields have values.
        DB values take precedence over defaults.
        """
        try:
            # Start with defaults
            policy = DEFAULT_RISK_POLICY.copy()
            
            if account:
                db_policy = await self.db.risk_policies.find_one({"account": account})
                if db_policy:
                    db_policy.pop("_id", None)
                    # Merge DB values on top of defaults
                    for key, value in db_policy.items():
                        if value is not None:  # Only override if DB has a non-None value
                            policy[key] = value
                    return policy
            
            # Global policy
            global_policy = await self.db.risk_policies.find_one({"account": None, "is_global": True})
            if global_policy:
                global_policy.pop("_id", None)
                # Merge global policy on top of defaults
                for key, value in global_policy.items():
                    if value is not None:
                        policy[key] = value
                return policy
            
            return policy
            
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
        
        # =====================================================================
        # Calculate LOSS PER LOT AT STOP using contract specifications
        # This is the core of Hull-style position sizing
        # =====================================================================
        
        # Get pip_value_per_lot from specs (critical for accurate calculation)
        pip_value_per_lot = instrument_specs.get("pip_value_per_lot", 10.0)
        pip_size = instrument_specs.get("pip_size", 0.0001)
        asset_class = instrument_specs.get("asset_class", "FX_MAJOR")
        margin_pct = instrument_specs.get("margin_pct", 0.5)  # Use margin from specs
        
        # Calculate loss per lot at stop based on asset class
        if asset_class == "Metals":
            # Metals: For XAUUSD, contract_size = 100 oz, stop in USD terms
            # Loss = stop_distance * (contract_size / 100) * 100 for gold
            # Or simply: stop_distance * pip_value_per_lot * pips
            if symbol == "XAUUSD":
                # Gold: $1 move per oz, 100 oz per lot = $100 per $1 move
                loss_per_lot_at_stop = stop_distance * 100  # stop_distance is in USD
            elif symbol == "XAGUSD":
                # Silver: contract_size = 5000 oz, pip_value_per_lot = 50
                loss_per_lot_at_stop = stop_distance * 50  # stop_distance is in USD
            else:
                # Other metals (XPTUSD, XPDUSD)
                loss_per_lot_at_stop = stop_distance * pip_value_per_lot
                
        elif asset_class in ["FX_MAJOR", "FX_CROSS"]:
            # Forex: Loss = pips * pip_value_per_lot
            # Note: stop_distance might be in PIPS (20) or PRICE (0.0020)
            # If stop_distance > 1, assume it's in pips directly
            # If stop_distance < 1, it's in price terms and needs to be converted to pips
            if stop_distance >= 1:
                # Already in pips (e.g., 20 pips)
                pips = stop_distance
            elif pip_size > 0:
                # Convert from price to pips (e.g., 0.0020 / 0.0001 = 20 pips)
                pips = stop_distance / pip_size
            else:
                # Fallback: assume standard 4-decimal pip
                pips = stop_distance * 10000
            loss_per_lot_at_stop = pips * pip_value_per_lot
            
        elif asset_class == "INDEX_CFD":
            # Indices: Loss = points * pip_value_per_lot (usually $1 per point)
            # stop_distance is in index points
            loss_per_lot_at_stop = stop_distance * pip_value_per_lot
            
        elif asset_class == "Commodities":
            # Commodities: contract_size matters
            # For oil (contract_size=1000 barrels), $1 move = $1000
            loss_per_lot_at_stop = stop_distance * contract_size * pip_value_per_lot / 1000
            
        elif asset_class == "Crypto":
            # Crypto: contract_size = 1, so loss = stop_distance * pip_value_per_lot
            loss_per_lot_at_stop = stop_distance * pip_value_per_lot
            
        else:
            # Generic fallback
            loss_per_lot_at_stop = stop_distance * pip_value_per_lot
        
        # Ensure minimum loss per lot to avoid division by zero
        loss_per_lot_at_stop = max(loss_per_lot_at_stop, 0.01)
        
        # =====================================================================
        # Calculate MAX LOTS based on RISK (stop-based sizing)
        # MaxLotsRisk = RiskBudget / LossPerLotAtStop
        # =====================================================================
        max_lots_risk = risk_budget / loss_per_lot_at_stop
        
        # =====================================================================
        # Calculate MAX LOTS based on MARGIN using specs margin_pct
        # Margin required per lot = (contract_size * price) * (margin_pct / 100)
        # Or use leverage: Margin = Notional / Leverage
        # =====================================================================
        
        # Get effective leverage from margin_pct
        # margin_pct of 0.2% = 500:1 leverage, 1% = 100:1, etc.
        effective_leverage = 100 / margin_pct if margin_pct > 0 else leverage
        
        # Calculate notional value per lot
        if current_price and current_price > 0:
            notional_per_lot = contract_size * current_price
        else:
            # Estimate based on typical values for each asset class
            if asset_class == "Metals":
                if symbol == "XAUUSD":
                    notional_per_lot = contract_size * 2650  # ~$2650/oz gold
                elif symbol == "XAGUSD":
                    notional_per_lot = contract_size * 30  # ~$30/oz silver
                else:
                    notional_per_lot = contract_size * 1000  # Generic metals
            elif asset_class in ["FX_MAJOR", "FX_CROSS"]:
                notional_per_lot = contract_size  # 100,000 units
            elif asset_class == "INDEX_CFD":
                # Estimate index values
                if symbol in ["US30"]:
                    notional_per_lot = contract_size * 43000
                elif symbol in ["NAS100", "UT100"]:
                    notional_per_lot = contract_size * 21000
                elif symbol in ["DE40", "GER40"]:
                    notional_per_lot = contract_size * 22000
                elif symbol in ["US500", "SPX500"]:
                    notional_per_lot = contract_size * 5800
                else:
                    notional_per_lot = contract_size * 10000
            elif asset_class == "Commodities":
                if symbol in ["USOUSD", "UKOUSD"]:
                    notional_per_lot = contract_size * 75  # ~$75/barrel
                elif symbol == "NATGAS":
                    notional_per_lot = contract_size * 3  # ~$3/MMBtu
                else:
                    notional_per_lot = contract_size * 100
            elif asset_class == "Crypto":
                if symbol == "BTCUSD":
                    notional_per_lot = contract_size * 95000  # ~$95k BTC
                elif symbol == "ETHUSD":
                    notional_per_lot = contract_size * 3500  # ~$3500 ETH
                else:
                    notional_per_lot = contract_size * 100  # Generic crypto
            else:
                notional_per_lot = contract_size
        
        # =====================================================================
        # Calculate MARGIN REQUIRED per lot using Lucrum's official formulas
        # Based on margin_calc_type from instrument specifications:
        # - FOREX: Lots * Contract_Size / Leverage * Percentage / 100
        # - CFD: Lots * Contract_Size * Market_Price * Percentage / 100
        # - CFDLEVERAGE: Lots * Contract_Size * Market_Price / Leverage * Percentage / 100
        # - FOREX_NO_LEVERAGE: Same as CFD (percentage-based, no leverage)
        # =====================================================================
        margin_calc_type = instrument_specs.get("margin_calc_type", "FOREX")
        lucrum_leverage = instrument_specs.get("lucrum_leverage", leverage)
        
        # Note: margin_pct is already in decimal form (0.01 = 1%)
        # We need to convert it to percentage for the formula
        margin_percentage = margin_pct  # Already 0.01 for 1%
        
        if margin_calc_type == "FOREX":
            # FOREX: Lots * Contract_Size / Leverage * Percentage / 100
            # For 1 lot: Contract_Size / Leverage * Percentage / 100
            # Example: 100,000 / 200 * 1 / 100 = $5 margin per lot (for 1% margin at 200:1)
            margin_per_lot = (contract_size / lucrum_leverage) * margin_percentage
            
        elif margin_calc_type in ["CFD", "FOREX_NO_LEVERAGE", "Forex-no leverage"]:
            # CFD/No Leverage: Lots * Contract_Size * Market_Price * Percentage / 100
            # This uses notional value * percentage (no leverage reduction)
            margin_per_lot = notional_per_lot * margin_percentage
            
        elif margin_calc_type == "CFDLEVERAGE":
            # CFD-Leverage: Lots * Contract_Size * Market_Price / Leverage * Percentage / 100
            # Example: 100 oz * $2650 / 200 * 0.01 = $13.25 margin per lot for gold
            margin_per_lot = (notional_per_lot / lucrum_leverage) * margin_percentage
            
        else:
            # Default fallback: use notional * margin_pct
            margin_per_lot = notional_per_lot * margin_percentage
        
        logger.debug(f"Margin calculation for {symbol}: type={margin_calc_type}, "
                    f"leverage={lucrum_leverage}, notional={notional_per_lot:.2f}, "
                    f"margin_pct={margin_percentage*100:.2f}%, margin_per_lot=${margin_per_lot:.2f}")
        
        # Max margin allowed from equity
        max_margin_allowed = equity * max_margin_pct
        
        # Max lots based on margin
        if margin_per_lot > 0:
            max_lots_margin = max_margin_allowed / margin_per_lot
        else:
            max_lots_margin = max_lot
        
        # =====================================================================
        # Final max lots = min(risk, margin) capped at instrument max
        # =====================================================================
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
            "asset_class": asset_class,
            "equity": equity,
            "risk_budget": round(risk_budget, 2),
            "risk_per_trade_pct": risk_per_trade_pct * 100,
            "stop_distance": stop_distance,
            "stop_source": stop_source,
            "loss_per_lot_at_stop": round(loss_per_lot_at_stop, 2),
            "max_lots_risk": round(self._floor_to_step(max_lots_risk, lot_step), 2),
            "contract_size": contract_size,
            "margin_calc_type": margin_calc_type,  # NEW: Track which formula was used
            "margin_pct": margin_pct,
            "lucrum_leverage": lucrum_leverage,  # NEW: Lucrum-specific leverage
            "effective_leverage": round(effective_leverage, 1),
            "notional_per_lot": round(notional_per_lot, 2),
            "margin_per_lot": round(margin_per_lot, 2),
            "max_margin_allowed": round(max_margin_allowed, 2),
            "max_lots_margin": round(self._floor_to_step(max_lots_margin, lot_step), 2),
            "max_lots_allowed": round(max_lots_allowed, 2),
            "binding_constraint": binding_constraint,
            "lot_step": lot_step,
            "min_lot": min_lot,
            "max_lot": max_lot,
            "pip_value_per_lot": pip_value_per_lot
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
        
        ============================================================================
        DRAWDOWN IS THE PARAMOUNT RISK FACTOR (due to leverage in forex day trading)
        ============================================================================
        
        PRIMARY PENALTY (Drawdown) - Applied FIRST:
        - 5% drawdown (WARNING): -30 points
        - 10% drawdown (CRITICAL): -60 points (automatic CRITICAL status)
        
        SECONDARY PENALTIES (only if drawdown is healthy):
        - Lot breach: -4 each (cap -20)
        - Risk-per-trade breach: -5 each (cap -25)
        - Margin breach: -8 first day, -4 additional (cap -20)
        - Daily loss breach: -15 each (cap -30)
        - Overnight breach: -10 each (cap -30)
        
        Labels:
        - 80-100: Strong (drawdown <5%, minimal breaches)
        - 60-79: Moderate (some breaches)
        - 40-59: Weak (5-10% drawdown OR multiple breaches)
        - 0-39: Critical (>10% drawdown - STOP AND REVIEW STRATEGY)
        """
        try:
            risk_policy = await self.get_risk_policy(account)
            
            # Get account info
            account_info = await self.db.mt5_accounts.find_one({"account": account})
            if not account_info:
                return self._empty_risk_score("Account not found")
            
            equity = account_info.get("equity", 0)
            initial_allocation = account_info.get("initial_allocation", equity)
            
            # Use peak equity if available, otherwise use initial allocation
            peak_equity = account_info.get("peak_equity", initial_allocation)
            if peak_equity < initial_allocation:
                peak_equity = initial_allocation
            
            # Get deals for the period (checks both mt5_deals AND mt5_deals_history)
            start_date = datetime.now(timezone.utc) - timedelta(days=period_days)
            deals = await self.get_deals_for_account(account, start_date, max_deals=1000)
            
            # ===== Calculate breaches and penalties =====
            score = 100  # Start at 100
            breach_details = []
            drawdown_alerts = []
            
            # ============================================================
            # STEP 1: DRAWDOWN CALCULATION - THE PRIMARY RISK METRIC
            # Calculate TRUE Maximum Drawdown from equity curve (deals)
            # ============================================================
            current_dd_pct = 0
            max_dd_pct = 0
            calculated_peak_equity = peak_equity
            
            # Build equity curve from deals to calculate real drawdown
            if deals and initial_allocation > 0:
                # Sort deals chronologically (oldest first)
                sorted_deals = sorted(deals, key=lambda d: d.get("time", 0))
                
                # Build equity curve by accumulating profits
                running_equity = initial_allocation
                running_peak = initial_allocation
                max_dd_amount = 0
                
                for deal in sorted_deals:
                    profit = deal.get("profit", 0)
                    swap = deal.get("swap", 0)
                    commission = deal.get("commission", 0)
                    
                    # Add all P&L components
                    running_equity += profit + swap + commission
                    
                    # Update peak if we have a new high
                    if running_equity > running_peak:
                        running_peak = running_equity
                    
                    # Calculate drawdown from peak
                    dd_amount = running_peak - running_equity
                    if dd_amount > max_dd_amount:
                        max_dd_amount = dd_amount
                
                # Calculate max drawdown percentage
                if running_peak > 0:
                    max_dd_pct = (max_dd_amount / running_peak) * 100
                
                # Use the calculated peak
                calculated_peak_equity = running_peak
                
                # Current drawdown = peak - current equity
                if calculated_peak_equity > 0 and equity > 0:
                    current_dd_pct = max(0, ((calculated_peak_equity - equity) / calculated_peak_equity) * 100)
                
                logger.info(f"Account {account}: Peak=${calculated_peak_equity:.2f}, Current=${equity:.2f}, Max DD={max_dd_pct:.2f}%, Current DD={current_dd_pct:.2f}%")
            else:
                # Fallback: simple calculation from stored values
                if peak_equity > 0:
                    current_dd_pct = max(0, ((peak_equity - equity) / peak_equity) * 100)
                elif initial_allocation > 0:
                    current_dd_pct = max(0, ((initial_allocation - equity) / initial_allocation) * 100)
            
            # Use the WORSE of current drawdown vs max historical drawdown
            effective_dd_pct = max(current_dd_pct, max_dd_pct)
            
            # Get drawdown thresholds from policy
            dd_warning_threshold = risk_policy.get("drawdown_warning_pct", 5.0)
            dd_critical_threshold = risk_policy.get("drawdown_critical_pct", 10.0)
            
            # Determine drawdown status based on BOTH current and max drawdown
            if effective_dd_pct >= dd_critical_threshold:
                drawdown_status = "critical"
                drawdown_penalty = RISK_SCORE_PENALTIES["drawdown_critical_breach"]
                score -= drawdown_penalty
                breach_details.insert(0, f"⛔ CRITICAL DRAWDOWN: {effective_dd_pct:.1f}% (threshold: {dd_critical_threshold}%) (-{drawdown_penalty})")
                drawdown_alerts.append({
                    "severity": "CRITICAL",
                    "message": f"STOP TRADING - Drawdown at {effective_dd_pct:.1f}% exceeds {dd_critical_threshold}% limit. Review strategy immediately.",
                    "action_required": "STOP"
                })
            elif effective_dd_pct >= dd_warning_threshold:
                drawdown_status = "warning"
                drawdown_penalty = RISK_SCORE_PENALTIES["drawdown_warning_breach"]
                score -= drawdown_penalty
                breach_details.insert(0, f"⚠️ WARNING DRAWDOWN: {effective_dd_pct:.1f}% (threshold: {dd_warning_threshold}%) (-{drawdown_penalty})")
                drawdown_alerts.append({
                    "severity": "WARNING",
                    "message": f"Drawdown at {effective_dd_pct:.1f}% - approaching critical level. Reduce position sizes.",
                    "action_required": "REDUCE_RISK"
                })
            elif effective_dd_pct >= 3.0:
                drawdown_status = "caution"
                # No penalty, but flag for awareness
                drawdown_alerts.append({
                    "severity": "CAUTION",
                    "message": f"Drawdown at {effective_dd_pct:.1f}% - monitor closely.",
                    "action_required": "MONITOR"
                })
            else:
                drawdown_status = "healthy"
            
            # ============================================================
            # STEP 2: SECONDARY PENALTIES (only apply if not already critical)
            # ============================================================
            
            # 2a) Lot breach penalties
            lot_breaches = await self._count_lot_breaches(deals, equity, risk_policy)
            lot_penalty = min(lot_breaches * RISK_SCORE_PENALTIES["lot_breach_per_trade"], 
                             RISK_SCORE_PENALTIES["lot_breach_cap"])
            score -= lot_penalty
            if lot_breaches > 0:
                breach_details.append(f"Lot breaches: {lot_breaches} (-{lot_penalty})")
            
            # 2b) Risk-per-trade breach penalties
            risk_breaches = self._count_risk_breaches(deals, initial_allocation, risk_policy)
            risk_penalty = min(risk_breaches * RISK_SCORE_PENALTIES["risk_per_trade_breach"],
                              RISK_SCORE_PENALTIES["risk_breach_cap"])
            score -= risk_penalty
            if risk_breaches > 0:
                breach_details.append(f"Risk breaches: {risk_breaches} (-{risk_penalty})")
            
            # 2c) Margin breach penalties
            margin_breach_days = self._count_margin_breach_days(account_info, risk_policy)
            if margin_breach_days > 0:
                margin_penalty = RISK_SCORE_PENALTIES["margin_breach_first_day"]
                if margin_breach_days > 1:
                    margin_penalty += (margin_breach_days - 1) * RISK_SCORE_PENALTIES["margin_breach_additional"]
                margin_penalty = min(margin_penalty, RISK_SCORE_PENALTIES["margin_breach_cap"])
                score -= margin_penalty
                breach_details.append(f"Margin breaches: {margin_breach_days} days (-{margin_penalty})")
            
            # 2d) Daily loss breach penalties
            daily_breaches = self._count_daily_loss_breaches(account_info, deals, risk_policy)
            daily_penalty = min(daily_breaches * RISK_SCORE_PENALTIES["daily_loss_breach"],
                               RISK_SCORE_PENALTIES["daily_loss_breach_cap"])
            score -= daily_penalty
            if daily_breaches > 0:
                breach_details.append(f"Daily loss breaches: {daily_breaches} (-{daily_penalty})")
            
            # 2e) Overnight breach penalties (check for account-specific overrides)
            overnight_breaches = self._count_overnight_breaches(deals, risk_policy, account)
            overnight_penalty = min(overnight_breaches * RISK_SCORE_PENALTIES["overnight_breach"],
                                   RISK_SCORE_PENALTIES["overnight_breach_cap"])
            score -= overnight_penalty
            if overnight_breaches > 0:
                breach_details.append(f"Overnight breaches: {overnight_breaches} (-{overnight_penalty})")
            
            # 2f) Trade duration breach penalties (for accounts with max_trade_duration_hours)
            account_override = ACCOUNT_POLICY_OVERRIDES.get(account, {})
            if account_override.get("max_trade_duration_hours"):
                duration_breaches = self._count_trade_duration_breaches(
                    deals, 
                    account_override.get("max_trade_duration_hours")
                )
                duration_penalty_per = account_override.get("trade_duration_penalty", 10)
                duration_penalty_cap = account_override.get("trade_duration_penalty_cap", 30)
                duration_penalty = min(duration_breaches * duration_penalty_per, duration_penalty_cap)
                score -= duration_penalty
                if duration_breaches > 0:
                    breach_details.append(f"Trade duration breaches (>{account_override.get('max_trade_duration_hours')}h): {duration_breaches} (-{duration_penalty})")
            
            # Clamp score to 0-100
            composite_score = max(0, min(100, score))
            
            # ============================================================
            # STEP 3: DETERMINE FINAL LABEL (Drawdown overrides other factors)
            # ============================================================
            # If drawdown is critical, force Critical label regardless of score
            if drawdown_status == "critical":
                label = "Critical"
                color = "#EF4444"  # Red
            elif composite_score >= RISK_SCORE_LABELS["strong"]["min"]:
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
            
            # Compute component metrics for detailed view
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
                # ============================================================
                # DRAWDOWN - PRIMARY RISK METRIC (prominently displayed)
                # ============================================================
                "drawdown": {
                    "current_pct": round(current_dd_pct, 2),
                    "max_pct": round(max_dd_pct, 2),  # Maximum historical drawdown
                    "effective_pct": round(effective_dd_pct, 2),  # Worse of current or max
                    "status": drawdown_status,
                    "warning_threshold": dd_warning_threshold,
                    "critical_threshold": dd_critical_threshold,
                    "alerts": drawdown_alerts,
                    "peak_equity": calculated_peak_equity,
                    "current_equity": equity,
                    "initial_allocation": initial_allocation,
                    "is_critical": drawdown_status == "critical",
                    "is_warning": drawdown_status == "warning"
                },
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
    
    async def analyze_drawdown_triggers(
        self,
        account: int,
        period_days: int = 90
    ) -> Dict[str, Any]:
        """
        QUANTITATIVE DRAWDOWN ANALYSIS
        ==============================
        Identifies exactly which trades triggered drawdown events.
        This is critical for algorithm-driven funds to optimize bot parameters.
        
        Returns:
        - Drawdown events (when DD exceeded thresholds)
        - Triggering trades for each event
        - Pattern analysis (symbols, time of day, lot sizes, trade direction)
        - Bot optimization recommendations
        """
        try:
            risk_policy = await self.get_risk_policy(account)
            dd_warning = risk_policy.get("drawdown_warning_pct", 5.0)
            dd_critical = risk_policy.get("drawdown_critical_pct", 10.0)
            
            # Get account info
            account_info = await self.db.mt5_accounts.find_one({"account": account})
            if not account_info:
                return {"success": False, "error": "Account not found"}
            
            initial_allocation = account_info.get("initial_allocation", 0)
            if initial_allocation <= 0:
                initial_allocation = account_info.get("equity", 100000)
            
            # Get all deals for the period
            start_date = datetime.now(timezone.utc) - timedelta(days=period_days)
            deals = await self.get_deals_for_account(account, start_date, max_deals=5000)
            
            if not deals:
                return {"success": False, "error": "No deals found for analysis"}
            
            # Sort deals chronologically
            sorted_deals = sorted(deals, key=lambda d: d.get("time", 0))
            
            # Build equity curve and identify drawdown events
            running_equity = initial_allocation
            running_peak = initial_allocation
            peak_timestamp = None
            
            drawdown_events = []
            current_dd_event = None
            dd_triggering_trades = []
            
            # Track statistics for pattern analysis
            all_dd_trades = []  # All trades that contributed to drawdowns
            
            for i, deal in enumerate(sorted_deals):
                profit = deal.get("profit", 0)
                swap = deal.get("swap", 0)
                commission = deal.get("commission", 0)
                total_pnl = profit + swap + commission
                
                prev_equity = running_equity
                running_equity += total_pnl
                
                # Check if this is a new peak
                if running_equity > running_peak:
                    # If we were in a drawdown, close that event
                    if current_dd_event:
                        current_dd_event["recovery_date"] = deal.get("time")
                        current_dd_event["recovery_equity"] = running_equity
                        current_dd_event["triggering_trades"] = dd_triggering_trades.copy()
                        current_dd_event["total_trades_in_dd"] = len(dd_triggering_trades)
                        drawdown_events.append(current_dd_event)
                        current_dd_event = None
                        dd_triggering_trades = []
                    
                    running_peak = running_equity
                    peak_timestamp = deal.get("time")
                
                # Calculate current drawdown percentage
                if running_peak > 0:
                    dd_pct = ((running_peak - running_equity) / running_peak) * 100
                else:
                    dd_pct = 0
                
                # Check if this trade pushed us into/deeper into drawdown
                if total_pnl < 0 and dd_pct > 0:
                    trade_info = {
                        "ticket": deal.get("ticket"),
                        "time": deal.get("time"),
                        "symbol": deal.get("symbol", ""),
                        "type": "BUY" if deal.get("type") == 0 else "SELL",
                        "volume": deal.get("volume", 0),
                        "price": deal.get("price", 0),
                        "profit": profit,
                        "swap": swap,
                        "commission": commission,
                        "total_pnl": total_pnl,
                        "equity_before": prev_equity,
                        "equity_after": running_equity,
                        "dd_pct_after": round(dd_pct, 2),
                        "dd_contribution_pct": round(abs(total_pnl) / running_peak * 100, 3) if running_peak > 0 else 0
                    }
                    
                    dd_triggering_trades.append(trade_info)
                    all_dd_trades.append(trade_info)
                    
                    # Check if this trade triggered a warning/critical threshold
                    prev_dd_pct = ((running_peak - prev_equity) / running_peak * 100) if running_peak > 0 else 0
                    
                    # Start new drawdown event if we crossed a threshold
                    if not current_dd_event:
                        if dd_pct >= dd_warning:
                            current_dd_event = {
                                "event_id": len(drawdown_events) + 1,
                                "start_date": peak_timestamp,
                                "peak_equity": running_peak,
                                "severity": "CRITICAL" if dd_pct >= dd_critical else "WARNING",
                                "max_dd_pct": dd_pct,
                                "trough_equity": running_equity,
                                "trough_date": deal.get("time"),
                                "first_trigger_trade": trade_info
                            }
                    else:
                        # Update existing event if DD got worse
                        if dd_pct > current_dd_event["max_dd_pct"]:
                            current_dd_event["max_dd_pct"] = dd_pct
                            current_dd_event["trough_equity"] = running_equity
                            current_dd_event["trough_date"] = deal.get("time")
                            if dd_pct >= dd_critical and current_dd_event["severity"] == "WARNING":
                                current_dd_event["severity"] = "CRITICAL"
                                current_dd_event["critical_trigger_trade"] = trade_info
            
            # Close any open drawdown event
            if current_dd_event:
                current_dd_event["triggering_trades"] = dd_triggering_trades
                current_dd_event["total_trades_in_dd"] = len(dd_triggering_trades)
                current_dd_event["status"] = "ONGOING"
                drawdown_events.append(current_dd_event)
            
            # ================================================================
            # PATTERN ANALYSIS - Identify what's causing drawdowns
            # ================================================================
            pattern_analysis = self._analyze_drawdown_patterns(all_dd_trades, sorted_deals)
            
            # ================================================================
            # BOT OPTIMIZATION RECOMMENDATIONS
            # ================================================================
            recommendations = self._generate_bot_recommendations(
                pattern_analysis, 
                drawdown_events, 
                dd_warning, 
                dd_critical
            )
            
            return {
                "success": True,
                "account": account,
                "analysis_period_days": period_days,
                "total_deals_analyzed": len(sorted_deals),
                "initial_allocation": initial_allocation,
                "current_equity": running_equity,
                "peak_equity": running_peak,
                "thresholds": {
                    "warning": dd_warning,
                    "critical": dd_critical
                },
                "drawdown_events": [
                    {
                        **event,
                        "max_dd_pct": round(event["max_dd_pct"], 2),
                        "loss_amount": round(event["peak_equity"] - event["trough_equity"], 2),
                        "triggering_trades": event.get("triggering_trades", [])[:10]  # Limit to top 10
                    }
                    for event in drawdown_events
                ],
                "total_drawdown_events": len(drawdown_events),
                "critical_events": len([e for e in drawdown_events if e["severity"] == "CRITICAL"]),
                "warning_events": len([e for e in drawdown_events if e["severity"] == "WARNING"]),
                "pattern_analysis": pattern_analysis,
                "bot_recommendations": recommendations,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing drawdown triggers: {e}")
            return {"success": False, "error": str(e)}
    
    def _analyze_drawdown_patterns(
        self, 
        dd_trades: List[Dict], 
        all_trades: List[Dict]
    ) -> Dict[str, Any]:
        """
        Analyze patterns in trades that caused drawdowns.
        Helps identify systematic issues in bot algorithms.
        """
        if not dd_trades:
            return {"has_patterns": False, "message": "No drawdown trades to analyze"}
        
        # 1. Symbol Analysis - Which instruments cause most drawdowns?
        symbol_losses = {}
        for trade in dd_trades:
            symbol = trade.get("symbol", "UNKNOWN")
            if symbol not in symbol_losses:
                symbol_losses[symbol] = {"count": 0, "total_loss": 0, "avg_dd_contribution": 0}
            symbol_losses[symbol]["count"] += 1
            symbol_losses[symbol]["total_loss"] += abs(trade.get("total_pnl", 0))
            symbol_losses[symbol]["avg_dd_contribution"] += trade.get("dd_contribution_pct", 0)
        
        # Calculate averages and sort
        for symbol in symbol_losses:
            if symbol_losses[symbol]["count"] > 0:
                symbol_losses[symbol]["avg_dd_contribution"] /= symbol_losses[symbol]["count"]
        
        worst_symbols = sorted(
            symbol_losses.items(), 
            key=lambda x: x[1]["total_loss"], 
            reverse=True
        )[:5]
        
        # 2. Time Analysis - What time of day do drawdowns occur?
        hour_distribution = {}
        for trade in dd_trades:
            trade_time = trade.get("time")
            if trade_time:
                if isinstance(trade_time, (int, float)):
                    hour = datetime.fromtimestamp(trade_time, tz=timezone.utc).hour
                else:
                    hour = trade_time.hour if hasattr(trade_time, 'hour') else 12
                if hour not in hour_distribution:
                    hour_distribution[hour] = {"count": 0, "total_loss": 0}
                hour_distribution[hour]["count"] += 1
                hour_distribution[hour]["total_loss"] += abs(trade.get("total_pnl", 0))
        
        worst_hours = sorted(
            hour_distribution.items(),
            key=lambda x: x[1]["total_loss"],
            reverse=True
        )[:5]
        
        # 3. Position Size Analysis - Are larger positions causing issues?
        volumes = [t.get("volume", 0) for t in dd_trades]
        avg_dd_volume = sum(volumes) / len(volumes) if volumes else 0
        
        all_volumes = [t.get("volume", 0) for t in all_trades if t.get("volume", 0) > 0]
        avg_all_volume = sum(all_volumes) / len(all_volumes) if all_volumes else 0
        
        volume_analysis = {
            "avg_dd_trade_volume": round(avg_dd_volume, 4),
            "avg_all_trade_volume": round(avg_all_volume, 4),
            "volume_ratio": round(avg_dd_volume / avg_all_volume, 2) if avg_all_volume > 0 else 0,
            "oversized_trades": avg_dd_volume > avg_all_volume * 1.5
        }
        
        # 4. Trade Direction Analysis - Are BUYs or SELLs causing more issues?
        buy_losses = sum(abs(t.get("total_pnl", 0)) for t in dd_trades if t.get("type") == "BUY")
        sell_losses = sum(abs(t.get("total_pnl", 0)) for t in dd_trades if t.get("type") == "SELL")
        buy_count = sum(1 for t in dd_trades if t.get("type") == "BUY")
        sell_count = sum(1 for t in dd_trades if t.get("type") == "SELL")
        
        direction_analysis = {
            "buy_losses": round(buy_losses, 2),
            "sell_losses": round(sell_losses, 2),
            "buy_count": buy_count,
            "sell_count": sell_count,
            "dominant_losing_direction": "BUY" if buy_losses > sell_losses else "SELL",
            "direction_bias": round(abs(buy_losses - sell_losses) / max(buy_losses + sell_losses, 1) * 100, 1)
        }
        
        # 5. Consecutive Loss Analysis - Are there losing streaks?
        max_consecutive = 0
        current_streak = 0
        consecutive_loss_periods = []
        
        for trade in dd_trades:
            if trade.get("total_pnl", 0) < 0:
                current_streak += 1
                if current_streak > max_consecutive:
                    max_consecutive = current_streak
            else:
                if current_streak >= 3:
                    consecutive_loss_periods.append(current_streak)
                current_streak = 0
        
        streak_analysis = {
            "max_consecutive_losses": max_consecutive,
            "loss_streak_periods": len(consecutive_loss_periods),
            "avg_streak_length": round(sum(consecutive_loss_periods) / len(consecutive_loss_periods), 1) if consecutive_loss_periods else 0
        }
        
        return {
            "has_patterns": True,
            "total_dd_trades": len(dd_trades),
            "worst_symbols": [
                {
                    "symbol": s[0],
                    "loss_count": s[1]["count"],
                    "total_loss": round(s[1]["total_loss"], 2),
                    "avg_dd_contribution": round(s[1]["avg_dd_contribution"], 3)
                }
                for s in worst_symbols
            ],
            "worst_trading_hours_utc": [
                {
                    "hour": h[0],
                    "loss_count": h[1]["count"],
                    "total_loss": round(h[1]["total_loss"], 2)
                }
                for h in worst_hours
            ],
            "volume_analysis": volume_analysis,
            "direction_analysis": direction_analysis,
            "streak_analysis": streak_analysis
        }
    
    def _generate_bot_recommendations(
        self,
        patterns: Dict[str, Any],
        events: List[Dict],
        dd_warning: float,
        dd_critical: float
    ) -> List[Dict[str, Any]]:
        """
        Generate actionable recommendations for bot optimization
        based on drawdown pattern analysis.
        """
        recommendations = []
        
        if not patterns.get("has_patterns"):
            return [{"priority": "INFO", "category": "GENERAL", "recommendation": "Insufficient data for pattern analysis"}]
        
        # 1. Symbol-based recommendations
        worst_symbols = patterns.get("worst_symbols", [])
        if worst_symbols:
            top_loser = worst_symbols[0]
            if top_loser["loss_count"] >= 3:
                recommendations.append({
                    "priority": "HIGH",
                    "category": "SYMBOL_FILTER",
                    "recommendation": f"Review {top_loser['symbol']} trading logic - {top_loser['loss_count']} trades caused ${top_loser['total_loss']:,.2f} in losses",
                    "action": f"Consider reducing position size or adding filters for {top_loser['symbol']}",
                    "parameter_suggestion": f"max_position_{top_loser['symbol'].lower()}: reduce by 50%"
                })
        
        # 2. Time-based recommendations
        worst_hours = patterns.get("worst_trading_hours_utc", [])
        if worst_hours:
            dangerous_hours = [h for h in worst_hours if h["loss_count"] >= 3]
            if dangerous_hours:
                hours_str = ", ".join([f"{h['hour']}:00 UTC" for h in dangerous_hours[:3]])
                recommendations.append({
                    "priority": "HIGH",
                    "category": "TIME_FILTER",
                    "recommendation": f"Avoid trading during high-loss hours: {hours_str}",
                    "action": "Add time-based filters to bot configuration",
                    "parameter_suggestion": f"blocked_hours: [{', '.join([str(h['hour']) for h in dangerous_hours[:3]])}]"
                })
        
        # 3. Volume-based recommendations
        vol_analysis = patterns.get("volume_analysis", {})
        if vol_analysis.get("oversized_trades"):
            recommendations.append({
                "priority": "CRITICAL",
                "category": "POSITION_SIZE",
                "recommendation": f"Drawdown trades are {vol_analysis['volume_ratio']:.1f}x larger than average - reduce position sizing",
                "action": "Implement dynamic position sizing based on recent volatility",
                "parameter_suggestion": f"max_lot_size: {vol_analysis['avg_all_volume']:.4f}"
            })
        
        # 4. Direction-based recommendations
        dir_analysis = patterns.get("direction_analysis", {})
        if dir_analysis.get("direction_bias", 0) > 30:
            losing_dir = dir_analysis["dominant_losing_direction"]
            recommendations.append({
                "priority": "MEDIUM",
                "category": "DIRECTION_BIAS",
                "recommendation": f"{losing_dir} trades causing {dir_analysis['direction_bias']:.0f}% more losses - review {losing_dir} entry logic",
                "action": f"Add confirmation filters for {losing_dir} entries or reduce {losing_dir} position sizes",
                "parameter_suggestion": f"{'buy' if losing_dir == 'BUY' else 'sell'}_size_multiplier: 0.5"
            })
        
        # 5. Streak-based recommendations
        streak_analysis = patterns.get("streak_analysis", {})
        if streak_analysis.get("max_consecutive_losses", 0) >= 5:
            recommendations.append({
                "priority": "HIGH",
                "category": "RISK_MANAGEMENT",
                "recommendation": f"Detected {streak_analysis['max_consecutive_losses']} consecutive losses - implement circuit breaker",
                "action": "Add automatic trading pause after N consecutive losses",
                "parameter_suggestion": f"max_consecutive_losses_before_pause: 3"
            })
        
        # 6. Drawdown threshold recommendations
        critical_events = [e for e in events if e["severity"] == "CRITICAL"]
        if len(critical_events) >= 2:
            recommendations.append({
                "priority": "CRITICAL",
                "category": "DRAWDOWN_CONTROL",
                "recommendation": f"{len(critical_events)} CRITICAL drawdown events detected - implement hard stop",
                "action": f"Add automatic position closure when drawdown reaches {dd_warning}%",
                "parameter_suggestion": f"auto_close_dd_threshold: {dd_warning}"
            })
        
        # Sort by priority
        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 5))
        
        return recommendations

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
        symbol_specs_cache = {}  # Cache instrument specs per symbol
        
        for deal in deals:
            symbol = deal.get("symbol", "")
            volume = deal.get("volume", 0)
            
            if not symbol or volume <= 0:
                continue
            
            # Cache instrument specs per symbol
            if symbol not in symbol_specs_cache:
                specs = await self.get_instrument_specs(symbol)
                max_calc = self.calculate_max_lots(equity, specs, risk_policy)
                symbol_specs_cache[symbol] = max_calc
            else:
                max_calc = symbol_specs_cache[symbol]
            
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
                    except ValueError:
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
        risk_policy: Dict,
        account: int = None
    ) -> int:
        """
        Count overnight position breaches (positions held past force-flat time)
        
        FIDUS RULE: All strategies are DAY TRADING ONLY
        - No positions can be held overnight
        - Force flat time: 21:50 UTC (16:50 NY time) - 10 min before rollover
        - Asia market opening (Sunday 5PM EST = Monday Asia open) is highest volatility
        - Gap risk is unacceptable for FIDUS
        
        EXCEPTION: Some accounts have custom rules (see ACCOUNT_POLICY_OVERRIDES)
        - Account 2215 (JOEL ALVES NASDAQ): Allowed to trade after hours
        
        Detection: Look for positions that:
        1. Opened on day N and closed on day N+1 or later
        2. Uses FIFO matching by symbol when position_id is not available
        """
        # Check for account-specific overrides
        account_override = ACCOUNT_POLICY_OVERRIDES.get(account, {}) if account else {}
        
        # If this account has skip_force_flat_penalty, don't count overnight breaches
        if account_override.get("skip_force_flat_penalty", False):
            logger.info(f"⏭️ Account {account} ({account_override.get('account_name', 'Unknown')}): Skipping overnight breach check (after-hours trader)")
            return 0
        
        # FIDUS DEFAULT: No overnight allowed (day trading only)
        if risk_policy.get("allow_overnight", False):
            return 0  # Overnight explicitly allowed, no breaches
        
        overnight_count = 0
        positions_by_ticket = {}  # For position_id-based matching
        symbol_entry_queue = {}   # For FIFO matching by symbol
        
        for deal in deals:
            symbol = deal.get("symbol", "")
            if not symbol:
                continue
            
            raw_position_id = deal.get("position_id") or deal.get("position")
            ticket = deal.get("ticket")
            
            # Determine if we have a valid position_id for matching
            use_fifo_matching = raw_position_id is None
            position_key = raw_position_id if not use_fifo_matching else ticket
            
            deal_time = deal.get("time")
            
            # Convert time to datetime if it's a timestamp
            if isinstance(deal_time, (int, float)):
                deal_time = datetime.fromtimestamp(deal_time, tz=timezone.utc)
            elif isinstance(deal_time, str):
                try:
                    deal_time = datetime.fromisoformat(deal_time.replace('Z', '+00:00'))
                except:
                    continue
            
            if deal_time is None:
                continue
            
            # In MT5: entry=0 is IN, entry=1 is OUT
            entry_type = deal.get("entry", -1)
            
            if entry_type == 0:  # Position opened
                entry_data = {
                    "open_time": deal_time,
                    "symbol": symbol,
                    "ticket": ticket
                }
                
                if use_fifo_matching:
                    # FIFO queue by symbol
                    if symbol not in symbol_entry_queue:
                        symbol_entry_queue[symbol] = []
                    symbol_entry_queue[symbol].append(entry_data)
                else:
                    # Direct position_id matching
                    positions_by_ticket[position_key] = entry_data
                    
            elif entry_type == 1:  # Position closed
                entry_data = None
                
                if use_fifo_matching:
                    # FIFO matching by symbol
                    if symbol in symbol_entry_queue and symbol_entry_queue[symbol]:
                        entry_data = symbol_entry_queue[symbol].pop(0)
                else:
                    # Direct position_id matching
                    if position_key in positions_by_ticket:
                        entry_data = positions_by_ticket[position_key]
                        del positions_by_ticket[position_key]
                
                if entry_data:
                    open_time = entry_data["open_time"]
                    close_time = deal_time
                    
                    # Check if held overnight (different calendar days)
                    open_date = open_time.date()
                    close_date = close_time.date()
                    
                    if close_date > open_date:
                        overnight_count += 1
                        logger.debug(f"⚠️ OVERNIGHT BREACH: {symbol} opened {open_time.isoformat()} closed {close_time.isoformat()}")
        
        return overnight_count
    
    def _count_trade_duration_breaches(
        self,
        deals: List[Dict],
        max_duration_hours: float
    ) -> int:
        """
        Count trades that exceed the maximum allowed duration.
        
        Used for accounts that trade after hours (like JOEL ALVES NASDAQ)
        where we monitor trade duration instead of force flat time.
        
        Args:
            deals: List of deal records
            max_duration_hours: Maximum allowed trade duration in hours
            
        Returns:
            Number of trades exceeding the duration limit
        """
        duration_breaches = 0
        positions_by_ticket = {}  # For position_id-based matching
        symbol_entry_queue = {}   # For FIFO matching by symbol
        
        for deal in deals:
            symbol = deal.get("symbol", "")
            if not symbol:
                continue
            
            raw_position_id = deal.get("position_id") or deal.get("position")
            ticket = deal.get("ticket")
            
            use_fifo_matching = raw_position_id is None
            position_key = raw_position_id if not use_fifo_matching else ticket
            
            deal_time = deal.get("time")
            
            # Convert time to datetime if needed
            if isinstance(deal_time, (int, float)):
                deal_time = datetime.fromtimestamp(deal_time, tz=timezone.utc)
            elif isinstance(deal_time, str):
                try:
                    deal_time = datetime.fromisoformat(deal_time.replace('Z', '+00:00'))
                except:
                    continue
            
            if deal_time is None:
                continue
            
            entry_type = deal.get("entry", -1)
            
            if entry_type == 0:  # Position opened
                entry_data = {
                    "open_time": deal_time,
                    "symbol": symbol,
                    "ticket": ticket
                }
                
                if use_fifo_matching:
                    if symbol not in symbol_entry_queue:
                        symbol_entry_queue[symbol] = []
                    symbol_entry_queue[symbol].append(entry_data)
                else:
                    positions_by_ticket[position_key] = entry_data
                    
            elif entry_type == 1:  # Position closed
                entry_data = None
                
                if use_fifo_matching:
                    if symbol in symbol_entry_queue and symbol_entry_queue[symbol]:
                        entry_data = symbol_entry_queue[symbol].pop(0)
                else:
                    if position_key in positions_by_ticket:
                        entry_data = positions_by_ticket[position_key]
                        del positions_by_ticket[position_key]
                
                if entry_data:
                    open_time = entry_data["open_time"]
                    close_time = deal_time
                    
                    # Calculate duration in hours
                    duration = (close_time - open_time).total_seconds() / 3600
                    
                    if duration > max_duration_hours:
                        duration_breaches += 1
                        logger.debug(f"⚠️ DURATION BREACH: {symbol} held for {duration:.2f}h (max: {max_duration_hours}h)")
        
        return duration_breaches
    
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
        """
        Calculate drawdown compliance - THE PARAMOUNT RISK METRIC
        
        Thresholds (FIDUS day trading with leverage):
        - <3%: Healthy (score 100)
        - 3-5%: Caution (score 80)
        - 5-10%: WARNING (score 40)
        - >10%: CRITICAL - STOP (score 0)
        """
        equity = account_info.get("equity", 0)
        peak_equity = account_info.get("peak_equity", initial_allocation)
        
        # Use peak equity for more accurate drawdown calculation
        reference_equity = max(peak_equity, initial_allocation) if peak_equity > 0 else initial_allocation
        
        # Calculate current drawdown from peak
        if reference_equity > 0:
            current_dd_pct = max(0, ((reference_equity - equity) / reference_equity) * 100)
        else:
            current_dd_pct = 0
        
        # Get thresholds from policy
        dd_warning = risk_policy.get("drawdown_warning_pct", 5.0)
        dd_critical = risk_policy.get("drawdown_critical_pct", 10.0)
        
        # Score based on drawdown - STRICT thresholds for day trading
        if current_dd_pct < 3.0:
            score = 100
            status = "HEALTHY"
            status_color = "#10B981"  # Green
        elif current_dd_pct < dd_warning:
            score = 80
            status = "CAUTION"
            status_color = "#F59E0B"  # Yellow
        elif current_dd_pct < dd_critical:
            score = 40
            status = "WARNING"
            status_color = "#F97316"  # Orange
        else:
            score = 0
            status = "CRITICAL - STOP"
            status_color = "#EF4444"  # Red
        
        return {
            "score": round(score, 1),
            "detail": f"Drawdown: {current_dd_pct:.2f}% | Status: {status}",
            "current_drawdown_pct": round(current_dd_pct, 2),
            "warning_threshold": dd_warning,
            "critical_threshold": dd_critical,
            "status": status,
            "status_color": status_color,
            "peak_equity": reference_equity,
            "current_equity": equity
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
        symbol_specs_cache = {}  # Cache instrument specs per symbol
        
        for deal in deals:
            symbol = deal.get("symbol", "")
            volume = deal.get("volume", 0)
            
            if not symbol or volume <= 0:
                continue
            
            total_evaluated += 1
            
            # Cache instrument specs per symbol
            if symbol not in symbol_specs_cache:
                specs = await self.get_instrument_specs(symbol)
                max_calc = self.calculate_max_lots(equity, specs, risk_policy)
                symbol_specs_cache[symbol] = max_calc
            else:
                max_calc = symbol_specs_cache[symbol]
            
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
        Analyzes ACTUAL deals to determine compliance with risk parameters
        """
        try:
            # Get account info
            account_info = await self.db.mt5_accounts.find_one({"account": account})
            if not account_info:
                return {"error": f"Account {account} not found"}
            
            equity = account_info.get("equity", 0)
            initial_allocation = account_info.get("initial_allocation", equity)
            risk_policy = await self.get_risk_policy(account)
            
            # Get deals for analysis (checks both mt5_deals AND mt5_deals_history)
            start_date = datetime.now(timezone.utc) - timedelta(days=period_days)
            deals = await self.get_deals_for_account(account, start_date, max_deals=5000)
            
            # ===== DEAL-BY-DEAL ANALYSIS =====
            deal_analysis = []
            symbol_analysis = {}
            symbol_max_lots_cache = {}  # Cache max_lots calculations per symbol
            total_trades = 0
            lot_breaches = 0
            risk_breaches = 0
            daily_pnl = {}  # For daily loss analysis
            
            # ===== TRADING HOURS COMPLIANCE TRACKING =====
            force_flat_time_str = risk_policy.get("force_flat_time_utc", "21:50")
            force_flat_hour, force_flat_minute = map(int, force_flat_time_str.split(":"))
            allow_overnight = risk_policy.get("allow_overnight", False)
            
            # Check for account-specific overrides (e.g., JOEL ALVES NASDAQ trades after hours)
            account_override = ACCOUNT_POLICY_OVERRIDES.get(account, {})
            skip_force_flat_penalty = account_override.get("skip_force_flat_penalty", False)
            max_trade_duration_hours = account_override.get("max_trade_duration_hours")
            trade_duration_breaches = []  # Track trades exceeding duration limit
            
            # Trade timing analysis
            trade_times = []  # List of all trade entry/exit times
            overnight_positions = []  # Positions held overnight
            late_trades = []  # Trades closed after force flat time
            trade_durations = []  # All trade durations in minutes
            positions_tracker = {}  # Track open positions by position_id
            symbol_entry_queue = {}  # FIFO queue for matching by symbol when position_id not available
            entry_hour_distribution = {}  # Hours of entries
            exit_hour_distribution = {}  # Hours of exits
            weekend_trades = []  # Trades during weekend/Asia open
            
            max_risk_per_trade = initial_allocation * (risk_policy.get("max_risk_per_trade_pct", 1.0) / 100)
            max_intraday_loss = initial_allocation * (risk_policy.get("max_intraday_loss_pct", 3.0) / 100)
            
            for deal in deals:
                symbol = deal.get("symbol", "")
                if not symbol:
                    continue
                
                total_trades += 1
                volume = deal.get("volume", 0)
                profit = deal.get("profit", 0)
                deal_time = deal.get("time")
                ticket = deal.get("ticket", "N/A")
                deal_type = deal.get("type", "")
                
                # Track daily P&L
                if deal_time:
                    if isinstance(deal_time, str):
                        try:
                            deal_time = datetime.fromisoformat(deal_time.replace('Z', '+00:00'))
                        except ValueError:
                            deal_time = None
                    elif isinstance(deal_time, (int, float)):
                        deal_time = datetime.fromtimestamp(deal_time, tz=timezone.utc)
                    
                    if deal_time:
                        date_key = deal_time.strftime("%Y-%m-%d")
                        daily_pnl[date_key] = daily_pnl.get(date_key, 0) + profit
                        
                        # ===== TRADING HOURS COMPLIANCE TRACKING =====
                        hour_key = deal_time.hour
                        raw_position_id = deal.get("position_id") or deal.get("position")
                        entry_type = deal.get("entry", -1)
                        
                        # Determine if we have a valid position_id for matching
                        # position_id can be None in some MT5 data exports
                        use_fifo_matching = raw_position_id is None
                        position_key = raw_position_id if not use_fifo_matching else ticket
                        
                        # Track entry times (entry=0 is IN)
                        if entry_type == 0 or (entry_type == -1 and deal_type in [0, 1]):
                            entry_hour_distribution[hour_key] = entry_hour_distribution.get(hour_key, 0) + 1
                            
                            entry_data = {
                                "ticket": ticket,
                                "symbol": symbol,
                                "volume": volume,
                                "entry_time": deal_time,
                                "entry_price": deal.get("price", 0)
                            }
                            
                            if use_fifo_matching:
                                # Use FIFO queue by symbol when position_id not available
                                if symbol not in symbol_entry_queue:
                                    symbol_entry_queue[symbol] = []
                                symbol_entry_queue[symbol].append(entry_data)
                            else:
                                # Use direct position_id matching
                                positions_tracker[position_key] = entry_data
                            
                            # Check if entry is during prohibited period (Sunday Asia open)
                            day_of_week = deal_time.weekday()  # 0=Monday, 6=Sunday
                            if day_of_week == 6:  # Sunday
                                weekend_trades.append({
                                    "ticket": ticket,
                                    "symbol": symbol,
                                    "time": deal_time.isoformat(),
                                    "issue": "Entry on Sunday (Asia open risk)"
                                })
                            
                            # Check if entry is after force flat time
                            # Skip this check for accounts with skip_force_flat_penalty (e.g., JOEL ALVES NASDAQ)
                            if not skip_force_flat_penalty:
                                if hour_key > force_flat_hour or (hour_key == force_flat_hour and deal_time.minute >= force_flat_minute):
                                    late_trades.append({
                                        "ticket": ticket,
                                        "symbol": symbol,
                                        "time": deal_time.isoformat(),
                                        "issue": f"Entry after force flat ({force_flat_time_str} UTC)"
                                    })
                        
                        # Track exit times (entry=1 is OUT)
                        elif entry_type == 1:
                            exit_hour_distribution[hour_key] = exit_hour_distribution.get(hour_key, 0) + 1
                            
                            # Try to find matching entry
                            entry_data = None
                            matched_ticket = ticket
                            
                            if use_fifo_matching:
                                # FIFO matching by symbol - pop earliest entry for this symbol
                                if symbol in symbol_entry_queue and symbol_entry_queue[symbol]:
                                    entry_data = symbol_entry_queue[symbol].pop(0)
                                    matched_ticket = entry_data.get("ticket", ticket)
                            else:
                                # Direct position_id matching
                                if position_key in positions_tracker:
                                    entry_data = positions_tracker[position_key]
                                    matched_ticket = position_key
                                    del positions_tracker[position_key]
                            
                            if entry_data:
                                entry_time = entry_data["entry_time"]
                                
                                # Calculate trade duration
                                duration_minutes = (deal_time - entry_time).total_seconds() / 60
                                trade_durations.append({
                                    "ticket": matched_ticket,
                                    "symbol": symbol,
                                    "entry_time": entry_time.isoformat(),
                                    "exit_time": deal_time.isoformat(),
                                    "duration_minutes": round(duration_minutes, 1),
                                    "duration_hours": round(duration_minutes / 60, 2),
                                    "profit": profit
                                })
                                
                                # Check for overnight position (different calendar days)
                                if entry_time.date() != deal_time.date():
                                    overnight_positions.append({
                                        "ticket": matched_ticket,
                                        "symbol": symbol,
                                        "entry_date": entry_time.date().isoformat(),
                                        "exit_date": deal_time.date().isoformat(),
                                        "duration_hours": round(duration_minutes / 60, 1),
                                        "profit": profit,
                                        "issue": "OVERNIGHT POSITION - Day trading violation"
                                    })
                            
                            # Check if exit was after force flat time (regardless of matching)
                            # Skip this check for accounts with skip_force_flat_penalty
                            if not skip_force_flat_penalty:
                                if hour_key > force_flat_hour or (hour_key == force_flat_hour and deal_time.minute >= force_flat_minute):
                                    late_trades.append({
                                        "ticket": ticket,
                                        "symbol": symbol,
                                        "time": deal_time.isoformat(),
                                        "issue": f"Exit after force flat ({force_flat_time_str} UTC)"
                                    })
                            
                            # Check trade duration for accounts with max_trade_duration_hours
                            if max_trade_duration_hours and duration_minutes > (max_trade_duration_hours * 60):
                                trade_duration_breaches.append({
                                    "ticket": matched_ticket,
                                    "symbol": symbol,
                                    "entry_time": entry_time.isoformat(),
                                    "exit_time": deal_time.isoformat(),
                                    "duration_hours": round(duration_minutes / 60, 2),
                                    "max_allowed_hours": max_trade_duration_hours,
                                    "profit": profit,
                                    "issue": f"Trade held for {duration_minutes/60:.1f}h (max: {max_trade_duration_hours}h)"
                                })
                
                # Symbol-level aggregation - cache instrument specs
                if symbol not in symbol_analysis:
                    specs = await self.get_instrument_specs(symbol)
                    # Pre-compute max_lots for this symbol using default stop distance
                    default_max_calc = self.calculate_max_lots(
                        equity, specs, risk_policy, 
                        specs.get("default_stop_distance", 10)
                    )
                    symbol_max_lots_cache[symbol] = default_max_calc
                    symbol_analysis[symbol] = {
                        "specs": specs,
                        "trades": 0,
                        "total_volume": 0,
                        "max_volume": 0,
                        "min_volume": float('inf'),
                        "total_pnl": 0,
                        "winning_trades": 0,
                        "losing_trades": 0,
                        "breached_trades": [],
                        "stop_distances": []
                    }
                
                sa = symbol_analysis[symbol]
                sa["trades"] += 1
                sa["total_volume"] += volume
                sa["max_volume"] = max(sa["max_volume"], volume)
                sa["min_volume"] = min(sa["min_volume"], volume)
                sa["total_pnl"] += profit
                if profit > 0:
                    sa["winning_trades"] += 1
                elif profit < 0:
                    sa["losing_trades"] += 1
                
                # Track stop distances for average calculation later
                sl = deal.get("sl", 0)
                price = deal.get("price", 0)
                stop_distance = abs(price - sl) if (sl > 0 and price > 0) else None
                
                if stop_distance:
                    sa["stop_distances"].append(stop_distance)
                
                # Use cached max_lots calculation for this symbol
                max_calc = symbol_max_lots_cache[symbol]
                
                # Check for lot size breach
                is_lot_breach = volume > max_calc["max_lots_allowed"]
                breach_pct = (volume / max_calc["max_lots_allowed"] * 100) if max_calc["max_lots_allowed"] > 0 else 0
                
                if is_lot_breach:
                    lot_breaches += 1
                    sa["breached_trades"].append({
                        "ticket": ticket,
                        "volume": volume,
                        "allowed": max_calc["max_lots_allowed"],
                        "breach_pct": breach_pct
                    })
                
                # Check for risk per trade breach (based on actual loss)
                is_risk_breach = profit < 0 and abs(profit) > max_risk_per_trade
                if is_risk_breach:
                    risk_breaches += 1
                
                # Note: Skipping deal_analysis append for performance
                # Only summary-level data is needed for the UI
            
            # ===== DAILY LOSS BREACH ANALYSIS =====
            daily_loss_breaches = []
            for date_key, pnl in daily_pnl.items():
                if pnl < -max_intraday_loss:
                    daily_loss_breaches.append({
                        "date": date_key,
                        "loss": round(pnl, 2),
                        "limit": round(-max_intraday_loss, 2)
                    })
            
            # ===== BUILD INSTRUMENTS SUMMARY =====
            instruments_analysis = []
            total_lot_breaches_by_symbol = []
            
            for symbol, data in symbol_analysis.items():
                specs = data["specs"]
                avg_stop = sum(data["stop_distances"]) / len(data["stop_distances"]) if data["stop_distances"] else specs.get("default_stop_distance", 10)
                
                max_calc = self.calculate_max_lots(equity, specs, risk_policy, avg_stop)
                
                is_breach = data["max_volume"] > max_calc["max_lots_allowed"]
                breach_count = len(data["breached_trades"])
                compliance_rate = ((data["trades"] - breach_count) / data["trades"] * 100) if data["trades"] > 0 else 100
                win_rate = (data["winning_trades"] / data["trades"] * 100) if data["trades"] > 0 else 0
                
                analysis = {
                    "symbol": symbol,
                    "name": specs.get("name", symbol),
                    "asset_class": specs.get("asset_class", "Unknown"),
                    "trades": data["trades"],
                    "winning_trades": data["winning_trades"],
                    "losing_trades": data["losing_trades"],
                    "win_rate": round(win_rate, 1),
                    "total_volume": round(data["total_volume"], 2),
                    "avg_volume": round(data["total_volume"] / data["trades"], 2) if data["trades"] > 0 else 0,
                    "max_volume_used": round(data["max_volume"], 2),
                    "min_volume_used": round(data["min_volume"], 2) if data["min_volume"] != float('inf') else 0,
                    "max_lots_allowed": max_calc["max_lots_allowed"],
                    "binding_constraint": max_calc["binding_constraint"],
                    "avg_stop_distance": round(avg_stop, 5),
                    "is_compliant": not is_breach,
                    "compliance_rate": round(compliance_rate, 1),
                    "breach_count": breach_count,
                    "breached_trades": data["breached_trades"][:5],  # Top 5 breaches
                    "total_pnl": round(data["total_pnl"], 2)
                }
                
                instruments_analysis.append(analysis)
                
                if is_breach:
                    total_lot_breaches_by_symbol.append({
                        "symbol": symbol,
                        "max_used": data["max_volume"],
                        "allowed": max_calc["max_lots_allowed"],
                        "breach_count": breach_count
                    })
            
            # ===== RISK CONTROL SCORE =====
            risk_score = await self.calculate_risk_control_score(account, period_days)
            
            # ===== COMPLIANCE SUMMARY =====
            overall_compliance = {
                "lot_size_compliance": {
                    "compliant_trades": total_trades - lot_breaches,
                    "breached_trades": lot_breaches,
                    "total_trades": total_trades,
                    "compliance_rate": round(((total_trades - lot_breaches) / total_trades * 100) if total_trades > 0 else 100, 1),
                    "status": "PASS" if lot_breaches == 0 else ("WARNING" if lot_breaches < 3 else "FAIL")
                },
                "risk_per_trade_compliance": {
                    "compliant_trades": total_trades - risk_breaches,
                    "breached_trades": risk_breaches,
                    "total_trades": total_trades,
                    "compliance_rate": round(((total_trades - risk_breaches) / total_trades * 100) if total_trades > 0 else 100, 1),
                    "max_risk_allowed": round(max_risk_per_trade, 2),
                    "status": "PASS" if risk_breaches == 0 else ("WARNING" if risk_breaches < 3 else "FAIL")
                },
                "daily_loss_compliance": {
                    "breach_days": len(daily_loss_breaches),
                    "max_daily_loss_allowed": round(max_intraday_loss, 2),
                    "breaches": daily_loss_breaches[:5],  # Top 5
                    "status": "PASS" if len(daily_loss_breaches) == 0 else "FAIL"
                },
                # ===== TRADING HOURS COMPLIANCE (DAY TRADING STRICT) =====
                "trading_hours_compliance": {
                    "overnight_positions": len(overnight_positions),
                    "late_trades": len(late_trades),
                    "weekend_trades": len(weekend_trades),
                    "force_flat_time": force_flat_time_str + " UTC",
                    "allow_overnight": allow_overnight,
                    "status": "PASS" if (len(overnight_positions) == 0 and len(late_trades) == 0) else "FAIL",
                    "violations": {
                        "overnight": overnight_positions[:10],  # Top 10
                        "late": late_trades[:10],
                        "weekend": weekend_trades[:10]
                    }
                },
                # ===== TRADE DURATION ANALYSIS =====
                "trade_duration_analysis": {
                    "total_trades_with_duration": len(trade_durations),
                    "avg_duration_minutes": round(sum(t["duration_minutes"] for t in trade_durations) / len(trade_durations), 1) if trade_durations else 0,
                    "max_duration_hours": round(max((t["duration_hours"] for t in trade_durations), default=0), 2),
                    "min_duration_minutes": round(min((t["duration_minutes"] for t in trade_durations), default=0), 1),
                    "durations": sorted(trade_durations, key=lambda x: -x["duration_minutes"])[:10],  # Top 10 longest trades
                    "day_trades_pct": round(len([t for t in trade_durations if t["duration_hours"] < 16]) / len(trade_durations) * 100, 1) if trade_durations else 100
                },
                # ===== ENTRY/EXIT HOUR DISTRIBUTION =====
                "time_distribution": {
                    "entry_hours": entry_hour_distribution,
                    "exit_hours": exit_hour_distribution,
                    "peak_entry_hour": max(entry_hour_distribution, key=entry_hour_distribution.get) if entry_hour_distribution else None,
                    "peak_exit_hour": max(exit_hour_distribution, key=exit_hour_distribution.get) if exit_hour_distribution else None
                }
            }
            
            # ===== GENERATE ACTION ITEMS & ALERTS =====
            action_items = []
            alerts = []
            
            # Lot size issues
            if lot_breaches > 0:
                breach_pct = (lot_breaches / total_trades * 100) if total_trades > 0 else 0
                action_items.append({
                    "priority": "HIGH" if breach_pct > 30 else "MEDIUM",
                    "category": "lot_size",
                    "issue": f"{lot_breaches} trades exceeded lot size limits ({breach_pct:.1f}% of trades)",
                    "fix": "Reduce position sizes per instrument to stay within MaxLotsAllowed"
                })
                for breach in total_lot_breaches_by_symbol[:3]:
                    alerts.append({
                        "type": "LOT_BREACH",
                        "severity": "WARNING",
                        "message": f"{breach['symbol']}: Using {breach['max_used']:.2f} lots, limit is {breach['allowed']:.2f}"
                    })
            
            # Risk per trade issues
            if risk_breaches > 0:
                action_items.append({
                    "priority": "HIGH",
                    "category": "risk_per_trade",
                    "issue": f"{risk_breaches} trades lost more than ${max_risk_per_trade:,.0f} (1% limit)",
                    "fix": "Use tighter stop-losses or reduce position sizes to cap risk per trade"
                })
                alerts.append({
                    "type": "RISK_BREACH",
                    "severity": "CRITICAL" if risk_breaches > 5 else "WARNING",
                    "message": f"{risk_breaches} trades exceeded max risk per trade (${max_risk_per_trade:,.0f})"
                })
            
            # Daily loss issues
            if len(daily_loss_breaches) > 0:
                action_items.append({
                    "priority": "HIGH",
                    "category": "daily_loss",
                    "issue": f"{len(daily_loss_breaches)} days exceeded daily loss limit (${max_intraday_loss:,.0f})",
                    "fix": "Implement hard daily loss cutoff - stop trading when 80% of limit reached"
                })
                for breach in daily_loss_breaches[:2]:
                    alerts.append({
                        "type": "DAILY_LOSS_BREACH",
                        "severity": "CRITICAL",
                        "message": f"{breach['date']}: Lost ${abs(breach['loss']):,.0f}, limit was ${max_intraday_loss:,.0f}"
                    })
            
            # ===== TRADING HOURS VIOLATIONS =====
            # Overnight positions are critical violations
            if len(overnight_positions) > 0:
                action_items.append({
                    "priority": "CRITICAL",
                    "category": "trading_hours",
                    "issue": f"{len(overnight_positions)} OVERNIGHT POSITIONS DETECTED - Day trading rule violated",
                    "fix": "ALL positions must be closed by 21:50 UTC. NO EXCEPTIONS."
                })
                for pos in overnight_positions[:3]:
                    alerts.append({
                        "type": "OVERNIGHT_POSITION",
                        "severity": "CRITICAL",
                        "message": f"🚨 {pos['symbol']} held overnight: {pos['entry_date']} → {pos['exit_date']} ({pos['duration_hours']}h)"
                    })
            
            # Late trades (after force flat time) - Skip for accounts with skip_force_flat_penalty
            if len(late_trades) > 0 and not skip_force_flat_penalty:
                action_items.append({
                    "priority": "HIGH",
                    "category": "trading_hours",
                    "issue": f"{len(late_trades)} trades executed after force flat time ({force_flat_time_str} UTC)",
                    "fix": "Stop all trading by 21:50 UTC to avoid overnight gap risk"
                })
                for trade in late_trades[:2]:
                    alerts.append({
                        "type": "LATE_TRADE",
                        "severity": "WARNING",
                        "message": f"⏰ {trade['symbol']} traded at {trade['time'][:19]} - after force flat"
                    })
            
            # Trade duration breaches (for accounts with max_trade_duration_hours like JOEL ALVES NASDAQ)
            if len(trade_duration_breaches) > 0:
                action_items.append({
                    "priority": "HIGH",
                    "category": "trade_duration",
                    "issue": f"{len(trade_duration_breaches)} trades exceeded {max_trade_duration_hours}h duration limit",
                    "fix": f"Close positions within {max_trade_duration_hours} hours to maintain day trading discipline"
                })
                for breach in trade_duration_breaches[:2]:
                    alerts.append({
                        "type": "DURATION_BREACH",
                        "severity": "WARNING",
                        "message": f"⏱️ {breach['symbol']} held for {breach['duration_hours']:.1f}h (max: {max_trade_duration_hours}h)"
                    })
            
            # Weekend/Asia open trades
            if len(weekend_trades) > 0:
                action_items.append({
                    "priority": "HIGH",
                    "category": "trading_hours",
                    "issue": f"{len(weekend_trades)} trades during high-risk periods (Sunday Asia open)",
                    "fix": "Avoid trading Sunday 17:00-22:00 EST due to extreme volatility"
                })
                alerts.append({
                    "type": "WEEKEND_RISK",
                    "severity": "WARNING",
                    "message": f"🌏 {len(weekend_trades)} trades during Sunday Asia open (highest volatility period)"
                })
            
            # ===== WHAT-IF SIMULATION DATA =====
            # Calculate projected scores at different equity levels
            current_score = risk_score.get("composite_score", 100)
            
            what_if_scenarios = []
            # Scenario: What if equity was 50% higher?
            higher_equity = equity * 1.5
            higher_max_risk = higher_equity * (risk_policy.get("max_risk_per_trade_pct", 1.0) / 100)
            higher_max_daily = higher_equity * (risk_policy.get("max_intraday_loss_pct", 3.0) / 100)
            what_if_scenarios.append({
                "scenario": "+50% equity",
                "new_equity": higher_equity,
                "new_risk_limit": higher_max_risk,
                "new_daily_limit": higher_max_daily,
                "projected_improvement": "More headroom for position sizing",
                "note": f"Risk per trade limit increases from ${max_risk_per_trade:,.0f} to ${higher_max_risk:,.0f}"
            })
            
            # Scenario: What if equity was 50% lower?
            lower_equity = equity * 0.5
            lower_max_risk = lower_equity * (risk_policy.get("max_risk_per_trade_pct", 1.0) / 100)
            lower_max_daily = lower_equity * (risk_policy.get("max_intraday_loss_pct", 3.0) / 100)
            what_if_scenarios.append({
                "scenario": "-50% equity",
                "new_equity": lower_equity,
                "new_risk_limit": lower_max_risk,
                "new_daily_limit": lower_max_daily,
                "projected_improvement": "Stricter limits - more breaches expected",
                "note": f"Risk per trade limit decreases from ${max_risk_per_trade:,.0f} to ${lower_max_risk:,.0f}"
            })
            
            # ===== DETAILED COMPLIANCE TABLE =====
            compliance_details = {
                "lot_size": {
                    "policy_limit": "MaxLotsAllowed per instrument",
                    "calculation": "min(RiskBudget/LossPerLot, MarginLimit)",
                    "breaches": lot_breaches,
                    "total_trades": total_trades,
                    "compliance_rate": round(((total_trades - lot_breaches) / total_trades * 100) if total_trades > 0 else 100, 1),
                    "penalty_applied": min(30, (lot_breaches // 5) * 6),
                    "by_instrument": [
                        {
                            "symbol": inst["symbol"],
                            "limit": inst["max_lots_allowed"],
                            "max_used": inst["max_volume_used"],
                            "breach_pct": round((inst["max_volume_used"] / inst["max_lots_allowed"] - 1) * 100, 1) if inst["max_lots_allowed"] > 0 and inst["max_volume_used"] > inst["max_lots_allowed"] else 0,
                            "status": "BREACH" if not inst["is_compliant"] else "OK"
                        }
                        for inst in instruments_analysis
                    ]
                },
                "risk_per_trade": {
                    "policy_limit": f"${max_risk_per_trade:,.0f} (1% of equity)",
                    "calculation": f"{risk_policy.get('max_risk_per_trade_pct', 1.0)}% x ${equity:,.0f} equity",
                    "breaches": risk_breaches,
                    "total_trades": total_trades,
                    "compliance_rate": round(((total_trades - risk_breaches) / total_trades * 100) if total_trades > 0 else 100, 1),
                    "penalty_applied": min(40, risk_breaches * 8)
                },
                "daily_loss": {
                    "policy_limit": f"${max_intraday_loss:,.0f} (3% of equity)",
                    "calculation": f"{risk_policy.get('max_intraday_loss_pct', 3.0)}% x ${equity:,.0f} equity",
                    "breach_days": len(daily_loss_breaches),
                    "breaches_detail": daily_loss_breaches[:5],
                    "penalty_applied": min(40, len(daily_loss_breaches) * 20)
                },
                # ===== DAY TRADING COMPLIANCE (STRICT) =====
                # Account-specific override for after-hours traders (e.g., JOEL ALVES NASDAQ)
                "trading_hours": {
                    "policy": "After-hours trading allowed - Monitor TRADE DURATION instead" if skip_force_flat_penalty else "ALL positions must be closed by force flat time. NO overnight positions.",
                    "force_flat_time": "N/A (after-hours trader)" if skip_force_flat_penalty else f"{force_flat_time_str} UTC (16:50 NY)",
                    "account_override": account_override.get("account_name") if skip_force_flat_penalty else None,
                    "overnight_positions_found": len(overnight_positions),
                    "late_trades_found": len(late_trades),
                    "weekend_trades_found": len(weekend_trades),
                    "overnight_violations": overnight_positions[:5] if not skip_force_flat_penalty else [],
                    "late_trade_violations": late_trades[:5] if not skip_force_flat_penalty else [],
                    "penalty_applied": 0 if skip_force_flat_penalty else min(45, len(overnight_positions) * 15),
                    "status": "COMPLIANT" if skip_force_flat_penalty or len(overnight_positions) == 0 else "NON-COMPLIANT"
                },
                "trade_duration": {
                    "total_trades_analyzed": len(trade_durations),
                    "average_duration_minutes": round(sum(t["duration_minutes"] for t in trade_durations) / len(trade_durations), 1) if trade_durations else 0,
                    "longest_trade_hours": round(max((t["duration_hours"] for t in trade_durations), default=0), 2),
                    "shortest_trade_minutes": round(min((t["duration_minutes"] for t in trade_durations), default=0), 1),
                    "day_trades_percentage": round(len([t for t in trade_durations if t["duration_hours"] < 16]) / len(trade_durations) * 100, 1) if trade_durations else 100,
                    "longest_trades": sorted(trade_durations, key=lambda x: -x["duration_minutes"])[:5],
                    # Add trade duration breach info for accounts with custom rules
                    "max_duration_hours": max_trade_duration_hours,
                    "duration_breaches": len(trade_duration_breaches) if max_trade_duration_hours else 0,
                    "duration_breach_details": trade_duration_breaches[:5] if max_trade_duration_hours else [],
                    "duration_policy": f"Trades must not exceed {max_trade_duration_hours}h" if max_trade_duration_hours else "No duration limit"
                },
                "trading_session_analysis": {
                    "entry_hours_utc": dict(sorted(entry_hour_distribution.items())),
                    "exit_hours_utc": dict(sorted(exit_hour_distribution.items())),
                    "most_active_entry_hour": max(entry_hour_distribution, key=entry_hour_distribution.get) if entry_hour_distribution else None,
                    "most_active_exit_hour": max(exit_hour_distribution, key=exit_hour_distribution.get) if exit_hour_distribution else None,
                    "trades_after_force_flat": len([t for t in late_trades if 'Exit' not in t.get('issue', '')])
                }
            }
            
            return {
                "account": account,
                "manager_name": account_info.get("manager_name", f"Account {account}"),
                "equity": equity,
                "initial_allocation": initial_allocation,
                "leverage": risk_policy.get("leverage", 200),
                "risk_policy": {
                    "max_risk_per_trade_pct": risk_policy.get("max_risk_per_trade_pct", 1.0),
                    "max_intraday_loss_pct": risk_policy.get("max_intraday_loss_pct", 3.0),
                    "max_margin_usage_pct": risk_policy.get("max_margin_usage_pct", 25.0)
                },
                "risk_control_score": risk_score,
                "compliance_summary": overall_compliance,
                "compliance_details": compliance_details,
                "action_items": action_items,
                "alerts": alerts,
                "what_if_scenarios": what_if_scenarios,
                "instruments": sorted(instruments_analysis, key=lambda x: x["trades"], reverse=True),
                "lot_breaches_by_symbol": total_lot_breaches_by_symbol,
                "daily_loss_breaches": daily_loss_breaches,
                "total_trades_analyzed": total_trades,
                "total_lot_breaches": lot_breaches,
                "total_risk_breaches": risk_breaches,
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
    
    # =========================================================================
    # COPY RATIO RECOMMENDATION ANALYSIS
    # =========================================================================
    
    async def analyze_copy_ratio(
        self,
        account: int,
        period_days: int = 30,
        skip_risk_score: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze an account's trading behavior and recommend optimal copy ratio.
        
        The copy ratio is a real-time risk control mechanism used in Social Trading.
        A ratio of 0.5 means copied trades will be 50% of the source trade size.
        
        This analysis:
        1. Calculates average and max lot size breaches
        2. Compares against FIDUS risk parameters
        3. Recommends optimal copy ratio to stay within limits
        4. Provides actionable recommendations
        
        Args:
            account: MT5 account number
            period_days: Analysis period in days
            skip_risk_score: Skip risk score calculation for faster response
            
        Returns:
            Dictionary with copy ratio analysis and recommendation
        """
        try:
            # Get account info
            account_info = await self.db.mt5_accounts.find_one({"account": account})
            if not account_info:
                return {"error": f"Account {account} not found"}
            
            manager_name = account_info.get("manager_name", f"Account {account}")
            equity = account_info.get("equity", 0) or account_info.get("balance", 0)
            initial_allocation = account_info.get("initial_allocation", equity)
            notes = account_info.get("notes", "")
            account_type = account_info.get("account_type", "real")
            
            # Extract current copy ratio from notes
            current_ratio = 1.0  # Default to 1:1
            import re
            ratio_match = re.search(r'(\d+\.?\d*)\s*ratio|at\s*(\d+\.?\d*)\s*ratio|@\s*(\d+\.?\d*)', notes.lower())
            if ratio_match:
                ratio_str = ratio_match.group(1) or ratio_match.group(2) or ratio_match.group(3)
                try:
                    current_ratio = float(ratio_str)
                except:
                    current_ratio = 1.0
            
            # Get risk policy
            risk_policy = await self.get_risk_policy(account)
            
            # Get deals for analysis
            start_date = datetime.now(timezone.utc) - timedelta(days=period_days)
            deals = await self.get_deals_for_account(account, start_date, max_deals=5000)
            
            if not deals:
                return {
                    "account": account,
                    "manager_name": manager_name,
                    "account_type": account_type,
                    "current_copy_ratio": current_ratio,
                    "recommended_ratio": current_ratio,
                    "ratio_change": 0,
                    "urgency": "INFO",
                    "action": "MAINTAIN",
                    "reasons": ["No trades found in analysis period - cannot calculate recommendation"],
                    "lot_analysis": None,
                    "valid_ratios": VALID_COPY_RATIOS
                }
            
            # Analyze lot sizes vs FIDUS limits
            lot_breaches = []
            total_lots = 0
            max_breach_pct = 0
            
            for deal in deals:
                symbol = deal.get("symbol", "")
                if not symbol:
                    continue
                
                volume = deal.get("volume", 0)
                if volume <= 0:
                    continue
                
                total_lots += volume
                
                # Get instrument specs to calculate max allowed
                specs = await self.get_instrument_specs(symbol)
                
                # Calculate max allowed lots based on risk policy
                max_lots_calc = self.calculate_max_lots(
                    equity if equity > 0 else initial_allocation,
                    specs,
                    risk_policy,
                    specs.get("default_stop_distance", 10)
                )
                
                max_allowed = max_lots_calc.get("max_lots", 1.0)
                
                if volume > max_allowed and max_allowed > 0:
                    breach_pct = ((volume - max_allowed) / max_allowed) * 100
                    lot_breaches.append({
                        "symbol": symbol,
                        "volume": volume,
                        "max_allowed": max_allowed,
                        "breach_pct": breach_pct,
                        "time": deal.get("time")
                    })
                    max_breach_pct = max(max_breach_pct, breach_pct)
            
            # Calculate averages
            avg_breach_pct = 0
            if lot_breaches:
                avg_breach_pct = sum(b["breach_pct"] for b in lot_breaches) / len(lot_breaches)
            
            # Calculate risk control score (optional - skip for bulk operations)
            composite_score = 70  # Default
            if not skip_risk_score:
                risk_score = await self.calculate_risk_control_score(account, period_days)
                composite_score = risk_score.get("composite_score", 70)
            
            # Get copy ratio recommendation
            recommendation = get_recommended_copy_ratio(
                current_ratio,
                avg_breach_pct,
                max_breach_pct,
                composite_score
            )
            
            # Build detailed analysis
            lot_analysis = {
                "total_trades_analyzed": len(deals),
                "trades_with_breaches": len(lot_breaches),
                "breach_rate": round(len(lot_breaches) / len(deals) * 100, 1) if deals else 0,
                "average_breach_pct": round(avg_breach_pct, 1),
                "max_breach_pct": round(max_breach_pct, 1),
                "worst_breaches": sorted(lot_breaches, key=lambda x: -x["breach_pct"])[:5]
            }
            
            # Generate recommendations
            actionable_recommendations = []
            
            if recommendation["action"] == "DECREASE":
                actionable_recommendations.append({
                    "priority": "HIGH" if recommendation["urgency"] in ["HIGH", "CRITICAL"] else "MEDIUM",
                    "action": f"Reduce copy ratio from {current_ratio} to {recommendation['recommended_ratio']}",
                    "impact": f"This will reduce trade sizes by {abs(recommendation['ratio_change'])*100:.0f}%",
                    "implementation": f"Update Social Trading copier settings: Set 'Lot Multiplier' to {recommendation['recommended_ratio']}"
                })
            elif recommendation["action"] == "INCREASE":
                actionable_recommendations.append({
                    "priority": "LOW",
                    "action": f"Consider increasing copy ratio from {current_ratio} to {recommendation['recommended_ratio']}",
                    "impact": f"This would increase trade sizes by {abs(recommendation['ratio_change'])*100:.0f}%",
                    "implementation": "Only increase if risk score remains above 80 for next 2 weeks"
                })
            
            # Add symbol-specific recommendations if certain symbols breach more
            symbol_breaches = {}
            for breach in lot_breaches:
                sym = breach["symbol"]
                if sym not in symbol_breaches:
                    symbol_breaches[sym] = {"count": 0, "avg_pct": 0}
                symbol_breaches[sym]["count"] += 1
                symbol_breaches[sym]["avg_pct"] += breach["breach_pct"]
            
            for sym, data in symbol_breaches.items():
                data["avg_pct"] = data["avg_pct"] / data["count"]
                if data["avg_pct"] > 50:
                    actionable_recommendations.append({
                        "priority": "MEDIUM",
                        "action": f"Consider disabling {sym} in copier or setting symbol-specific max lot",
                        "impact": f"{sym} has {data['count']} breaches averaging {data['avg_pct']:.0f}% over limit",
                        "implementation": f"In Social Trading: Use 'Disable Symbols' feature for {sym} or set per-symbol max lot"
                    })
            
            return {
                "account": account,
                "manager_name": manager_name,
                "account_type": account_type,
                "equity": round(equity, 2),
                "initial_allocation": round(initial_allocation, 2),
                "notes": notes,
                "risk_control_score": composite_score,
                
                # Current configuration
                "current_copy_ratio": current_ratio,
                "current_ratio_source": "Extracted from account notes" if ratio_match else "Default (1.0)",
                
                # Recommendation
                "recommended_ratio": recommendation["recommended_ratio"],
                "ratio_change": recommendation["ratio_change"],
                "urgency": recommendation["urgency"],
                "action": recommendation["action"],
                "reasons": recommendation["reasons"],
                
                # Analysis details
                "lot_analysis": lot_analysis,
                "actionable_recommendations": actionable_recommendations,
                
                # Reference
                "valid_ratios": VALID_COPY_RATIOS,
                "period_days": period_days,
                "analysis_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing copy ratio for account {account}: {e}")
            return {"error": str(e), "account": account}

