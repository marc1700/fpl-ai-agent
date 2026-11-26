import json

from fpl.agent_tools import (
    get_current_squad,
    evaluate_current_squad,
    find_transfer_candidates,
    evaluate_transfer,
)

available_functions = [
    {
        "type": "function",
        "function": {
            "name": "get_current_squad",
            "description": "Retrieve the user's current FPL squad, player IDs, positions, and bank balance.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "evaluate_current_squad",
            "description": "Evaluate the user's current squad for a gameweek. Return the optimal starting XI, captain, formation, and expected points.",
            "parameters": {
                "type": "object",
                "properties": {
                    "gameweek": {
                        "type": "integer",
                        "description": "The FPL gameweek to evaluate.",
                    },
                },
                "required": ["gameweek"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_transfer_candidates",
            "description": "Find affordable potential replacement players for a player in the user's squad, sorted by projected points.",
            "parameters": {
                "type": "object",
                "properties": {
                    "outgoing_id": {
                        "type": "integer",
                        "description": "ID of the player being considered for sale.",
                    },
                    "gameweek": {
                        "type": "integer",
                        "description": "The gameweek to evaluate.",
                    },
                    "top_n": {
                        "type": "integer",
                        "description": "Maximum number of candidates to return.",
                    },
                },
                "required": ["outgoing_id", "gameweek"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "evaluate_transfer",
            "description": "Simulate a hypothetical FPL transfer and compare the expected points of the current and alternative squads. Does not make a real transfer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "outgoing_id": {
                        "type": "integer",
                        "description": "ID of the player to sell.",
                    },
                    "incoming_id": {
                        "type": "integer",
                        "description": "ID of the player to buy.",
                    },
                    "gameweek": {
                        "type": "integer",
                        "description": "The gameweek to evaluate.",
                    },
                },
                "required": ["outgoing_id", "incoming_id", "gameweek"],
            },
        },
    },
]

def call_function_fpl(tool_call, verbose: bool = False) -> dict:
    function_name = tool_call.function.name # get the name of the function requested be the llm
    function_args = json.loads(tool_call.function.arguments or "{}") # convert the llms json argument into a python dictionary

    if verbose == True:
        print(f" - Calling function: {function_name}({function_args})")
    else:
        print(f" - Calling function: {function_name}") # print the function being called

    function_map = { # map tool names to their python implementations
        "get_current_squad": get_current_squad,
        "evaluate_current_squad": evaluate_current_squad,
        "find_transfer_candidates": find_transfer_candidates,
        "evaluate_transfer": evaluate_transfer,
    }

    if function_name not in function_map:
        result = {"error": f"Unkown function: {function_name}"}

    else:
        try:
            result = function_map[function_name](**function_args) # execute the python function with the arguments chosen by the llm

        except (ValueError, KeyError, TypeError, StopIteration) as error:
            result = {"error": str(error)}

    return {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps(result),
    }
