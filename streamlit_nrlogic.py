# app.py
import streamlit as st
import pandas as pd
import io, zipfile, gc

from notebook_func_nr import process_input

st.set_page_config(page_title="NR Data Processor")
st.title("📒 NR → Server Splits")

# Initialize flags
if "downloaded" not in st.session_state:
    st.session_state.downloaded = False

uploaded = st.file_uploader(
    "Upload your NR File",
    type=["xls", "xlsx", "csv"]
)

# 1) Only process if there's an upload, we haven't processed yet, and not downloaded
if uploaded is not None and "file_outputs" not in st.session_state and not st.session_state.downloaded:
    if uploaded.name.lower().endswith(("xls", "xlsx")):
        df_in = pd.read_excel(uploaded)
    else:
        df_in = pd.read_csv(uploaded)

    with st.spinner("Processing…"):
        st.session_state.file_outputs = process_input(df_in)

    # drop the large DataFrame reference
    del df_in
    gc.collect()

    st.success("✅ Processing complete — ready to download!")

# 2) If processing is done and not yet downloaded, show the ZIP download
if "file_outputs" in st.session_state and not st.session_state.downloaded:
    # Build ZIP once
    if "zip_buffer" not in st.session_state:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for fname, buf in st.session_state.file_outputs:
                zf.writestr(fname, buf.getvalue())
        zip_buffer.seek(0)
        st.session_state.zip_buffer = zip_buffer

    # Download button
    clicked = st.download_button(
        label="📥 Download all Server files as ZIP",
        data=st.session_state.zip_buffer,
        file_name="NR_server_files.zip",
        mime="application/zip"
    )

    if clicked:
        # Mark downloaded and free memory
        st.session_state.downloaded = True
        del st.session_state.file_outputs
        del st.session_state.zip_buffer
        gc.collect()
        st.success("🗑️ Memory cleared. Reload or re-upload to process another file.")

# 3) If we've already downloaded, just show a prompt
elif st.session_state.downloaded:
    st.info("You’ve downloaded and freed memory. To run again, reload the page or upload a new file.")
