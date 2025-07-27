import streamlit as st
import pandas as pd
import zipfile
from pathlib import Path
import tempfile

st.set_page_config(
    page_title="CSV/Excel Merger",
    page_icon="📊",
    layout="wide"
)

def main():
    st.title("📊 CSV/Excel Files Merger")
    st.markdown("Upload a ZIP file containing CSV/Excel files to merge them into a single file")
    
    with st.expander("How to use"):
        st.markdown("""
        1. Create a ZIP file containing your CSV/Excel files
        2. Upload the ZIP using the file uploader below
        3. Wait for processing to complete
        4. Download the merged file
        """)
    
    uploaded_zip = st.file_uploader("Choose a ZIP file", type="zip")
    
    if uploaded_zip:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            zip_path = tmp_path / "uploaded_files.zip"
            
            # Save uploaded file
            with open(zip_path, "wb") as f:
                f.write(uploaded_zip.getvalue())
            
            # Extract ZIP
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmp_path)
                extracted_files = zip_ref.namelist()
            
            if not extracted_files:
                st.warning("ZIP file is empty!")
                return
            
            st.success(f"📁 Extracted {len(extracted_files)} files")
            
            # Read all supported files
            all_dfs = []
            supported_extensions = ('.csv', '.xlsx', '.xls')
            
            for file in extracted_files:
                file_path = tmp_path / file
                ext = file_path.suffix.lower()
                
                if ext not in supported_extensions:
                    st.warning(f"Skipped unsupported file: {file}")
                    continue
                
                try:
                    if ext == '.csv':
                        df = pd.read_csv(file_path)
                    else:  # Excel files
                        df = pd.read_excel(file_path)
                    all_dfs.append(df)
                    st.info(f"✅ Read {file} ({len(df)} rows)")
                except Exception as e:
                    st.error(f"❌ Error reading {file}: {str(e)}")
            
            if not all_dfs:
                st.error("No valid CSV/Excel files found")
                return
            
            # Merge DataFrames
            try:
                merged_df = pd.concat(all_dfs, ignore_index=True)
                st.success(f"🧩 Merged {len(all_dfs)} files into {len(merged_df)} rows")
                
                # Show sample data
                st.subheader("Preview of Merged Data")
                st.dataframe(merged_df.head(10))
                
                # Save to Excel
                output_path = tmp_path / "merged_data.xlsx"
                merged_df.to_excel(output_path, index=False)
                
                # Download button
                with open(output_path, "rb") as f:
                    st.download_button(
                        label="📥 Download Merged File",
                        data=f,
                        file_name="merged_data.xlsx",
                        mime="application/vnd.ms-excel"
                    )
                
            except Exception as e:
                st.error(f"Error merging files: {str(e)}")
    else:
        st.info("👆 Please upload a ZIP file to get started")

if __name__ == "__main__":
    main()