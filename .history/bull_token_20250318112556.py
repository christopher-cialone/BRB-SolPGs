from seahorse.prelude import *
from run_token import mint_rewards  # Import for CPI

# declare_id('3DwGL4aQ4ypgTrLNpMimy7gt8ASJndjW2Hed6T9S6Sjj')
declare_id('3DwGL4aQ4ypgTrLNpMimy7gt8ASJndjW2Hed6T9S6Sjj')

class ProgramState(Account):
    treasury: Pubkey
    mint: Pubkey
    total_staked: u64

class UserData(Account):
    staked_amount: u64
    stake_timestamp: i64

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
    state.total_staked = 0
    mint.mint_to(treasury, authority, 75_000_000)  # 75M BULL initial supply

@instruction
def stake(
    authority: Signer,
    state: ProgramState,
    user: Empty[UserData],
    user_token: TokenAccount,
    vault: TokenAccount,
    token_program: TokenProgram
):
    user = user.init(payer=authority)
    user_token.transfer(authority, vault, amount)
    user.staked_amount += amount
    user.stake_timestamp = Clock.get().unix_timestamp
    state.total_staked += amount

@instruction
def unstake(
    authority: Signer,
    state: ProgramState,
    user: UserData,
    user_token: TokenAccount,
    vault: TokenAccount,
    token_program: TokenProgram
):
    assert user.staked_amount >= amount, "Insufficient stake"
    current_time = Clock.get().unix_timestamp
    staked_days = (current_time - user.stake_timestamp) // 86400
    reward = (amount * staked_days * 5) // 36500  # 5% APY simplified
    vault.transfer(authority, user_token, amount + reward)
    user.staked_amount -= amount
    state.total_staked -= amount

@instruction
def burn_for_perks(
    authority: Signer,
    user_token: TokenAccount,
    mint: Token,
    run_user_token: TokenAccount,
    run_mint: Token,
    run_treasury: TokenAccount,
    run_state: ProgramState,
    token_program: TokenProgram,
    run_program: Program
):
    assert amount >= 1000, "Insufficient burn"
    user_token.burn(authority, amount)
    run_amount = amount // 10  # 100 RUN per 1000 BULL
    mint_rewards(run_program, run_state, run_user_token, run_mint, run_treasury, token_program, run_amount)


