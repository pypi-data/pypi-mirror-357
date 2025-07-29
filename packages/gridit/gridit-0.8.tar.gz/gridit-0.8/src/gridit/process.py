"""Process Gridit command."""

import numpy as np

from . import Grid


class ProcessGridit(Grid):
    """Process Gridit command."""

    def __init__(self, *args, **kwargs):
        fill = kwargs.pop("fill") if "fill" in kwargs else 0
        dtype = kwargs.pop("dtype") if "dtype" in kwargs else np.uint8
        self.new_array(fill=fill, dtype=dtype)
        super().__init__(*args, **kwargs)

    def new_array(self, fill=0, dtype=np.uint8):
        """Initialize a new array object."""
        self.array = np.ma.array(self.shape, dtype=dtype)
        self.array.mask = True

    def array_from_vector(
        self, fname: str, attribute: str, fill=None, refine: int = 1, layer=None
    ):
        """See :py:meth:`Grid.array_from_vector` for all options."""
        if fill is not None and not self.array.mask.all():
            pass
        super().array_from_vector(
            fname=fname, attribute=attribute, refine=refine, layer=layer
        )
