
from experiments.test_loss import test_loss

"""
**ADD TESTS FOR THE FOLLOWING**

under pipeline/utils:
- conveyor_gen
- prod_line

under pipeline/sub_module_wrapper.py:
- make sure that forward propagation doesn't save activations that aren't the first ones
- make sure that the activations are saved in the correct order
- make sure that stuff is calculated correctly
- make sure that backward propagation works properly

under pipeline/pipeline_parallel.py:
- check correctness of __div_to_mbs
- check that forward works and has the same output as the same model undivided
- check that the use of backward works with the hook works like the model undivided
- take a model and create 2 identical copies, train each with the same random state in the start and make sure they are
    the same in the end (should have the same parameters and outputs at every step
- make sure it works with [1, 2, 3, 4] different devices
"""

num_classes = 1000
num_batches = 3
batch_size = 120
image_w = 224
image_h = 224


def run_pipeline_tests():
    # test_resnet50_time()
    test_loss()


if __name__ == '__main__':
    run_pipeline_tests()
