import pandas as pd
import numpy as np
import re
import streamlit as st
from typing import List


def get_odds_cols(df: pd.DataFrame, exclusions: list = []):
    df = df[[c for c in df.columns if c not in exclusions]]
    return df.select_dtypes(include=[np.float64])


def remove_vig(df: pd.DataFrame, market):
    if market == 'win':
        scalar = 1
    elif market == 'frl':
        scalar = 1
    else:
        scalar = int(re.search('\d+$', market)[0])
    for c in df.columns:
        # df[f'{c}_no_vig'] = df[c] - (df[c].sum() - 1) / len(df[c])
        df[f'{c}_no_vig'] = df[c] / (df[c].sum() / scalar)
    return df[[c for c in df.columns if 'no_vig' in c]]


def calculate_consensus(row, clip_at_zero: bool = True):
    val = row.mean()
    if clip_at_zero:
        val = val if val > 0 else 0
    return val


def fetch_probs_from_datagolf(markets: List[str] = ['win', 'top_5', 'top_10', 'top_20', 'frl']) -> pd.DataFrame:
    df_all = pd.DataFrame()

    for market in markets:
        url = f"https://feeds.datagolf.com/betting-tools/outrights?tour=pga&market={market}&file_format=csv&odds_format=percent&key={st.secrets['data_golf_api_key']}"

        df = pd.read_csv(url)
        if df.shape[0] <= 1:
            continue

        df_odds = get_odds_cols(df)
        df_odds['consensus'] = df_odds.apply(lambda r: calculate_consensus(r), axis=1)
        df_odds = remove_vig(df_odds, market)

        df_consensus = df.join(df_odds['consensus_no_vig'])
        df_consensus[f'consensus_{market}'] = df_consensus['consensus_no_vig']

        df_consensus = df_consensus.set_index(['event_name', 'player_name'])[[f'consensus_{market}']]
        if df_all.empty:
            df_all = df_consensus.copy()
        else:
            df_all = df_all.join(df_consensus)

    expected_cols = [f'consensus_{m}' for m in markets]

    for col in expected_cols:
        if col not in df_all.columns:
            df_all[col] = 0

    df_all = df_all[expected_cols].copy()

    # Split out probabilities
    df_all['prob_1'] = df_all['consensus_win']

    prob_2_thru_5 = (df_all['consensus_top_5'] - df_all['consensus_win']) / 4
    for i in range(2, 6):
        df_all[f'prob_{i}'] = prob_2_thru_5

    prob_6_thru_10 = (df_all['consensus_top_10'] - df_all['consensus_top_5']) / 5
    for i in range(6, 11):
        df_all[f'prob_{i}'] = prob_6_thru_10

    prob_11_thru_20 = (df_all['consensus_top_20'] - df_all['consensus_top_10']) / 10
    for i in range(11, 13):
        df_all[f'prob_{i}'] = prob_11_thru_20

    return df_all


def update_workbook_probability_table(df: pd.DataFrame, file_name: str = 'Auction Valuations v1.xlsx'):
    with pd.ExcelWriter(file_name, mode='a', if_sheet_exists='replace') as xl:
        df.to_excel(xl, sheet_name='Probability Table')


def fetch_best_odds(
        markets: List[str] = ['win', 'top_5', 'top_10', 'top_20', 'frl', 'mc', 'make_cut']
) -> pd.DataFrame:
    dfs = []

    for market in markets:
        url = f'https://feeds.datagolf.com/betting-tools/outrights?tour=pga&market={market}&file_format=csv&odds_format=american&key=9d8451cdbdf7bcbbe0a0270ab308'

        df = pd.read_csv(url)
        if df.shape[0] <= 1:
            continue

        df['market'] = 'miss_cut' if market == 'mc' else market

        drop_cols = [
            'datagolf_baseline',
            'datagolf_base_history_fit',
            'dg_id',
            'last_updated'
        ]
        df = df[[c for c in df.columns if c not in drop_cols]]

        dfs.append(df.set_index(['event_name', 'market', 'player_name']))

    df = pd.concat(dfs).reset_index()
    numeric_cols = df.select_dtypes(include='number').columns
    df = df.style.apply(
        lambda x: ['background-color: green' if v == x.max() else '' for v in x],
        subset=numeric_cols,
        axis=1,
    )
    return df


def update_workbook_best_odds(workbook, df):
    with pd.ExcelWriter(workbook, mode='a', if_sheet_exists='replace') as xl:
        df.to_excel(xl, sheet_name='Best Odds', index=False)
