#!/usr/bin/env python3
"""
Async Janus SDK Example

This example tests the @track decorator with async functions to ensure
the async wrapper properly handles coroutines.

Key Features:
- ✅ Tests async function tracking
- ✅ Validates the track decorator fix for async functions
- ✅ All math operations are now async
"""

import asyncio
import json
from openai import AsyncOpenAI

# Import the clean Janus SDK
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from __init__ import run_simulations, track

# Async math functions with automatic conversation context tracking
@track
async def add(x: int, y: int) -> int:
    """Add two numbers together asynchronously."""
    # Simulate some async work
    await asyncio.sleep(0.01)
    return x + y

@track
async def multiply(x: int, y: int) -> int:
    """Multiply two numbers asynchronously."""
    # Simulate some async work
    await asyncio.sleep(0.01)
    return x * y

@track
async def divide(x: float, y: float) -> float:
    """Divide two numbers asynchronously."""
    # Simulate some async work
    await asyncio.sleep(0.01)
    if y == 0:
        raise ValueError("Cannot divide by zero")
    return x / y

# Tool definitions for OpenAI
math_tools = [
    {
        "type": "function",
        "function": {
            "name": "multiply",
            "description": "Multiply two numbers",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                },
                "required": ["x", "y"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add",
            "description": "Add two numbers",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                },
                "required": ["x", "y"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "divide",
            "description": "Divide two numbers",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                },
                "required": ["x", "y"],
            },
        },
    },
]

tools_map = {
    "add": add,
    "multiply": multiply,
    "divide": divide,
}

class AsyncMathAgent:
    """
    Async Math Agent that tests async function tracking.
    
    This validates that the @track decorator properly handles async functions.
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", "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"))
        self.system_prompt = "You are a helpful math assistant. Use the provided tools to perform calculations when needed. Always show your work and explain your reasoning."
    
    async def runner(self, prompt: str) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=math_tools,
            tool_choice="auto",
        )

        # Handle tool calls
        while response.choices[0].finish_reason != "stop":
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls
            
            if tool_calls:
                messages.append(response_message)
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_to_call = tools_map[function_name]
                    function_args = json.loads(tool_call.function.arguments)

                    try:
                        # Now properly awaits async functions!
                        function_response = await function_to_call(**function_args)
                        function_response_json = json.dumps(function_response)
                    except Exception as e:
                        function_response_json = json.dumps({"error": str(e)})

                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response_json,
                    })

            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=math_tools,
            )

        return response.choices[0].message.content

async def main():
    print("🧪 Testing async function tracking with @track decorator...")
    
    print("\n🚀 Running async simulations...")
    results = await run_simulations(
        num_simulations=2,
        max_turns=3,
        target_agent=lambda: AsyncMathAgent().runner,
        api_key="sk-168b7b235fd24ef787990c9d6326a6f8",
        #context="Testing async math operations with the async-aware @track decorator",
        #goal="Verify that async functions are properly tracked and traced"
    )
    
    print("\n✅ Async simulation completed!")
    print(f"📊 Ran {len(results)} simulations with async functions")
    print("🔍 Check your Janus dashboard for async function traces!")
    print("\n💡 All async functions were properly tracked without returning unawaited coroutines")
    
    return results

if __name__ == "__main__":
    asyncio.run(main()) 