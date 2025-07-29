import json
import numpy as np


class ucarballJsonEncoder(json.JSONEncoder):
    def default(self, o):
        # it cannot normally serialize np.int64 and possibly other np data types
        if type(o).__module__ == np.__name__:
            return o.item()
        return super(ucarballJsonEncoder, self).default(o)
