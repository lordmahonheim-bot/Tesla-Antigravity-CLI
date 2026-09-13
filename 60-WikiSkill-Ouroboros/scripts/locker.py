#!/usr/bin/env python3
import fcntl
import os
from types import TracebackType
from typing import Optional, Type, IO

class FS_Lock:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.fd: Optional[IO] = None

    def __enter__(self):
        # Ouvre ou crée le fichier sans tronquer son contenu
        self.fd = open(self.filepath, 'a+')
        try:
            # LOCK_EX: Exclusif, LOCK_NB: Non-bloquant
            fcntl.flock(self.fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.fd.close()
            self.fd = None
            raise BlockingIOError(f"Le fichier {self.filepath} est déjà verrouillé par un autre processus.")
        except Exception as e:
            self.fd.close()
            self.fd = None
            raise e
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> None:
        if self.fd:
            try:
                fcntl.flock(self.fd.fileno(), fcntl.LOCK_UN)
            finally:
                self.fd.close()

if __name__ == "__main__":
    # Test CLI pour vérifier le verrou non-bloquant
    import sys
    import time
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <fichier_a_verrouiller>", file=sys.stderr)
        sys.exit(1)
        
    try:
        with FS_Lock(sys.argv[1]):
            print(f"Verrou acquis sur {sys.argv[1]}. Maintien pour 5 secondes...")
            time.sleep(5)
            print("Relâchement du verrou.")
    except BlockingIOError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
