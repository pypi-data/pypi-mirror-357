from typing import Dict, Optional, Mapping, Any
from collections.abc import Mapping, MutableMapping
from collections import OrderedDict
from copy import deepcopy
from weakref import ref
from torch import nn


class ModelScheduler(nn.Module):
    __attr__: Dict[str, Any]
    model_reference: ref[nn.Module]

    @staticmethod
    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        nn.Module.__init__(instance)
        instance.__dict__['__attr__'] = {}
        return instance
    
    def __init__(self, model: nn.Module):
        device = next(model.parameters()).device
        self.__dict__['model_reference'] = ref(model)
        self.model = deepcopy(model).to(device)
        self.to(device)
        self.count = 0
    
    def __setattr__(self, name, value):
        dict_length = len(self.__dict__)
        if name in self.__attr__:
            self.__attr__.pop(name)
        super().__setattr__(name, value)
        if len(self.__dict__) > dict_length:
            self.__dict__.pop(name)
            self.__attr__[name] = value
    
    def __delattr__(self, name):
        if name in self.__attr__:
            self.__attr__.pop(name)
        else:
            super().__delattr__(name)
    
    def __getattr__(self, name):
        if name in self.__attr__:
            return self.__attr__[name]
        return super().__getattr__(name)
    
    def __repr__(self):
        return super().__repr__()
    
    def update_model(self):
        pass
    
    def step(self):
        self.update_model()
        self.count += 1
    
    def state_dict(self, *args, destination: Optional[Mapping[str, Any]] = None, prefix: str = '', keep_vars: bool = False) -> MutableMapping[str, Any]:
        destination = super().state_dict(*args, destination=destination, prefix=prefix, keep_vars=keep_vars)
        if not isinstance(destination, MutableMapping):
            destination = OrderedDict(destination.items())
        for name, value in self.__attr__.items():
            destination[prefix + name] = value
        return destination
    
    def _load_from_state_dict(
        self,
        state_dict,
        prefix,
        local_metadata,
        strict,
        missing_keys,
        unexpected_keys,
        error_msgs,
    ):
        if not hasattr(state_dict, '__delitem__'):
            state_dict = OrderedDict(state_dict.items())
        for name in self.__attr__.keys():
            try:
                self.__attr__[name] = state_dict.pop(prefix + name)
            except KeyError:
                missing_keys.append(prefix + name)
        return super()._load_from_state_dict(
            state_dict,
            prefix,
            local_metadata,
            strict,
            missing_keys,
            unexpected_keys,
            error_msgs,
        )