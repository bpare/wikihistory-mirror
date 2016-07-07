import bisect
import difflib
import networkx as nx

# Models individual insertions and deletions as Patches, revisions as
#   PatchSets, and the history of ownership of text as a PatchModel

class PatchType:
    """
        Add if text was inserted. Delete if text was removed
    """
    ADD = 0
    DELETE = 1




class Patch:
    """
        A Patch is a contiguous block of added or deleted words
            representing a single edit.
    """
    def __init__(self, pid, ptype, start, end):
        assert ptype == PatchType.ADD or ptype == PatchType.DELETE
        assert start >= 0
        assert end > start

        self.pid = pid
        self.ptype = ptype
        self.start = start
        self.end = end
        self.length = end - start




class PatchSet:
    """
        A PatchSet is a list of Patches (edits) that belong to the
        same revision.

        Each Patch implicitly depend on preceding Patches.
    """

    def __init__(self):
        self.patches = []

    @classmethod
    def psdiff(cls, startid, old, new):
        """
            Compares 2 vesions of text at a word level to identify 
                the individual edits (insertions and deletions).
        """
        ptype = None
        ps = cls()
        start = None
        pid = startid

        # Obtain a list of differences between the texts
        diff = difflib.ndiff(old, new)
        
        # Split the differences into Patches
        index = 0
        for line in diff:
            if line[0] == ' ':
                # If equal, terminate any current patch.
                if ptype is not None:
                    ps.append_patch(Patch(pid, ptype, start, index))
                    pid+=1
                    if ptype == PatchType.DELETE:
                        index = start
                    ptype = None
                index += 1
            elif line[0] == '+':
                # If addition, terminate any current DELETE patch.
                if ptype == PatchType.DELETE:
                    ps.append_patch(Patch(pid, ptype, start, index))
                    pid+=1
                    index = start
                    ptype = None
                # Begin a new ADD patch, or extend an existing one.
                if ptype is None:
                    ptype = PatchType.ADD
                    start = index
                index += 1
            elif line[0] == '-':
                # If deletion, terminate any current ADD patch.
                if ptype == PatchType.ADD:
                    ps.append_patch(Patch(pid, ptype, start, index))
                    pid+=1
                    ptype = None
                # Begin a new DELETE patch, or extend an existing one.
                if ptype is None:
                    ptype = PatchType.DELETE
                    start = index
                index += 1
            # Skip line[0] == '?' completely.

        # Terminate and add any remaining patch.
        if ptype is not None:
            ps.append_patch(Patch(pid, ptype, start, index))

        return ps

    def append_patch(self, p):
        self.patches.append(p)




class PatchModel:
    """
        A PatchModel model gives ownership of indices of the current text to
            the Patch that last modified that section of text.
    """
    model=[]   # A sorted list of end indices and Patch IDs.
    graph = nx.DiGraph()
    sizes = {}


    def apply_patch(self, p):
        """
            Adds Patch, p, to the model and graph
        """
        self.graph.add_node(p.pid)
        self.sizes[p.pid]=p.length
        if not self.model:
            self.model.append((p.end, p.pid))
        
        elif p.ptype == PatchType.ADD:
            # Find indices that share a range with p
            sin = bisect.bisect_left(
                [end for (end, pid) in self.model], p.start)
            ein = bisect.bisect_right(
                [end for (end, pid) in self.model], p.start)

            # Add dependencies
            # (every patch that ends where p starts and the proceeding patch)
            for (end, pid) in self.model[sin:(ein + 1)]:
                self.graph.add_edge(p.pid, pid, weight=1)

            # Remove intermediates if present.
            # Leave the first preceeding Patch
            if sin != ein:
                del self.model[(sin + 1):ein]
            # Else, split the surrounding span.
            else:
                (end, pid) = self.model[sin]
                self.model.insert(sin, (p.start, pid))
            ein = sin + 1

            # Insert.
            self.model.insert(ein, (p.end, p.pid))

            # Update proceeding spans.
            self.model[(ein + 1):] = \
                [(end + p.length, pid) for (end, pid) \
                in self.model[(ein + 1):]]


        elif p.ptype == PatchType.DELETE:
            # Find indices of Patches who fall in the deleted range.
            sin = bisect.bisect_right(
                [end for (end, pid) in self.model], p.start)
            ein = bisect.bisect_left(
                [end for (end, pid) in self.model], p.end)

            # Add dependencies to graph
            for (end, pid) in self.model[sin:(ein + 1)]:
                self.graph.add_edge(p.pid, pid, weight=1)

            # Adjust indices to include Patches that end where p starts
            #   or end where p ends.
            if sin != bisect.bisect_left(
               [end for (end, pid) in self.model], p.start): sin -= 1
            if ein != bisect.bisect_right(
                [end for (end, pid) in self.model], p.end): ein += 1

            # Shrink the preceding span and remove intermediates if present
            (end, pid) = self.model[sin]
            if sin != ein:
                self.model[sin] = (p.start, pid)
                del self.model[(sin + 1):ein]
            # Else, split the surrounding span.
            else:
                self.model.insert(sin, (p.start, pid))
            ein = sin + 1

            # Insert.
            self.model.insert(ein, (p.start, p.pid))

            # Update the proceeding spans.
            self.model[(ein + 1):] = \
                [(end - p.length, pid) for (end, pid) \
                in self.model[(ein + 1):]]

        else:
            assert False
