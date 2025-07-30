""" 2. Input Transformer with Timing Analysis """
from IPython import get_ipython
import time

from IPython.core.inputtransformer2 import TransformerManager


class PasteDetectionTransformer(TransformerManager):
    def __init__(self, *args, **kwargs):
        self.last_input_time = 0
        self.input_history = []
        super().__init__(*args, **kwargs)

    def transform_cell(self, cell):
        current_time = time.time()
        time_since_last = current_time - self.last_input_time

        # If entire cell appeared very quickly, likely pasted
        if len(cell.strip()) > 20 and time_since_last < 1.0:
            print(f"\n⚠️  Large input detected in {time_since_last:.2f}s - was this pasted?")
            response = input("Did you paste this code? (y/n): ")
            if response.lower().startswith('y'):
                print("💡 Try retyping it for better learning retention!")

        self.last_input_time = current_time
        self.input_history.append((cell, current_time))

        return cell


ip = None


def install():
    """ Install transformer into the current iPython session """
    global ip
    ip = get_ipython()
    paste_detector = PasteDetectionTransformer()
    ip.input_transformer_manager.cleanup_transforms.append(paste_detector.transform_cell)


if __name__ == '__main__':
    ip = install()
