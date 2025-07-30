#!/usr/bin/env python3

"""
AsyncSend command implementation for the JrDev application.
This command sends a message to the LLM and optionally saves the response to a file,
without waiting for the response to be returned to the terminal.
"""

import os
import asyncio
import uuid
from typing import Any, List
from jrdev.ui.ui import PrintType
from jrdev.file_operations.file_utils import JRDEV_DIR

RESPONSES_DIR = os.path.join(JRDEV_DIR, "responses")

def ensure_responses_dir():
    """
    Ensure the 'responses' directory exists in the JrDev root directory.
    """
    if not os.path.exists(RESPONSES_DIR):
        os.makedirs(RESPONSES_DIR)

async def handle_asyncsend(app: Any, args: List[str], worker_id: str) -> None:
    """
    Handle the /asyncsend command to send a message and optionally save the response to a file.
    This command returns control to the terminal immediately while processing continues in background.

    Args:
        app: The Application instance
        args: Command arguments [filename] [prompt...]
    """

    if len(args) < 2:
        app.ui.print_text(
            "Usage: /asyncsend [filename] <prompt>", print_type=PrintType.ERROR
        )
        app.ui.print_text(
            "Example: /asyncsend How can I optimize this code?",
            print_type=PrintType.INFO,
        )
        app.ui.print_text(
            "Example with file: /asyncsend my_response.txt Tell me the design patterns in this codebase\n(Saves to responses/my_response.txt)",
            print_type=PrintType.INFO,
        )
        app.ui.print_text(
            "Note: If a filename is provided, it will be saved in the 'responses' directory under the main JrDev directory.",
            print_type=PrintType.INFO,
        )
        return

    # Generate a unique job ID
    job_id = str(uuid.uuid4())[:8]

    # Check if the first argument is a filename (not a path) or part of the prompt
    if len(args) >= 3 and not args[1].startswith("/"):
        filename = args[1]
        prompt = " ".join(args[2:])

        # Only allow a filename, not a path
        if os.path.basename(filename) != filename or os.path.dirname(filename):
            app.ui.print_text(
                "Error: Only a filename (not a path) is allowed. The file will be saved in the 'responses' directory.",
                print_type=PrintType.ERROR,
            )
            return

        # Ensure the responses directory exists
        ensure_responses_dir()
        filepath = os.path.join(RESPONSES_DIR, filename)

        app.logger.info(f"Starting async task #{job_id} to save response to {filepath}")
        app.ui.print_text(
            f"Task #{job_id} started: Saving response to {filepath}",
            print_type=PrintType.INFO,
        )

        # Create a task to process the request in the background
        async def background_task():
            # Use the currently active message thread
            msg_thread = app.get_current_thread()

            try:
                app.logger.info(
                    f"Background task #{job_id} sending message to model on message thread: {msg_thread.thread_id}"
                )
                response = await app.send_message(
                    msg_thread, prompt, writepath=filepath, print_stream=False, worker_id=worker_id
                )
                if response:
                    app.logger.info(f"Background task #{job_id} completed successfully")
                else:
                    app.logger.error(f"Background task #{job_id} failed to get response")
                # Task monitor will handle cleanup of completed tasks
            except Exception as e:
                error_msg = str(e)
                app.logger.error(
                    f"Background task #{job_id} failed with error: {error_msg} on message thread: {msg_thread.thread_id}"
                )
                # Task monitor will handle cleanup of failed tasks

        # Schedule the task but don't wait for it
        task = asyncio.create_task(background_task())
        app.state.active_tasks[job_id] = {
            "task": task,
            "type": "file_response",
            "path": filepath,
            "prompt": prompt[:30] + "..." if len(prompt) > 30 else prompt,
            "timestamp": asyncio.get_event_loop().time(),
        }
    else:
        # No filename provided, just send the message
        prompt = " ".join(args[1:])

        app.logger.info(f"Starting async task #{job_id} to process message")

        # Create a task to process the request in the background
        async def background_task():
            # Use the currently active message thread
            msg_thread = app.get_current_thread()

            try:
                app.logger.info(
                    f"Background task #{job_id} sending message to model on message thread: {msg_thread.thread_id}"
                )
                response = await app.send_message(msg_thread, prompt)
                if response:
                    app.logger.info(f"Background task #{job_id} completed successfully")
                else:
                    app.logger.error(f"Background task #{job_id} failed to get response")
                # Task monitor will handle cleanup of completed tasks
            except Exception as e:
                error_msg = str(e)
                app.logger.error(
                    f"Background task #{job_id} failed with error: {error_msg}"
                )
                # Task monitor will handle cleanup of failed tasks

        # Schedule the task but don't wait for it
        task = asyncio.create_task(background_task())
        app.state.active_tasks[job_id] = {
            "task": task,
            "type": "message",
            "prompt": prompt[:30] + "..." if len(prompt) > 30 else prompt,
            "timestamp": asyncio.get_event_loop().time(),
        }
