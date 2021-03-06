from typing import Any, Dict, List, Optional

import torch
import torch.nn as nn

from ..utils import Tensors, traverse_model, traverse_params_buffs, model_scopes, _count_elements
from .control_flow_graph import Graph, NodeTypes
from .network_profiler import profileNetwork

__all__ = ['graph_builder', 'profileNetwork']


def graph_builder(model: nn.Module, sample_batch: Tensors, kwargs: Optional[Dict] = None, max_depth: int = 1000, weights: Optional[Dict[str, Any]] = None, basic_blocks: Optional[List[nn.Module]] = None, use_profiler=False) -> Graph:
    '''
    returns a graph that models the control flow of the given network by tracing it's forward pass

    Parameters:
    model:
        the network we wish to model
    sample_batch:
        a sample input to use for tracing
    kwargs:
        keyword args to pass to the model
    max_depth:
        how far down we go in the model tree determines the detail level of the graph
    basic_blocks:
        an optional list of modules that if encountered will not be broken down
    weights:
        an optional dictionary from scopes to Node weights
    use_profiler:
        wether to use weights given by our profiler
        this option supersedes the wieghts option defaults to False
    '''
    weights = weights if weights != None else {}
    if kwargs is None:
        kwargs = {}
    if not isinstance(sample_batch, tuple):
        sample_batch = (sample_batch,)

    if use_profiler:
        weights = profileNetwork(model, sample_batch, kwargs=kwargs, max_depth=max_depth,
                                 basic_blocks=basic_blocks)

    buffer_param_names = map(lambda t: t[1], traverse_params_buffs(model))
    buffer_param_names = list(buffer_param_names)

    layerNames = model_scopes(model, depth=max_depth,
                              basic_blocks=basic_blocks)
    layerNames = list(layerNames)

    # trace the model and build a graph
    with torch.no_grad():
        trace_graph, _ = torch.jit.get_trace_graph(
            model, sample_batch, kwargs)
        trace_graph = trace_graph.graph()

    num_inputs = _count_elements(*sample_batch) + len(kwargs)

    graph = Graph(layerNames, num_inputs, buffer_param_names,
                  trace_graph, weights, basic_blocks, max_depth)

    return graph
