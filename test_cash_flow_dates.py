#!/usr/bin/env python3

import os
import sys
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

# Import the cash flow function (simulated)
def add_days(date_obj, days):
    return date_obj + timedelta(days=days)

def calculate_first_payment(investment_date, product):
    days_map = {
        'FIDUS_CORE': 90,      # 60 incubation + 30 days
        'FIDUS_BALANCE': 150,   # 60 incubation + 90 days  
        'FIDUS_DYNAMIC': 240    # 60 incubation + 180 days
    }
    return add_days(investment_date, days_map.get(product, 90))

def calculate_contract_end(investment_date):
    return add_days(investment_date, 426)

def get_payment_interval(product):
    return {
        'FIDUS_CORE': 30,      # Monthly
        'FIDUS_BALANCE': 90,    # Quarterly
        'FIDUS_DYNAMIC': 180    # Semi-annual
    }.get(product, 30)

def get_number_of_payments(product):
    return {
        'FIDUS_CORE': 12,      # 12 monthly payments
        'FIDUS_BALANCE': 4,     # 4 quarterly payments
        'FIDUS_DYNAMIC': 2      # 2 semi-annual payments
    }.get(product, 12)

def get_months_per_period(product):
    return {
        'FIDUS_CORE': 1,       # 1 month
        'FIDUS_BALANCE': 3,     # 3 months
        'FIDUS_DYNAMIC': 6      # 6 months
    }.get(product, 1)

async def test_alejandro_schedule():
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'fidus_production')]
    
    try:
        investments = await db.investments.find({'client_id': 'client_alejandro'}).to_list(length=None)
        
        for inv in investments:
            print(f'\n=== {inv["fund_code"]} FUND SCHEDULE ===')
            print(f'Investment Date: {inv["created_at"]}')
            print(f'Amount: ${inv["principal_amount"]:,.2f}')
            
            investment_date = inv['created_at']
            if hasattr(investment_date, 'replace'):
                investment_date = investment_date.replace(tzinfo=None)
            
            fund_code = inv['fund_code']
            product = f'FIDUS_{fund_code}'
            
            # Calculate key dates
            incubation_end = add_days(investment_date, 60)
            first_payment = calculate_first_payment(investment_date, product)
            contract_end = calculate_contract_end(investment_date)
            
            print(f'Incubation End: {incubation_end} (Day 60)')
            print(f'First Payment: {first_payment} (Day {(first_payment - investment_date).days})')
            print(f'Contract End: {contract_end} (Day 426)')
            
            # Generate payment schedule
            monthly_rates = {
                'FIDUS_CORE': 0.015,
                'FIDUS_BALANCE': 0.025,
                'FIDUS_DYNAMIC': 0.035
            }
            monthly_rate = monthly_rates.get(product, 0.015)
            
            interval = get_payment_interval(product)
            number_of_payments = get_number_of_payments(product)
            months_per_period = get_months_per_period(product)
            interest_per_payment = inv['principal_amount'] * monthly_rate * months_per_period
            
            print(f'\nPayment Details:')
            print(f'  Interest Rate: {monthly_rate*100}% per month')
            print(f'  Payment Frequency: Every {interval} days')
            print(f'  Interest per Payment: ${interest_per_payment:,.2f}')
            print(f'  Number of Payments: {number_of_payments} + 1 final')
            
            print(f'\nPayment Schedule:')
            current_date = first_payment
            
            for i in range(1, number_of_payments + 1):
                days_from_investment = (current_date - investment_date).days
                print(f'  Payment {i}: {current_date.strftime("%B %d, %Y")} (Day {days_from_investment}) -> ${interest_per_payment:,.2f}')
                current_date = add_days(current_date, interval)
            
            # Final payment
            final_amount = inv['principal_amount'] + interest_per_payment
            print(f'  Payment {number_of_payments + 1}: {contract_end.strftime("%B %d, %Y")} (Day 426) -> ${final_amount:,.2f} (FINAL)')
            
    except Exception as e:
        print(f'Error: {e}')
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_alejandro_schedule())