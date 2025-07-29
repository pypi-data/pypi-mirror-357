from dao_treasury import TreasuryTx

from yearn_treasury.rules.ignore.swaps import swaps


@swaps("Unwrapper")
def is_unwrapper(tx: TreasuryTx) -> bool:
    return "Contract: Unwrapper" in [tx.from_nickname, tx.to_nickname]
