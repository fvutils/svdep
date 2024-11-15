import dataclasses as dc
from typing import List

@dc.dataclass
class FileInfo(object):
    name : str
    timestamp : int
    checked : bool = False
    includes : List[str] = dc.field(default_factory=list)

    def to_dict(self):
        ret = {
            "name": self.name,
            "timestamp": self.timestamp,
            "includes": []
        }
        for inc in self.includes:
            ret["includes"].append(inc)
        
        return ret

