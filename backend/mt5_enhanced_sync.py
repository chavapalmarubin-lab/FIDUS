"""
Enhanced MT5 Sync Service with Transfer Classification
Critical Fix: Tracks profit withdrawals for accurate P&L calculation

This module:
1. Retrieves MT5 deal history
2. Classifies transfers (profit vs capital movements)
3. Calculates true P&L including profit withdrawals
4. Stores enriched data in MongoDB

Author: Emergent AI
Priority: CRITICAL
"""

import MetaTrader5 as mt5
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
import logging
import os
from motor.motor_asyncio import AsyncIOMotorClient
from mt5_transfer_classifier import (
    categorize_deal_history,
    calculate_true_pnl,
    SEPARATION_ACCOUNT,
    TRADING_ACCOUNTS
)

logger = logging.getLogger(__name__)

# MT5 Configuration
MT5_PATH = "C:\\Program Files\\MEX Atlantic MT5 Terminal\\terminal64.exe"

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client.fidus_production


class EnhancedMT5Sync:
    """Enhanced MT5 sync with transfer classification"""
    
    def __init__(self):
        self.accounts = [
            {
                'login': 886557,
                'password': 'FIDUS13@',
                'server': 'MEXAtlantic-MT5',
                'name': 'BALANCE 1',
                'type': 'trading'
            },
            {
                'login': 886066,
                'password': 'FIDUS13@',
                'server': 'MEXAtlantic-MT5',
                'name': 'BALANCE 2',
                'type': 'trading'
            },
            {
                'login': 886602,
                'password': 'FIDUS13@',
                'server': 'MEXAtlantic-MT5',
                'name': 'BALANCE 3',
                'type': 'trading'
            },
            {
                'login': 885822,
                'password': 'FIDUS13@',
                'server': 'MEXAtlantic-MT5',
                'name': 'CORE',
                'type': 'trading'
            },
            {
                'login': 886528,
                'password': 'FIDUS13@',
                'server': 'MEXAtlantic-MT5',
                'name': 'SEPARATION',
                'type': 'separation'
            }
        ]
    
    def get_deal_history(self, account_config: Dict[str, Any], days: int = 90) -> Optional[List[Dict[str, Any]]]:
        """
        Get MT5 deal history for an account
        
        Args:
            account_config: Account configuration dict
            days: Number of days of history to retrieve
        
        Returns:
            List of deal dicts or None if error
        """
        
        try:
            # Initialize MT5
            if not mt5.initialize(path=MT5_PATH):
                logger.error(f"MT5 initialization failed for {account_config['login']}")
                return None
            
            # Login to account
            if not mt5.login(
                account_config['login'],
                password=account_config['password'],
                server=account_config['server']
            ):
                logger.error(f"MT5 login failed for {account_config['login']}")
                mt5.shutdown()
                return None
            
            # Get deal history
            start_date = datetime.now() - timedelta(days=days)
            end_date = datetime.now()
            
            deals = mt5.history_deals_get(start_date, end_date)
            
            if deals is None:
                logger.warning(f"No deal history for account {account_config['login']}")
                mt5.shutdown()
                return []
            
            # Convert to dict list
            deal_list = []
            for deal in deals:
                # Only process balance operations (type 2)
                if deal.type == 2:  # DEAL_TYPE_BALANCE
                    deal_list.append({
                        'ticket': deal.ticket,
                        'time': datetime.fromtimestamp(deal.time),
                        'amount': deal.profit,  # Negative for withdrawals
                        'comment': deal.comment,
                        'type': 'balance_operation'
                    })
            
            mt5.shutdown()
            return deal_list
            
        except Exception as e:
            logger.error(f"Error getting deal history for {account_config['login']}: {str(e)}")
            try:
                mt5.shutdown()
            except:
                pass
            return None
    
    def get_account_info(self, account_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get current MT5 account info
        
        Args:
            account_config: Account configuration dict
        
        Returns:
            Dict with account info or None if error
        """
        
        try:
            # Initialize MT5
            if not mt5.initialize(path=MT5_PATH):
                logger.error(f"MT5 initialization failed for {account_config['login']}")
                return None
            
            # Login to account
            if not mt5.login(
                account_config['login'],
                password=account_config['password'],
                server=account_config['server']
            ):
                logger.error(f"MT5 login failed for {account_config['login']}")
                mt5.shutdown()
                return None
            
            # Get account info
            account_info = mt5.account_info()
            
            if account_info is None:
                logger.error(f"Failed to get account info for {account_config['login']}")
                mt5.shutdown()
                return None
            
            result = {
                'balance': account_info.balance,
                'equity': account_info.equity,
                'profit': account_info.profit,
                'margin': account_info.margin,
                'free_margin': account_info.margin_free,
                'margin_level': account_info.margin_level if account_info.margin > 0 else 0,
                'currency': account_info.currency
            }
            
            mt5.shutdown()
            return result
            
        except Exception as e:
            logger.error(f"Error getting account info for {account_config['login']}: {str(e)}")
            try:
                mt5.shutdown()
            except:
                pass
            return None
    
    async def sync_account_enhanced(self, account_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Sync single account with enhanced transfer classification
        
        Args:
            account_config: Account configuration dict
        
        Returns:
            Dict with sync results or None if error
        """
        
        logger.info(f"📊 Syncing account {account_config['name']} ({account_config['login']})...")
        
        try:
            # Get current account state
            account_info = self.get_account_info(account_config)
            if not account_info:
                logger.error(f"❌ Failed to get account info for {account_config['login']}")
                return None
            
            # Get deal history
            deals = self.get_deal_history(account_config, days=90)
            if deals is None:
                logger.error(f"❌ Failed to get deal history for {account_config['login']}")
                return None
            
            # Categorize deal history
            categorized = categorize_deal_history(deals)
            
            # Calculate true P&L
            pnl_data = calculate_true_pnl(account_info['profit'], categorized)
            
            # Prepare MongoDB document
            mongo_doc = {
                'account_number': account_config['login'],
                'account_name': account_config['name'],
                'account_type': account_config['type'],
                
                # Current state
                'balance': account_info['balance'],
                'equity': account_info['equity'],
                'margin': account_info['margin'],
                'free_margin': account_info['free_margin'],
                'margin_level': account_info['margin_level'],
                'currency': account_info['currency'],
                
                # P&L breakdown
                'displayed_pnl': pnl_data['displayed_pnl'],
                'profit_withdrawals': pnl_data['profit_withdrawals'],
                'profit_returns': pnl_data['profit_returns'],
                'net_profit_withdrawals': pnl_data['net_profit_withdrawals'],
                'true_pnl': pnl_data['true_pnl'],
                
                # Transfer breakdown
                'inter_account_transfers': pnl_data['inter_account_transfers'],
                'external_operations': categorized['totals']['external'],
                
                # Deal history (categorized)
                'deal_history': {
                    'profit_withdrawals': [
                        {
                            'time': d['time'].isoformat(),
                            'amount': abs(d['amount']),
                            'destination': d['classification'].get('destination'),
                            'comment': d['comment'],
                            'ticket': d['ticket']
                        }
                        for d in categorized['profit_withdrawals']
                    ],
                    'inter_account_transfers': [
                        {
                            'time': d['time'].isoformat(),
                            'amount': abs(d['amount']),
                            'destination': d['classification'].get('destination'),
                            'source': d['classification'].get('source'),
                            'comment': d['comment'],
                            'ticket': d['ticket']
                        }
                        for d in categorized['inter_account_transfers']
                    ],
                    'totals': categorized['totals'],
                    'counts': categorized['counts']
                },
                
                # Flags
                'has_profit_withdrawals': pnl_data['has_withdrawals'],
                'has_inter_account_transfers': pnl_data['has_inter_account'],
                'needs_manual_review': categorized['needs_review'],
                
                # Metadata
                'last_sync': datetime.now(timezone.utc),
                'sync_status': 'success'
            }
            
            # Store in MongoDB
            await db.mt5_accounts.update_one(
                {'account_number': account_config['login']},
                {'$set': mongo_doc},
                upsert=True
            )
            
            logger.info(f"✅ {account_config['name']}: True P&L = ${pnl_data['true_pnl']:.2f} "
                       f"(Displayed: ${pnl_data['displayed_pnl']:.2f} + "
                       f"Withdrawals: ${pnl_data['net_profit_withdrawals']:.2f})")
            
            return pnl_data
            
        except Exception as e:
            logger.error(f"❌ Error syncing account {account_config['login']}: {str(e)}")
            return None
    
    async def sync_all_accounts(self) -> Dict[str, Any]:
        """
        Sync all 5 accounts (4 trading + 1 separation)
        
        Returns:
            Dict with sync results for all accounts
        """
        
        logger.info("=" * 80)
        logger.info("🚀 STARTING ENHANCED MT5 SYNC WITH TRANSFER CLASSIFICATION")
        logger.info("=" * 80)
        
        results = {}
        success_count = 0
        
        for account in self.accounts:
            result = await self.sync_account_enhanced(account)
            results[account['login']] = result
            if result:
                success_count += 1
        
        logger.info("=" * 80)
        logger.info(f"✅ Sync complete: {success_count}/{len(self.accounts)} accounts synced successfully")
        logger.info("=" * 80)
        
        return results
    
    async def get_unified_fund_performance(self) -> Dict[str, Any]:
        """
        Get unified fund performance from MongoDB (single source of truth)
        
        Returns:
            Dict with complete fund performance data
        """
        
        # Get all trading accounts
        trading_accounts = await db.mt5_accounts.find({
            'account_number': {'$in': TRADING_ACCOUNTS}
        }).to_list(length=None)
        
        # Get separation account
        separation_account = await db.mt5_accounts.find_one({
            'account_number': SEPARATION_ACCOUNT
        })
        
        # Calculate fund assets
        mt5_trading_pnl = sum(acc.get('true_pnl', 0) for acc in trading_accounts)
        separation_balance = separation_account.get('balance', 0) if separation_account else 0
        broker_rebates = 0  # Placeholder
        
        total_fund_assets = mt5_trading_pnl + separation_balance + broker_rebates
        
        # Verification: Sum of profit withdrawals should ≈ separation balance
        total_profit_withdrawals = sum(
            acc.get('net_profit_withdrawals', 0) for acc in trading_accounts
        )
        
        difference = abs(total_profit_withdrawals - separation_balance)
        withdrawal_match = difference < 100  # Allow $100 difference for broker interest
        
        return {
            'fund_assets': {
                'mt5_trading_pnl': round(mt5_trading_pnl, 2),
                'separation_interest': round(separation_balance, 2),
                'broker_rebates': round(broker_rebates, 2),
                'total': round(total_fund_assets, 2)
            },
            
            'account_breakdown': [
                {
                    'account': acc['account_number'],
                    'name': acc['account_name'],
                    'displayed_pnl': round(acc.get('displayed_pnl', 0), 2),
                    'profit_withdrawals': round(acc.get('net_profit_withdrawals', 0), 2),
                    'true_pnl': round(acc.get('true_pnl', 0), 2),
                    'inter_account_transfers': round(acc.get('inter_account_transfers', 0), 2)
                }
                for acc in trading_accounts
            ],
            
            'verification': {
                'total_profit_withdrawals': round(total_profit_withdrawals, 2),
                'separation_account_balance': round(separation_balance, 2),
                'difference': round(difference, 2),
                'match': withdrawal_match,
                'status': 'VERIFIED ✅' if withdrawal_match else 'MISMATCH ⚠️',
                'note': 'Small difference acceptable due to broker interest on separation account'
            },
            
            'data_source': 'mt5_mongodb_unified',
            'last_updated': datetime.now(timezone.utc).isoformat()
        }


# Quick test/sync script
async def run_enhanced_sync():
    """Run enhanced sync for all accounts"""
    sync_service = EnhancedMT5Sync()
    results = await sync_service.sync_all_accounts()
    
    # Get unified performance
    performance = await sync_service.get_unified_fund_performance()
    
    print("\n" + "=" * 80)
    print("📊 UNIFIED FUND PERFORMANCE")
    print("=" * 80)
    print(f"MT5 Trading P&L: ${performance['fund_assets']['mt5_trading_pnl']:.2f}")
    print(f"Separation Interest: ${performance['fund_assets']['separation_interest']:.2f}")
    print(f"Total Fund Assets: ${performance['fund_assets']['total']:.2f}")
    print("\n" + "=" * 80)
    print("✅ VERIFICATION")
    print("=" * 80)
    print(f"Status: {performance['verification']['status']}")
    print(f"Profit Withdrawals: ${performance['verification']['total_profit_withdrawals']:.2f}")
    print(f"Separation Balance: ${performance['verification']['separation_account_balance']:.2f}")
    print(f"Difference: ${performance['verification']['difference']:.2f}")
    print("=" * 80)


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_enhanced_sync())
