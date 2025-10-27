import streamlit as st
import pandas as pd
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os
import re
from datetime import datetime
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="GST Invoice & Annexure Generator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .title-section {
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Helper functions
def merge_address(order_row):
    """Merge address fields from order data"""
    cols = [
        'Ship To Address Line 1',
        'Ship To Address Line 2',
        'Ship To Address Line 3',
        'Ship To City',
        'Ship To State',
        'Ship To ZIP Code',
    ]
    
    address_parts = []
    for col in cols:
        val = str(order_row.get(col, ''))
        if val and val != 'nan' and val.strip():
            address_parts.append(val.strip())
    return ', '.join(address_parts)

def sanitize_filename(filename):
    """Remove invalid characters from filename"""
    filename = filename.replace('/', '_').replace('\\', '_')
    filename = re.sub(r'[<>:"|?*]', '_', filename)
    return filename

def format_date_only(date_str):
    """Extract only date from datetime string"""
    try:
        date_str = str(date_str).strip()
        if 'PM' in date_str or 'AM' in date_str:
            date_part = date_str.split('PM')[0].split('AM')[0].strip()
        else:
            date_part = date_str
        date_part = re.sub(r'\d{1,2}:\d{2}:\d{2}\s*', '', date_part).strip()
        return date_part
    except:
        return date_str

def clean_currency(value):
    """Clean currency value"""
    try:
        val_str = str(value).strip()
        val_str = val_str.replace('₹', '').replace('Rs.', '').replace('Rs', '')
        val_str = val_str.replace(',', '').strip()
        return float(val_str)
    except ValueError:
        return 0.0

class PDFInvoice(FPDF):
    def __init__(self):
        super().__init__()
        self.is_annexure_page = False

    def header(self):
        if self.is_annexure_page:
            return
        
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 10, 'TAX INVOICE', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.ln(4)
        
        self.set_font('Helvetica', 'B', 10)
        self.cell(0, 5, 'Bill From:', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('Helvetica', '', 9)
        self.multi_cell(0, 4, 'KAMALA-E-RETAIL,\n34-C, Shreeji Estate Vasta Devdi Road,\nSURAT GUJARAT - 395004\nGSTIN: 24ABAFK8424H1ZG', align='L')
        self.ln(2)
        
        self.set_font('Helvetica', 'B', 10)
        self.cell(0, 5, 'Bill To:', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('Helvetica', '', 9)
        self.multi_cell(0, 4, 'COCOBLU RETAIL LIMITED,\n71, Brahmin Mitra Mandal Society,\nOpp. Jalram Temple, Ellisbridge, AHMEDABAD, GUJARAT - 380006\nGSTIN: 24AAJCC8517E1ZR', align='L')
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')

# Initialize session state
if 'invoice_df' not in st.session_state:
    st.session_state.invoice_df = None
if 'orders_df' not in st.session_state:
    st.session_state.orders_df = None

# Title
st.markdown("<div class='title-section'><h1>📄 GST Invoice & Annexure Generator</h1></div>", unsafe_allow_html=True)

# Sidebar
st.sidebar.header("📁 File Management")

invoice_file = st.sidebar.file_uploader(
    "📋 Upload Invoice CSV",
    type="csv",
    key="invoice_uploader"
)

if invoice_file:
    try:
        st.session_state.invoice_df = pd.read_csv(invoice_file)
        st.sidebar.success("✓ Invoice CSV Loaded")
    except Exception as e:
        st.sidebar.error(f"✗ Error: {str(e)}")

orders_file = st.sidebar.file_uploader(
    "📋 Upload Orders CSV",
    type="csv",
    key="orders_uploader"
)

if orders_file:
    try:
        st.session_state.orders_df = pd.read_csv(orders_file)
        st.sidebar.success("✓ Orders CSV Loaded")
    except Exception as e:
        st.sidebar.error(f"✗ Error: {str(e)}")

# Main content
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.session_state.invoice_df is None or st.session_state.orders_df is None:
        st.info("📌 Upload both CSV files from the sidebar")
    else:
        invoice_ids = sorted(st.session_state.invoice_df['Invoice ID'].unique().tolist())
        selected_invoice_id = st.selectbox("🏷️ Select Invoice ID:", options=invoice_ids)
        
        if st.checkbox("Preview Data"):
            preview_data = st.session_state.invoice_df[
                st.session_state.invoice_df['Invoice ID'] == selected_invoice_id
            ]
            st.dataframe(preview_data, use_container_width=True)
        
        if st.button("🔄 Generate Merged PDF", use_container_width=True):
            try:
                with st.spinner("⏳ Generating PDF..."):
                    sub_inv = st.session_state.invoice_df[
                        st.session_state.invoice_df['Invoice ID'] == selected_invoice_id
                    ]
                    
                    if sub_inv.empty:
                        st.error("❌ No data found")
                    else:
                        pdf = PDFInvoice()
                        pdf.set_auto_page_break(auto=True, margin=15)
                        pdf.add_page()
                        
                        invoice_date = format_date_only(sub_inv.iloc[0]['Invoice date'])
                        
                        pdf.set_font("Helvetica", 'B', 10)
                        pdf.cell(95, 6, f"Invoice No.: {selected_invoice_id}", border=1, align='L')
                        pdf.cell(0, 6, f"Invoice Date: {invoice_date}", border=1, align='L')
                        pdf.ln()
                        pdf.ln(4)
                        
                        col_names = ["ASIN", "SKU", "HSN", "Qty", "Rate", "Amount", "GST%", "CGST", "SGST", "Total"]
                        col_widths = [22, 28, 18, 12, 18, 20, 12, 18, 18, 22]
                        
                        pdf.set_font("Helvetica", 'B', 9)
                        pdf.set_fill_color(200, 200, 200)
                        for i, col in enumerate(col_names):
                            pdf.cell(col_widths[i], 7, col, border=1, align='C', fill=True)
                        pdf.ln()
                        
                        pdf.set_font("Helvetica", '', 8)
                        grand_total = 0
                        total_cgst = 0
                        total_sgst = 0
                        total_amount = 0
                        
                        for idx, row in sub_inv.iterrows():
                            qty = int(row['Quantity'])
                            item_cost = clean_currency(row['Item Cost'])
                            rate = item_cost / qty if qty else 0
                            gst_rate_str = str(row['GST Rate']).replace('%', '').strip()
                            gst_rate = float(gst_rate_str)
                            cgst_amt = item_cost * gst_rate / 100 / 2
                            sgst_amt = item_cost * gst_rate / 100 / 2
                            total = item_cost + cgst_amt + sgst_amt
                            
                            total_amount += item_cost
                            total_cgst += cgst_amt
                            total_sgst += sgst_amt
                            grand_total += total
                            
                            vals = [
                                str(row['ASIN'])[:22],
                                str(row['SKU'])[:28],
                                str(row['HSN'])[:18],
                                str(qty),
                                f"{rate:.2f}",
                                f"{item_cost:.2f}",
                                f"{gst_rate:.0f}%",
                                f"{cgst_amt:.2f}",
                                f"{sgst_amt:.2f}",
                                f"{total:.2f}"
                            ]
                            
                            for i, val in enumerate(vals):
                                pdf.cell(col_widths[i], 6, str(val), border=1, align='C')
                            pdf.ln()
                        
                        pdf.set_font("Helvetica", 'B', 9)
                        pdf.set_fill_color(220, 220, 220)
                        total_col_width = sum(col_widths[0:5])
                        
                        pdf.cell(total_col_width, 7, 'TOTAL', border=1, align='R', fill=True)
                        pdf.cell(col_widths[5], 7, f"{total_amount:.2f}", border=1, align='C', fill=True)
                        pdf.cell(col_widths[6], 7, '', border=1, align='C', fill=True)
                        pdf.cell(col_widths[7], 7, f"{total_cgst:.2f}", border=1, align='C', fill=True)
                        pdf.cell(col_widths[8], 7, f"{total_sgst:.2f}", border=1, align='C', fill=True)
                        pdf.cell(col_widths[9], 7, f"{grand_total:.2f}", border=1, align='C', fill=True)
                        pdf.ln(8)
                        
                        pdf.set_font("Helvetica", 'B', 11)
                        pdf.set_fill_color(76, 175, 80)
                        pdf.set_text_color(255, 255, 255)
                        pdf.cell(0, 8, f"Grand Total: Rs. {grand_total:.2f}", border=1, align='C', fill=True)
                        pdf.set_text_color(0, 0, 0)
                        pdf.ln(12)
                        
                        pdf.set_font("Helvetica", '', 9)
                        pdf.cell(0, 5, 'For KAMLA-E-RETAIL', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='R')
                        pdf.ln(15)
                        pdf.cell(0, 5, 'Authorized Signatory', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='R')
                        
                        pdf.is_annexure_page = True
                        pdf.add_page()
                        
                        pdf.set_font('Helvetica', 'B', 14)
                        pdf.cell(0, 10, 'Annexure', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
                        pdf.ln(8)
                        
                        pdf.set_font('Helvetica', 'B', 10)
                        pdf.set_fill_color(200, 200, 200)
                        pdf.cell(35, 8, 'Order ID', 1, align='C', fill=True)
                        pdf.cell(45, 8, 'Invoice ID', 1, align='C', fill=True)
                        pdf.cell(0, 8, 'Address', 1, align='C', fill=True)
                        pdf.ln()
                        
                        pdf.set_font('Helvetica', '', 9)
                        inv_orders = sub_inv['Order ID'].unique().tolist()
                        
                        for oid in inv_orders:
                            order_match = st.session_state.orders_df[
                                st.session_state.orders_df['Order ID'] == oid
                            ]
                            
                            if not order_match.empty:
                                order_row = order_match.iloc[0]
                                addr = merge_address(order_row)
                            else:
                                addr = 'Address not found'
                            
                            lines = []
                            current_line = ""
                            words = addr.split(' ')
                            
                            for word in words:
                                if len(current_line) + len(word) + 1 <= 50:
                                    current_line += word + ' '
                                else:
                                    if current_line.strip():
                                        lines.append(current_line.strip())
                                    current_line = word + ' '
                            
                            if current_line.strip():
                                lines.append(current_line.strip())
                            
                            if not lines:
                                lines = [addr]
                            
                            pdf.cell(35, 7, str(oid), 1, align='L')
                            pdf.cell(45, 7, str(selected_invoice_id), 1, align='L')
                            pdf.cell(0, 7, lines[0], 1, align='L')
                            pdf.ln()
                            
                            for i in range(1, len(lines)):
                                pdf.cell(35, 7, '', 1, align='L')
                                pdf.cell(45, 7, '', 1, align='L')
                                pdf.cell(0, 7, lines[i], 1, align='L')
                                pdf.ln()
                        
                        pdf_bytes = pdf.output()
                        
                        st.success("✅ PDF Generated Successfully!")
                        
                        safe_invoice_id = sanitize_filename(selected_invoice_id)
                        filename = f"Invoice_Annexure_{safe_invoice_id}.pdf"
                        
                        st.download_button(
                            label="⬇️ Download PDF",
                            data=pdf_bytes,
                            file_name=filename,
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Amount", f"₹{total_amount:.2f}")
                        with col2:
                            st.metric("CGST", f"₹{total_cgst:.2f}")
                        with col3:
                            st.metric("SGST", f"₹{total_sgst:.2f}")
                        with col4:
                            st.metric("Grand Total", f"₹{grand_total:.2f}")
                        
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

st.divider()
st.markdown("""
    <div style='text-align: center; color: #999; font-size: 12px; margin-top: 2rem;'>
        <p>GST Invoice & Annexure Generator v1.0 | Powered by Streamlit</p>
    </div>
""", unsafe_allow_html=True)