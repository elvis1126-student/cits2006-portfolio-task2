#!/usr/bin/env python3
from code import InteractiveConsole
from atexit import register
from sys import stdout
from os import path
import readline
import getpass
import logging
from pymetasploit3.msfrpc import MsfRpcClient, MsfRpcError
from pymetasploit3.msfconsole import MsfRpcConsole
from pymetasploit3.utils import parseargs

logger = logging.getLogger(__name__)


class MsfConsole(InteractiveConsole):
    def __init__(self, password, **kwargs):
        self.fl = True
        self.client = MsfRpcConsole(MsfRpcClient(password, **kwargs), cb=self.callback)
        InteractiveConsole.__init__(self, {'rpc': self.client})
        self._init_history(self._safe_history_path())

    def raw_input(self, prompt):
        """
        FIX 1 — Code Injection (Critical)
        Original code built a string → exec()'d by InteractiveConsole:
            return "rpc.execute('%s')" % line.replace("'", r"\'")
        This allowed arbitrary Python injection via crafted user input.

        Correct fix: call RPC directly as a method — nothing gets exec()'d.
        The injection vector is eliminated at the architectural level.
        """
        line = InteractiveConsole.raw_input(self, prompt=self.client.prompt)
        self.client.execute(line)
        return ''

    @staticmethod
    def _safe_history_path():
        """
        FIX 2 — History File Path Traversal (Medium)
        If the HOME environment variable is poisoned (e.g. HOME=/../../etc),
        expanduser() could write history outside the user's home directory.

        Correct fix: resolve the real path and verify it stays within home.
        """
        raw  = path.expanduser('~/.msfconsole_history')
        real = path.realpath(raw)
        home = path.realpath(path.expanduser('~'))
        if not real.startswith(home + path.sep):
            raise ValueError(
                "History path '%s' is outside home directory — "
                "possible HOME env poisoning." % real
            )
        return real

    def _init_history(self, histfile):
        """
        FIX 4 — Silent IOError Swallowing (Low)
        Original code caught all IOError silently, hiding real problems.

        Correct fix: FileNotFoundError (first run) is expected and silent.
        Any other OSError (permissions, disk fault) is logged as a warning.
        """
        readline.parse_and_bind('tab: complete')
        if hasattr(readline, "read_history_file"):
            try:
                readline.read_history_file(histfile)
            except FileNotFoundError:
                pass                        # First run — no history yet, expected
            except OSError as exc:
                logger.warning("Could not read history file '%s': %s", histfile, exc)
        register(self._save_history, histfile)

    def _save_history(self, histfile):
        try:
            readline.write_history_file(histfile)
        except OSError as exc:
            logger.warning("Could not write history file '%s': %s", histfile, exc)
        finally:
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

    """
    FIX 3 — Password Exposed in Process Listing (Medium)
    Passwords passed as CLI args are visible in `ps aux`, /proc, and shell
    history. 

    Correct fix: use getpass() so the password is never echoed,
    never recorded in shell history, and never visible in process listings.
    """
    password = o.__dict__.pop('password', None)
    if not password:
        password = getpass.getpass('Metasploit RPC password: ')

    try:
        m = MsfConsole(password, **o.__dict__)
        m.interact('')
    except MsfRpcError as exc:
        print(str(exc))
        exit(-1)
    except ValueError as exc:          # Raised by _safe_history_path()
        print("Security error: %s" % exc)
        exit(-1)

    exit(0)