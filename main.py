import os
from dotenv import load_dotenv
from openai import OpenAI
import argparse
from prompts import system_prompt
from call_function import available_functions
import json
from call_function import call_function

def main():
    load_dotenv()
    api_key = os.environ.get("OPENROUTER_API_KEY")

    if api_key is None:
        raise RuntimeError("OPENROUTER_API_KEY was not found")

    print("API key loaded successfully!")

    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verboseoutput")
    args = parser.parse_args()

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.user_prompt},
    ]

    for _ in range(20):
        response = client.chat.completions.create(
            model="nvidia/nemotron-3.5-super-vl:free",
            messages=messages,
            temperature=0,
            tools=available_functions,
        )

        if response.usage is None:
            raise RuntimeError("Token usage information is missing")

        if args.verbose == True:
            print(f"User prompt: {args.user_prompt}")
            print(f"Prompt tokens: {response.usage.prompt_tokens}")
            print(f"Response tokens: {response.usage.completion_tokens}")

        message = response.choices[0].message
        messages.append(message)

        if message.tool_calls:
            for tool_call in message.tool_calls:
                result_message = call_function(tool_call, verbose=args.verbose)
                messages.append(result_message)

                if not result_message["content"]:
                    raise RuntimeError("Function returned empty content")

                if args.verbose == True:
                    print(f"-> {result_message['content']}")

        else:
            print("Final response:")
            print(message.content)
            break

    else:
        print("Error: Agent reached the maximum of 20 iterations without producing a final response!")
        raise SystemExit(1)

if __name__ == "__main__":
    main()
