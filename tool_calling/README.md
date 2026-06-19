# Tool Calling Agent
Basic tool-calling agent that multiplies two numbers using the OpenAI function calling API.

## Insights
- The LLM cannot execute code — it only selects the tool and provides arguments; Python does the execution
- Tool definitions are passed as a separate `tools` parameter, not inside the messages list
- The tool calling flow requires two API calls: one to get the tool call, one to get the final response
- The assistant message from the first response must be appended to messages before the tool result
- The tool result message uses role `"tool"`, not `"user"`, and must include `tool_call_id` to match the call
- The SDK response is a Python object — use attribute access (`.id`, `.function.name`) not dict access (`["id"]`)
- `tool_call.function.arguments` is a JSON string — parse it with `json.loads()` before using it as a dict
- The system prompt controls how the model formats its response (e.g. plain text vs LaTeX)
- Always check if `tool_calls` is present before assuming the model wants to use a tool