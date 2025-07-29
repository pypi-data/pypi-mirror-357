from dao_treasury import TreasuryTx
from yearn_treasury.rules.ignore.swaps import swaps


gearbox = swaps("Gearbox")


@gearbox("Deposit")
def is_gearbox_deposit(tx: TreasuryTx) -> bool:
    txhash = tx.hash
    log_index = tx.log_index
    return (
        txhash == "0x5666b03add778468482fb376e65761128f9f5051b487f3efc996a55c3620d6d4"
        and log_index in (366, 367)
    ) or (
        txhash == "0x9e113dda11fcd758df2fe94a641aa7afe6329afec4097a8cb5d6fb68489cf7d8"
        and log_index in (74, 75)
    )


@gearbox("Withdrawal")
def is_gearbox_withdrawal(tx: TreasuryTx) -> bool:
    txhash = tx.hash
    return txhash == "0xb98d8f4dd3d9de50e6fec700fb8e5a732e5a564b7edfe365f97e601694536bb5" or (
        txhash == "0x1d9e7930d0bf6725a4ffff43e284dfa9d10e34e16460e75d01a7f05a98e252a6"
        and tx.log_index in (212, 213)
    )
