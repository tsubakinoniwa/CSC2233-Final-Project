# NFS Concurrency Visualizer
Brief introduction of the project here.

We assume that all clients only write to one file on the server, since 
writing to different files either completely removes the issues with concurrent
updates, or just pushes the same problem across multiple files. For example, if
processes `p1` and `p2` write to file `A` while processes `p3` and `p4` write to
file `B`, all the potential confusing aspects of working with NFS is revealed with
file `A`, and so there is no need to support multiple files.

## Supported NFS Protocol (Subset of NFSv2)
Our project only supports a subset of all the procedures defined in NFSv2.

* `NFSPROC_LOOKUP`: While our server only has one file, this procedure is needed 
when client opens the signle file by issuing `fopen()` from user-space APIs, see
below.
* `NFSPROC_GETATTR`: Used by `NFSPROC_READ` and `NFSPROC_WRITE` as the first step.
For dramatic effect, we assume that there is no cache anywhere in the system, and
we show that even then, concurrent writes produce noticeable effects. The problem
only worsens as more constructs (like cache) that violate consistency requirements
are added.
* `NFSPROC_READ`
* `NFSPROC_WRITE`

## Server-Side Behavior of Our NFS Implementation
Since the server only serves one file, its implementation is straightforward. 
Recall that servers in NFS cannot have write caches for crash consistency reasons
without extra infrastructure to ensure crash consistency. In our simulation, we
simply assume that every call to `NFSPROC_WRITE` will be written through.

## Client File I/O APIs
We assume that the clients are exposed the following operations on 

## Client-Side Behavior of Our NFS Implementation
As mentioned briefly in the "Supported NFS Protocol" section, we assume that our
client do not have read caches or attribute caches. We show that even in this
"best case" scenario (equivalently, one can think of the cache being invalidated
just as when it is needed), concurrency produces noticeable effects to users
of NFS.

## Staging Area
(Some other points that we should mention)
* We assume the server runs a Unix-like file system, in which file-locking is by
default disabled. Client requests are served in their entireties based on the
order of arrival.