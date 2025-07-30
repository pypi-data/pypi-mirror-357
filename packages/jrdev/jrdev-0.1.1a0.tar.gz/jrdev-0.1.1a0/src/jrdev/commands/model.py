#!/usr/bin/env python3

"""
Model command implementation for the JrDev terminal.
Manages the user's list of available models and the active chat model.
"""
from typing import List
from jrdev.ui.ui import PrintType
from jrdev.utils.string_utils import is_valid_name, is_valid_cost, is_valid_context_window


def _parse_bool(val: str) -> bool:
    """Parse a string to boolean, accepting common true/false values."""
    true_vals = {"1", "true", "yes", "y", "on"}
    false_vals = {"0", "false", "no", "n", "off"}
    if val.lower() in true_vals:
        return True
    if val.lower() in false_vals:
        return False
    raise ValueError(f"Invalid boolean value: {val}")


def _parse_model_arguments(app, args: List[str], start_idx: int) -> dict:
    """Parse and validate model arguments starting from given index."""
    name = args[start_idx]
    provider = args[start_idx+1]
    is_think_str = args[start_idx+2]
    input_cost_str = args[start_idx+3]
    output_cost_str = args[start_idx+4]
    context_window_str = args[start_idx+5]

    if not is_valid_name(name):
        app.ui.print_text(
            f"Invalid model name '{name}'. Allowed: 1-64 chars, alphanumeric, underscore, hyphen; no path separators.",
            PrintType.ERROR
        )
        return None
    if not is_valid_name(provider):
        app.ui.print_text(
            f"Invalid provider name '{provider}'. Allowed: 1-64 chars, alphanumeric, underscore, hyphen; no path separators.",
            PrintType.ERROR
        )
        return None
    try:
        is_think = _parse_bool(is_think_str)
    except ValueError as e:
        app.ui.print_text(f"Invalid value for is_think: {e}", PrintType.ERROR)
        return None
    try:
        input_cost_float = float(input_cost_str)
    except ValueError:
        app.ui.print_text(f"Invalid value for input_cost: '{input_cost_str}' (must be a float)", PrintType.ERROR)
        return None
    if not is_valid_cost(input_cost_float):
        app.ui.print_text(f"input_cost must be between 0 and 1000 (dollars per 1,000,000 tokens).", PrintType.ERROR)
        return None
    try:
        output_cost_float = float(output_cost_str)
    except ValueError:
        app.ui.print_text(f"Invalid value for output_cost: '{output_cost_str}' (must be a float)", PrintType.ERROR)
        return None
    if not is_valid_cost(output_cost_float):
        app.ui.print_text(f"output_cost must be between 0 and 1000 (dollars per 1,000,000 tokens).", PrintType.ERROR)
        return None
    try:
        context_window = int(context_window_str)
    except ValueError:
        app.ui.print_text(f"Invalid value for context_window: '{context_window_str}' (must be integer)", PrintType.ERROR)
        return None
    if not is_valid_context_window(context_window):
        app.ui.print_text(f"context_window must be between 1 and 1,000,000,000.", PrintType.ERROR)
        return None

    input_cost = int(round(input_cost_float * 10))
    output_cost = int(round(output_cost_float * 10))
    
    return {
        'name': name,
        'provider': provider,
        'is_think': is_think,
        'input_cost': input_cost,
        'output_cost': output_cost,
        'context_window': context_window
    }


async def handle_model(app, args: List[str], worker_id: str):
    """
    Handle the /model command to manage available models and set the active chat model.

    Args:
        app: The Application instance.
        args: Command arguments:
              /model list
              /model set <model_name>
              /model remove <model_name>
              /model add <name> <provider> <is_think> <input_cost> <output_cost> <context_window>
              /model edit <name> <provider> <is_think> <input_cost> <output_cost> <context_window>
        worker_id: The ID of the worker processing the command (unused in this handler).
    """

    current_chat_model = app.state.model
    available_model_names = app.get_model_names()
    
    detailed_usage_message = (
        "Manages available AI models and the active chat model.\n"
        "Usage:\n"
        "  /model list                       - Shows all models available in your user_models.json.\n"
        "  /model set <model_name>           - Sets the active model for the chat.\n"
        "  /model remove <model_name>        - Removes a model from your user_models.json.\n"
        "  /model add <name> <provider> <is_think> <input_cost> <output_cost> <context_window>\n"
        "      - Add a new model to your user_models.json.\n"
        "        <input_cost> and <output_cost> are the cost per 1,000,000 tokens (as a float, in dollars).\n"
        "  /model edit <name> <provider> <is_think> <input_cost> <output_cost> <context_window>\n"
        "      - Edit an existing model in your user_models.json.\n"
        "        Parameters are the same as for the 'add' command.\n"
        "Example: /model add gpt-4 openai true 0.10 0.30 8192\n"
    )

    if len(args) < 2:
        current_chat_model_display = current_chat_model if current_chat_model else "Not set"
        app.ui.print_text(f"Current chat model: {current_chat_model_display}", print_type=PrintType.INFO)
        app.ui.print_text(detailed_usage_message, print_type=PrintType.INFO)
        if available_model_names:
            app.ui.print_text(f"Available models: {', '.join(available_model_names)}", print_type=PrintType.INFO)
        else:
            app.ui.print_text("No models available in your configuration.", PrintType.INFO)
        return

    subcommand = args[1].lower()

    if subcommand == "list":
        if not available_model_names:
            app.ui.print_text("No models available in your user configuration (user_models.json).", PrintType.INFO)
        else:
            app.ui.print_text("Available models (from your user_models.json):", PrintType.INFO)
            for m_name in available_model_names:
                app.ui.print_text(f"  - {m_name}")
        return

    elif subcommand == "set":
        if len(args) < 3:
            app.ui.print_text("Usage: /model set <model_name>", PrintType.ERROR)
            if available_model_names:
                app.ui.print_text(f"Available models: {', '.join(available_model_names)}", PrintType.INFO)
            else:
                app.ui.print_text("No models available to set.", PrintType.INFO)
            return
        
        model_name_to_set = args[2]
        if model_name_to_set in available_model_names:
            app.set_model(model_name_to_set) # This handles persistence of chat_model and UI update
            app.ui.print_text(f"Chat model set to: {model_name_to_set}", print_type=PrintType.SUCCESS)
        else:
            app.ui.print_text(f"Error: Model '{model_name_to_set}' not found in your configuration.", PrintType.ERROR)
            if available_model_names:
                app.ui.print_text(f"Available models: {', '.join(available_model_names)}", PrintType.INFO)
            else:
                app.ui.print_text("No models available in your configuration.", PrintType.INFO)
        return

    elif subcommand == "remove":
        if len(args) < 3:
            app.ui.print_text("Usage: /model remove <model_name>", PrintType.ERROR)
            if available_model_names:
                app.ui.print_text(f"Available models: {', '.join(available_model_names)}", PrintType.INFO)
            else:
                app.ui.print_text("No models available to remove.", PrintType.INFO)
            return

        model_name_to_remove = args[2]
        current_models_full_data = app.get_models() # Fetches List[Dict[str, Any]]

        if not any(m['name'] == model_name_to_remove for m in current_models_full_data):
            app.ui.print_text(f"Error: Model '{model_name_to_remove}' not found in your configuration.", PrintType.ERROR)
            return

        if not app.remove_model(model_name_to_remove):
            app.logger.info(f"Failed to remove model {model_name_to_remove}")
            app.ui.print_text(f"Failed to remove model {model_name_to_remove}")
            return

        app.logger.info(f"Removed model {model_name_to_remove}")
        app.ui.print_text(f"Removed model {model_name_to_remove}")
        return

    elif subcommand == "add":
        # /model add <name> <provider> <is_think> <input_cost> <output_cost> <context_window>
        if len(args) < 8:
            app.ui.print_text(
                "Usage: /model add <name> <provider> <is_think> <input_cost> <output_cost> <context_window>",
                PrintType.ERROR
            )
            app.ui.print_text(
                "Example: /model add gpt-4 openai true 0.10 0.30 8192\n"
                "  <input_cost> and <output_cost> are the cost per 1,000,000 tokens (as a float, in dollars).",
                PrintType.INFO
            )
            return

        model_data = _parse_model_arguments(app, args, 2)
        if not model_data:
            return

        # Check for duplicate model name
        if model_data['name'] in available_model_names:
            app.ui.print_text(f"A model named '{model_data['name']}' already exists in your configuration.", PrintType.ERROR)
            return

        # Add the model
        success = app.add_model(model_data['name'], model_data['provider'], model_data['is_think'], 
                              model_data['input_cost'], model_data['output_cost'], model_data['context_window'])
        if success:
            app.logger.info(f"Added model {model_data['name']} (provider: {model_data['provider']})")
            app.ui.print_text(f"Successfully added model '{model_data['name']}' (provider: {model_data['provider']})", PrintType.SUCCESS)
        else:
            app.logger.info(f"Failed to add model {model_data['name']} (provider: {model_data['provider']})")
            app.ui.print_text(f"Failed to add model '{model_data['name']}' (provider: {model_data['provider']})", PrintType.ERROR)
        return

    elif subcommand == "edit":
        # /model edit <name> <provider> <is_think> <input_cost> <output_cost> <context_window>
        if len(args) < 8:
            app.ui.print_text(
                "Usage: /model edit <name> <provider> <is_think> <input_cost> <output_cost> <context_window>",
                PrintType.ERROR
            )
            app.ui.print_text(
                "Example: /model edit gpt-4 openai true 0.10 0.30 8192\n"
                "  <input_cost> and <output_cost> are the cost per 1,000,000 tokens (as a float, in dollars).",
                PrintType.INFO
            )
            return

        model_data = _parse_model_arguments(app, args, 2)
        if not model_data:
            return

        # Check model exists
        if model_data['name'] not in available_model_names:
            app.ui.print_text(f"Error: Model '{model_data['name']}' not found in your configuration.", PrintType.ERROR)
            return

        # Edit the model
        success = app.edit_model(model_data['name'], model_data['provider'], model_data['is_think'], 
                              model_data['input_cost'], model_data['output_cost'], model_data['context_window'])
        if success:
            app.logger.info(f"Edited model {model_data['name']} (provider: {model_data['provider']})")
            app.ui.print_text(f"Successfully edited model '{model_data['name']}' (provider: {model_data['provider']})", PrintType.SUCCESS)
        else:
            app.logger.info(f"Failed to edit model {model_data['name']} (provider: {model_data['provider']})")
            app.ui.print_text(f"Failed to edit model '{model_data['name']}' (provider: {model_data['provider']})", PrintType.ERROR)
        return

    else:
        app.ui.print_text(f"Unknown subcommand: {subcommand}", PrintType.ERROR)
        app.ui.print_text(detailed_usage_message, PrintType.INFO)