# This file is part of the 'servants' package (formerly 'sap_tool').
# It is a simple library for prototyping and learning agent-based reasoning with tools.
# For usage and documentation, see the README.md.

from .__init__ import *

from typing import Callable
import inspect
import json
import threading
import time

__all__ = ["Tool", "Servant", "Master", "execute_tool", "process_tool_calls"]

tools_system_message = '''
You have the ability to call tools to help you complete your task.
When you need to use a tool, return ONLY the JSON schema for the tool call like this:
{
  "name": "tool_name",
  "parameters": {
    "parameter_name": "parameter_value"
  }
}

After calling a tool, you will receive the result and should continue with your reasoning.
Do not repeat the same tool call multiple times.
'''

def execute_tool(llm_tool_response: str, available_tools: list) -> str:
    # ...existing code...
    try:
        json_str = extract_json_from_text(llm_tool_response)
        if not json_str:
            return json.dumps({"error": "No valid JSON found in response"})
        tool_call = json.loads(json_str)
        tool_name = tool_call.get("name")
        tool_args = tool_call.get("parameters", {})
        if isinstance(tool_args, str):
            tool_args = json.loads(tool_args)
        for tool in available_tools:
            if tool.name == tool_name:
                result = tool.function(**tool_args)
                return json.dumps({"tool": tool.name, "result": result})
        return json.dumps({"error": f"Tool '{tool_name}' not found"})
    except Exception as exc:
        return json.dumps({"error": str(exc)})
    return "{}"  

class Tool:
    # ...existing code...
    def __init__(self, function: Callable, name: str, description: str):
        self.function = function
        self.name = name
        self.description = description
        self.python_type_to_json_schema = {
            "str": "string",
            "float": "number",
            "int": "integer",
            "bool": "boolean",
            "dict": "object",
            "list": "array",
            "None": "null"
        }
    def build_tool_schema(self):
        parameters = inspect.signature(self.function).parameters
        properties = {}
        for param_name, param in parameters.items():
            properties[param_name] = {"type": self.python_type_to_json_schema[str(param.annotation.__name__)]}
        schema = {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object", 
                    "properties": properties,
                    "required": [param_name for param_name, param in parameters.items()]
                }
            }
        }
        return schema

class Servant:
    # ...existing code...
    def __init__(self, tools: list = None, show_memory: bool = False):
        self.tools = tools if tools is not None else []
        self._thinking_thread = None
        self._thinking_result = None
        self._thinking_messages = None
        self._pause_event = threading.Event()
        self._stop_event = threading.Event()
        self.status = "idle"
        self.error = None
        self.memory = ShortTermMemory()
        self.show_memory = show_memory
        self._register_memory_tools()
    def _register_memory_tools(self):
        def memory_add_tool(key: str, value: str) -> str:
            self.memory.add(key, value)
            return f"Memory set: {key} -> {value}"
        def memory_get_tool(key: str) -> str:
            value = self.memory.get(key)
            if value is not None:
                return f"Memory for '{key}': {value}"
            else:
                return f"No memory found for key: {key}"
        def memory_list_tool() -> str:
            entries = self.memory.list()
            return json.dumps(entries)
        self.memory_tools = [
            Tool(memory_add_tool, "add_memory", "Add or update a key-value pair in short-term memory."),
            Tool(memory_get_tool, "get_memory", "Retrieve a value from short-term memory and increment its hit count."),
            Tool(memory_list_tool, "list_memory", "List all key-value pairs in short-term memory, sorted by hit count.")
        ]
    def _reset_events(self):
        self._pause_event.clear()
        self._stop_event.clear()
    def thinking_loop(self, problem, chat_completion_func, system_message, max_iterations=5, tools=None, callback=None):
        # ...existing code...
        self._reset_events()
        def _loop():
            nonlocal tools
            try:
                self.status = "running"
                if tools:
                    tools_info = f"\n\n{tools_system_message}\n\nAvailable tools:\n"
                    for tool in tools:
                        schema = tool.build_tool_schema()
                        function_info = schema["function"]
                        tools_info += f"- {function_info['name']}: {function_info['description']}\n"
                        tools_info += f"  Parameters: {json.dumps(function_info['parameters']['properties'], indent=2)}\n"
                    sys_msg = system_message + tools_info
                else:
                    sys_msg = system_message
                messages = [
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": f"Solve this problem step by step. Split your reasoning into steps and say 'Final Answer:' when done.\nProblem: {problem}"}
                ]
                final_message = None
                for i in range(max_iterations):
                    if self._stop_event.is_set():
                        self.status = "stopped"
                        break
                    while self._pause_event.is_set() and not self._stop_event.is_set():
                        self.status = "paused"
                        time.sleep(0.1)
                    if not self._stop_event.is_set():
                        self.status = "running"
                        ai_message = chat_completion_func(messages)
                        print(f"{ai_message}\n")
                        messages.append({"role": "assistant", "content": ai_message})
                        if tools and extract_json_from_steps([{"role": "assistant", "content": ai_message}]):
                            tool_result = execute_tool(ai_message, tools)
                            try:
                                result_obj = json.loads(tool_result)
                                if "result" in result_obj:
                                    tool_feedback = f"Tool result: {result_obj['result']}. Continue with your reasoning."
                                    messages.append({"role": "user", "content": tool_feedback})
                                    print(f"Tool executed: {result_obj['result']}\n")
                                elif "error" in result_obj:
                                    tool_feedback = f"Tool error: {result_obj['error']}. Try again or continue differently."
                                    messages.append({"role": "user", "content": tool_feedback})
                                    print(f"Tool error: {result_obj['error']}\n")
                            except Exception as e:
                                print(f"Error processing tool result: {str(e)}")
                        elif "Final Answer:" in ai_message:
                            final_message = ai_message
                            break
                        else:
                            messages.append({"role": "user", "content": "Continue reasoning step by step. If you have the answer, say 'Final Answer:'."})
                    if self.show_memory:
                        print(f"[Memory] {json.dumps(self.memory.list(), indent=2)}\n")
                if final_message is None and messages:
                    final_message = messages[-1]["content"]
                self._thinking_result = final_message
                self._thinking_messages = messages
                if callback:
                    callback(final_message, messages)
                self.status = "idle"
            except Exception as e:
                self.error = e
                self.status = "error"
                print(f"Error in thinking loop: {str(e)}")
        if self._thinking_thread and self._thinking_thread.is_alive():
            self.stop()
        self._thinking_thread = threading.Thread(target=_loop, daemon=True)
        self._thinking_thread.start()
        return self
    def pause(self):
        if self._thinking_thread and self._thinking_thread.is_alive():
            self._pause_event.set()
            return True
        return False
    def resume(self):
        if self._thinking_thread and self._thinking_thread.is_alive() and self._pause_event.is_set():
            self._pause_event.clear()
            return True
        return False
    def stop(self):
        if self._thinking_thread and self._thinking_thread.is_alive():
            self._stop_event.set()
            self._pause_event.clear()
            self._thinking_thread.join(timeout=2)
            return True
        return False
    def get_thinking_result(self):
        return self._thinking_result, self._thinking_messages
    def is_running(self):
        return self._thinking_thread and self._thinking_thread.is_alive() and not self._pause_event.is_set()
    def is_paused(self):
        return self._thinking_thread and self._thinking_thread.is_alive() and self._pause_event.is_set()

class Master:
    # ...existing code...
    def __init__(self, servants: list = None):
        self.servants = servants if servants is not None else []
    def add_servant(self, servant):
        if servant not in self.servants:
            self.servants.append(servant)
    def remove_servant(self, servant):
        if servant in self.servants:
            self.servants.remove(servant)
    def run(self, problem, chat_completion_func, system_message, max_iterations=5, tools=None, callback=None):
        for servant in self.servants:
            if servant.status == "idle" or servant.status == "error":
                servant.thinking_loop(
                    problem=problem, 
                    chat_completion_func=chat_completion_func, 
                    system_message=system_message, 
                    max_iterations=max_iterations, 
                    tools=tools, 
                    callback=callback
                )
        return self
    def pause(self):
        paused = []
        for servant in self.servants:
            if servant.pause():
                paused.append(servant)
        return paused
    def resume(self):
        resumed = []
        for servant in self.servants:
            if servant.resume():
                resumed.append(servant)
        return resumed
    def stop(self):
        stopped = []
        for servant in self.servants:
            if servant.stop():
                stopped.append(servant)
        return stopped
    def get_status(self):
        return {i: servant.status for i, servant in enumerate(self.servants)}
    def get_results(self):
        results = []
        for i, servant in enumerate(self.servants):
            result, messages = servant.get_thinking_result()
            if result is not None:
                results.append((i, result))
        return results

def extract_json_from_text(text):
    import re
    matches = re.finditer(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text)
    for match in matches:
        json_str = match.group(0)
        try:
            json.loads(json_str)
            return json_str
        except Exception:
            continue
    return None

def extract_json_from_steps(messages):
    for m in messages:
        if m["role"] == "assistant":
            json_str = extract_json_from_text(m["content"])
            if json_str:
                return json_str
    return None

def process_tool_calls(messages, available_tools):
    tool_call_json = extract_json_from_steps(messages)
    if tool_call_json:
        tool_result = execute_tool(tool_call_json, available_tools)
        try:
            result_obj = json.loads(tool_result)
            if "result" in result_obj:
                return f"Tool execution result: {result_obj['result']}"
            elif "error" in result_obj:
                return f"Tool execution error: {result_obj['error']}"
            else:
                return "Tool execution result: No result found."
        except Exception:
            return f"Tool execution result: {tool_result}"
    else:
        return "Tool execution result: No tool call detected in any step."

class ShortTermMemory:
    def __init__(self):
        self._memory = []
    def add(self, key: str, value: str):
        for entry in self._memory:
            if entry["key"] == key:
                entry["value"] = value
                return
        self._memory.append({"key": key, "value": value, "hits": 0})
        self._sort()
    def get(self, key: str):
        for entry in self._memory:
            if entry["key"] == key:
                entry["hits"] += 1
                self._sort()
                return entry["value"]
        return None
    def list(self):
        return [{"key": e["key"], "value": e["value"], "hits": e["hits"]} for e in self._memory]
    def _sort(self):
        self._memory.sort(key=lambda e: e["hits"], reverse=True)
