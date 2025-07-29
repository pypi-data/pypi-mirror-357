import socket
import subprocess
import os
from urllib.parse import urlparse

"""
When the bot is started:
1. Test if simplex-chat client is running
2. If not, start it
3. If it is running, do nothing
"""

class AutorunTrait:
    def _set_simplex_chat_client_params(self,
                                        url: str,
                                        executable_path: str = "simplex-chat",
                                        database_name: str = "simplex-bot-database"):
        # Parse URL to get host and port
        parsed = urlparse(url)
        self.__simplex_chat_client_host = parsed.hostname or 'localhost'
        self.__simplex_chat_client_port = parsed.port or 5225
        self.__simplex_chat_client_path = executable_path
        self.__simplex_chat_database_name = database_name

    def _test_simplex_chat_client_running(self):
        # Try to connect to the socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.__simplex_chat_client_host, self.__simplex_chat_client_port))
            sock.close()
            return True
        except (socket.error, ConnectionRefusedError):
            return False

    def _start_simplex_chat_client(self):
        cmd = [
            self.__simplex_chat_client_path,
            "-p", str(self.__simplex_chat_client_port),
            "-d", self.__simplex_chat_database_name
        ]

        try:
            if os.name == 'nt':  # Windows
                subprocess.Popen(cmd, 
                    creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL)
            else:  # Unix-like
                subprocess.Popen(cmd,
                    start_new_session=True,
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL)
        except Exception as e:
            raise RuntimeError(f"Failed to start simplex-chat client: {str(e)}\n"
                               f"Please check if the path to the simplex-chat client is correct.")
