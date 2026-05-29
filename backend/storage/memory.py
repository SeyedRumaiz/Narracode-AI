memory_store = {}

def save_memory(session_id: str, data: dict):
    if session_id not in memory_store:
        memory_store[session_id] = []
    memory_store[session_id].append(data)


def get_memory(session_id: str):
    return memory_store.get(session_id, [])
