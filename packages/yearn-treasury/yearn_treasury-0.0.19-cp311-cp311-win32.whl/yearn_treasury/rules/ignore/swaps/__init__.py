from typing import Final

from dao_treasury import IgnoreSortRule, SortRuleFactory, ignore


swaps: Final[SortRuleFactory[IgnoreSortRule]] = ignore("Swaps")


from yearn_treasury.rules.ignore.swaps.aave import *
from yearn_treasury.rules.ignore.swaps.compound import *
from yearn_treasury.rules.ignore.swaps.gearbox import *
from yearn_treasury.rules.ignore.swaps.pooltogether import *
from yearn_treasury.rules.ignore.swaps.uniswap import *
from yearn_treasury.rules.ignore.swaps.unwrapper import *
from yearn_treasury.rules.ignore.swaps.vaults import *
from yearn_treasury.rules.ignore.swaps.yla import *
