import json
import asyncio
from telethon import TelegramClient

async def main():
    # Load config
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found.")
        return

    api_id = config.get("telegram_api_id")
    api_hash = config.get("telegram_api_hash")
    
    if not api_id or not api_hash:
        print("Error: telegram_api_id or telegram_api_hash missing in config.")
        return

    print(f"Connecting with API ID: {api_id}...")
    
    # Use the same session name 'CSB' to reuse the existing session file
    client = TelegramClient("CSB", api_id, api_hash)
    
    await client.connect()
    
    if not await client.is_user_authorized():
        print("Client is NOT authorized. You might need to run the main app to login interactively first.")
        # We don't want to trigger interactive login here effectively as it might hang if run in background
        return

    print("Client authorized successfully.")

    # 1. List some dialogs to check visibility
    print("\n--- Listing first 10 Dialogs ---")
    dialogs = await client.get_dialogs(limit=10)
    for d in dialogs:
        print(f"Name: {d.name}, ID: {d.id}, Is Channel: {d.is_channel}, Is Group: {d.is_group}")

    # 2. Try fetching from configured chats
    chats = config.get("chats_to_summarize", [])
    print(f"\n--- Testing Configured Chats ({len(chats)}) ---")
    
    for chat_cfg in chats:
        chat_id = chat_cfg.get("id")
        print(f"\nAsking for Chat ID: {chat_id}")
        
        try:
            print(f"Resolving entity for: '{chat_id}' (Type: {type(chat_id)})")
            
            # Try to get entity
            entity = await client.get_entity(chat_id)
            
            # Inspect what we got
            print(f"  Resolved to Type: {type(entity)}")
            print(f"  ID: {entity.id}")
            
            title = getattr(entity, 'title', None)
            if not title:
                # Fallback for users
                username = getattr(entity, 'username', '')
                first = getattr(entity, 'first_name', '')
                last = getattr(entity, 'last_name', '')
                title = f"User: {first} {last} (@{username})"
            
            print(f"  Title/Name: {title}")
            
            # Try fetching history
            print(f"  Fetching last 5 messages from {entity.id}...")
            messages = await client.get_messages(entity, limit=5)
            print(f"  Fetched {len(messages)} messages:")
            for msg in messages:
                content = msg.text[:50].replace('\n', ' ') if msg.text else "[Non-text]"
                date = msg.date
                sender = await msg.get_sender()
                sender_name = "Unknown"
                if sender:
                     sender_name = getattr(sender, 'first_name', '') or getattr(sender, 'title', 'Unknown')
                
                print(f"    [{date}] {sender_name}: {content}...")

        except Exception as e:
            print(f"FAILED to access chat {chat_id}: {e}")
            import traceback
            traceback.print_exc()

    # 3. Try to match config name 'Hills' to the ID found in dialogs manually
    print("\n--- Manual ID Lookup Test ---")
    target_name = "交易群 Ver.20251006"
    found_id = "-1003195054812"
    for d in dialogs:
        if d.name == target_name:
            found_id = d.id
            break
    
    if found_id:
        print(f"Found '{target_name}' in dialogs with ID: {found_id}. Trying to fetch using THIS ID...")
        try:
             entity = await client.get_entity(found_id)
             messages = await client.get_messages(entity, limit=5)
             print(f"  SUCCESS! Fetched {len(messages)} messages using ID {found_id}.")
             for msg in messages:
                 print(f"    [{msg.date}] {msg.sender.first_name}: {msg.text}")
        except Exception as e:
             print(f"  Failed with ID {found_id}: {e}")
    else:
        print(f"Could not find '{target_name}' in dialog list.")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
