from seahorse.prelude import *
from run_token import mint_rewards  # Import for CPI

declare_id('3DwGL4aQ4ypgTrLNpMimy7gt8ASJndjW2Hed6T9S6Sjj')

class RaceState(Account):
    active: bool
    step_count: u8
    positions: Array[u8, 4]
    odds: Array[u8, 4]
    winner: Option[u8]
    bets: Map[Pubkey, u64]
    runner_bets: Map[Pubkey, u8]
    total_pool: u64

@instruction
def start_race(authority: Signer, race: Empty[RaceState]):
    race = race.init(payer=authority)
    race.active = True
    race.step_count = 0
    race.total_pool = 0
    for i in range(4):
        race.positions[i] = 0
        race.odds[i] = 25

@instruction
def place_bet(
    authority: Signer,
    race: RaceState,
    user_token: TokenAccount,
    vault: TokenAccount,
    token_program: TokenProgram,
    runner_id: u8,
    amount: u64
):
    assert race.active, "No active race"
    assert runner_id < 4, "Invalid runner"
    user_token.transfer(authority, vault, amount)
    race.bets[authority.key()] = race.bets.get(authority.key(), 0) + amount
    race.runner_bets[authority.key()] = runner_id
    race.total_pool += amount

@instruction
def run_step(
    race: RaceState,
    vault: TokenAccount,
    user_token: TokenAccount,  # Simplified; needs per-user resolution
    run_treasury: TokenAccount,
    run_mint: Token,
    run_state: ProgramState,
    switchboard: SwitchboardFunctionAccountData,
    token_program: TokenProgram,
    run_program: Program
):
    assert race.active, "No active race"
    assert race.step_count < 8, "Race finished"
    random = switchboard.latest_result % 100
    cumulative = 0
    for i in range(4):
        cumulative += race.odds[i]
        if random < cumulative:
            race.positions[i] += 1
            if race.positions[i] >= 8:
                race.winner = i
                race.active = False
                distribute_payouts(race, vault, user_token, run_treasury, run_mint, run_state, token_program, run_program)
            break
    race.step_count += 1

def distribute_payouts(
    race: RaceState,
    vault: TokenAccount,
    user_token: TokenAccount,  # Placeholder
    run_treasury: TokenAccount,
    run_mint: Token,
    run_state: ProgramState,
    token_program: TokenProgram,
    run_program: Program
):
    winner = race.winner.unwrap()
    fee = race.total_pool // 20  # 5% fee
    payout_pool = race.total_pool - fee
    vault.transfer(vault, run_treasury, fee)  # Needs PDA authority
    for user, bet in race.bets.items():
        if race.runner_bets[user] == winner:
            payout = (bet * payout_pool) // race.total_pool
            vault.transfer(vault, user_token, payout)  # Simplified
            mint_rewards(run_program, run_state, user_token, run_mint, run_treasury, token_program, 100)
        else:
            mint_rewards(run_program, run_state, user_token, run_mint, run_treasury, token_program, 20)
