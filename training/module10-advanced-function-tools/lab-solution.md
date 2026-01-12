---
sidebar_position: 3
title: "Lab Solution"
---

# Lab 10 Solution: Building a Personal Finance Assistant

## Goal

This file contains the complete code for the `agent.py` script in the Personal Finance Assistant lab.

### `finance_assistant/agent.py`

```python
from __future__ import annotations
from google.adk.agents import Agent

# Tool 1: Calculate compound interest
def calculate_compound_interest(
    principal: float,
    annual_rate: float,
    years: int,
    compounds_per_year: int = 1
) -> dict:
    """
    Calculate compound interest for savings or investments.

    This function computes how much an initial investment will grow to
    over time with compound interest. It uses the standard compound interest
    formula: A = P(1 + r/n)^(nt)

    Args:
        principal: Initial investment amount (e.g., 10000 for $10,000)
        annual_rate: Annual interest rate as decimal (e.g., 0.06 for 6%)
        years: Number of years to compound
        compounds_per_year: How often interest compounds per year (default: 1 for annual)

    Returns:
        Dict with calculation results and formatted report
    """
    try:
        # Validate inputs
        if principal <= 0:
            return {
                'status': 'error',
                'report': 'Error: Investment principal must be greater than zero.'
            }
        if annual_rate < 0 or annual_rate > 1:
            return {
                'status': 'error',
                'report': 'Error: Annual interest rate must be between 0 and 1 (e.g., 0.06 for 6%).'
            }
        if years <= 0:
            return {
                'status': 'error',
                'report': 'Error: Investment period must be positive.'
            }

        # Calculate compound interest
        rate_per_period = annual_rate / compounds_per_year
        total_periods = years * compounds_per_year
        final_amount = principal * (1 + rate_per_period) ** total_periods
        interest_earned = final_amount - principal

        # Format human-readable report
        report = (
            f"After {years} years at {annual_rate*100:.1f}% annual interest "
            f"(compounded {compounds_per_year} times per year), "
            f"your ${principal:,.0f} investment will grow to "
            f"${final_amount:,.2f}. That's ${interest_earned:,.2f} in interest!"
        )
        return {
            'status': 'success',
            'report': report
        }
    except Exception as e:
        return {
            'status': 'error',
            'report': f'Error calculating compound interest: {str(e)}'
        }

# Tool 2: Calculate loan payments
def calculate_loan_payment(
    loan_amount: float,
    annual_rate: float,
    years: int
) -> dict:
    """Calculate monthly loan payments using the standard amortization formula.

    Args:
        loan_amount: Total loan amount (e.g., 300000 for $300,000)
        annual_rate: Annual interest rate as decimal (e.g., 0.045 for 4.5%)
        years: Loan term in years

    Returns:
        Dict with payment calculation results and formatted report
    """
    try:
        # Validate inputs
        if loan_amount <= 0:
            return {'status': 'error', 'report': 'Error: Loan amount must be positive.'}
        if annual_rate < 0 or annual_rate > 1:
            return {'status': 'error', 'report': 'Error: Annual interest rate must be between 0 and 1.'}
        if years <= 0:
            return {'status': 'error', 'report': 'Error: Loan term must be positive.'}

        # Convert to monthly calculations
        monthly_rate = annual_rate / 12
        total_months = years * 12

        if monthly_rate == 0:
            monthly_payment = loan_amount / total_months
        else:
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** total_months) / ((1 + monthly_rate) ** total_months - 1)

        total_paid = monthly_payment * total_months
        total_interest = total_paid - loan_amount

        report = (
            f"For a ${loan_amount:,.0f} loan at {annual_rate*100:.1f}% interest "
            f"over {years} years, your monthly payment will be "
            f"${monthly_payment:,.2f}. Over the life of the loan, you'll pay "
            f"${total_paid:,.2f} total, with ${total_interest:,.2f} being interest."
        )
        return {
            'status': 'success',
            'report': report
        }
    except Exception as e:
        return {'status': 'error', 'report': f'Error calculating loan payment: {str(e)}'}

# Tool 3: Calculate savings needed
def calculate_monthly_savings(
    target_amount: float,
    years: int,
    annual_return: float = 0.05
) -> dict:
    """Calculate monthly savings needed to reach a financial goal.

    Args:
        target_amount: Target savings amount (e.g., 50000 for $50,000)
        years: Number of years to save
        annual_return: Expected annual return as decimal (default: 0.05 for 5%)

    Returns:
        Dict with savings calculation results and formatted report
    """
    try:
        # Validate inputs
        if target_amount <= 0:
            return {'status': 'error', 'report': 'Error: Savings target must be positive.'}
        if years <= 0:
            return {'status': 'error', 'report': 'Error: Savings period must be positive.'}
        if annual_return < 0:
            return {'status': 'error', 'report': 'Error: Annual return rate cannot be negative.'}

        monthly_return = annual_return / 12
        total_months = years * 12

        if monthly_return == 0:
            monthly_savings = target_amount / total_months
        else:
            monthly_savings = target_amount * (monthly_return / ((1 + monthly_return) ** total_months - 1))

        total_contributed = monthly_savings * total_months
        report = (
            f"To reach ${target_amount:,.0f} in {years} years with a "
            f"{annual_return*100:.1f}% annual return, you need to save "
            f"${monthly_savings:,.2f} per month."
        )
        return {
            'status': 'success',
            'report': report
        }
    except Exception as e:
        return {'status': 'error', 'report': f'Error calculating monthly savings: {str(e)}'}

# Define the agent with all tools
root_agent = Agent(
    name="finance_assistant",
    model="gemini-2.5-flash",
    description="A financial calculation assistant for investments, loans, and savings goals.",
    instruction=(
        "You are a helpful personal finance assistant. You can help users with:\n"
        "- Calculating compound interest for savings and investments\n"
        "- Computing monthly payments for loans (mortgages, car loans, etc.)\n"
        "- Determining how much to save monthly to reach financial goals\n"
        "\n"
        "When users ask financial questions:\n"
        "1. Use the appropriate calculation tool.\n"
        "2. Explain the results in simple terms.\n"
        "3. Be encouraging and positive about their financial planning!\n"
        "\n"
        "You are NOT a licensed financial advisor - remind users to consult professionals for major decisions."
    ),
    tools=[
        calculate_compound_interest, 
        calculate_loan_payment, 
        calculate_monthly_savings
    ]
)
```

### Self-Reflection Answers

1.  **Why is it a good practice for a tool to perform its own input validation, even though the LLM is usually good at providing the correct arguments?**
    *   **Answer:** LLMs are probabilistic and can occasionally "hallucinate" or make errors, especially with edge cases (like negative numbers for time). Validating inputs within the tool ensures the function doesn't crash or produce mathematically invalid results (like division by zero). It adds a layer of deterministic safety that is critical for robust software. Furthermore, returning a specific error message allows the agent to understand *why* the call failed and potentially correct itself or inform the user.

2.  **In the parallel execution test, the two tool calls are independent. Can you think of a scenario where a user's query might seem like it could be parallelized, but actually requires the tools to be run sequentially?**
    *   **Answer:** A sequential dependency occurs when the *output* of the first tool is required as the *input* for the second. For example: "Find the current stock price of Google, and then calculate how many shares I can buy with $1000." The agent must first call `get_stock_price('GOOG')`, wait for the result (e.g., $150), and *only then* can it perform the calculation (1000 / 150). The ADK handles this naturally: the agent will make the first call, receive the result, and then make the second call in a subsequent turn.

3.  **How does providing a pre-formatted, human-readable `report` in the tool's return dictionary simplify the agent's `instruction` prompt?**
    *   **Answer:** By including a `report` string (e.g., "Your monthly payment is $500..."), you reduce the burden on the LLM to format the raw data. Instead of needing complex instructions like "Take the 'payment' field from the result, format it as currency, and construct a sentence," you can simply instruct the agent to "Relay the tool's report to the user." This makes the agent's behavior more consistent and reduces the chance of the LLM misinterpreting the raw numbers.