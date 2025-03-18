from seahorse.prelude import *

declare_id('RunTokenProgramId')

class ProgramState(Account):
    treasury: Pubkey
    mint: Pubkey

@instruction
def initialize(
    authority: Signer,
    state: Empty[ProgramState],
    treasury: TokenAccount,
    mint: Token,
    token_program: TokenProgram
):
    state = state.init(payer=authority)
    state.treasury = treasury.key()
    state.mint = mint.key()

@instruction
def mint_rewards(
    state: ProgramState,
    user_token: TokenAccount,
    mint: Token,
    treasury: TokenAccount,
    token_program: TokenProgram,
    amount: u64
):
    mint.mint_to(user_token, treasury, amount)

@instruction
def burn_for_boost(
    authority: Signer,
    user_token: TokenAccount,
    mint: Token,
    token_program: TokenProgram,
    amount: u64
):
    assert amount >= 500, "Insufficient burn"
    user_token.burn(authority, amount)
    # Odds boost would call RaceProgram (not implemented here)

@instruction
def buy_upgrade(
    authority: Signer,
    user_token: TokenAccount,
    treasury: TokenAccount,
    token_program: TokenProgram,
    amount: u64
):
    assert amount >= 1000, "Insufficient burn"
    user_token.transfer(authority, treasury, amount)
    # Upgrade logic would call RaceProgram
