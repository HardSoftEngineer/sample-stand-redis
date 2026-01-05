import pkgutil
import importlib
from types import ModuleType
from typing import Dict


def load_examples(package_name):
    """
    Loads all modules from the examples package,
    containing the function do(redis_client)
    """
    examples = {}

    package = importlib.import_module(package_name)

    for module_info in pkgutil.iter_modules(package.__path__):
        name = module_info.name

        if name.startswith("_"):
            continue

        full_module_name = f"{package_name}.{name}"
        module = importlib.import_module(full_module_name)

        if hasattr(module, "do"):
            examples[name] = module

    return examples
