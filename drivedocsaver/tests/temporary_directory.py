import os
import random
import shutil
import tempfile


class TemporaryDirectory(object):
    def __init__(self):
        if "RUNNER_TEMP" in os.environ:
            temporary_dir_path = os.path.join(os.environ["RUNNER_TEMP"],
                                              str(random.randint(0, 9999999999999)))
            os.makedirs(temporary_dir_path)
            self.path = temporary_dir_path
        else:
            self.path = tempfile.mkdtemp()
        print(f"Created temporary directory at {self.path}")

    def __enter__(self):
        return self.path

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.path)
        print(f"Deleted temporary directory at {self.path}")
