import hmac

import pandas as pd
import streamlit as st
from functions import (
    fetch_probs_from_datagolf,
    update_workbook_probability_table,
    fetch_best_odds,
    update_workbook_best_odds,
    read_auction_bid_export,
    update_workbook_auction_table,
)


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.


file_name = 'Auction Valuations v3.xlsx'


def refresh_whole_new_workbook(auction_bid_export: pd.DataFrame):
    update_workbook_probability_table(fetch_probs_from_datagolf(), file_name=file_name)
    update_workbook_best_odds(file_name, fetch_best_odds())
    update_workbook_auction_table(file_name, auction_bid_export)


st.title('Calcutta Auction Valuation')

st.markdown('## Before or During Auction')
st.markdown('### Download New Workbook')
auction_bids = st.file_uploader("Load export from auction site", type="xlsx")
if auction_bids is not None:
    # st.success('You may now download the workbook.')
    df_bid_export = read_auction_bid_export(auction_bids)
    with open(file_name, "rb") as file:
        refresh_whole_new_workbook(df_bid_export)
        file_byte = file.read()

        st.download_button(label="Download Pre-Auction Workbook",
                           data=file_byte,
                           file_name=f"{file_name}",
                           mime='application/octet-stream')

st.markdown('---')
st.markdown('## Updates After Auction')
auction_workbook = st.file_uploader("Select in-progress workbook", type="xlsx")
st.markdown('### Update Best Odds tab')
if auction_workbook is not None:
    with pd.ExcelFile(auction_workbook) as xl:
        update_workbook_best_odds(xl, fetch_best_odds())

        st.download_button(label="Fetch Latest Odds",
                           data=xl.io.getvalue(),
                           file_name=f"{auction_workbook.name}",
                           mime='application/octet-stream')
else:
    st.warning("Please load existing auction workbook. For a brand new workbook with latest odds, "
               "simply download a new pre-auction workbook.")

