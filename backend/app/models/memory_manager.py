"""
Memory manager using LangChain ConversationBufferMemory.

This provides a per-session short-term memory (MVP). Memory is kept in-process
and will be forgotten when cleared or when the process restarts. The Chrome
extension can provide a `session_id` to keep memory across requests within the
same extension session. If no session_id is provided, memory is transient.

Uses LangChain's ConversationBufferMemory to avoid custom memory logic.
"""
from typing import Optional
import os
import time
from threading import Lock
import logging

logger = logging.getLogger(__name__)

# Record which ConversationBufferMemory implementation we use
MEMORY_IMPL = None

# ConversationBufferMemory moved between langchain versions; try common locations
try:
    from langchain.memory import ConversationBufferMemory
    MEMORY_IMPL = 'langchain.memory'
except Exception:
    try:
        from langchain.memory.buffer import ConversationBufferMemory
        MEMORY_IMPL = 'langchain.memory.buffer'
    except Exception:
        try:
            from langchain.memory.buffer_memory import ConversationBufferMemory
            MEMORY_IMPL = 'langchain.memory.buffer_memory'
        except Exception:
            # Couldn't import LangChain's ConversationBufferMemory.
            # Provide a minimal fallback that mimics the parts of the
            # ConversationBufferMemory API we use (load_memory_variables, save_context).
            class ConversationBufferMemory:
                def __init__(self, memory_key: str = "history", return_messages: bool = False):
                    self.memory_key = memory_key
                    self.return_messages = return_messages
                    self._history_lines = []

                def load_memory_variables(self, inputs: dict) -> dict:
                    # Return a dict with the memory_key pointing to the concatenated history
                    return {self.memory_key: "\n".join(self._history_lines)}

                def save_context(self, inputs: dict, outputs: dict) -> None:
                    # Expect inputs contains a user text under some key like 'input'
                    user_text = inputs.get('input') or inputs.get('question') or str(inputs)
                    assistant_text = outputs.get('output') or outputs.get('response') or str(outputs)
                    if user_text:
                        self._history_lines.append(f"User: {user_text}")
                    if assistant_text:
                        self._history_lines.append(f"Assistant: {assistant_text}")

                def clear(self):
                    self._history_lines = []

    # Log which implementation is active
    if MEMORY_IMPL:
        logger.info(f"Memory implementation loaded: {MEMORY_IMPL}")
    else:
        logger.info("Memory implementation: fallback (simple in-process) is active")

# TTL for idle memories (seconds). Default: 1 hour. Set to 0 to disable expiry.
MEMORY_TTL_SECONDS = int(os.getenv('MEMORY_TTL_SECONDS', '3600'))


class MemoryEntry:
    def __init__(self, memory: ConversationBufferMemory):
        self.memory = memory
        self.last_access = time.time()

    def touch(self):
        self.last_access = time.time()


class MemoryManager:
    """Simple in-process memory manager keyed by session_id.

    NOTE: This is an MVP implementation that uses LangChain's memory object.
    It intentionally keeps data in-process to respect privacy and simplicity.
    """

    def __init__(self):
        self._store = {}  # session_id -> MemoryEntry
        self._lock = Lock()

    def get_memory(self, session_id: Optional[str]) -> ConversationBufferMemory:
        """Return a ConversationBufferMemory for the session_id.

        If session_id is None, returns a transient (new) memory that is not
        stored globally.
        """
        if not session_id:
            # transient memory (not persisted in store)
            return ConversationBufferMemory(memory_key="history", return_messages=False)

        with self._lock:
            entry = self._store.get(session_id)
            if entry:
                entry.touch()
                return entry.memory

            # create new memory and store
            mem = ConversationBufferMemory(memory_key="history", return_messages=False)
            self._store[session_id] = MemoryEntry(mem)
            return mem

    def clear_memory(self, session_id: str) -> bool:
        """Clear and remove memory for a session_id. Returns True if removed."""
        with self._lock:
            if session_id in self._store:
                del self._store[session_id]
                return True
            return False

    def cleanup_expired(self):
        """Remove entries not accessed within TTL.

        Call periodically if desired. For MVP we don't spawn a background
        thread automatically; caller may invoke this method.
        """
        if MEMORY_TTL_SECONDS <= 0:
            return
        now = time.time()
        with self._lock:
            to_delete = [sid for sid, e in self._store.items() if now - e.last_access > MEMORY_TTL_SECONDS]
            for sid in to_delete:
                del self._store[sid]


# single global manager instance to be imported where needed
manager = MemoryManager()
