#!/usr/bin/env python3

from code import InteractiveConsole
from atexit import register
from sys import stdout
from os import path
import readline

from pymetasploit3.msfrpc import MsfRpcClient, MsfRpcError
from pymetasploit3.msfconsole import MsfRpcConsole
from pymetasploit3.utils import parseargs


class SafeMsfConsole(InteractiveConsole):

    def __init__(self, password, **kwargs):
        self.fl = True
        self.client = MsfRpcConsole(
            MsfRpcClient(password, **kwargs),
            cb=self.callback
        )

        # No longer exposing raw execution context
        super().__init__({})

        self.init_history(path.expanduser('~/.msfconsole_history'))

    def raw_input(self, prompt):
        """
        Get user input safely WITHOUT constructing Python code.
        """
        line = super().raw_input(prompt=self.client.prompt)

        # --- Basic input validation ---
        if "\n" in line or "\r" in line:
            print("[-] Invalid input: newline characters are not allowed")
            return ""

        return line

    def push(self, line):
        """
        Override execution to directly call the client instead of eval.
        """
        try:
            if line.strip():
                self.client.execute(line)
        except Exception as e:
            print(f"[!] Error: {e}")
        return False  # prevent InteractiveConsole from evaluating anything

    def init_history(self, histfile):
        readline.parse_and_bind('tab: complete')
        if hasattr(readline, "read_history_file"):
            try:
                readline.read_history_file(histfile)
            except IOError:
                pass
            register(self.save_history, histfile)

    def save_history(self, histfile):
        readline.write_history_file(histfile)
        del self.client
        print('bye!')

    def callback(self, d):
        stdout.write('\n%s' % d['data'])
        if not self.fl:
            stdout.write('\n%s' % d['prompt'])
            stdout.flush()
        else:
            self.fl = False


if __name__ == '__main__':
    o = parseargs()
    try:
        m = SafeMsfConsole(o.__dict__.pop('password'), **o.__dict__)
        m.interact('')
    except MsfRpcError as e:
        print(str(e))
        exit(-1)
    exit(0)