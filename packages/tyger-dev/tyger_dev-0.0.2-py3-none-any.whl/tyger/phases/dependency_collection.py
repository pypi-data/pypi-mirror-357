import ast
from typing import Any

from tyger.parser import Parser
from tyger.phase import Phase


def resolve_full_name(module: str, level: int, package_name: str = "") -> str:
    if level > 0:
        # We need to resolve the full name of the module
        if not package_name:
            raise ImportError("attempted relative import with no known parent package")

        package_name_tokens = package_name.split(".")
        package_name_prefix = '.'.join(package_name_tokens[:-level])
        module = f"{package_name_prefix}.{module}"
    return module


class DependencyCollectionPhase(Phase):
    def run(self, source: ast.Module, **kwargs) -> tuple[ast.Module, dict[str, Any]]:
        deps = self.collect_dependencies(source.body)
        kwargs['dependencies'] = deps
        return source, kwargs

    def collect_dependencies(self, stmts: list[ast.stmt], package_name="") -> dict[str, ast.Module]:
        deps: dict[str, ast.Module] = {}
        for st in stmts:
            match st:
                case ast.FunctionDef(_, _, body):
                    func_deps = self.collect_dependencies(body, package_name)
                    deps.update(func_deps)
                case ast.For(_, _, body, orelse) | ast.While(_, body, orelse) | ast.If(_, body, orelse):
                    body_deps = self.collect_dependencies(body, package_name)
                    orelse_deps = self.collect_dependencies(orelse, package_name)
                    deps.update(body_deps)
                    deps.update(orelse_deps)
                case ast.ImportFrom(module, names, level):
                    full_module_name = resolve_full_name(module, level, package_name)
                    if full_module_name.startswith("tyger") or full_module_name.startswith("typing"):
                        continue
                    st.__full_name__ = full_module_name
                    module_tokens = full_module_name.split(".")
                    for i, token in enumerate(module_tokens):
                        module_name = ".".join(module_tokens[:i+1])
                        module_ast = self.parser.parse_module(module_name)
                        module_deps = self.collect_dependencies(module_ast.body, module_name)
                        deps.update(module_deps)
                        deps[module_name] = module_ast

                    for name in names:
                        try:
                            submodule_name = f"{full_module_name}.{name.name}"
                            submodule_ast = self.parser.parse_module(submodule_name)
                            submodule_deps = self.collect_dependencies(submodule_ast.body, submodule_name)
                            deps.update(submodule_deps)
                            deps[submodule_name] = submodule_ast
                        except ModuleNotFoundError:
                            # Maybe the name is in the module
                            continue

                case ast.Import(names):
                    for name in names:
                        if name.name.startswith("tyger") or name.name.startswith("typing"):
                            continue
                        module_tokens = name.name.split(".")
                        for i in range(len(module_tokens)):
                            module_name = ".".join(module_tokens[:i+1])
                            module_ast = self.parser.parse_module(module_name)
                            module_deps = self.collect_dependencies(module_ast.body, module_name)
                            deps.update(module_deps)
                            deps[module_name] = module_ast

        return deps

    def __init__(self, cwd: str = ""):
        self.parser = Parser(cwd)
