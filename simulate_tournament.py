#!/usr/local/bin/python3
import copy
import random
import argparse
import numpy as np
import pandas as pd

from typing import List, Tuple, Dict, Any
# mypy --ignore-missing-imports *.py

def calcExpected(p1: float, p2: float) -> float:
    return 1 / (1 + 10**((p2 - p1) / 400))


def calcExpectedQ(p1: float, p2: float) -> float:
    return p1/(p1+p2)


def simRound(players: List[str], players_elo: Dict) -> List[str]:
    # Simulate a round.
    # For each pairs of players simulate match and return winners
    nextRound = []
    for idx in range(0, len(players), 2):
        playerOne = players[idx]
        playerTwo = players[idx + 1]
        expected = calcExpected(players_elo[playerOne],
                                players_elo[playerTwo])
        if playerTwo == 'bye' or (not playerOne == 'bye' and random.random() < expected):
            winner = playerOne
        else:
            winner = playerTwo
        nextRound.append(winner)
    return nextRound


def simBracket(players: List[str], players_elo: Dict, players_res: Dict) -> None:
    # Simulate Tournament
    # Simulate each round and update player stats
    for _ in range(int(np.log2(len(players)))):
        players = simRound(players, players_elo)
        rem = len(players)
        for player in players:
            players_res[player][rem] += 1


def sims(first_round: List[str], players_elo: Dict, players_res: Dict, iters: int) -> None:
    # Run multiple MC simulations
    for idx in range(iters):
        if idx % (iters / 10) == 0:
            print(f"Iteration: {idx}")
        simBracket(first_round, players_elo, players_res)
    print('Finished!')


def extract_elo(players: List[str], players_elo_df: Any,
                players_elo: Dict, players_res: Dict,
                results: Dict, surface: str) -> Tuple[List[float], int]:
    # Extract elo from dataframe and populate dicts for simulations
    missing = 0
    elo_list = []
    for name in players:
        if name == 'bye':
            # First round bye
            elo = 0.0
        elif name in players_elo_df.index:
            # Ranked player
            elo = players_elo_df.loc[name, surface]
        else:
            # Unranked player/ not found
            missing += 1
            print(f'Missing player: {name}')
            elo = 1000.0

        elo_list.append(elo)
        players_elo[name] = elo
        players_res[name] = copy.deepcopy(results)
    return elo_list, missing


def base_results(draw_size: int) -> Dict:
    # Creat empty dict with results
    results = {}
    for rd in range(int(np.log2(draw_size))-1, -1, -1):
        results[2**rd] = 0
    return results


if __name__ == "__main__":
    # Input parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', action='store', required=True, dest='fname_elo', help='File name of elo ranking')
    parser.add_argument('-d', action='store', required=True, dest='fname_draw', help='File name of the draw')
    parser.add_argument('-i', action='store', required=True, dest='iters', help='Number of MC iterations')
    parser.add_argument('-s', action='store', required=True, dest='surface', help='Surface type Hard|Clay|Grass')
    parser.add_argument('-m', action='store_true', required=False, dest='missing', default=False, help='Check missing players')
    arginput = parser.parse_args()
    iters = int(arginput.iters)
    
    # Prepare output name
    tournament_folder = arginput.fname_draw.split('.')[0]
    tournament_list = tournament_folder.split('/')
    tournament = tournament_list[0] if len(tournament_list) == 1 else tournament_list[1]
    fname_output = f"predictions/{tournament}_res{iters}.csv"
    
    print('-'*120)
    print('Preparing tournament')

    # Read & Create elo dataframe
    players_elo_df = pd.read_csv(arginput.fname_elo)
    players_elo_df['Player'] = players_elo_df['Player'].apply(lambda x: x.lower())
    players_elo_df = players_elo_df.set_index('Player')
    
    # Read & Create draw dataframe
    players_draw_df = pd.read_csv(arginput.fname_draw, header=None, names=['name'])
    players_draw_df['name'] = players_draw_df['name'].apply(lambda x: x.lower())
    first_round = players_draw_df['name'].tolist()

    # Prepare dicts for simulations
    players_elo: Dict = {}
    players_res: Dict = {}
    results = base_results(len(players_draw_df))
    players_draw_df['elo'], missing = extract_elo(first_round, players_elo_df,
                                                  players_elo, players_res, results,
                                                  arginput.surface)
    print(f"Total missing players {missing}")
    if arginput.missing and not missing == 0:
        res = input('Continue ([y]/n): ').lower()
        if res=='n' or res=='no':
            quit()

    # Monte-Carlo Simulation of the tournament
    print('-'*120)
    print('Starting MC simulations')
    sims(first_round, players_elo, players_res, iters)
    
    # Create results dataframe
    players_res_df = pd.DataFrame.from_dict(players_res, orient='index')
    players_res_df.reset_index(inplace=True)
    for key in results:
        players_res_df[key] = players_res_df[key].apply(lambda x: x / iters)
    players_res_df.rename(columns={"index": "name", 8: 'QF', 4: 'SF', 2: 'F', 1: 'W'}, inplace=True)
    
    # Merge Draw and Results dataframes
    players_full_df = pd.merge(players_draw_df, players_res_df, on='name')
    sort_order = list(players_full_df.columns)[1:]
    sort_order.reverse()
    players_full_df.sort_values(by=sort_order, ascending=False, inplace=True)
    players_full_df = players_full_df.set_index('name')

    # Print and save resuls
    print('-'*120)
    print(players_full_df.head(10))
    print('-'*120)
    print(f"Saving file: {fname_output}")
    print('-'*120)
    players_full_df.to_csv(fname_output)
