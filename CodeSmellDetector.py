import ast

import GlobalDefaults


class NormalizeVariableNames(ast.NodeTransformer):
    def __init__(self):
        self.var_map = {}
        self.counter = 0

    def visit_Name(self, node):
        if node.id not in self.var_map:
            self.var_map[node.id] = f"var_{self.counter}"
            self.counter += 1
        return ast.copy_location(ast.Name(id=self.var_map[node.id], ctx=node.ctx), node)

class CodeSmellDetector(ast.NodeVisitor):
    node_list = []
    long_funcs = []
    long_params = []
    tokenized_funcs = []
    duplicate_funcs = {}
    unique_duplicate_funcs = {}
    def __init__(self, file_path):
        self.file_path = file_path
        self.code = self.read_file()
        self.get_functions_from_file()
        self.identify_long_funcs()
        self.identify_long_params()
        self.identify_duplicate_funcs()

    def visit_FunctionDef(self, node):
        self.node_list.append(node)

    def read_file(self):
        with open(self.file_path, "r") as file:
            return file.read()

    def print_code(self):
        print(self.code)

    def get_functions_from_file(self):
        tree = ast.parse(self.code)
        self.visit(tree)

    def identify_long_funcs(self):
        for node in self.node_list:
            func_start = node.lineno
            func_end = max(child.lineno for child in ast.walk(node) if hasattr(child, "lineno"))
            func_len = func_end - func_start + 1
            print(f"Function {node.name} length: {func_len} lines")
            if (func_len > GlobalDefaults.LONG_FUNC_THRESHOLD) :
                self.long_funcs.append(node)

    def identify_long_params(self):
        for node in self.node_list:
            param_num = 0
            if node.args.args is not None:
                for arg in node.args.args:
                    print(arg.arg)
                    param_num += 1
            if node.args.vararg is not None:
                print(node.args.vararg.arg)
                param_num += 1
            if node.args.kwonlyargs is not None:
                for arg in node.args.kwonlyargs:
                    print(arg)
                    param_num += 1
            if node.args.kwarg is not None:
                for arg in node.args.kwarg:
                    print(arg)
                    param_num += 1
            if param_num > GlobalDefaults.LONG_PARAM_THRESHOLD:
                self.long_params.append(node.name)

    def jaccard_similarity(self, set1, set2):
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        intersection_len = len(intersection)
        union_len = len(union)
        return intersection_len / union_len
    def identify_duplicate_funcs(self):
        for node in self.node_list:
            self.tokenized_funcs.append(self.normalize_and_tokenize_func(node))

        for i in range (0, len(self.tokenized_funcs)) :
            curr_func = self.tokenized_funcs[i]
            for j in range (0, len(self.tokenized_funcs)) :
                if j == i:
                    continue
                similarity = self.jaccard_similarity(curr_func, self.tokenized_funcs[j])
                if similarity >= GlobalDefaults.JACCARD_SIMILARITY_THRESHOLD :
                    if self.node_list[i].name in self.duplicate_funcs:
                        self.duplicate_funcs[self.node_list[i].name].append(self.node_list[j].name)
                    else:
                        self.duplicate_funcs[self.node_list[i].name] = []
                        self.duplicate_funcs[self.node_list[i].name].append(self.node_list[j].name)
        self.create_unique_duplicate_func_list()
        print(self.duplicate_funcs)

    def normalize_and_tokenize_func(self, node):
        node_to_func = ast.unparse(node)
        func_tree = ast.parse(node_to_func)
        normalizer = NormalizeVariableNames()
        normalized_tree = normalizer.visit(func_tree)
        ast.fix_missing_locations(normalized_tree)
        normalized_func = ast.unparse(normalized_tree)
        normalized_func_list = normalized_func.split('\n')
        normalized_func_list_without_funcdef = [s for s in normalized_func_list if not s.startswith(GlobalDefaults.DEF_KEYWORD)]
        return set(normalized_func_list_without_funcdef)

    def create_unique_duplicate_func_list(self):
        for key in self.duplicate_funcs.keys():
            dup_list = self.duplicate_funcs[key]
            for list_mem in dup_list:
                if list_mem in self.duplicate_funcs:
                    self.duplicate_funcs[list_mem].remove(key)
        for key in list(self.duplicate_funcs.keys()):
            if len(self.duplicate_funcs[key]) == 0:
                self.duplicate_funcs.pop(key)
        print(self.duplicate_funcs)


