# Agent Handoffs

Handoffs allow agents to transfer control to other specialized agents.

## Basic Handoff

```python
from agents import Agent, Runner

# Specialized agents
sales_agent = Agent(
    name="SalesAgent",
    instructions="You are a sales specialist. Help with purchases and pricing."
)

support_agent = Agent(
    name="SupportAgent",
    instructions="You are a tech support specialist. Help with technical issues."
)

# Main agent with handoffs
triage_agent = Agent(
    name="TriageAgent",
    instructions="""You are a triage agent.

If the user has a sales question, hand off to SalesAgent.
If the user has a technical issue, hand off to SupportAgent.
Otherwise, help them directly.""",
    handoffs=[sales_agent, support_agent]
)

# Run - agent will hand off as needed
result = Runner.run_sync(triage_agent, "I need help installing the software")
print(f"Handled by: {result.last_agent.name}")
print(result.final_output)
```

## Handoff Configuration

```python
from agents import Agent, Handoff

# Create agent
specialist = Agent(
    name="Specialist",
    instructions="You are a domain specialist."
)

# Create handoff with configuration
handoff = Handoff(
    agent=specialist,
    description="Hand off to specialist for complex domain questions",
    input_filter=lambda ctx, input: input  # Optional: filter input
)

main_agent = Agent(
    name="Main",
    instructions="Help users. Hand off complex questions to Specialist.",
    handoffs=[handoff]
)
```

## Handoff with Input Transformation

```python
from agents import Agent, Handoff, RunContext

def transform_input(ctx: RunContext, input_data):
    """Transform input before handoff."""
    # Add context or modify input
    return {
        "original_query": input_data,
        "user_id": ctx.context.get("user_id"),
        "timestamp": datetime.now().isoformat()
    }

specialist = Agent(name="Specialist", instructions="...")

handoff = Handoff(
    agent=specialist,
    description="Specialist handoff",
    input_filter=transform_input
)
```

## Conditional Handoffs

```python
from agents import Agent, function_tool

# Agents for different scenarios
refund_agent = Agent(
    name="RefundAgent",
    instructions="Handle refund requests. Be empathetic."
)

billing_agent = Agent(
    name="BillingAgent",
    instructions="Handle billing questions."
)

# Main agent decides when to hand off
main_agent = Agent(
    name="CustomerService",
    instructions="""You are customer service.

Analyze the customer's request:
- For refund requests -> hand off to RefundAgent
- For billing questions -> hand off to BillingAgent
- For general questions -> answer directly

Always be helpful and professional.""",
    handoffs=[refund_agent, billing_agent]
)
```

## Multi-Level Handoffs

```python
# Level 1: Entry point
l1_support = Agent(
    name="L1Support",
    instructions="""You are L1 support.

Handle simple questions directly.
For complex issues, hand off to L2Support.""",
    handoffs=[]  # Will be set after L2 is defined
)

# Level 2: Advanced support
l2_support = Agent(
    name="L2Support",
    instructions="""You are L2 support.

Handle complex technical issues.
For unresolved issues, hand off to L3Support.""",
    handoffs=[]
)

# Level 3: Expert support
l3_support = Agent(
    name="L3Support",
    instructions="""You are L3 expert support.

Handle the most complex issues. You are the final escalation point."""
)

# Set up handoff chain
l2_support.handoffs = [l3_support]
l1_support.handoffs = [l2_support]

# Run from L1
result = Runner.run_sync(l1_support, "My server keeps crashing randomly")
```

## Handoff with Tools

```python
from agents import Agent, function_tool

@function_tool
def lookup_order(order_id: str) -> str:
    """Look up order details."""
    return f"Order {order_id}: Shipped, arriving tomorrow"

@function_tool
def process_refund(order_id: str, reason: str) -> str:
    """Process a refund."""
    return f"Refund processed for order {order_id}"

# Agent with tools AND handoff capability
order_agent = Agent(
    name="OrderAgent",
    instructions="Look up orders and process refunds.",
    tools=[lookup_order, process_refund]
)

sales_agent = Agent(
    name="SalesAgent",
    instructions="Handle new orders and upsells."
)

main_agent = Agent(
    name="Main",
    instructions="""Route requests:
- Order issues -> OrderAgent
- New purchases -> SalesAgent""",
    handoffs=[order_agent, sales_agent]
)
```

## Tracking Handoffs

```python
from agents import Agent, Runner

agent_a = Agent(name="AgentA", instructions="...")
agent_b = Agent(name="AgentB", instructions="...")

main = Agent(
    name="Main",
    instructions="...",
    handoffs=[agent_a, agent_b]
)

result = Runner.run_sync(main, "Query")

# Check which agent produced final output
print(f"Started with: Main")
print(f"Ended with: {result.last_agent.name}")

# Check all items for handoff events
for item in result.new_items:
    if hasattr(item, "type") and item.type == "handoff":
        print(f"Handoff occurred")
```

## Complete Example

```python
"""
Multi-agent customer service system
"""

from agents import Agent, Runner, function_tool

# Tools for order agent
@function_tool
def get_order_status(order_id: str) -> str:
    """Get status of an order."""
    return f"Order {order_id}: In transit, ETA 2 days"

@function_tool
def cancel_order(order_id: str) -> str:
    """Cancel an order."""
    return f"Order {order_id} has been cancelled. Refund in 3-5 days."

# Tools for account agent
@function_tool
def reset_password(email: str) -> str:
    """Send password reset email."""
    return f"Password reset link sent to {email}"

@function_tool
def update_profile(field: str, value: str) -> str:
    """Update user profile."""
    return f"Updated {field} to {value}"

# Specialized agents
order_agent = Agent(
    name="OrderSupport",
    instructions="""You handle order-related issues.
- Check order status
- Cancel orders if requested
Be helpful and provide tracking information.""",
    tools=[get_order_status, cancel_order]
)

account_agent = Agent(
    name="AccountSupport",
    instructions="""You handle account-related issues.
- Password resets
- Profile updates
Be security-conscious and helpful.""",
    tools=[reset_password, update_profile]
)

technical_agent = Agent(
    name="TechSupport",
    instructions="""You handle technical issues.
- App problems
- Website issues
- Error messages
Ask clarifying questions and provide step-by-step solutions."""
)

# Main triage agent
triage_agent = Agent(
    name="CustomerService",
    instructions="""You are the first point of contact for customers.

Analyze their request and route appropriately:
- Order questions (shipping, cancellation) -> OrderSupport
- Account issues (password, profile) -> AccountSupport
- Technical problems (app, website) -> TechSupport

For simple greetings or unclear requests, ask clarifying questions.""",
    handoffs=[order_agent, account_agent, technical_agent]
)

# Example usage
queries = [
    "Where is my order #12345?",
    "I forgot my password",
    "The app keeps crashing"
]

for query in queries:
    print(f"\nUser: {query}")
    result = Runner.run_sync(triage_agent, query)
    print(f"[{result.last_agent.name}]: {result.final_output}")
```
