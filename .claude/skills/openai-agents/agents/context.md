# Agent Context

Context allows passing data and state through agent execution.

## Basic Context

```python
from agents import Agent, Runner

agent = Agent(
    name="Greeter",
    instructions="Greet the user by name if available in context."
)

# Pass context data
result = Runner.run_sync(
    agent,
    "Hello!",
    context={"user_name": "Alice", "user_id": "123"}
)
```

## Accessing Context in Tools

```python
from agents import Agent, Runner, function_tool, RunContext

@function_tool
def get_user_data(ctx: RunContext) -> str:
    """Get data for the current user."""
    user_id = ctx.context.get("user_id")
    
    if not user_id:
        return "No user logged in"
    
    # Fetch user data
    return f"User {user_id}: Premium account, member since 2020"

@function_tool
def save_preference(ctx: RunContext, key: str, value: str) -> str:
    """Save a user preference."""
    user_id = ctx.context.get("user_id")
    
    # Save to database
    save_to_db(user_id, key, value)
    
    return f"Saved {key}={value} for user {user_id}"

agent = Agent(
    name="UserAgent",
    instructions="Help users manage their account.",
    tools=[get_user_data, save_preference]
)

result = Runner.run_sync(
    agent,
    "What's my account status?",
    context={"user_id": "usr_123"}
)
```

## Context Object

```python
from agents import RunContext

@function_tool
def tool_with_context(ctx: RunContext, param: str) -> str:
    """Tool demonstrating context access."""
    
    # Access custom context data
    custom_data = ctx.context.get("custom_key")
    
    # Access the current agent
    agent_name = ctx.agent.name
    
    # Get all context keys
    all_keys = list(ctx.context.keys())
    
    return f"Agent: {agent_name}, Keys: {all_keys}"
```

## Typed Context

```python
from typing import TypedDict, Optional
from agents import Agent, Runner, function_tool, RunContext

class UserContext(TypedDict):
    user_id: str
    user_name: str
    email: Optional[str]
    is_premium: bool

@function_tool
def check_premium(ctx: RunContext) -> str:
    """Check if user has premium access."""
    user_ctx: UserContext = ctx.context
    
    if user_ctx.get("is_premium"):
        return f"Yes, {user_ctx['user_name']} has premium access!"
    else:
        return f"No, {user_ctx['user_name']} is on the free plan."

agent = Agent(
    name="PremiumChecker",
    instructions="Check user premium status.",
    tools=[check_premium]
)

context: UserContext = {
    "user_id": "123",
    "user_name": "Alice",
    "email": "alice@example.com",
    "is_premium": True
}

result = Runner.run_sync(agent, "Am I premium?", context=context)
```

## Modifying Context During Execution

```python
from agents import Agent, Runner, function_tool, RunContext

@function_tool
def login(ctx: RunContext, username: str) -> str:
    """Simulate user login."""
    # Update context for subsequent tool calls
    ctx.context["user_id"] = f"usr_{username}"
    ctx.context["logged_in"] = True
    
    return f"Logged in as {username}"

@function_tool
def get_profile(ctx: RunContext) -> str:
    """Get user profile."""
    if not ctx.context.get("logged_in"):
        return "Please log in first"
    
    user_id = ctx.context["user_id"]
    return f"Profile for {user_id}"

agent = Agent(
    name="AuthAgent",
    instructions="Handle user authentication and profile access.",
    tools=[login, get_profile]
)

result = Runner.run_sync(
    agent,
    "Login as john and then show my profile",
    context={}  # Start with empty context
)
```

## Context with Handoffs

```python
from agents import Agent, Runner, Handoff, RunContext

def add_handoff_info(ctx: RunContext, input_data):
    """Add information before handoff."""
    return {
        **input_data,
        "original_agent": ctx.agent.name,
        "handoff_timestamp": datetime.now().isoformat()
    }

specialist = Agent(
    name="Specialist",
    instructions="Handle specialized queries."
)

handoff = Handoff(
    agent=specialist,
    description="Specialist handoff",
    input_filter=add_handoff_info
)

main = Agent(
    name="Main",
    instructions="Route to Specialist.",
    handoffs=[handoff]
)

# Context is preserved through handoffs
result = Runner.run_sync(
    main,
    "I need specialized help",
    context={"session_id": "abc123"}
)
```

## Complete Example

```python
"""
E-commerce agent with user context
"""

from typing import TypedDict, List
from agents import Agent, Runner, function_tool, RunContext

class ShopContext(TypedDict):
    user_id: str
    cart: List[dict]
    is_member: bool

@function_tool
def add_to_cart(ctx: RunContext, product_id: str, quantity: int = 1) -> str:
    """Add product to shopping cart."""
    cart = ctx.context.get("cart", [])
    
    cart.append({
        "product_id": product_id,
        "quantity": quantity
    })
    
    ctx.context["cart"] = cart
    return f"Added {quantity}x {product_id} to cart"

@function_tool
def view_cart(ctx: RunContext) -> str:
    """View items in cart."""
    cart = ctx.context.get("cart", [])
    
    if not cart:
        return "Your cart is empty"
    
    lines = ["Your cart:"]
    for item in cart:
        lines.append(f"  - {item['product_id']} x{item['quantity']}")
    
    return "\n".join(lines)

@function_tool
def checkout(ctx: RunContext) -> str:
    """Process checkout."""
    cart = ctx.context.get("cart", [])
    
    if not cart:
        return "Cannot checkout - cart is empty"
    
    user_id = ctx.context.get("user_id", "guest")
    is_member = ctx.context.get("is_member", False)
    
    total = len(cart) * 10  # Simplified pricing
    discount = 0.1 if is_member else 0
    
    final = total * (1 - discount)
    
    # Clear cart after checkout
    ctx.context["cart"] = []
    
    result = f"Order placed for {user_id}!\n"
    result += f"Items: {len(cart)}\n"
    result += f"Total: ${total:.2f}\n"
    if discount:
        result += f"Member discount: {discount*100:.0f}%\n"
        result += f"Final: ${final:.2f}"
    
    return result

agent = Agent(
    name="ShopAssistant",
    instructions="""You are a shopping assistant.

Help users:
- Add items to cart
- View their cart
- Checkout

Member users get 10% off.""",
    tools=[add_to_cart, view_cart, checkout]
)

# Run with context
context: ShopContext = {
    "user_id": "user_123",
    "cart": [],
    "is_member": True
}

result = Runner.run_sync(
    agent,
    "Add a laptop and 2 keyboards to my cart, then checkout",
    context=context
)

print(result.final_output)
```
