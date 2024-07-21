import streamlit as st
from functions import fetch_probs_from_datagolf, update_workbook_probability_table


file_name = 'Auction Valuations v1.xlsx'


def refresh_and_download_workbook():
    df_probs = fetch_probs_from_datagolf()
    update_workbook_probability_table(df_probs, file_name=file_name)


st.title('Calcutta Auction Valuation')

with open(file_name, "rb") as template_file:
    refresh_and_download_workbook()
    template_byte = template_file.read()

    st.download_button(label="Download Workbook",
                       data=template_byte,
                       file_name=f"{file_name}",
                       mime='application/octet-stream')
