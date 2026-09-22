class DAG:
    def __init__(self):
        self.graph = {}
        self.depends = {}
                
    def _has_path(self, u, v):
        visited = set()
        stack = [u]
        
        while stack:
            node = stack.pop()
            if node == v:
                return True
            visited.add(node)
            for nxt in self.graph[node]:
                if nxt not in visited:
                    stack.append(nxt)
        return False
    def add_task(self, task_id):
        if task_id not in self.graph:
            self.graph[task_id] = []
            self.depends[task_id] = []
    
    def add_edge(self, predecessor, successor):
        self.add_task(predecessor)
        self.add_task(successor)
        if successor in self.graph[predecessor]:
            return
        if self._has_path(successor, predecessor):
            raise ValueError("Cyclic Dependency Given, cannot create DAG")
        self.graph[predecessor].append(successor)
        self.depends[successor].append(predecessor)
        
    def get_dependencies(self, task_id):
        if task_id not in self.graph:
            raise ValueError("Invalid task provided")
        return list(self.depends[task_id])
        
    