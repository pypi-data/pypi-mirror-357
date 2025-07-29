"""
Simple routing implementation
"""

class Route:
    def __init__(self, path, handler, methods=None):
        self.path = path
        self.handler = handler
        self.methods = methods or ["GET"]

class Router:
    def __init__(self):
        self.routes = []
    
    def add_route(self, path, handler, methods=None):
        route = Route(path, handler, methods)
        self.routes.append(route)
        return route
    
    def match(self, path, method="GET"):
        for route in self.routes:
            if route.path == path and method in route.methods:
                return route
        return None
    
    def handle(self, path, method="GET", *args, **kwargs):
        route = self.match(path, method)
        if route:
            return route.handler(*args, **kwargs)
        return None