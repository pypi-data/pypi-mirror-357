import os
import threading
import multiprocessing
import pickle
import zlib
import logging
import time
from collections import deque
from typing import Optional, List
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from base64 import urlsafe_b64encode

logger = logging.getLogger("UltraQueue")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Try to load shared C lib
try:
    from ctypes import cdll, c_char_p, c_int, create_string_buffer
    LIB = cdll.LoadLibrary("./raw/ultraqueue.dll")  # or .dll on Windows
    HAS_C_LIB = True
except Exception:
    LIB = None
    HAS_C_LIB = False
    # We won't log here by default, logging controlled by flag

class UltraQueueError(Exception):
    pass

class UltraQueue:
    def __init__(
        self,
        save_path: Optional[str] = None,
        max_mem_items: int = 100_000,
        encryption_key: Optional[bytes | str] = None,  # Accept bytes or str now
        auto_persist_interval: int = 10,
        use_ultraqueue: bool = False,
        logging_enabled: bool = False,
    ):
        self.use_ultraqueue = use_ultraqueue and HAS_C_LIB
        self.save_path = save_path
        self.max_mem_items = max_mem_items
        self.encryption_key = encryption_key
        self.auto_persist_interval = auto_persist_interval
        self._stop_event = threading.Event()
        self._lock = multiprocessing.Lock()
        self.logging_enabled = logging_enabled

        # Key derivation helper
        def _derive_fernet_key(password: str, salt: bytes = b"ultraqueue-salt") -> bytes:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100_000,
            )
            return urlsafe_b64encode(kdf.derive(password.encode()))

        # Handle encryption_key input
        if isinstance(encryption_key, str):
            derived_key = _derive_fernet_key(encryption_key)
            self._fernet = Fernet(derived_key)
        elif isinstance(encryption_key, bytes):
            self._fernet = Fernet(encryption_key)
        else:
            self._fernet = None

        if self.use_ultraqueue:
            if self.save_path:
                LIB.initialize_queue_lock()
        else:
            self.queue = deque()

        if self.save_path and not self.use_ultraqueue and os.path.exists(self.save_path):
            try:
                self._load_from_disk()
            except Exception as e:
                self._log("error", f"Failed to load persisted queue: {e}")

        if self.save_path and not self.use_ultraqueue:
            self._persistence_thread = threading.Thread(target=self._auto_persist_worker, daemon=True)
            self._persistence_thread.start()

    def _log(self, level: str, msg: str):
        if not self.logging_enabled:
            return
        if level == "info":
            logger.info(msg)
        elif level == "warning":
            logger.warning(msg)
        elif level == "error":
            logger.error(msg)

    def push(self, item: str) -> None:
        if not isinstance(item, str):
            raise ValueError("Only strings are supported")
        if self.use_ultraqueue:
            res = LIB.ultraqueue_push(c_char_p(self.save_path.encode()), c_char_p(item.encode()))
            if res != 0:
                raise UltraQueueError("Failed to push item to C queue")
        else:
            with self._lock:
                self.queue.append(item)

    def pop(self) -> Optional[str]:
        if self.use_ultraqueue:
            buf = create_string_buffer(4096)
            res = LIB.ultraqueue_pop(c_char_p(self.save_path.encode()), buf, c_int(4096))
            return buf.value.decode() if res == 0 else None
        else:
            with self._lock:
                return self.queue.popleft() if self.queue else None

    def push_batch(self, items: List[str]) -> None:
        for item in items:
            self.push(item)

    def pop_batch(self, n: int) -> List[str]:
        return [self.pop() for _ in range(n) if self.length() > 0]

    def length(self) -> int:
        if self.use_ultraqueue:
            return LIB.ultraqueue_len(c_char_p(self.save_path.encode()))
        with self._lock:
            return len(self.queue)

    def save(self, path: Optional[str] = None, encryption_key: Optional[bytes] = None):
        if self.use_ultraqueue:
            self._log("info", "C backend handles persistence automatically.")
            return

        final_path = path or self.save_path
        if final_path is None:
            self._log("warning", "Save skipped: no save_path provided.")
            return

        self._save_to_path(final_path, Fernet(encryption_key) if encryption_key else self._fernet)

    def _save_to_path(self, path: str, fernet: Optional[Fernet]):
        with self._lock:
            try:
                data = pickle.dumps(list(self.queue))
                compressed = zlib.compress(data)
                to_write = fernet.encrypt(compressed) if fernet else compressed
                with open(path, 'wb') as f:
                    f.write(to_write)
                self._log("info", f"Queue saved to {path} with {len(self.queue)} items.")
            except Exception as e:
                self._log("error", f"Failed to save queue: {e}")

    def _load_from_disk(self):
        with self._lock:
            try:
                with open(self.save_path, 'rb') as f:
                    data = f.read()
                    if self._fernet:
                        try:
                            data = self._fernet.decrypt(data)
                        except Exception as e:
                            raise UltraQueueError(
                                "Failed to decrypt data: possibly wrong encryption key."
                            ) from e

                    try:
                        decompressed = zlib.decompress(data)
                        items = pickle.loads(decompressed)
                    except Exception as e:
                        raise UltraQueueError(
                            "Failed to decompress or unpickle data: data corrupted or key wrong."
                        ) from e

                    self.queue = deque(items)
                    self._log("info", f"Queue loaded with {len(self.queue)} items.")
            except UltraQueueError:
                raise  # propagate explicitly
            except Exception as e:
                # General file errors or unexpected
                self._log("error", f"Failed to load persisted queue: {e}")
                raise UltraQueueError("Failed to load persisted queue.") from e



    def _auto_persist_worker(self):
        while not self._stop_event.is_set():
            time.sleep(self.auto_persist_interval)
            self._persist_to_disk()

    def _persist_to_disk(self):
        if self.save_path:
            self._save_to_path(self.save_path, self._fernet)

    def stop(self):
        self._stop_event.set()
        if hasattr(self, "_persistence_thread"):
            self._persistence_thread.join(timeout=5)
        if not self.use_ultraqueue and self.save_path:
            self._persist_to_disk()
        self._log("info", "UltraQueue stopped and persisted if needed.")

    def __del__(self):
        try:
            self.stop()
            if self.use_ultraqueue and hasattr(LIB, "cleanup_queue_lock"):
                LIB.cleanup_queue_lock()
            elif not self.use_ultraqueue and self.save_path:
                self._persist_to_disk()
            self._log("info", "UltraQueue instance deleted and resources cleaned up.")
        except Exception as e:
            self._log("error", f"__del__ cleanup failed: {e}")

    def __len__(self):
        return self.length()
    
    def __iter__(self):
        if self.use_ultraqueue:
            raise NotImplementedError("Iteration not supported in C backend mode")
        with self._lock:
            return iter(list(self.queue))


    def __repr__(self):
        return f"UltraQueue len={len(self)} backend={'C' if self.use_ultraqueue else 'deque'}"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def enable_logging(self):
        self.logging_enabled = True

    def disable_logging(self):
        self.logging_enabled = False
