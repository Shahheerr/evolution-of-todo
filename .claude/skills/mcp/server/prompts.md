# MCP Prompts

Prompts are pre-defined templates that AI assistants can use.

## Defining Prompts

### Basic Prompt

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.prompt()
def code_review() -> str:
    """Prompt for code review."""
    return """Please review the following code for:
1. Bugs and errors
2. Security vulnerabilities
3. Performance issues
4. Code style and best practices

Provide specific suggestions for improvement."""
```

### Prompt with Parameters

```python
@mcp.prompt()
def analyze_code(language: str, code: str) -> str:
    """Analyze code in a specific language."""
    return f"""Analyze the following {language} code:

```{language}
{code}
```

Identify any issues and suggest improvements."""
```

### Prompt with Arguments

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.prompt()
def summarize(
    content: str,
    style: str = "concise",
    max_length: int = 100
) -> str:
    """
    Generate a summary prompt.
    
    Args:
        content: Content to summarize
        style: Summary style (concise, detailed, bullet)
        max_length: Maximum words in summary
    """
    return f"""Summarize the following content in a {style} style.
Keep the summary under {max_length} words.

Content:
{content}"""
```

## Message-Based Prompts

For multi-turn or structured prompts:

```python
from mcp.server.fastmcp import FastMCP
from mcp.types import PromptMessage, TextContent

mcp = FastMCP("my-server")

@mcp.prompt()
def chat_with_context(context: str, question: str) -> list[PromptMessage]:
    """Create a contextual chat prompt."""
    return [
        PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text=f"Context: {context}"
            )
        ),
        PromptMessage(
            role="assistant",
            content=TextContent(
                type="text",
                text="I've understood the context. What would you like to know?"
            )
        ),
        PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text=question
            )
        )
    ]
```

## Prompt Metadata

```python
@mcp.prompt(
    name="code-review",
    description="Comprehensive code review prompt"
)
def code_review_prompt(code: str) -> str:
    return f"Review this code:\n{code}"
```

## Dynamic Prompts

```python
@mcp.prompt()
async def database_query_prompt(table: str) -> str:
    """Generate prompt with database schema."""
    
    # Fetch schema dynamically
    async with pool.acquire() as conn:
        columns = await conn.fetch(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = $1",
            table
        )
    
    schema = "\n".join([f"- {c['column_name']}: {c['data_type']}" for c in columns])
    
    return f"""You are querying the '{table}' table with the following schema:

{schema}

Write a SQL query to answer the user's question."""
```

## Complete Example

```python
from mcp.server.fastmcp import FastMCP
from mcp.types import PromptMessage, TextContent

mcp = FastMCP("prompt-server")

# Simple text prompt
@mcp.prompt()
def explain_concept(concept: str, audience: str = "beginner") -> str:
    """Generate explanation prompt."""
    return f"""Explain the concept of "{concept}" to a {audience} audience.

Use simple language and provide examples.
If appropriate, include analogies to make the concept clearer."""

# Prompt for code generation
@mcp.prompt()
def generate_code(
    task: str,
    language: str,
    constraints: str = ""
) -> str:
    """Generate code generation prompt."""
    constraint_section = f"\nConstraints:\n{constraints}" if constraints else ""
    
    return f"""Write {language} code to accomplish the following task:

Task: {task}
{constraint_section}

Requirements:
1. Write clean, well-documented code
2. Include error handling
3. Follow {language} best practices"""

# Multi-message prompt
@mcp.prompt()
def debug_session(error: str, code: str) -> list[PromptMessage]:
    """Create a debugging session prompt."""
    return [
        PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text=f"I'm getting this error:\n\n```\n{error}\n```"
            )
        ),
        PromptMessage(
            role="assistant",
            content=TextContent(
                type="text",
                text="I see the error. Can you share the relevant code?"
            )
        ),
        PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text=f"Here's the code:\n\n```\n{code}\n```"
            )
        )
    ]

# Template prompt with options
@mcp.prompt()
def write_documentation(
    code: str,
    doc_type: str = "api",  # api, tutorial, readme
    include_examples: bool = True
) -> str:
    """Generate documentation writing prompt."""
    
    doc_instructions = {
        "api": "Write API documentation with function signatures, parameters, and return values.",
        "tutorial": "Write a step-by-step tutorial explaining how to use this code.",
        "readme": "Write a README.md file for this project."
    }
    
    instruction = doc_instructions.get(doc_type, doc_instructions["api"])
    example_note = "\nInclude code examples for each feature." if include_examples else ""
    
    return f"""{instruction}{example_note}

Code to document:

```
{code}
```"""

if __name__ == "__main__":
    mcp.run()
```
