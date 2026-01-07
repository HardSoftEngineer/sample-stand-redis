import sys
import importlib

from app import Application
from errors import InfrastructureUnavailableError

def get_args():
    args = {}

    if len(sys.argv) == 2:
        args['example_names'] = sys.argv[1]

    return args 

def main():
    args = get_args()

    # 
    example_names = args.get('example_names')
    
    # 
    try:
        app = Application(confs={})
        app.run_example_names(example_names)
    except InfrastructureUnavailableError as exc:
        print(f"[FATAL] {exc}")
        sys.exit(1)

if __name__ == "__main__":
    main()
