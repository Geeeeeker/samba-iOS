# Python 3.12+ compatibility shim for imp module
import sys

try:
    import imp as _imp
except ImportError:
    import importlib
    import importlib.util
    import types

    class _imp:
        """Minimal imp replacement for Python 3.12+"""
        C_EXTENSION = 3
        PY_SOURCE = 1
        PKG_DIRECTORY = 5
        PY_COMPILED = 2
        C_BUILTIN = 6
        PY_FROZEN = 7

        @staticmethod
        def find_module(name, path=None):
            try:
                if path:
                    for p in path:
                        spec = importlib.util.find_spec(name, p)
                        if spec is not None:
                            break
                else:
                    spec = importlib.util.find_spec(name)
            except (ModuleNotFoundError, ValueError):
                spec = None

            if spec is None:
                raise ImportError(f"No module named {name}")
            return (None, spec.origin if spec.origin else "", ('', '', _imp.PKG_DIRECTORY))

        @staticmethod
        def load_module(name, file, pathname, description):
            if pathname and pathname.endswith('.py'):
                spec = importlib.util.spec_from_file_location(name, pathname)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[name] = module
                    spec.loader.exec_module(module)
                    return module
            # Fallback
            return importlib.import_module(name)

        @staticmethod
        def new_module(name):
            return types.ModuleType(name)

        @staticmethod
        def load_source(name, pathname):
            spec = importlib.util.spec_from_file_location(name, pathname)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[name] = module
                spec.loader.exec_module(module)
                return module
            raise ImportError(f"Cannot load source {pathname}")

# Export the module (either real imp or our shim)
imp = _imp
