# Agent Report: Anthropic Agent SDK Research
Completed: 2026-02-16
Agent: Researcher

## Research Question
What is the Anthropic Agent SDK (claude-agent-sdk)? How does it work, what are the core concepts (agents, tools, handoffs, guardrails), and how can it be integrated with Streamlit?

## Executive Summary
The Anthropic Agent SDK (formerly Claude Code SDK) is a production-ready Python and TypeScript library that enables developers to build autonomous AI agents powered by Claude. The SDK provides built-in tools for file operations, command execution, web access, and code editing, along with sophisticated features like subagents, hooks, MCP integration, and session management. It operates on a fundamental principle: give agents computer access so they work like humans do. The SDK is actively maintained (current version 0.1.36 as of Feb 2026) and suitable for production deployment with proper guardrails.

## Findings

### 1. Package Installation and Current Status
**Confidence:** High

**Python Package:**
```bash
pip install claude-agent-sdk
```

**TypeScript Package:**
```bash
npm install @anthropic-ai/claude-agent-sdk
```

**Current Version:** 0.1.36 (released February 13, 2026)

**Requirements:**
- Python 3.10+ for Python SDK
- Node.js for TypeScript SDK
- Anthropic API key (set as `ANTHROPIC_API_KEY` environment variable)
- Claude Code CLI is **automatically bundled** with the package

**Evidence:**
- PyPI package page shows version 0.1.36 with frequent updates
- GitHub repositories: [claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python) and [claude-agent-sdk-typescript](https://github.com/anthropics/claude-agent-sdk-typescript)
- Official documentation at [platform.claude.com/docs/en/agent-sdk/overview](https://platform.claude.com/docs/en/agent-sdk/overview)

**SDK Status:** Active development, marked as "Alpha" but production-ready with proper implementation

**Source:**
- PyPI: https://pypi.org/project/claude-agent-sdk/
- GitHub: https://github.com/anthropics/claude-agent-sdk-python
- Docs: https://platform.claude.com/docs/en/agent-sdk/overview

---

### 2. Core Concepts

**Confidence:** High

#### 2.1 Agents
Agents are autonomous AI systems that can read files, run commands, search the web, edit code, and more. The SDK gives agents "a computer" - the same tools developers use.

**Key principle:** Agents work best when equipped with human-like capabilities: file access, terminal commands, code execution, and iterative debugging.

**Agent Loop Framework:**
1. **Gather Context** - Search files, access APIs, pull relevant information
2. **Take Action** - Execute tools, write code, run commands
3. **Verify Work** - Check output against rules, get visual feedback, iterate

#### 2.2 Tools
Built-in tools available out of the box (no implementation required):

| Tool | Function |
|------|----------|
| **Read** | Read any file in the working directory |
| **Write** | Create new files |
| **Edit** | Make precise edits to existing files |
| **Bash** | Run terminal commands, scripts, git operations |
| **Glob** | Find files by pattern (`**/*.ts`, `src/**/*.py`) |
| **Grep** | Search file contents with regex |
| **WebSearch** | Search the web for current information |
| **WebFetch** | Fetch and parse web page content |
| **AskUserQuestion** | Ask the user clarifying questions with multiple choice options |
| **Task** | Spawn subagents for focused subtasks |

**Custom Tools:** Can be defined as Python functions using the `@tool` decorator, creating in-process MCP servers without subprocess overhead.

#### 2.3 Handoffs (Subagents)
Subagents enable:
- Parallel task execution across multiple specialized workers
- Context window isolation (only relevant information returned to orchestrator)
- Hierarchical multi-agent workflows

**Pattern:** Main agent acts as orchestrator, delegating specific subtasks to specialized subagents that report back with results.

**Implementation:**
- Include `Task` in `allowedTools`
- Define custom agents with `AgentDefinition` (Python) or agent config objects (TypeScript)
- Messages from subagents include `parent_tool_use_id` for tracking

#### 2.4 Guardrails
Multi-layered safety and control mechanisms:

**Permission Modes:**
- Standard mode: Prompts for approval before tool execution
- `acceptEdits`: Auto-approve file edits
- `bypassPermissions`: No prompts (for trusted operations)

**Tool Restrictions:**
- Fine-grained control via `allowed_tools` parameter
- Per-tool allow/deny policies
- Custom hooks can validate, block, or transform tool calls

**Safety Hooks:**
- `PreToolUse`: Validate/block before execution (e.g., dangerous shell commands)
- `PostToolUse`: Log/audit after execution
- Hook matchers allow regex patterns to target specific tools

**Sandboxing:**
- Always run in sandboxed containers (Docker, gVisor, Firecracker)
- Ephemeral containers for multi-tenant applications
- Environment isolation per user/task

**Evidence:** Official documentation provides detailed permission modes, hooks system, and safety patterns. Codacy article demonstrates implementing security guardrails.

**Source:**
- https://platform.claude.com/docs/en/agent-sdk/permissions
- https://platform.claude.com/docs/en/agent-sdk/hooks
- https://blog.codacy.com/equipping-claude-code-with-deterministic-security-guardrails

---

### 3. Tool Use Architecture

**Confidence:** High

#### 3.1 Built-in Tool Execution
The SDK handles the entire tool execution loop autonomously:

```python
# With Client SDK - you implement the loop
response = client.messages.create(...)
while response.stop_reason == "tool_use":
    result = your_tool_executor(response.tool_use)
    response = client.messages.create(tool_result=result, **params)

# With Agent SDK - Claude handles it
async for message in query(prompt="Fix the bug in auth.py"):
    print(message)
```

#### 3.2 Custom Tools Pattern
Create Python functions as tools using in-process MCP servers:

```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("greet", "Greet a user", {"name": str})
async def greet_user(args):
    return {
        "content": [
            {"type": "text", "text": f"Hello, {args['name']}!"}
        ]
    }

server = create_sdk_mcp_server(
    name="my-tools",
    version="1.0.0",
    tools=[greet_user]
)

options = ClaudeAgentOptions(
    mcp_servers={"tools": server},
    allowed_tools=["mcp__tools__greet"]
)
```

#### 3.3 Tool Design Best Practices
- **Surface primary actions**: Tools appear prominently in context
- **Clear scoping**: Well-defined, single-purpose tools
- **Good documentation**: Tool descriptions guide Claude's decisions
- **Test thoroughly**: Validate tool behavior under various conditions

#### 3.4 Advanced Tool Use Features (Beta)
Three new capabilities announced:
1. **Tool Search Tool** - Dynamic discovery and loading of tools on-demand
2. **Tool Use Examples** - Express usage patterns beyond JSON Schema
3. **Programmatic Tool Calling** - Manage context and intermediate results

**Source:**
- https://platform.claude.com/docs/en/agent-sdk/overview
- https://www.anthropic.com/engineering/advanced-tool-use

---

### 4. Multi-Agent Orchestration and Handoffs

**Confidence:** High

#### 4.1 Architecture Patterns
Anthropic published guidance identifying three scenarios where multi-agent architecture delivers value, while warning that most teams don't need it.

**Key Insight:** Multi-agent implementations typically consume **3-10x more tokens** than single-agent approaches due to:
- Duplicating context across agents
- Coordination messages
- Summarizing results for handoffs

#### 4.2 When to Use Multi-Agent
**Context-centric decomposition works better:**
- Agent handling a feature should also handle its tests (already has context)
- Verification subagents are consistently successful (validate without needing full context)
- Parallel task execution where subtasks are truly independent

**2026 Update - Agent Teams:**
Anthropic released "agent teams" capability with Opus 4.6, enabling multiple agents to work simultaneously and coordinate directly rather than sequentially through an orchestrator.

#### 4.3 Subagent Implementation
```python
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition

async for message in query(
    prompt="Use the code-reviewer agent to review this codebase",
    options=ClaudeAgentOptions(
        allowed_tools=["Read", "Glob", "Grep", "Task"],
        agents={
            "code-reviewer": AgentDefinition(
                description="Expert code reviewer for quality and security reviews.",
                prompt="Analyze code quality and suggest improvements.",
                tools=["Read", "Glob", "Grep"],
            )
        },
    ),
):
    if hasattr(message, "result"):
        print(message.result)
```

#### 4.4 Memory Management for Handoffs
- Summarize completed work phases before transitions
- Store essential information in external memory
- Spawn fresh subagents with clean contexts when approaching limits
- Maintain continuity through careful handoff summaries

**Source:**
- https://www.anthropic.com/engineering/multi-agent-research-system
- https://blockchain.news/news/anthropic-multi-agent-ai-framework-guide
- https://techcrunch.com/2026/02/05/anthropic-releases-opus-4-6-with-new-agent-teams/

---

### 5. Key Patterns for Building Agents

**Confidence:** High

#### 5.1 Anthropic's 6 Composable Patterns
1. **Prompt Chaining** - Sequential processing where each step builds on the previous
2. **Routing** - Intelligent classification and routing of tasks
3. **Parallelization** - Concurrent execution of multiple subtasks
4. **Orchestrator-Workers** - Dynamic task breakdown and delegation
5. **Evaluator-Optimizer** - Iterative improvement through feedback loops
6. **Verification Subagents** - Dedicated agents for testing/validation

#### 5.2 Three Guiding Principles
1. **Keep architecture simple** - Start small, build modularly
2. **Make reasoning visible** - Show how agents plan and decide
3. **Ensure reliable tool interactions** - Clear scope, documentation, testing

#### 5.3 Context Engineering
- Structure file systems intentionally - folder organization influences what agents consider
- Start with agentic search (grep, file inspection) before semantic search
- Use automatic context compaction for extended operations
- Project structure acts as "context engineering"

#### 5.4 Verification Strategies
Three layers of validation:
1. **Rules-based feedback** - Linting, formal error checking (TypeScript > JavaScript)
2. **Visual validation** - Screenshots for HTML rendering, layout verification
3. **LLM judgment** - Secondary models evaluate fuzzy criteria (slower but flexible)

#### 5.5 Code as Output
"Code excels as agent output because it's precise, composable, and infinitely reusable."
- Complex operations benefit from code-based solutions
- Code provides clear audit trail
- Enables programmatic verification

**Source:**
- https://aimultiple.com/building-ai-agents
- https://claude.com/blog/building-agents-with-the-claude-agent-sdk
- https://github.com/ThibautMelen/agentic-workflow-patterns

---

### 6. Streaming Responses

**Confidence:** High

#### 6.1 Enabling Streaming
Set `include_partial_messages` (Python) or `includePartialMessages` (TypeScript) to true:

```python
options = ClaudeAgentOptions(
    include_partial_messages=True
)
```

#### 6.2 Event Types

**Without streaming enabled:**
- `SystemMessage` - Session initialization
- `AssistantMessage` - Complete responses
- `ResultMessage` - Final result
- `CompactBoundaryMessage` - History compaction indicator

**With streaming enabled:**
- All above types
- `StreamEvent` - Partial message updates during streaming (only with `include_partial_messages=True`)

#### 6.3 Processing Streaming Content
```python
# Display text as it's generated
for event in stream:
    if event.type == "content_block_delta":
        if event.delta.type == "text_delta":
            print(event.delta.text, end="", flush=True)
```

#### 6.4 Interactive Conversations
Use `ClaudeSDKClient` for bidirectional streaming conversations:

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async with ClaudeSDKClient(options=options) as client:
    await client.query("First question")
    async for msg in client.receive_response():
        print(msg)

    await client.query("Follow-up question")
    async for msg in client.receive_response():
        print(msg)
```

**Source:**
- https://platform.claude.com/docs/en/agent-sdk/streaming-output
- https://platform.claude.com/docs/en/agent-sdk/python

---

### 7. Streamlit Integration

**Confidence:** Medium

#### 7.1 Why Streamlit + Claude Agent SDK
Streamlit is emerging as "the fastest way to build UIs for Claude-powered AI agents" in 2025-2026. The combination leverages:
- Streamlit's rapid UI prototyping
- Claude Agent SDK's autonomous capabilities
- Python-native integration (both are Python-first)

#### 7.2 Integration Patterns
**Architecture:**
```
User Input (Streamlit) → Claude Agent SDK → Agent Actions → Results (Streamlit Display)
```

**Key Considerations:**
- Use `st.spinner()` for long-running agent operations
- Stream agent responses into `st.write()` or `st.markdown()` for real-time updates
- Store session state using `st.session_state` for conversation continuity
- Use `st.chat_message()` and `st.chat_input()` for conversational interfaces

#### 7.3 Example Pattern
```python
import streamlit as st
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Ask Claude to help with your code"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Stream agent response
        options = ClaudeAgentOptions(
            allowed_tools=["Read", "Write", "Bash"],
            include_partial_messages=True
        )

        async with ClaudeSDKClient(options=options) as client:
            await client.query(prompt)
            async for msg in client.receive_response():
                if hasattr(msg, "text"):
                    full_response += msg.text
                    message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
```

#### 7.4 Available Resources
- **Streamlit agent-skills** - Collection of instruction sets for AI coding assistants
  - Repository: https://github.com/streamlit/agent-skills
- **Community examples** - Multiple tutorials and blog posts on Medium
- **Claude Agent SDK demos** - Official repository with multi-agent examples
  - Repository: https://github.com/anthropics/claude-agent-sdk-demos

**Limitations:**
- No official Streamlit integration guide in Anthropic docs (as of Feb 2026)
- Most examples use basic Anthropic client SDK, not full Agent SDK
- Need to handle async properly in Streamlit's synchronous execution model

**Source:**
- https://medium.com/@hadiyolworld007/streamlit-as-the-ui-layer-for-claude-powered-agents-9ff2e98f3744
- https://github.com/streamlit/agent-skills
- https://medium.com/@prakash.sukhwal/building-your-own-ai-code-assistant-a-fun-weekend-project-with-claude-and-streamlit-ed4d8054bcdf

---

## Codebase Analysis
N/A - This research focused on external SDK and documentation, not the current codebase.

## Recommendations

### For Immediate Use
1. **Start with `query()` function** - Simplest entry point for basic agent operations
2. **Use built-in tools first** - Read, Write, Edit, Bash, Glob, Grep are production-ready
3. **Enable streaming** - Set `include_partial_messages=True` for better UX
4. **Implement basic guardrails** - Use `allowed_tools` to restrict capabilities initially

### For Production Deployment
1. **Use `ClaudeSDKClient`** for bidirectional conversations and complex workflows
2. **Implement comprehensive hooks** - `PreToolUse` for validation, `PostToolUse` for auditing
3. **Add traceability** - Log every tool call and decision with `parent_tool_use_id` tracking
4. **Container isolation** - Run in sandboxed Docker/gVisor/Firecracker containers
5. **Monitor token usage** - Multi-agent workflows consume 3-10x more tokens
6. **Start single-agent** - Only add subagents when truly needed (parallel work, context isolation)

### For Streamlit Integration
1. **Use async-aware patterns** - Wrap agent calls properly for Streamlit's execution model
2. **Leverage chat components** - `st.chat_message()` and `st.chat_input()` for conversational UX
3. **Session persistence** - Store conversation state in `st.session_state`
4. **Visual feedback** - Use `st.spinner()` and streaming updates for long operations
5. **Consider latency** - Agent operations can take seconds to minutes, design UX accordingly

### Architecture Decision
**Single-Agent First:** Start with one agent using built-in tools. Only introduce subagents when:
- Parallel execution of independent tasks is needed
- Context window limits are reached
- Specialized expertise domains require isolation

**Token Budget:** Plan for 3-10x token multiplication if using multi-agent architecture.

---

## Sources

### Official Documentation
- [Agent SDK Overview](https://platform.claude.com/docs/en/agent-sdk/overview)
- [Python SDK Reference](https://platform.claude.com/docs/en/agent-sdk/python)
- [Streaming Output](https://platform.claude.com/docs/en/agent-sdk/streaming-output)
- [Hooks Documentation](https://platform.claude.com/docs/en/agent-sdk/hooks)
- [Permissions](https://platform.claude.com/docs/en/agent-sdk/permissions)

### Package Repositories
- [PyPI - claude-agent-sdk](https://pypi.org/project/claude-agent-sdk/)
- [GitHub - claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python)
- [GitHub - claude-agent-sdk-typescript](https://github.com/anthropics/claude-agent-sdk-typescript)
- [GitHub - claude-agent-sdk-demos](https://github.com/anthropics/claude-agent-sdk-demos)

### Technical Articles
- [The Complete Guide to Building Agents with the Anthropic Agent SDK](https://gist.github.com/dabit3/93a5afe8171753d0dbfd41c80033171d)
- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Anthropic Shares Multi-Agent AI Framework for Developers](https://blockchain.news/news/anthropic-multi-agent-ai-framework-guide)
- [Anthropic releases Opus 4.6 with new 'agent teams'](https://techcrunch.com/2026/02/05/anthropic-releases-opus-4-6-with-new-agent-teams/)
- [Building AI Agents with Anthropic's 6 Composable Patterns](https://aimultiple.com/building-ai-agents)

### Security & Production
- [Equipping Claude Code with Deterministic Security Guardrails](https://blog.codacy.com/equipping-claude-code-with-deterministic-security-guardrails)
- [Agents At Work: The 2026 Playbook for Building Reliable Agentic Workflows](https://promptengineering.org/agents-at-work-the-2026-playbook-for-building-reliable-agentic-workflows/)

### Streamlit Integration
- [Streamlit as the UI Layer for Claude-Powered Agents](https://medium.com/@hadiyolworld007/streamlit-as-the-ui-layer-for-claude-powered-agents-9ff2e98f3744)
- [Building Your Own AI Code Assistant with Claude and Streamlit](https://medium.com/@prakash.sukhwal/building-your-own-ai-code-assistant-a-fun-weekend-project-with-claude-and-streamlit-ed4d8054bcdf)
- [GitHub - streamlit/agent-skills](https://github.com/streamlit/agent-skills)

### Tutorials
- [Getting started with Anthropic Claude Agent SDK — Python](https://medium.com/@aiablog/getting-started-with-anthropic-claude-agent-sdk-python-826a2216381d)
- [Claude Agent SDK Tutorial: Create Agents Using Claude Sonnet 4.5](https://www.datacamp.com/tutorial/how-to-use-claude-agent-sdk)
- [How to Use Claude Agent SDK: Step-by-Step AI Agent Tutorial](https://skywork.ai/blog/how-to-use-claude-agent-sdk-step-by-step-ai-agent-tutorial/)

---

## Open Questions

### API Limits and Rate Limiting
- What are the rate limits for Agent SDK vs standard API?
- How does token counting work with built-in tool execution?
- Are there special quotas for long-running agent operations?

### Advanced MCP Integration
- How to integrate existing MCP servers (GitHub, Slack, etc.)?
- Can custom MCP servers be distributed as packages?
- What's the performance overhead of external vs in-process MCP servers?

### Streamlit Production Patterns
- Best practices for handling agent timeouts in Streamlit?
- How to implement interrupt/cancel for long-running agents in Streamlit UI?
- Patterns for showing tool execution progress in real-time?

### Cost Optimization
- Techniques to minimize token usage in multi-agent workflows?
- When does context compaction trigger and what's the impact?
- How to estimate costs for production agent workloads?

---

## Notes for Requesting Agent

### Key Takeaways
1. **SDK is production-ready** despite "Alpha" label - actively maintained with frequent releases
2. **Start simple** - The `query()` function and built-in tools cover most use cases
3. **Multi-agent has high token cost** - Only use when parallelism or context isolation truly needed
4. **Guardrails are essential** - Permission modes, hooks, and sandboxing prevent dangerous operations
5. **Streamlit integration is viable** but requires handling async properly and designing for latency

### Implementation Priority
If building a Claude-powered agent system:
1. Prototype with `query()` and built-in tools
2. Add streaming for better UX
3. Implement basic guardrails (allowed_tools, permission modes)
4. Add Streamlit UI with chat components
5. Layer in hooks for auditing/validation
6. Only add subagents when single-agent hits limits

### Watch Out For
- Token multiplication in multi-agent setups (3-10x)
- Context window management in long-running operations
- Async/await handling when integrating with Streamlit
- Sandbox/container requirements for production deployment
- API key management (never use claude.ai login for third-party products)
