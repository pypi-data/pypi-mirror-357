#!/usr/bin/env python3

"""
Models command implementation for the JrDev terminal.
"""
from typing_extensions import Any, List, TypedDict

# Import curses with Windows compatibility
try:
    import curses
    CURSES_AVAILABLE = True
except ImportError:
    curses = None
    CURSES_AVAILABLE = False

from jrdev.ui.ui import PrintType
from jrdev.ui.model_selector import interactive_model_selector, text_based_model_selector
from pydantic import parse_obj_as


class ModelInfo(TypedDict):
    """Type definition for model information."""
    name: str
    provider: str
    is_think: bool
    input_cost: int
    output_cost: int
    context_tokens: int


async def handle_models(app: Any, args: List[str], worker_id: str) -> None:
    """
    Handle the /models command to list all available models.

    Args:
        app: The Application instance
        args: Command arguments (unused)
    """

    # Get all models
    models_list = app.get_models()

    # Sort models first by provider, then by name alphabetically
    models = parse_obj_as(List[ModelInfo], models_list)
    sorted_models = sorted(
        models,
        key=lambda model: (model["provider"], model["name"])
    )

    # Use curses-based interactive selector if available, otherwise use text-based selector
    use_curses = CURSES_AVAILABLE and not (len(args) > 1 and args[1] == "--no-curses")
    if app.ui.ui_name == "textual":
        use_curses = False
    if use_curses:
        try:
            selected_model = curses.wrapper(
                interactive_model_selector,
                app,
                sorted_models
            )

            if selected_model:
                # User selected a model
                app.set_model(selected_model)
                app.ui.print_text(f"Model changed to: {app.state.model}", print_type=PrintType.SUCCESS)
        except Exception as e:
            # Handle any curses errors gracefully
            app.ui.print_text(f"Error in model selection: {str(e)}", print_type=PrintType.ERROR)
            # Fall back to text-based selector
            app.ui.print_text("Falling back to text-based model selection", print_type=PrintType.INFO)
            await text_based_model_selector(app, sorted_models)
    else:
        # Use text-based selector
        await text_based_model_selector(app, sorted_models)
