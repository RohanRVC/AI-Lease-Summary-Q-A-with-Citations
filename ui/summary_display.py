import streamlit as st

from extraction.schema import LeaseSummary


def render_lease_summary(summary: LeaseSummary) -> None:
    """Display lease summary as an expandable section and a table-like view."""
    data = summary.to_display_dict()
    with st.expander("Lease summary (structured extraction)", expanded=True):
        for label, value in data.items():
            st.markdown(f"**{label}**  \n{value}")
    # Optional: also as a compact table
    st.dataframe(
        {"Field": list(data.keys()), "Value": list(data.values())},
        width="stretch",
        hide_index=True,
    )
    # Additional terms discovered by LLM (not in standard schema)
    if getattr(summary, "additional_terms_from_document", None) and summary.additional_terms_from_document.strip():
        with st.expander("Additional terms found in document", expanded=True):
            lines = [line.strip() for line in summary.additional_terms_from_document.strip().split("\n") if line.strip()]
            if lines:
                for line in lines:
                    st.markdown(f"- {line}")
            else:
                st.markdown(summary.additional_terms_from_document)
