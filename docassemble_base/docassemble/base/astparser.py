import ast
import re

fix_assign = re.compile(r'\.(\[[^\]]*\])')
valid_variable_match = re.compile(r'^[^\d][A-Za-z0-9\_]*$')

class myextract(ast.NodeVisitor):
    def __init__(self):
        self.stack = []
        self.in_subscript = 0
        self.seen_name = False
    def visit_Name(self, node):
        if not (self.in_subscript > 0 and self.seen_name is True):
            self.stack.append(node.id)
            if self.in_subscript > 0:
                self.seen_name = True
        ast.NodeVisitor.generic_visit(self, node)
    def visit_Attribute(self, node):
        self.stack.append(node.attr)
        ast.NodeVisitor.generic_visit(self, node)
    def visit_Subscript(self, node):
        if hasattr(node.slice.value, 'id'):
            self.stack.append('[' + str(node.slice.value.id) + ']')
            self.in_subscript += 1
            self.seen_name = False
        elif hasattr(node.slice.value, 'n'):
            self.stack.append('[' + str(node.slice.value.n) + ']')
            self.in_subscript += 1
            self.seen_name = False
        ast.NodeVisitor.generic_visit(self, node)
        if hasattr(node.slice.value, 'id'):
            self.in_subscript -= 1

class myvisitnode(ast.NodeVisitor):
    def __init__(self):
        self.names = {}
        self.targets = {}
        self.depth = 0;
        self.calls = set()
    def generic_visit(self, node):
        #logmessage(' ' * self.depth + type(node).__name__)
        self.depth += 1
        ast.NodeVisitor.generic_visit(self, node)
        self.depth -= 1
    def visit_Call(self, node):
        self.calls.add(node.func)
        if hasattr(node.func, 'id') and node.func.id in ['showif', 'showifdef', 'value', 'defined'] and len(node.args) and node.args[0].__class__.__name__ == 'Str' and hasattr(node.args[0], 's') and re.search(r'^[^\d]', node.args[0].s):
            self.names[node.args[0].s] = 1
        ast.NodeVisitor.generic_visit(self, node)
    def visit_Attribute(self, node):
        if node not in self.calls:
            crawler = myextract()
            crawler.visit(node)
            self.names[fix_assign.sub(r'\1', ".".join(reversed(crawler.stack)))] = 1
        ast.NodeVisitor.generic_visit(self, node)
    def visit_ExceptHandler(self, node):
        if node.name is not None and hasattr(node.name, 'id') and node.name.id is not None:
            self.targets[node.name.id] = 1
        ast.NodeVisitor.generic_visit(self, node)
    def visit_Assign(self, node):
        for key, val in ast.iter_fields(node):
            if key == 'targets':
                for subnode in val:
                    if type(subnode) is ast.Tuple:
                        for subsubnode in subnode.elts:
                            crawler = myextract()
                            crawler.visit(subsubnode)
                            self.targets[fix_assign.sub(r'\1', ".".join(reversed(crawler.stack)))] = 1
                    else:
                        crawler = myextract()
                        crawler.visit(subnode)
                        self.targets[fix_assign.sub(r'\1', ".".join(reversed(crawler.stack)))] = 1
        self.depth += 1
        #ast.NodeVisitor.generic_visit(self, node)
        self.generic_visit(node)
        self.depth -= 1
    def visit_FunctionDef(self, node):
        if hasattr(node, 'name'):
            self.targets[node.name] = 1
    def visit_Import(self, node):
        for alias in node.names:
            if alias.asname is None:
                the_name = alias.name
            else:
                the_name = alias.asname
            while(re.search(r'\.', the_name)):
                self.targets[the_name] = 1
                the_name = re.sub(r'\.[^\.]+$', '', the_name)
            self.targets[the_name] = 1
    def visit_ImportFrom(self, node):
        for alias in node.names:
            if alias.asname is None:
                the_name = alias.name
            else:
                the_name = alias.asname
            while(re.search(r'\.', the_name)):
                self.targets[the_name] = 1
                the_name = re.sub(r'\.[^\.]+$', '', the_name)
            self.targets[the_name] = 1
    def visit_For(self, node):
        if hasattr(node.target, 'id'):
            self.targets[node.target.id] = 1
        self.generic_visit(node)
    def visit_Name(self, node):
        self.names[node.id] = 1
        #ast.NodeVisitor.generic_visit(self, node)
        self.generic_visit(node)

