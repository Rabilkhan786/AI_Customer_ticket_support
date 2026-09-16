
"""Streamlit UI for the support ticket system."""

import os

import pandas as pd
import requests
import streamlit as st


API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000",
)


st.set_page_config(
    page_title="AI Support Ticket Intelligence",
    page_icon="🎫",
    layout="wide",
)


st.title("AI Support Ticket Intelligence")
st.write(
    "Ask questions about support tickets and "
    "view detected anomalies."
)


# -------------------------
# Natural-language queries
# -------------------------

st.header("Ask a Question")

question = st.text_input(
    "Enter your question",
    placeholder="How many tickets are currently open?",
)

if st.button("Ask"):
    if not question.strip():
        st.warning("Please enter a question.")

    else:
        try:
            response = requests.post(
                f"{API_URL}/query",
                json={"question": question},
                timeout=30,
            )

            response.raise_for_status()
            result = response.json()

            if result["sql"] is None:
                st.warning(result["explanation"])

            else:
                st.subheader("Result")

                data = result["data"]

                if data:
                    st.dataframe(
                        pd.DataFrame(data),
                        use_container_width=True,
                    )
                else:
                    st.info("No matching records found.")

                st.subheader("Explanation")
                st.write(result["explanation"])

                with st.expander("Generated SQL"):
                    st.code(
                        result["sql"],
                        language="sql",
                    )

        except requests.RequestException as error:
            st.error(
                f"Could not connect to the API: {error}"
            )


# -------------------------
# Anomaly detection
# -------------------------

st.divider()
st.header("Anomaly Detection")

if st.button("Detect Anomalies"):
    try:
        response = requests.get(
            f"{API_URL}/anomalies",
            timeout=30,
        )

        response.raise_for_status()
        result = response.json()

        resolution_anomalies = result[
            "resolution_time_anomalies"
        ]

        priority_anomalies = result[
            "priority_anomalies"
        ]

        st.subheader(
            f"Long Resolution Times "
            f"({len(resolution_anomalies)})"
        )

        if resolution_anomalies:
            st.dataframe(
                pd.DataFrame(resolution_anomalies),
                use_container_width=True,
            )
        else:
            st.info(
                "No long resolution-time anomalies found."
            )

        st.subheader(
            f"Unresolved High/Critical Tickets "
            f"({len(priority_anomalies)})"
        )

        if priority_anomalies:
            st.dataframe(
                pd.DataFrame(priority_anomalies),
                use_container_width=True,
            )
        else:
            st.info(
                "No unresolved priority anomalies found."
            )

    except requests.RequestException as error:
        st.error(
            f"Could not connect to the API: {error}"
        )