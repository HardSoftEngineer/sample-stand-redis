import traceback

from redis_client import get_client
from loader import load_examples


class Application:
    def __init__(self, confs):
        self.confs = confs

        self.__init_redis_client()
        self.__init_examples()

    def __init_redis_client(self):
        redis_client = get_client()
        if redis_client is None:
            raise ValueError("Error, redis_client is None")
        self.redis_client = redis_client

    def __init_examples(self):
        examples = load_examples("examples")
        if not examples:
            raise ValueError("No examples found")
        self.examples = examples

    def get_example_module(self, example_name):
        if example_name is None:
            return
        if example_name in self.examples:
            module = self.examples[example_name]
            return module

    def run_module(self, name):
        print(f"run name: {name}")
        module = self.get_example_module(name)
        module.do(redis_client=self.redis_client)

    def get_all_example_names(self) -> list[str]:
        example_names = self.examples.keys()
        print(f"example_names: {example_names} type: {type(example_names)} type[0]: {type(example_names[0])}")
        return example_names

    def parse_example_names(self, example_names_str: str | None) -> list[str]:
        """
        Converts the argument string to a list.
        - None        -> []
        - "a"         -> ["a"]
        - "a,b"       -> ["a", "b"]
        - "a, b ,c"   -> ["a", "b", "c"]
        """
        if not example_names_str:
            return []

        return [
            name.strip()
            for name in example_names_str.split(",")
            if name.strip()
        ]

    def prepare_example_names(self, example_names):
        if example_names is None:
            print("Get empty arg example_name, set default all")
            example_names_run = self.get_all_example_names()
        elif isinstance(example_names, str):
            example_names_run = self.parse_example_names(example_names)
        return example_names_run

    def run_example_names(self, example_names):
        example_names_run = self.prepare_example_names(example_names)
        for example_name in example_names_run:
            try:
                print(f"\n=== {example_name} ===")
                self.run_module(example_name)
            except:
                print(traceback.print_exc())
