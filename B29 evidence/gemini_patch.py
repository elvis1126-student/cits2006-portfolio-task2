#!/usr/bin/env python3

import os
import readline
import sys
from atexit import register

from pymetasploit3.msfrpc import MsfRpcClient, MsfRpcError
from pymetasploit3.msfconsole import MsfRpcConsole
from pymetasploit3.utils import parseargs

class SecureMsfConsole:
    def __init__(self, password, **kwargs):
        # 1. Initialize the Client
        self.client = MsfRpcClient(password, **kwargs)
        
        # 2. Initialize the Console with the output callback
        # The callback is what prints the MSF output to your screen
        self.console = MsfRpcConsole(self.client, cb=self.callback)
        
        # 3. Setup History
        self.histfile = os.path.expanduser('~/.msfconsole_history')
        self.init_history(self.histfile)

    def init_history(self, histfile):
        """Securely loads and registers history saving."""
        readline.parse_and_bind('tab: complete')
        if os.path.exists(histfile):
            try:
                readline.read_history_file(histfile)
            except (IOError, PermissionError):
                pass
        register(self.save_history, histfile)

    def save_history(self, histfile):
        """Saves history and performs clean teardown."""
        try:
            readline.write_history_file(histfile)
        except Exception:
            pass 
        print('\n[*] Session terminated.')

    def callback(self, data_dict):
        """Handles data coming back from the RPC server."""
        if 'data' in data_dict:
            # We use sys.stdout.write for raw output handling
            sys.stdout.write(data_dict['data'])
            sys.stdout.flush()

    def run(self):
        """The main interactive loop."""
        print("[*] MSF RPC Shell Active. Type 'exit' to quit.")
        
        while True:
            try:
                # Always grab the freshest prompt from the console object
                current_prompt = self.console.prompt if self.console.prompt else 'msf > '
                
                # 'input()' is safe here because we are NOT passing 
                # the result into eval() or exec().
                user_input = input(current_prompt).strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'quit']:
                    break

                # VULNERABILITY FIXED: 
                # We call the method directly. 'user_input' is treated 
                # strictly as a string argument to the execute function.
                self.console.execute(user_input)

            except EOFError:
                break
            except KeyboardInterrupt:
                print("\n[*] Interrupt received. Type 'exit' to close.")
            except Exception as e:
                print(f"\n[!] Unexpected Error: {e}")

if __name__ == '__main__':
    # parseargs handles --host, --port, --password, --ssl
    parser_args = parseargs()
    config = parser_args.__dict__
    
    # Ensure password exists
    pwd = config.pop('password', None)
    if not pwd:
        print("[-] Error: Missing password. Use --password <pass>")
        sys.exit(1)

    try:
        # Create and run the console
        shell = SecureMsfConsole(pwd, **config)
        shell.run()
    except MsfRpcError as e:
        print(f"[-] Failed to connect to Metasploit RPC: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[-] Critical failure: {e}")
        sys.exit(1)