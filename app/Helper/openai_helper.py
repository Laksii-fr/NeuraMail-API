from openai import OpenAI
import app.models.model_types as model_type
import app.utils.mongo_utils as mongo
import asyncio
import time
import os

client = OpenAI()
# Create a new thread
def create_thread():
    print("Executed 1.1: Starting thread creation...")
    thread = client.beta.threads.create()
    print(f"Executed 1.2: Thread created with ID: {thread.id}")
    return thread

# Asynchronous method to handle multiple chat instances
async def create_new_chat(chats: list[model_type.AssistantChat]):
    print(f"Executed 2.1: Starting process for {len(chats)} chats...")
    tasks = [create_chat(chat) for chat in chats]  # Create tasks for each chat
    print(f"Executed 2.2: Created {len(tasks)} chat tasks, awaiting completion...")
    all_results = await asyncio.gather(*tasks)  # Wait for all tasks to finish
    print("Executed 2.3: All chat tasks completed. Results below:")
    print(all_results)
    return all_results

# Asynchronous method to handle a single chat instance
async def create_chat(chat: model_type.AssistantChat):
    print(f"Executed 2.2.1: Starting chat for thread ID: {chat.threadId}")
    response = await create_assistant_chat(chat)  # Await response
    print(f"Executed 2.2.2: Processing completed for chat with thread ID: {chat.threadId}")
    return response

# Asynchronous method for creating an assistant chat
async def create_assistant_chat(chat: model_type.AssistantChat):
    print(f"Executed 2.2.2.1: Creating a run for thread ID: {chat.threadId}")
    run = create_run(chat)  # Create a run
    print(f"Executed 2.2.2.2: Run created, awaiting run completion...")
    run = await wait_on_run(run, chat.threadId)  # Wait for run to finish
    print(f"Executed 2.2.2.3: Run completed for thread ID: {chat.threadId}, fetching response...")
    response = await get_response(chat.threadId)  # Get the response
    prettified_response = prettify_single_response(response)
    print(f"Executed 2.2.2.4: Response received and processed for thread ID: {chat.threadId}")
    return prettified_response

# Submitting a message and creating a run
def create_run(chat: model_type.AssistantChat):
    print(f"Executed 2.2.2.1.1: Submitting message to thread ID: {chat.threadId}")
    submit_message(chat)  # Submit the message
    run = client.beta.threads.runs.create(  # Create the run
        thread_id=chat.threadId,
        assistant_id=chat.astId,
    )
    print(f"Executed 2.2.2.1.2: Run created with ID: {run.id} for thread ID: {chat.threadId}")
    return run

# Submitting a message to the thread
def submit_message(chat: model_type.AssistantChat):
    print(f"Executed 2.2.2.1.1.1: Sending message to thread ID: {chat.threadId}: {chat.message}")
    client.beta.threads.messages.create(
        thread_id=chat.threadId,
        role="user",
        content=chat.message,
    )
    print(f"Executed 2.2.2.1.1.2: Message submitted to thread ID: {chat.threadId}")

# Wait for the run to finish
async def wait_on_run(run, thread_id):
    print(f"Executed 2.2.2.2.1: Waiting for run {run.id} to complete for thread ID: {thread_id}...")
    while run.status in ["queued", "in_progress"]:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id,
        )
        print(f"Executed 2.2.2.2.2: Run {run.id} status: {run.status}")
        await asyncio.sleep(0.5)  # Async sleep to avoid blocking the loop
    print(f"Executed 2.2.2.2.3: Run {run.id} completed with status: {run.status}")
    return run

# Asynchronously get the response from the thread
async def get_response(thread_id: str):
    print(f"Executed 2.2.2.3.1: Fetching response for thread ID: {thread_id}...")
    response = client.beta.threads.messages.list(thread_id=thread_id, order="asc")
    print(f"Executed 2.2.2.3.2: Response fetched for thread ID: {thread_id}")
    return response

# Prettify the response
def prettify_single_response(response):
    print("\n\nExecuted 2.2.2.4.1: Prettifying response...\n\n", response)
    
    # Access the last message from the data list of the response
    last_message = response.data[-1]
    
    prettified = {
        "id": last_message.id,
        "role": last_message.role,
        "message": last_message.content[0].text.value,
        "thread_id": last_message.thread_id,
        "created_at": last_message.created_at
    }
    print(f"Executed 2.2.2.4.2: Prettified response: {prettified}")
    return prettified


def create_assistant(prompt):
    assistant = client.beta.assistants.create(
        name="Assistant",
        instructions=prompt,
        model="gpt-4o-mini",
    )
    print(f"Assistant created with ID: {assistant.id}")
    return assistant
