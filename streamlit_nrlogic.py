# app.py
import streamlit as st
import pandas as pd
import io, zipfile, gc

from notebook_func_nr import process_input

st.set_page_config(page_title="NR Data Processor")
st.title("📒 NR data file → Server Uploadable Splits")

# ─── 1) Initialize session‐state flag ────────────────────────────
if "downloaded" not in st.session_state:
    st.session_state.downloaded = False

# ─── 2) Show uploader only if we haven't downloaded yet ──────────
if not st.session_state.downloaded:
    uploaded = st.file_uploader(
        "Upload your NR File",
        type=["xls", "xlsx", "csv"],
        key="uploader"
    )
else:
    uploaded = None

# ─── 3) Process the uploaded file once ──────────────────────────
if (
    uploaded is not None
    and "file_outputs" not in st.session_state
    and not st.session_state.downloaded
):
    # Read into DataFrame
    if uploaded.name.lower().endswith(("xls", "xlsx")):
        df_in = pd.read_excel(uploaded)
    else:
        df_in = pd.read_csv(uploaded)

    with st.spinner("Processing…"):
        # process_input should return List[Tuple[str, BytesIO]]
        st.session_state.file_outputs = process_input(df_in)

    # Free the original DataFrame
    del df_in
    gc.collect()

    st.success("✅ Processing complete — ready to download!")

# ─── 4) Build ZIP & show download button ─────────────────────────
if "file_outputs" in st.session_state and not st.session_state.downloaded:
    # Build ZIP once
    if "zip_buffer" not in st.session_state:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for fname, file_buf in st.session_state.file_outputs:
                zf.writestr(fname, file_buf.getvalue())
        buf.seek(0)
        st.session_state.zip_buffer = buf

    # Single download button for all server files
    clicked = st.download_button(
        label="📥 Download all Server files as ZIP",
        data=st.session_state.zip_buffer,
        file_name="NR_server_files.zip",
        mime="application/zip"
    )

    if clicked:
        # 1) Mark downloaded
        st.session_state.downloaded = True

        # 2) Drop everything big
        del st.session_state.file_outputs
        del st.session_state.zip_buffer

        # 3) Also remove the uploader’s stored file
        st.session_state.pop("uploader", None)

        # 4) Force a GC sweep
        gc.collect()

        st.success("🗑️ Memory cleared. Reload or re-upload to process another file.")

# ─── 5) After download, just show a prompt ────────────────────────
elif st.session_state.downloaded:
    st.info("You’ve downloaded and freed memory. To run again, reload the page or upload a new file.")
