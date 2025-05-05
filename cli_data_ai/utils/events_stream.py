import asyncio
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, ItemHelpers, Runner, function_tool
import logging 
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

async def stream_events(agent, input_question, context, max_turns):
    result = Runner.run_streamed(agent, input=(input_question), context=context, max_turns=max_turns)

    async for event in result.stream_events():
        match event.type:
            case "raw_response_event":
                if isinstance(event.data, ResponseTextDeltaEvent):
                    console.print(event.data.delta, end="")

            case "agent_updated_stream_event":
                console.print(f"\n🧠 Agent switched to: {event.new_agent.name}")

            case "run_item_stream_event":
                item = event.item
                match item.type:
                    case "message_output_item":
                        console.print(f"\n📤 Message output:\n{ItemHelpers.text_message_output(item)}\n")
                    case "tool_call_item":
                        raw_call = event.item.raw_item
                        console.print(f"\n🛠️ Tool called: {raw_call.name}")
                        console.print(f"   Arguments: {raw_call.arguments}")
                    case "tool_call_output_item":
                        console.print(f"\n✅ Tool output: {item.output}")
                    case "final_output_item":
                        console.print(f"\n🏁 Final output:\n{item.output}")
                    case "planning_start_item":
                        console.print(f"\n📍 Planning started...")
                    case "planning_response_item":
                        console.print(f"\n🧭 Plan selected: {item.response}")
                    case _:
                        console.print(f"\n🔹 Unhandled run_item_stream_event type: {item.type}")

            case "run_step_stream_event":
                console.print(f"\n🔄 Step: {event.step}")

            case "tool_start_stream_event":
                console.print(f"\n⚙️ Tool execution started: {event.tool.name}")

            case "tool_finish_stream_event":
                console.print(f"\n✅ Tool execution finished: {event.tool.name}")

            case "agent_finish_stream_event":
                console.print(f"\n🚪 Agent '{event.agent.name}' finished its turn")

            case "handoff_event":
                console.print(f"\n🔁 Handoff to agent: {event.handoff.agent.name} with input: {event.handoff.input}")

            case "error_stream_event":
                console.print(f"\n❌ Error occurred: {event.error}")

            case _:
                console.print(f"\n🌀 Unknown event type: {event.type} — Raw: {event}")

    console.print("\n=== ✅ Run complete ===")