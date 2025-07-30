import asyncio
import json
import os
import sys
import threading
import time
# SDK imports
from agents import Agent, Runner, function_tool, add_trace_processor, RunHooks
from agents.tracing import FunctionSpanData, TracingProcessor
import logging
from agents import ModelSettings
logger = logging.getLogger('openai.agents')

# Color Codes
def COLORS():
    return {
        'RESET': "\033[0m",
        'RED': "\033[91m",
        'GREEN': "\033[92m",
        'YELLOW': "\033[93m",
        'BLUE': "\033[94m",
        'MAGENTA': "\033[95m",
        'CYAN': "\033[96m",
        'WHITE': "\033[97m",
        'GREY': "\033[90m",
    }

class Spinner:
    """
    CLI spinner to indicate processing.
    Automatically recreates its thread so that start() can be called multiple times.
    """
    _frames = ['|', '/', '-', '\\']
    def __init__(self, message="Processing"):
        self.message = message
        self._stop = threading.Event()
        self._pause = threading.Event()
        self._thread = None

    def _clear_line(self):
        sys.stdout.write('\r')
        sys.stdout.write('\033[K')
        sys.stdout.flush()

    def _spin(self):
        idx = 0
        while not self._stop.is_set():
            if not self._pause.is_set():
                sys.stdout.write(f"\r{self.message} {self._frames[idx % len(self._frames)]}")
                sys.stdout.flush()
                idx += 1
            time.sleep(0.1)
        self._clear_line()

    def start(self):
        # only start a new thread if none exists or previous has finished
        if self._thread is None or not self._thread.is_alive():
            self._stop.clear()
            self._pause.clear()
            self._thread = threading.Thread(target=self._spin, daemon=True)
            self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread is not None:
            self._thread.join()
            self._thread = None

    def pause(self):
        self._pause.set()
        self._clear_line()

    def resume(self):
        self._pause.clear()
        sys.stdout.write('\r')
        sys.stdout.flush()
import time
class PrintFunctionSpansProcessor(TracingProcessor):
    def __init__(self, spinner):
        self.colors = COLORS()
        self.spinner = spinner
        self.logger = logging.getLogger("openai.agents")
    time.sleep(10)
    def on_span_start(self, span):
        self.spinner.pause()
        if isinstance(span.span_data, FunctionSpanData):
            tool_name = span.span_data.name
            msg_map = {
                "kyvos_sql_generation_prompt": "Preparing prompt for SQL generation...",
                "kyvos_list_semantic_models": "Retrieving available semantic models...",
                "kyvos_list_semantic_model_columns": "Fetching semantic model column details...",
                "kyvos_execute_query": "Executing the SQL query...",
            }
            msg = msg_map.get(tool_name)
            if msg:
                print(f"{self.colors['BLUE']}[Tool Start]{self.colors['RESET']} {msg}")
        self.spinner.resume()

    def on_span_end(self, span):
        self.spinner.pause()
        if isinstance(span.span_data, FunctionSpanData):
            r, g, reset = self.colors['RED'], self.colors['GREEN'], self.colors['RESET']
            tool_name = span.span_data.name
            args = span.span_data.input or '{}'
            parsed_args = json.loads(args)
            if tool_name == "kyvos_list_semantic_model_columns":
                model = parsed_args.get("table_name")
                print(f"{g}[Tool Complete]{reset} '{tool_name}' executed with Semantic model: `{model}`")
                logger.info(f"'{tool_name}' executed with Semantic model: `{model}`")
            elif tool_name == "kyvos_execute_query":
                query = parsed_args.get("query")
                print(f"{g}[Tool Complete]{reset} '{tool_name}' executed with Query: `{query}`")
                logger.info(f"'{tool_name}' executed with Query: `{query}`")
            else:
                print(f"{g}[Tool Complete]{reset} '{tool_name}' executed")
                logger.info(f"'{tool_name}' executed")
        self.spinner.resume()
    def on_trace_end(self, trace):
        pass  # Optional: implement if needed
    def on_trace_start(self, trace):
        pass  # Optional: implement if needed
    def force_flush(self):
        pass  # Optional: implement if needed

    def shutdown(self):
        pass  # Optional: implement if needed
# Register trace processor once
spinner = Spinner(message=f"{COLORS()['GREY']}Thinking...{COLORS()['RESET']}")
add_trace_processor(PrintFunctionSpansProcessor(spinner))

async def run_interaction(mcp_server: str):
    logger.info("Starting interaction with MCP server: %s", mcp_server)
    model_name= os.getenv("OPENAI_MODEL_NAME","gpt-4o")
    settings = ModelSettings(parallel_tool_calls=False)
    agent = Agent(
        name="Assistant",
        mcp_servers=[mcp_server],
        model=model_name,
        model_settings=settings
    )
    last_result = None
    tools = await mcp_server.list_tools()
    logger.info(f"Check MCP Server tools: {tools}")
    while True:
        try:
            user_input = input("NLQ> ").strip()
        except (KeyboardInterrupt, EOFError):
            spinner.stop()
            print("\nSession terminated by user.")
            return

        if user_input.lower() == "/exit":
            spinner.stop()
            print("Exiting... Thank you!")
            sys.exit()
        if user_input.lower() == "/clear":
            spinner.stop()
            last_result = None
            print("[Context cleared] Starting fresh conversation!\n")
            continue
        if not user_input:
            continue

        # build payload
        payload = last_result.to_input_list() + [{"role": "user", "content": user_input}] if last_result else user_input
        spinner.start()
        try:
            last_result = await Runner.run(agent, payload)
            spinner.stop()
            print(f"[Assistant Response]: {last_result.final_output}\n")
        except KeyboardInterrupt:
            spinner.stop()
            print("\nSession terminated by user during query.")
            return
        except Exception as e:
            spinner.stop()
            print(f"[Error] An unexpected error occurred: {e}\n")


def main():
    mcp_server = sys.argv[1]
    asyncio.run(run_interaction(mcp_server))

if __name__ == "__main__":
    main()