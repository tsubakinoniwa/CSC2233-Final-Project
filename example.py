from sim.sim import Sim
from sim.server import Server
from sim.client_filesys import ClientFileSystem


def proc_1_main(server: Server):
    fs = ClientFileSystem(server)
    fd = yield from fs.create('/bar.txt')
    if fd == -1:
        fd = yield from fs.open('/bar.txt')

    for _ in range(3):  # Write "1" three times
        yield from fs.append(fd, '1')


def proc_2_main(server: Server):
    fs = ClientFileSystem(server)
    fd = yield from fs.create('/bar.txt')
    if fd == -1:
        fd = yield from fs.open('/bar.txt')

    for _ in range(3):  # Write "2" three times.
        yield from fs.append(fd, '2')


if __name__ == '__main__':
    sim = Sim([proc_1_main, proc_2_main])
    sim.explore(verbose=False)
    sim.summarize()