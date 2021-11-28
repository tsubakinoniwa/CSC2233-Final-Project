from copy import deepcopy
from typing import List, Callable, Any

from .server import Server
from .request import Request


class Sim:
    """
    Main simulation class.

    This class is responsible for exploring all interleaving of NFS operations
    from processes supplied by the caller of an instance of this class.

    Two executions (interleaving of NFS operations) are considered equal if
    the response returned to each process is the same, and that the file content
    on the server is the same at the end. For example, if two threads only read
    the same file and do not modify it in any way, then all interleaving are
    considered the same.

    Importantly, the caller of this class must ensure that the supplied process
    threads does not have an (implicit) infinite loop. Otherwise, the simulation
    will not terminate (until either the machine runs out of memory or the sim
    raises an RecursionError).
    """

    class Result:
        """
        Struct for the result of each execution
        """

        def __init__(self, n: int):
            self.n = n
            self.responses = [[] for _ in range(n)]
            self.file_content = ''

        def add_response(self, i, resp):
            self.responses[i].append(resp)

        def __hash__(self):
            res = self.n
            for resp in self.responses:
                for s in resp:
                    res = (res << 1) ^ hash(s)
            res = (res << 1) ^ hash(self.file_content)
            return res

        def __eq__(self, other):
            if not isinstance(other, Sim.Result):
                return False

            if self.__hash__() != other.__hash__():
                return False

            if self.n != other.n:
                return False

            for resp, o_resp in zip(self.responses, other.responses):
                if resp != o_resp:
                    return False

            return self.file_content == other.file_content

    def __init__(self, proc_mains: List[Callable[[Server], Any]]):
        self.n = len(proc_mains)
        self.proc_mains = proc_mains  # Pointers to entry functions
        self.results = set()  # Stores unique results

        # Used in our depth-first search
        self._steps = [True] * self.n  # Whether some process has any step left
        self._hist = []
        self._result = Sim.Result(self.n)

    def explore(self, verbose=False):
        if not self.proc_mains:
            raise Exception("No main functions supplied")
        self._dfs(verbose=verbose)

    def _exec_hist(self):
        server = Server()
        processes = [p(server) for p in self.proc_mains]
        requests = [next(p) for p in processes]  # Prime the generators

        for ind in self._hist:
            try:
                resp = requests[ind].serve()
                requests[ind] = processes[ind].send(resp)
            except StopIteration:
                # This process has already terminated. No need to change
                # self._steps since this must have been handled in _dfs.
                pass

        return server, processes, requests

    def _dfs(self, verbose=False):
        """
        Use backtracking to explore all interleaving of NFS operations from
        each process supplied to this object at construction time.
        :param verbose: Whether or not to print the currently explored history
        """

        if verbose:  # Print the history of steps
            s = ''.join(map(lambda x: str(x), self._hist))
            print(s, end='\r', flush=True)

        server, processes, requests = self._exec_hist()

        end = True  # Whether all threads have finished
        for i in range(self.n):
            changed_steps = False
            added_result = False

            if not self._steps[i]:
                continue  # Cannot schedule this thread to do more

            end = False
            try:
                req = requests[i]
                resp = req.serve()
                if req.type == Request.Type.READ:
                    if len(resp) == 1:  # This read returned NFSERR_NOENT
                        pass
                    else:
                        added_result = True
                        self._result.add_response(i, resp[2])

                requests[i] = processes[i].send(resp)
            except StopIteration:
                self._steps[i] = False  # No more steps for this process
                changed_steps = True

            self._hist.append(i)
            self._dfs(verbose=verbose)
            self._hist.pop()   # Restore _hist
            if changed_steps:  # Restore _steps
                self._steps[i] = True
            if added_result:   # Restore _result
                self._result.responses[i].pop()

        if end:
            res = deepcopy(self._result)
            res.file_content = ''.join(server.files['foo.txt'])
            self.results.add(res)

    def summarize(self):
        """
        Print a summary of the unique results found by the simulation
        """
        print('=' * 50)
        print(f'The simulation found {len(self.results)} unique executions.')
        print('=' * 50)

        for i, res in enumerate(self.results):
            print('')
            print('-' * 50)
            print(f"Scenario #{i}")
            print('-' * 50)
            for p, m in enumerate(res.responses):
                if m:
                    print(f'p{p}: {str(m)}')
            print(f'File: {res.file_content}')
            print('-' * 50)
