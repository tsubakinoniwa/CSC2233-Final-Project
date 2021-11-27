from enum import Enum


class Server:
    """
    Simplified server only serving a single file and supporting two
    NFS operations
    """
    def __init__(self):
        self.file = []  # The single file served by the server

    def NFSPROC_GETATTR(self):
        return len(self.file)

    def NFSPROC_WRITE(self, pos, s):
        end = min(pos + len(s), len(self.file))
        for i in range(pos, end):
            self.file[i] = s[i - pos]

        if pos + len(s) <= len(self.file):
            return

        for i in range(len(self.file), pos + len(s)):
            self.file.append(s[i - pos])


class Request:
    """
    Class that represents the NFS operation request sent by a client.
    """
    class Type(Enum):
        NFSGetAttr = 1
        NFSWrite = 2

    def __init__(self, op_type: Type, proc, *args):
        self.op_type = op_type
        self.proc = proc
        self.args = args

    def serve(self):
        return self.proc(*self.args)


class ClientFileSystem:
    def __init__(self, server: Server):
        self.server = server  # The NFS server the client is connected to

    def size(self):
        res = (yield Request(Request.Type.NFSGetAttr, self.server.NFSPROC_GETATTR))
        return res

    def append(self, s):
        # The scheduler (implemented in our simulation) would handle
        # the handling of our request!

        # Get the size of the file
        offset = yield Request(Request.Type.NFSGetAttr, self.server.NFSPROC_GETATTR)

        # Write to the file
        yield Request(Request.Type.NFSWrite, self.server.NFSPROC_WRITE, offset, s)


def proc_p1_main(server: Server):
    fs = ClientFileSystem(server)

    while (yield from fs.size()) < 3:
        yield from fs.append('1')


def proc_p2_main(server: Server):
    fs = ClientFileSystem(server)

    while (yield from fs.size()) < 3:
        yield from fs.append('2')


def dfs(proc_mains, steps, hist):
    """
    Explore all interleaving of NFS operations using depth-first search.
    """

    # First generate the processes and run them up to speed
    server = Server()
    processes = [p(server) for p in proc_mains]
    requests  = [next(p) for p in processes]
    for ind in hist:
        try:
            requests[ind] = processes[ind].send(requests[ind].serve())
        except StopIteration:
            pass  # The process has terminated execution

    end = True  # Whether all threads have finished
    for i in range(len(steps)):
        if not steps[i]:
            continue  # Cannot schedule this thread to do more

        end = False
        n_steps = steps.copy()
        try:
            requests[i] = processes[i].send(requests[i].serve())
        except StopIteration:
            n_steps[i] = False  # No more steps for this process
            pass

        n_hist = hist.copy()
        n_hist.append(i)

        dfs(proc_mains, n_steps, n_hist)

    if end:
        print(''.join(server.file))


if __name__ == '__main__':
    dfs([proc_p1_main, proc_p2_main], [True, True], [])
    # server = Server()  # A single server instance shared by all processes
    # processes = [proc_p1_main(server), proc_p2_main(server)]
    # requests  = [next(p) for p in processes]  # Run each proc to 1st NFS req

    # # Serve p1's request and run p1 to its next NFS request, and do the same
    # # thing for p2
    # for i in range(2):
    #     requests[i] = processes[i].send(requests[i].serve())

    # # Now, serve p2's request and run it to completion...
    # try:
    #     requests[1] = processes[1].send(requests[1].serve())
    # except StopIteration:
    #     print('Process p2 finished')  # And do nothing else!

    # # ... and then serve p1's request and run it to completion
    # try:
    #     requests[0] = processes[0].send(requests[0].serve())
    # except StopIteration:
    #     print('Process p1 finished')

    # # And the grand reveal...
    # print('NFSServer file content: ', end='')
    # print(''.join(server.file) + '\n')