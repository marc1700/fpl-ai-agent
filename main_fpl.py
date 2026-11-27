import os
from openai import OpenAI
import argparse
from prompts_fpl import system_prompt
import json
from call_function_fpl import available_functions, call_function_fpl
from dotenv import load_dotenv
from ollama import Client
from types import SimpleNamespace

def main():
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verboseoutput")
    args = parser.parse_args()

    """
    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama", # we do not need authentication, so we can just write a string
        timeout=300.0,
    )
    """

    # try ollama client:
    client = Client(
        host="http://localhost:11434",
        timeout=500.0,
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.user_prompt},
    ]

    evaluated_transfers = {} # store all transfers considered during this agent run

    for iteration in range(20): # allow up to 20 llm requests
        """
        response = client.chat.completions.create(
            model="gemma4:e4b",
            messages=messages,
            temperature=0,
            tools=available_functions,
            max_tokens=4096, # allow more output tokens
            reasoning_effort="none",
        )
        """

        # try ollama api request
        response = client.chat(
            model="gemma4:e4b",
            messages=messages,
            tools=available_functions,
            think=True,
            options={
                "num_ctx": 8192,
                "num_predict": 4096,
                "temperature": 0
            },
        )

        ### add this to find out why the answer are always truncated
        print("Done reason:", response.done_reason)
        print("Generated tokens:", response.eval_count)
        print("Thinking characters:", len(response.message.thinking or ""))
        print("Answer characters:", len(response.message.content or ""))
        print("Prompt tokens:", response.prompt_eval_count)
        print("Generated tokens:", response.eval_count)
        print("Done reason:", response.done_reason)

        """
        if response.usage is None:
            raise RuntimeError("Token usage information is missing")

        if args.verbose == True:
            print(f"User prompt: {args.user_prompt}")
            print(f"Prompt tokens: {response.usage.prompt_tokens}")
            print(f"Response tokens: {response.usage.completion_tokens}")
        """

        # try ollama token usage:
        if args.verbose:
            print(f"\nLLM request: {iteration + 1}")
            print(f"Prompt tokens: {response.prompt_eval_count or 0}")
            print(f"Response tokens: {response.eval_count or 0}")

        """
        message = response.choices[0].message
        messages.append(message)

        # find out why the llm gave truncated response
        print("Finish reason:", response.choices[0].finish_reason)
        """

        #try ollama response message
        message = response.message

        messages.append(message) # save the assistant message, including any tool calls

        if message.tool_calls:
            for tool_call in message.tool_calls:

                # convert ollamas tool call to the format expected by call_function_fpl()
                openai_tool_call = SimpleNamespace(
                    id="ollama-tool",
                    function=SimpleNamespace(
                        name=tool_call.function.name,
                        arguments=json.dumps(tool_call.function.arguments),
                    )
                )

                # execute the tool
                result_message = call_function_fpl(
                    openai_tool_call, 
                    verbose=args.verbose
                )

                if not result_message["content"]:
                    raise RuntimeError("Function returned empty content")

                # Append the tool result normally
                messages.append({
                    "role": "tool",
                    "tool_name": tool_call.function.name,
                    "content": result_message["content"],
                })

                # Automatically store evaluated transfers in Python
                if tool_call.function.name == "evaluate_transfer":
                    transfer_result = json.loads(result_message["content"])

                    transfer_key = (
                        tool_call.function.arguments["outgoing_id"],
                        tool_call.function.arguments["incoming_id"],
                        tool_call.function.arguments["gameweek"],
                    )

                    evaluated_transfers[transfer_key] = transfer_result

                if args.verbose:
                    print(f"-> {result_message['content']}")

            # After ALL tool calls, compress the conversation if transfers were evaluated
            if any(
                tool_call.function.name == "evaluate_transfer"
                for tool_call in message.tool_calls
            ):

                # Build a compact history of evaluated transfers
                transfer_summary = "Transfers already evaluated:\n"

                for (outgoing_id, incoming_id, gameweek), result in evaluated_transfers.items():
                    transfer_summary += (
                        f"- GW{gameweek}: {outgoing_id} -> {incoming_id},"
                        f"expected points: {result['new_expected_points']:.2f}, "
                        f"improvement: {result['improvement']:+.2f},"
                        f"remaining bank: {result['remaining_bank']:.1f}m\n"
                    )

                # Find the best transfer evaluated so far
                best_key, best_result = max(
                    evaluated_transfers.items(),
                    key=lambda item: item[1]["improvement"],
                )

                # Add the best transfer to the summary
                transfer_summary += (
                    f"\nCurrent squad: {best_result['current_expected_points']:.2f} expected points\n"
                    f"Best transfer so far: {best_key[0]} -> {best_key[1]}\n"
                    f"Expected points after transfer: {best_result['new_expected_points']:.2f}\n"
                    f"Improvement: {best_result['improvement']:+.2f}\n"
                )
                
                # Replace the old conversation history
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": args.user_prompt},
                    {
                        "role": "user",
                        "content": (
                            transfer_summary
                            + "\nContinue investigating transfer options. "
                            + "Do not repeat previously evaluated transfers."
                        ),
                    },
                ]

        else:
            print("Final response:")
            print(message.content)
            break

    else:
        print("Error: Agent reached the maximum of 20 iteratations!")
        raise SystemExit(1)

if __name__ == "__main__":
    main()

