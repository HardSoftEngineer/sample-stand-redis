import sys
import importlib

from redis_client import get_client

EXAMPLES = {
    "kv": "basic_kv",
    "lists": "lists",
    "hashes": "hashes",
}


def run_example(example_name: str, redis_client) -> bool:
    module_name = EXAMPLES.get(example_name)

    if not module_name:
        print(f"[ERROR] Example '{example_name}' is not registered")
        return False

    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as e:
        print(f"[ERROR] Module '{module_name}' not found: {e}")
        return False

    if not hasattr(module, "do"):
        print(f"[ERROR] Example '{example_name}' has no do(redis_client)")
        return False

    try:
        module.do(redis_client=redis_client)
    except Exception as e:
        print(f"[ERROR] Runtime error in example '{example_name}': {e}")
        return False

    return True


def print_help():
    print("Usage: python main.py <example|all>")
    print("Available examples:")
    for name in EXAMPLES:
        print(f" - {name}")

def get_args():
    args = {}

    # 
    if len(sys.argv) < 2:
        print_help()

    elif len(sys.argv) == 2:
        args['example_name'] = sys.argv[1]

    return args 

def main():
    args = get_args()
    
    # 
    redis_client = get_client()
    if redis_client is None:
        print(f"Error, redis_client is None")
        return

    # 
    example_name = args.get('example_name')
    if example_name is None:
        example_name = "all"
    # 
    if example_name == "all":
        print("Running  all examples")
        for name in EXAMPLES:
            print(f"Example: {name}")
            run_example(example_name=name, redis_client=redis_client)
        return
    # 
    elif example_name not in EXAMPLES:
        print(f"Unknown example: {example_name}")
        return 
    
    run_example(example_name=example_name, redis_client=redis_client)

if __name__ == "__main__":
    main()
