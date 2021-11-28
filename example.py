from sim.sim import Sim
from sim.server import Server
from sim.client_filesys import ClientFileSystem


def proc_1_main(server: Server):
    fs = ClientFileSystem(server)
    fd = yield from fs.open('foo.txt')

    while (yield from fs.size(fd)) < 1:
        yield from fs.append(fd, '1')


def proc_2_main(server: Server):
    fs = ClientFileSystem(server)
    fd = yield from fs.open('foo.txt')

    while (yield from fs.size(fd)) < 1:
        yield from fs.append(fd, '2')


def proc_3_main(server: Server):
    fs = ClientFileSystem(server)
    fd = yield from fs.open('foo.txt')

    while (yield from fs.size(fd)) < 1:
        yield from fs.append(fd, '3')


if __name__ == '__main__':
    sim = Sim([proc_1_main, proc_2_main, proc_3_main])
    sim.explore(verbose=True)
    sim.summarize()
