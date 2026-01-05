import sys
import importlib

from app import Application


def get_args():
    args = {}

    if len(sys.argv) == 2:
        args['example_name'] = sys.argv[1]

    return args 

def main():
    args = get_args()

    # 
    example_name = args.get('example_name')
    
    # 
    app = Application(confs={})
    app.run_example_names(example_name)

if __name__ == "__main__":
    main()
