# Multi-Tool Agent
Multi-tool calling agent that converts temperatures and calculates rectangle areas using the OpenAI function calling API.

## Insights
- Multiple tools are passed as a list to the `tools` parameter; the model routes to whichever fits the query.
- Dispatching to the right function is cleaner with a `dict` map (`{"name": fn}`) than a chain of `if/elif` checks.
- The assistant message must be appended once before any tool result messages. Ordering matters.
- When the model calls multiple tools in a single response, each one needs its own `"tool"` result message with a matching `tool_call_id`.
- Iterating over `tool_calls` in one response (parallel calls) is a separate concern from the agentic loop that handles multiple rounds of API calls. They are two nested levels, not one.
- The `while model_response.tool_calls` loop is what makes this an agent: the LLM controls how many rounds of execution happen, not the caller.
- Wrapping tool execution in `try/except` and returning an error string (instead of raising) keeps the loop alive and lets the model handle failures gracefully.
- Unhandled tool names fail silently if not caught. Always check the tool name exists in the dispatch map before calling.
- `tool_call.function.name` and `tool_call.function.arguments` are attributes, not dict keys.
- `tool_call.function.arguments` is a JSON string. Parse it with `json.loads()` before unpacking as `**kwargs`.
- The model can hallucinate a plausible answer when a tool lacks the capability it needs (e.g. Kelvin input passed to a C/F-only converter). A wrong tool definition is a tool capability gap, not a prompt issue.
