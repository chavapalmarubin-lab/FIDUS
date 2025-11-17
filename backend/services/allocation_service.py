"""
Investment Committee Allocation Service
Handles all business logic for fund allocations, manager assignments, and capital management
"""
from typing import List, Dict, Optional
from datetime import datetime
from bson import ObjectId


class AllocationService:
    """Service for managing fund allocations and manager assignments"""
    
    def __init__(self, db):
        self.db = db
        self.fund_allocation_state = db.fund_allocation_state
        self.allocation_history = db.allocation_history
        self.mt5_accounts = db.mt5_accounts
        self.money_managers = db.money_managers
    
    async def get_fund_state(self, fund_type: str) -> Optional[Dict]:
        """Get current allocation state for a fund"""
        
        state = await self.fund_allocation_state.find_one({
            "fund_type": fund_type
        }, {"_id": 0})
        
        return state
    
    async def initialize_fund(self, fund_type: str) -> Dict:
        """Initialize a new fund with zero allocations"""
        
        new_state = {
            "fund_type": fund_type,
            "total_capital": 0.00,
            "allocated_capital": 0.00,
            "unallocated_capital": 0.00,
            "cash_reserves": 0.00,
            "manager_allocations": [],
            "last_updated": datetime.utcnow(),
            "updated_by": "system",
            "status": "active"
        }
        
        await self.fund_allocation_state.insert_one(new_state)
        return new_state
    
    async def preview_allocation(
        self,
        fund_type: str,
        manager_name: str,
        new_allocation: float,
        account_distribution: List[Dict]
    ) -> Dict:
        """Preview allocation change without applying"""
        
        # Get current state
        state = await self.get_fund_state(fund_type)
        if not state:
            return {
                "is_valid": False,
                "errors": ["Fund not initialized"]
            }
        
        # Validation
        errors = []
        warnings = []
        
        # Check if amount is positive
        if new_allocation <= 0:
            errors.append("Allocation amount must be greater than 0")
        
        # Check if enough unallocated capital
        current_manager_allocation = 0
        for alloc in state["manager_allocations"]:
            if alloc["manager_name"] == manager_name:
                current_manager_allocation = alloc["allocated_amount"]
                break
        
        required_capital = new_allocation - current_manager_allocation
        if required_capital > state["unallocated_capital"]:
            errors.append(
                f"Insufficient unallocated capital. "
                f"Available: ${state['unallocated_capital']:,.2f}, "
                f"Required: ${required_capital:,.2f}"
            )
        
        # Check account distribution
        if account_distribution:
            dist_total = sum(d["amount"] for d in account_distribution)
            if abs(dist_total - new_allocation) > 0.01:
                errors.append(
                    f"Account distribution (${dist_total:,.2f}) "
                    f"must equal allocation amount (${new_allocation:,.2f})"
                )
        
        # Calculate impact
        impact = {
            "unallocated_before": state["unallocated_capital"],
            "unallocated_after": state["unallocated_capital"] - required_capital,
            "manager_allocation_before": current_manager_allocation,
            "manager_allocation_after": new_allocation,
            "total_capital_change": 0.00
        }
        
        return {
            "is_valid": len(errors) == 0,
            "impact": impact,
            "warnings": warnings,
            "errors": errors
        }
    
    async def apply_allocation(
        self,
        fund_type: str,
        manager_name: str,
        amount: float,
        account_distribution: List[Dict],
        notes: str,
        user_id: str
    ) -> Dict:
        """Apply allocation to a manager"""
        
        # Preview first to validate
        preview = await self.preview_allocation(
            fund_type, manager_name, amount, account_distribution
        )
        
        if not preview["is_valid"]:
            raise ValueError(f"Invalid allocation: {', '.join(preview['errors'])}")
        
        # Get current state
        state = await self.get_fund_state(fund_type)
        
        # Check if manager already has allocation
        manager_exists = False
        old_amount = 0
        
        for i, alloc in enumerate(state["manager_allocations"]):
            if alloc["manager_name"] == manager_name:
                manager_exists = True
                # Update existing allocation
                old_amount = alloc["allocated_amount"]
                state["manager_allocations"][i]["allocated_amount"] = amount
                state["manager_allocations"][i]["accounts"] = account_distribution
                state["manager_allocations"][i]["allocation_percentage"] = (amount / state["total_capital"]) * 100 if state["total_capital"] > 0 else 0
                break
        
        if not manager_exists:
            # Add new manager allocation
            state["manager_allocations"].append({
                "manager_name": manager_name,
                "allocated_amount": amount,
                "allocation_percentage": (amount / state["total_capital"]) * 100 if state["total_capital"] > 0 else 0,
                "accounts": account_distribution
            })
        
        # Update totals
        required_capital = amount - old_amount
        state["allocated_capital"] += required_capital
        state["unallocated_capital"] -= required_capital
        state["last_updated"] = datetime.utcnow()
        state["updated_by"] = user_id
        
        # Save to database
        await self.fund_allocation_state.update_one(
            {"fund_type": fund_type},
            {"$set": state}
        )
        
        # Update MT5 accounts
        for account_dist in account_distribution:
            await self.mt5_accounts.update_one(
                {"account": account_dist["account_number"]},
                {"$set": {
                    "allocated_capital": account_dist["amount"],
                    "manager_assigned": manager_name,
                    "fund_type": fund_type,
                    "allocation_type": account_dist.get("type", "master"),
                    "last_allocation_update": datetime.utcnow()
                }}
            )
        
        # Update money_managers
        await self.money_managers.update_one(
            {"name": manager_name},
            {"$set": {
                "current_allocation": {
                    "fund_type": fund_type,
                    "allocated_amount": amount,
                    "accounts": account_distribution,
                    "last_updated": datetime.utcnow()
                }
            }}
        )
        
        # Create history record
        await self._create_history_record(
            fund_type=fund_type,
            action_type="manager_added" if old_amount == 0 else ("allocation_increased" if amount > old_amount else "allocation_decreased"),
            affected_manager=manager_name,
            before_state={
                "total_capital": state["total_capital"],
                "allocated_capital": state["allocated_capital"] - required_capital,
                "unallocated_capital": state["unallocated_capital"] + required_capital,
                "manager_allocation": old_amount
            },
            after_state={
                "total_capital": state["total_capital"],
                "allocated_capital": state["allocated_capital"],
                "unallocated_capital": state["unallocated_capital"],
                "manager_allocation": amount
            },
            financial_impact={
                "capital_change": 0,
                "loss_amount": 0,
                "gain_amount": 0,
                "allocation_change": amount - old_amount
            },
            notes=notes,
            user_id=user_id
        )
        
        return state
    
    async def remove_manager(
        self,
        fund_type: str,
        manager_name: str,
        actual_balance: float,
        expected_allocation: float,
        loss_handling: str,
        notes: str,
        user_id: str
    ) -> Dict:
        """Remove manager and return capital to pool"""
        
        # Calculate loss/gain
        loss = expected_allocation - actual_balance
        
        # Get current state
        state = await self.get_fund_state(fund_type)
        
        # Find and remove manager allocation
        manager_allocation = None
        for i, alloc in enumerate(state["manager_allocations"]):
            if alloc["manager_name"] == manager_name:
                manager_allocation = alloc
                del state["manager_allocations"][i]
                break
        
        if not manager_allocation:
            raise ValueError(f"Manager {manager_name} not found in allocations")
        
        # Handle loss based on strategy
        if loss_handling == "absorb_loss":
            # Reduce total capital
            state["total_capital"] -= loss
            state["unallocated_capital"] += actual_balance
        elif loss_handling == "cover_from_reserves":
            # Keep total capital, use reserves
            state["cash_reserves"] -= loss
            state["unallocated_capital"] += actual_balance
        elif loss_handling == "mark_receivable":
            # Track separately (future enhancement)
            state["unallocated_capital"] += actual_balance
        
        # Update totals
        state["allocated_capital"] -= expected_allocation
        state["last_updated"] = datetime.utcnow()
        state["updated_by"] = user_id
        
        # Save to database
        await self.fund_allocation_state.update_one(
            {"fund_type": fund_type},
            {"$set": state}
        )
        
        # Update MT5 accounts
        for account in manager_allocation["accounts"]:
            await self.mt5_accounts.update_one(
                {"account": account["account_number"]},
                {"$set": {
                    "allocated_capital": 0,
                    "manager_assigned": None,
                    "last_allocation_update": datetime.utcnow()
                }}
            )
        
        # Update money_managers (keep active if just reallocating)
        await self.money_managers.update_one(
            {"name": manager_name},
            {"$set": {
                "current_allocation": None
            }}
        )
        
        # Create history record
        await self._create_history_record(
            fund_type=fund_type,
            action_type="manager_removed",
            affected_manager=manager_name,
            affected_accounts=[acc["account_number"] for acc in manager_allocation["accounts"]],
            before_state={
                "total_capital": state["total_capital"] + loss if loss_handling == "absorb_loss" else state["total_capital"],
                "allocated_capital": state["allocated_capital"] + expected_allocation,
                "unallocated_capital": state["unallocated_capital"] - actual_balance,
                "manager_allocation": expected_allocation
            },
            after_state={
                "total_capital": state["total_capital"],
                "allocated_capital": state["allocated_capital"],
                "unallocated_capital": state["unallocated_capital"],
                "manager_allocation": 0
            },
            financial_impact={
                "capital_change": -loss if loss_handling == "absorb_loss" else 0,
                "loss_amount": loss if loss > 0 else 0,
                "gain_amount": abs(loss) if loss < 0 else 0,
                "allocation_change": -expected_allocation
            },
            notes=notes,
            user_id=user_id
        )
        
        return {
            "fund_type": fund_type,
            "total_capital_before": state["total_capital"] + loss if loss_handling == "absorb_loss" else state["total_capital"],
            "total_capital_after": state["total_capital"],
            "capital_change": -loss if loss_handling == "absorb_loss" else 0,
            "unallocated_before": state["unallocated_capital"] - actual_balance,
            "unallocated_after": state["unallocated_capital"],
            "loss_amount": loss if loss > 0 else 0,
            "manager_removed": manager_name
        }
    
    async def adjust_fund_capital(
        self,
        fund_type: str,
        new_total_capital: float,
        reason: str,
        notes: str,
        user_id: str
    ) -> Dict:
        """Adjust total fund capital"""
        
        state = await self.get_fund_state(fund_type)
        if not state:
            raise ValueError(f"Fund {fund_type} not found")
        
        # Validate new total >= allocated
        if new_total_capital < state["allocated_capital"]:
            raise ValueError(
                f"New total capital (${new_total_capital:,.2f}) cannot be less than "
                f"allocated capital (${state['allocated_capital']:,.2f})"
            )
        
        old_total = state["total_capital"]
        capital_change = new_total_capital - old_total
        
        # Update state
        state["total_capital"] = new_total_capital
        state["unallocated_capital"] += capital_change
        state["last_updated"] = datetime.utcnow()
        state["updated_by"] = user_id
        
        # Save
        await self.fund_allocation_state.update_one(
            {"fund_type": fund_type},
            {"$set": state}
        )
        
        # Create history
        await self._create_history_record(
            fund_type=fund_type,
            action_type=reason,
            affected_manager="N/A",
            before_state={
                "total_capital": old_total,
                "allocated_capital": state["allocated_capital"],
                "unallocated_capital": state["unallocated_capital"] - capital_change,
                "manager_allocation": 0
            },
            after_state={
                "total_capital": new_total_capital,
                "allocated_capital": state["allocated_capital"],
                "unallocated_capital": state["unallocated_capital"],
                "manager_allocation": 0
            },
            financial_impact={
                "capital_change": capital_change,
                "loss_amount": 0,
                "gain_amount": 0,
                "allocation_change": 0
            },
            notes=notes,
            user_id=user_id
        )
        
        return {
            "fund_type": fund_type,
            "total_capital_before": old_total,
            "total_capital_after": new_total_capital,
            "capital_change": capital_change,
            "unallocated_before": state["unallocated_capital"] - capital_change,
            "unallocated_after": state["unallocated_capital"]
        }
    
    async def _create_history_record(
        self,
        fund_type: str,
        action_type: str,
        affected_manager: str,
        before_state: Dict,
        after_state: Dict,
        financial_impact: Dict,
        notes: str,
        user_id: str,
        affected_accounts: List[int] = None
    ):
        """Create history record"""
        
        record = {
            "timestamp": datetime.utcnow(),
            "fund_type": fund_type,
            "action_type": action_type,
            "performed_by": user_id,
            "affected_manager": affected_manager,
            "affected_accounts": affected_accounts or [],
            "before_state": before_state,
            "after_state": after_state,
            "financial_impact": financial_impact,
            "notes": notes
        }
        
        await self.allocation_history.insert_one(record)
    
    async def get_history(
        self,
        fund_type: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        manager_name: Optional[str] = None,
        action_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get allocation history"""
        
        query = {"fund_type": fund_type}
        
        if start_date:
            query["timestamp"] = {"$gte": datetime.fromisoformat(start_date)}
        if end_date:
            if "timestamp" in query:
                query["timestamp"]["$lte"] = datetime.fromisoformat(end_date)
            else:
                query["timestamp"] = {"$lte": datetime.fromisoformat(end_date)}
        
        if manager_name:
            query["affected_manager"] = manager_name
        
        if action_type:
            query["action_type"] = action_type
        
        cursor = self.allocation_history.find(query, {"_id": 0}).sort("timestamp", -1).limit(limit)
        history = await cursor.to_list(length=limit)
        
        return history
    
    async def get_available_managers(self, fund_type: Optional[str] = None) -> List[Dict]:
        """Get managers available for allocation"""
        
        # Get all active and pending managers
        query = {"status": {"$in": ["active", "pending_activation"]}}
        
        managers = await self.money_managers.find(query, {"_id": 0}).to_list(None)
        
        # Add account availability info
        for manager in managers:
            accounts = manager.get("assigned_accounts", [])
            manager["accounts"] = []
            
            for account_num in accounts:
                account = await self.mt5_accounts.find_one({"account": account_num}, {"_id": 0})
                if account:
                    manager["accounts"].append({
                        "account_number": account_num,
                        "type": account.get("allocation_type", "master"),
                        "broker": account.get("broker", "Unknown"),
                        "is_available": account.get("manager_assigned") is None or account.get("manager_assigned") == manager["name"]
                    })
        
        return managers
    
    async def get_manager_actual_balance(self, manager_name: str) -> float:
        """Get actual balance from MT5 accounts for a manager"""
        
        # Get manager's accounts
        manager = await self.money_managers.find_one({"name": manager_name})
        if not manager:
            return 0.0
        
        accounts = manager.get("assigned_accounts", [])
        total_balance = 0.0
        
        for account_num in accounts:
            account = await self.mt5_accounts.find_one({"account": account_num})
            if account:
                total_balance += account.get("equity", 0.0)
        
        return total_balance
