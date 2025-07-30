
  
from dataclasses import dataclass
from typing import Optional, Union, Literal, TypedDict, Any, Tuple, List
from qpace import Ctx, Backtest
from qpace_content import _lib
  
  
def accdist(ctx: Ctx) -> List[float]:
    """
`accdist`
    """

    return _lib.Incr_fn_accdist_648dad(ctx).collect()

class AccdistLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Accdist:
    """
`accdist`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_accdist_648dad(ctx)
        self.locals = AccdistLocals(self.inner)

    def next(self, ) -> Optional[float]:
        return self.inner.next()
    

def rsi(ctx: Ctx, src: List[float], length: Optional[int]) -> List[float]:
    """
`rsi`
    """

    return _lib.Incr_fn_rsi_085b61(ctx).collect(_10091_src=src, _10092_length=length)

class RsiLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Rsi:
    """
`rsi`
    """
    
    def __init__(self, ctx: Ctx):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_rsi_085b61(ctx)
        self.locals = RsiLocals(self.inner)

    def next(self, src: float, length: Optional[int]) -> Optional[float]:
        return self.inner.next(_10091_src=src, _10092_length=length)
    
          