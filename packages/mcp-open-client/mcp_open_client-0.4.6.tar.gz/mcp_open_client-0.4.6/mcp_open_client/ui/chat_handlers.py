import uuid
import json
from typing import Optional, List, Dict, Any
from nicegui import ui, app
from .message_parser import parse_and_render_message
from .history_manager import history_manager
import asyncio
import json

# Global variables
current_conversation_id: Optional[str] = None
stats_update_callback: Optional[callable] = None

def get_conversation_storage() -> Dict[str, Any]:
    """Get or initialize conversation storage"""
    if 'conversations' not in app.storage.user:
        app.storage.user['conversations'] = {}
    return app.storage.user['conversations']

def create_new_conversation() -> str:
    """Create a new conversation and return its ID"""
    global current_conversation_id
    conversation_id = str(uuid.uuid4())
    conversations = get_conversation_storage()
    conversations[conversation_id] = {
        'id': conversation_id,
        'title': f'Conversation {len(conversations) + 1}',
        'messages': [],
        'created_at': str(uuid.uuid1().time),
        'updated_at': str(uuid.uuid1().time)
    }
    current_conversation_id = conversation_id
    app.storage.user['conversations'] = conversations
    return conversation_id

def load_conversation(conversation_id: str) -> None:
    """Load a specific conversation"""
    global current_conversation_id
    conversations = get_conversation_storage()
    if conversation_id in conversations:
        current_conversation_id = conversation_id
        # Update stats when conversation changes
        if stats_update_callback:
            stats_update_callback()

def get_current_conversation_id() -> Optional[str]:
    """Get the current conversation ID"""
    return current_conversation_id

def set_stats_update_callback(callback: callable) -> None:
    """Set the callback function to update stats"""
    global stats_update_callback
    stats_update_callback = callback

def get_messages() -> List[Dict[str, Any]]:
    """Get messages from current conversation"""
    if not current_conversation_id:
        return []
    
    conversations = get_conversation_storage()
    if current_conversation_id in conversations:
        return conversations[current_conversation_id]['messages'].copy()
    return []

def add_message(role: str, content: str, tool_calls: Optional[List[Dict[str, Any]]] = None, tool_call_id: Optional[str] = None) -> None:
    """Add a message to the current conversation"""
    if not current_conversation_id:
        create_new_conversation()
    
    conversations = get_conversation_storage()
    if current_conversation_id in conversations:
        message = {
            'role': role,
            'content': content,
            'timestamp': str(uuid.uuid1().time)
        }
        
        # Add tool calls if present (for assistant messages)
        if tool_calls:
            message['tool_calls'] = tool_calls
            
        # Add tool call ID if present (for tool messages)
        if tool_call_id:
            message['tool_call_id'] = tool_call_id
        
        # Process message through history manager for size limits
        processed_message = history_manager.process_message_for_storage(message)
        print(f"Message processed: original size: {len(json.dumps(message))}, processed size: {len(json.dumps(processed_message))}")
        
        conversations[current_conversation_id]['messages'].append(processed_message)
        conversations[current_conversation_id]['updated_at'] = str(uuid.uuid1().time)
        app.storage.user['conversations'] = conversations
        
        # Log conversation size
        conv_size = history_manager.get_conversation_size(current_conversation_id)
        print(f"Conversation {current_conversation_id} size: {conv_size['total_tokens']} tokens ({conv_size['total_chars']} chars), {conv_size['message_count']} messages")
        
        # Check if conversation or total history needs cleanup
        if history_manager.settings['auto_cleanup']:
            # Cleanup conversation if needed
            conv_cleanup = history_manager.cleanup_conversation_if_needed(current_conversation_id)
            if conv_cleanup:
                print(f"Conversation cleanup performed for {current_conversation_id}")
            
            # Note: Global history cleanup disabled - only per-conversation limits apply
        
        # Update stats in UI if callback is set
        if stats_update_callback:
            stats_update_callback()

def find_tool_response(tool_call_id: str) -> Optional[str]:
    """Find the tool response for a given tool call ID"""
    messages = get_messages()
    for msg in messages:
        if (msg.get('role') == 'tool' and 
            msg.get('tool_call_id') == tool_call_id):
            return msg.get('content', '')
    return None

def render_message_to_ui(message: dict, message_container) -> None:
    """Render a single message to the UI"""
    role = message.get('role', 'user')
    content = message.get('content', '')
    tool_calls = message.get('tool_calls', [])
    tool_call_id = message.get('tool_call_id')
    was_truncated = message.get('_truncated', False)
    original_length = message.get('_original_length', 0)
    
    with message_container:
        if role == 'user':
            with ui.card().classes('user-message message-bubble ml-auto mb-4 max-w-4xl bg-blue-900/20 border-l-4 border-blue-400') as user_card:
                ui.label('You:').classes('font-bold text-blue-300')
                parse_and_render_message(content, user_card)
                
                # Show truncation notice if message was truncated
                if was_truncated:
                    ui.label(f'⚠️ Message truncated (original: {original_length:,} chars)').classes('text-xs text-yellow-400 mt-2 italic')
        elif role == 'assistant':
            with ui.card().classes('assistant-message message-bubble mb-4 max-w-5xl bg-gray-800/30 border-l-4 border-gray-500') as bot_card:
                ui.label('Assistant:').classes('font-bold text-gray-300')
                if content:
                    parse_and_render_message(content, bot_card)
                
                # Show truncation notice if message was truncated
                if was_truncated:
                    ui.label(f'⚠️ Message truncated (original: {original_length:,} chars)').classes('text-xs text-yellow-400 mt-2 italic')
                
                # Show tool calls if present
                if tool_calls:
                    ui.separator().classes('my-2')
                    for i, tool_call in enumerate(tool_calls):
                        function_info = tool_call.get('function', {})
                        tool_name = function_info.get('name', 'unknown')
                        tool_args = function_info.get('arguments', '{}')
                        
                        # Find corresponding tool response
                        tool_call_id = tool_call.get('id')
                        tool_response = find_tool_response(tool_call_id) if tool_call_id else None
                        
                        with ui.expansion(f"{tool_name}",
                                        icon=None,
                                        value=False).classes('w-full max-w-full border-l-4 border-blue-400 mb-2 overflow-hidden text-sm').props('dense header-class="text-sm font-normal"'):
                            # Tool Call Section
                            ui.label('Call:').classes('font-semibold text-blue-300 mt-1')
                            ui.code(tool_name, language='text').classes('w-full overflow-x-auto')
                            ui.label('Arguments:').classes('font-semibold text-blue-300')
                            try:
                                # Try to format JSON arguments nicely
                                formatted_args = json.dumps(json.loads(tool_args), indent=2)
                                ui.code(formatted_args, language='json').classes('w-full overflow-x-auto')
                            except:
                                ui.code(tool_args, language='json').classes('w-full overflow-x-auto')
                            
                            # Tool Response Section (if available)
                            if tool_response:
                                ui.separator().classes('my-3')
                                ui.label('Response:').classes('font-semibold text-emerald-300')
                                # Use HTML with strict width control to prevent horizontal expansion
                                import html
                                escaped_response = html.escape(tool_response)
                                ui.html(f'''<div style="width: 100%; max-width: 100%; overflow: hidden; box-sizing: border-box;">
                                    <pre style="white-space: pre-wrap; word-wrap: break-word; overflow-wrap: anywhere; width: 100%; max-width: 100%; margin: 0; padding: 0.5rem; background: transparent; font-family: monospace; font-size: 0.875rem; overflow: hidden; box-sizing: border-box;">{escaped_response}</pre>
                                </div>''')
        elif role == 'tool':
            # Skip individual tool messages - they're now grouped with assistant messages
            pass

def save_current_conversation() -> None:
    """Save current conversation to storage"""
    # This is automatically handled by NiceGUI's storage system
    pass

def clear_messages() -> None:
    """Clear messages from current conversation"""
    if not current_conversation_id:
        return
    
    conversations = get_conversation_storage()
    if current_conversation_id in conversations:
        conversations[current_conversation_id]['messages'] = []
        conversations[current_conversation_id]['updated_at'] = str(uuid.uuid1().time)
        app.storage.user['conversations'] = conversations

def get_all_conversations() -> Dict[str, Any]:
    """Get all conversations"""
    return get_conversation_storage()

def delete_conversation(conversation_id: str) -> None:
    """Delete a conversation"""
    global current_conversation_id
    conversations = get_conversation_storage()
    if conversation_id in conversations:
        del conversations[conversation_id]
        app.storage.user['conversations'] = conversations
        
        # If we deleted the current conversation, clear the current ID
        if current_conversation_id == conversation_id:
            current_conversation_id = None

# Global variable to track scroll debouncing
_scroll_timer = None

async def safe_scroll_to_bottom(scroll_area, delay=0.2):
    """Safely scroll to bottom with error handling and improved timing"""
    global _scroll_timer
    
    try:
        # Cancel any existing scroll timer to debounce multiple calls
        if _scroll_timer is not None:
            _scroll_timer.cancel()
        
        # Create a new timer with the specified delay
        def do_scroll():
            try:
                scroll_area.scroll_to(percent=1.0)
            except Exception as e:
                print(f"Scroll error (non-critical): {e}")
        
        # Use ui.timer for better DOM synchronization
        _scroll_timer = ui.timer(delay, do_scroll, once=True)
        
    except Exception as e:
        print(f"Scroll setup error (non-critical): {e}")

def render_tool_call_and_result(chat_container, tool_call, tool_result):
    """Render tool call and result in the UI"""
    with chat_container:
        with ui.card().classes('w-full max-w-full mb-2 bg-yellow-100 overflow-hidden'):
            with ui.element('div').classes('w-full max-w-full overflow-hidden p-2'):
                ui.label('Tool Call:').classes('font-bold')
                ui.markdown(f"**Name:** {tool_call['function']['name']}")
                ui.code(tool_call['function']['arguments'], language='json').classes('w-full max-w-full overflow-x-auto')
        
        with ui.card().classes('w-full max-w-full mb-2 bg-green-100 overflow-hidden'):
            with ui.element('div').classes('w-full max-w-full overflow-hidden p-2'):
                ui.label('Tool Result:').classes('font-bold')
                ui.code(json.dumps(tool_result, indent=2), language='json').classes('w-full max-w-full overflow-x-auto')

async def send_message_to_mcp(message: str, server_name: str, chat_container, message_input):
    """Send message to MCP server and handle response"""
    from mcp_open_client.mcp_client import mcp_client_manager
    
    # Add user message to conversation
    add_message('user', message)
    
    # Clear input
    message_input.value = ''
    
    try:
        # Show spinner while waiting for response
        with chat_container:
            with ui.row().classes('w-full justify-start mb-2'):
                spinner_card = ui.card().classes('bg-gray-200 p-2')
                with spinner_card:
                    ui.spinner('dots', size='md')
                    ui.label('Thinking...')
        
        # Get available tools and resources
        tools = await mcp_client_manager.list_tools()
        resources = await mcp_client_manager.list_resources()
        
        # Prepare the context for the LLM
        context = {
            "message": message,
            "tools": tools,
            "resources": resources
        }
        
        # Send the context to the LLM
        try:
            llm_response = await mcp_client_manager.generate_response(context)
            
            # Check if the LLM response contains tool calls
            if isinstance(llm_response, dict) and 'tool_calls' in llm_response:
                for tool_call in llm_response['tool_calls']:
                    tool_name = tool_call['function']['name']
                    tool_args = json.loads(tool_call['function']['arguments'])
                    
                    # Execute the tool call
                    tool_result = await mcp_client_manager.call_tool(tool_name, tool_args)
                    
                    # Add tool call to conversation
                    add_message('assistant', f"Calling tool: {tool_name}", tool_calls=[tool_call])
                    
                    # Add tool result to conversation
                    add_message('tool', json.dumps(tool_result, indent=2), tool_call_id=tool_call['id'])
                    
                    # Render tool call and result in UI
                    render_tool_call_and_result(chat_container, tool_call, tool_result)
                
                # Add final assistant response to conversation
                if 'content' in llm_response:
                    add_message('assistant', llm_response['content'])
                    with chat_container:
                        ui.markdown(f"**AI:** {llm_response['content']}").classes('bg-blue-100 p-2 rounded-lg mb-2 max-w-full overflow-wrap-anywhere')
            else:
                # Add assistant response to conversation
                add_message('assistant', llm_response)
                with chat_container:
                    ui.markdown(f"**AI:** {llm_response}").classes('bg-blue-100 p-2 rounded-lg mb-2 max-w-full overflow-wrap-anywhere')
        except Exception as llm_error:
            error_message = f'Error generating LLM response: {str(llm_error)}'
            add_message('assistant', error_message)
            with chat_container:
                ui.markdown(f"**Error:** {error_message}").classes('bg-red-100 p-2 rounded-lg mb-2 max-w-full overflow-wrap-anywhere')
        
        # Remove spinner
        spinner_card.delete()
        
        # Scroll to bottom after adding new content
        await safe_scroll_to_bottom(chat_container)
        
    except Exception as e:
        print(f"Error in send_message_to_mcp: {e}")
        # Remove spinner if error occurs
        if 'spinner_card' in locals():
            spinner_card.delete()
        
        error_message = f'Error communicating with MCP server: {str(e)}'
        add_message('assistant', error_message)

async def handle_send(input_field, message_container, api_client, scroll_area):
    """Handle sending a message asynchronously"""
    if input_field.value and input_field.value.strip():
        message = input_field.value.strip()
        
        # Ensure we have a current conversation
        if not get_current_conversation_id():
            create_new_conversation()
        
        # Add user message to conversation storage
        add_message('user', message)
        
        # Clear input
        input_field.value = ''
        
        # Re-render all messages to show the new user message
        message_container.clear()
        from .chat_interface import render_messages
        render_messages(message_container)
        
        # Auto-scroll to bottom after adding user message
        await safe_scroll_to_bottom(scroll_area, delay=0.15)
        
        # Send message to API and get response
        try:
            # Show spinner while waiting for response
            with message_container:
                spinner = ui.spinner('dots', size='lg')
            # No need to scroll here, spinner is small
            
            # Get full conversation history for context
            conversation_messages = get_messages()
            
            # Convert to API format
            api_messages = []
            for msg in conversation_messages:
                api_msg = {
                    "role": msg["role"],
                    "content": msg["content"]
                }
                
                # Include tool_calls for assistant messages
                if msg["role"] == "assistant" and "tool_calls" in msg:
                    api_msg["tool_calls"] = msg["tool_calls"]
                
                # Include tool_call_id for tool messages
                if msg["role"] == "tool" and "tool_call_id" in msg:
                    api_msg["tool_call_id"] = msg["tool_call_id"]
                
                api_messages.append(api_msg)
            
            # Get available MCP tools for tool calling
            from .handle_tool_call import get_available_tools, is_tool_call_response, extract_tool_calls, handle_tool_call
            available_tools = await get_available_tools()
            
            # Call LLM with tools if available
            if available_tools:
                response = await api_client.chat_completion(api_messages, tools=available_tools)
            else:
                response = await api_client.chat_completion(api_messages)
            
            # Check if response contains tool calls
            if is_tool_call_response(response):
                # Handle tool calls
                tool_calls = extract_tool_calls(response)
                
                # Add the assistant message with tool calls to conversation
                assistant_message = response['choices'][0]['message']
                add_message('assistant', assistant_message.get('content', ''), tool_calls=assistant_message.get('tool_calls'))
                
                # Update UI immediately after adding assistant message with tool calls
                message_container.clear()
                from .chat_interface import render_messages
                render_messages(message_container)
                await safe_scroll_to_bottom(scroll_area, delay=0.1)
                
                # Process each tool call
                tool_results = []
                for tool_call in tool_calls:
                    tool_result = await handle_tool_call(tool_call)
                    tool_results.append(tool_result)
                    
                    # Add tool result to conversation storage
                    add_message('tool', tool_result['content'], tool_call_id=tool_result['tool_call_id'])
                    
                    # Update UI immediately after each tool result
                    message_container.clear()
                    render_messages(message_container)
                    await safe_scroll_to_bottom(scroll_area, delay=0.1)
                
                # Update API messages with assistant message including tool calls
                api_messages.append({
                    "role": "assistant",
                    "content": assistant_message.get('content'),
                    "tool_calls": assistant_message.get('tool_calls')
                })
                
                # Add tool results to API messages
                for tool_result in tool_results:
                    api_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_result['tool_call_id'],
                        "content": tool_result['content']
                    })
                
                # Continue processing until no more tool calls
                while True:
                    final_response = await api_client.chat_completion(api_messages, tools=available_tools)
                    
                    # Check if this response also has tool calls
                    if is_tool_call_response(final_response):
                        # Process additional tool calls
                        additional_tool_calls = extract_tool_calls(final_response)
                        
                        # Add the assistant message with tool calls
                        assistant_message = final_response['choices'][0]['message']
                        add_message('assistant', assistant_message.get('content', ''), tool_calls=assistant_message.get('tool_calls'))
                        
                        # Update UI immediately after adding assistant message with tool calls
                        message_container.clear()
                        from .chat_interface import render_messages
                        render_messages(message_container)
                        await safe_scroll_to_bottom(scroll_area, delay=0.1)
                        
                        # Update API messages
                        api_messages.append({
                            "role": "assistant",
                            "content": assistant_message.get('content'),
                            "tool_calls": assistant_message.get('tool_calls')
                        })
                        
                        # Process each additional tool call
                        additional_tool_results = []
                        for tool_call in additional_tool_calls:
                            tool_result = await handle_tool_call(tool_call)
                            additional_tool_results.append(tool_result)
                            
                            # Add tool result to conversation storage
                            add_message('tool', tool_result['content'], tool_call_id=tool_result['tool_call_id'])
                            
                            # Update UI immediately after each tool result
                            message_container.clear()
                            render_messages(message_container)
                            await safe_scroll_to_bottom(scroll_area, delay=0.1)
                        
                        # Add tool results to API messages
                        for tool_result in additional_tool_results:
                            api_messages.append({
                                "role": "tool",
                                "tool_call_id": tool_result['tool_call_id'],
                                "content": tool_result['content']
                            })
                        
                        # Continue the loop to get next response
                        continue
                    else:
                        # No more tool calls, this is the final text response
                        bot_response = final_response['choices'][0]['message']['content']
                        add_message('assistant', bot_response)
                        break
                
            else:
                # Regular response without tool calls
                bot_response = response['choices'][0]['message']['content']
                
                # Add assistant response to conversation storage
                add_message('assistant', bot_response)
            
            # Remove spinner safely
            try:
                if spinner and hasattr(spinner, 'parent_slot') and spinner.parent_slot:
                    spinner.delete()
            except (ValueError, AttributeError):
                # Spinner already removed or doesn't exist
                pass
            
            # Re-render all messages (this will show everything including tool calls and responses)
            message_container.clear()
            from .chat_interface import render_messages
            render_messages(message_container)
            
            # Refresh conversation manager to update sidebar
            from .conversation_manager import conversation_manager
            conversation_manager.refresh_conversations_list()
            
            # Auto-scroll to bottom after adding bot response (longer delay for complex rendering)
            await safe_scroll_to_bottom(scroll_area, delay=0.25)
            
        except Exception as e:
            # Remove spinner if error occurs
            try:
                if 'spinner' in locals() and spinner and hasattr(spinner, 'parent_slot') and spinner.parent_slot:
                    spinner.delete()
            except (ValueError, AttributeError):
                # Spinner already removed or doesn't exist
                pass
            
            # Add error message to conversation storage
            error_message = f'Error: {str(e)}'
            add_message('assistant', error_message)
            
            # Add error message to UI
            with message_container:
                with ui.card().classes('mr-auto ml-4 max-w-md') as error_card:
                    ui.label('System:').classes('font-bold mb-2 text-red-600')
                    parse_and_render_message(error_message, error_card)
            
            # Refresh conversation manager to update sidebar
            from .conversation_manager import conversation_manager
            conversation_manager.refresh_conversations_list()
            
            # Auto-scroll to bottom after error message
            await safe_scroll_to_bottom(scroll_area, delay=0.2)
    else:
        # we'll just ignore
        pass