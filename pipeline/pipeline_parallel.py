import torch
import torch.nn as nn

from pipeline.utils import prod_line
from pipeline.sub_module_wrapper import SubModuleWrapper


class PipelineParallel(nn.Module):
    """

    """

    def __init__(self, submodules, devices, mb_size):
        super(PipelineParallel, self).__init__()

        self.mb_size = mb_size
        self.devices = devices
        self.submodules = [SubModuleWrapper(sm, dev) for sm, dev in
                           zip(submodules, devices)]

    def __div_to_mbs(self, tensor: torch.Tensor) -> torch.Tensor:
        return tensor.view((-1, self.mb_size, *tuple(tensor.shape[1:])))

    def forward(self, input: torch.Tensor):
        input = self.__div_to_mbs(input)

        results = prod_line(
            input, self.submodules,
            last_ac=lambda x: x.to('cpu')
        )

        return torch.cat(results, dim=0)

    def backward(self, loss_fn, results, targets):
        num_samples = float(results.shape[0])
        results = self.__div_to_mbs(results)
        targets = self.__div_to_mbs(targets)

        losses = [loss_fn(res.detach(), tar.detach()) for res, tar in
                  zip(results, targets)]
        losses = [torch.sum(loss) / num_samples for loss in losses]

        for loss in losses:
            loss.backwards()

        grads = [loss.grad for loss in losses[::-1]]

        actions = [m.backward for m in self.submodules[::-1]]
        prod_line(grads, actions, output_results=False)
