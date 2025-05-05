import asyncio
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, ItemHelpers, Runner, function_tool
import logging 

async def stream_events(agent, input_question, context, max_turns):
    result = Runner.run_streamed(agent, input=(input_question), context=context, max_turns=max_turns)

    async for event in result.stream_events():
        match event.type:
            case "raw_response_event":
                if isinstance(event.data, ResponseTextDeltaEvent):
                    print(event.data.delta, end="", flush=True)

            case "agent_updated_stream_event":
                print(f"\n🧠 Agent switched to: {event.new_agent.name}", flush=True)

            case "run_item_stream_event":
                item = event.item
                match item.type:
                    case "message_output_item":
                        print(f"\n📤 Message output:\n{ItemHelpers.text_message_output(item)}\n", flush=True)
                    case "tool_call_item":
                        raw_call = event.item.raw_item
                        print(f"\n🛠️ Tool called: {raw_call.name}")
                        print(f"   Arguments: {raw_call.arguments}", flush=True)
                    case "tool_call_output_item":
                        print(f"\n✅ Tool output: {item.output}", flush=True)
                    case "final_output_item":
                        print(f"\n🏁 Final output:\n{item.output}", flush=True)
                    case "planning_start_item":
                        print(f"\n📍 Planning started...", flush=True)
                    case "planning_response_item":
                        print(f"\n🧭 Plan selected: {item.response}", flush=True)
                    case _:
                        print(f"\n🔹 Unhandled run_item_stream_event type: {item.type}", flush=True)

            case "run_step_stream_event":
                print(f"\n🔄 Step: {event.step}", flush=True)

            case "tool_start_stream_event":
                print(f"\n⚙️ Tool execution started: {event.tool.name}", flush=True)

            case "tool_finish_stream_event":
                print(f"\n✅ Tool execution finished: {event.tool.name}", flush=True)

            case "agent_finish_stream_event":
                print(f"\n🚪 Agent '{event.agent.name}' finished its turn", flush=True)

            case "handoff_event":
                print(f"\n🔁 Handoff to agent: {event.handoff.agent.name} with input: {event.handoff.input}", flush=True)

            case "error_stream_event":
                print(f"\n❌ Error occurred: {event.error}", flush=True)

            case _:
                print(f"\n🌀 Unknown event type: {event.type} — Raw: {event}", flush=True)

    print("\n=== ✅ Run complete ===")