from server import active_writers, players  # Import dinamico

def send_chat(sender_id, message):
    for pid, writer in active_writers.items():
        if pid != sender_id:
            writer.write(f"[{sender_id}] {message}\n".encode())

def send_room_chat(sender_id, message):
    level = players[sender_id]["level"]
    for pid, writer in active_writers.items():
        if pid != sender_id and players.get(pid, {}).get("level") == level:
            writer.write(f"[Stanza {level}] {sender_id}: {message}\n".encode())
