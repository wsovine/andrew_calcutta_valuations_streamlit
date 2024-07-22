import hmac
import streamlit as st
from functions import fetch_probs_from_datagolf, update_workbook_probability_table


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
