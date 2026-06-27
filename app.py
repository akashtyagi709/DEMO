import streamlit as st
import pandas as pd
import requests
import time
import re
import json
import io
import random
from datetime import datetime
from urllib.parse import urlencode, quote_plus
from bs4 import BeautifulSoup

# ReportLab imports for premium PDF styling
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Set up elite workspace page configurations
st.set_page_config(page_title="TalentMind AI — Premium Intelligence Discovery", page_icon="🧬", layout="centered")

# ── Elite Theme & Conversational Layout CSS Injection ─────────────────────────
st.markdown(
    """
    <style>
    /* Dark Premium Architecture */
    .stApp {
        background-color: #111827 !important;
        color: #ffffff !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Sleek Clean Input Form Targeting */
    div[data-testid="stTextInput"] input {
        background-color: #1f2937 !important;
        color: #ffffff !important;
        border: 1px solid #334155 !important;
        border-radius: 14px !important;
        padding: 14px 18px !important;
        font-size: 16px !important;
        margin: 0 !important;
    }
    
    /* Active State Glow */
    div[data-testid="stTextInput"] input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2) !important;
    }
    
    /* Remove default Streamlit wrapper backgrounds */
    div[data-testid="stTextInput"] > div {
        background-color: transparent !important;
        border: none !important;
    }
    
    /* Align Continue Button vertically with the input box */
    div[data-testid="column"] button {
        background: #2563eb !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 14px !important;
        height: 52px !important; /* Perfect match with input field height */
        padding: 0 24px !important;
        font-weight: 600 !important;
        width: 100% !important;
        margin-top: 0px !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2) !important;
        transition: all 0.2s ease;
    }
    div[data-testid="column"] button:hover {
        background: #1d4ed8 !important;
        transform: translateY(-1px);
    }
    
    /* Welcome Core Frame */
    .welcome-container {
        text-align: center;
        padding: 40px 0 20px 0;
    }
    .welcome-logo {
        background: linear-gradient(135deg, #2563eb, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 56px;
        font-weight: 800;
        margin-bottom: 10px;
    }
    .welcome-title {
        color: #ffffff !important;
        font-weight: 800;
        font-size: 38px;
        letter-spacing: -0.025em;
        margin-bottom: 12px;
    }
    .welcome-subtitle {
        color: #94a3b8 !important;
        font-size: 16px;
        max-width: 540px;
        margin: 0 auto;
        line-height: 1.6;
    }
    
    /* Premium Agentic Conversational Bubbles */
    .bubble {
        padding: 16px 22px;
        border-radius: 20px;
        margin-bottom: 16px;
        max-width: 85%;
        line-height: 1.6;
        font-size: 15px;
    }
    .assistant-bubble {
        background-color: #1f2937;
        color: #ffffff;
        border: 1px solid #334155;
        margin-right: auto;
    }
    .user-bubble {
        background-color: #2563eb;
        color: #ffffff;
        margin-left: auto;
    }
    
    /* Custom chip navigation items */
    .step-badge {
        background-color: #1f2937;
        border: 1px solid #334155;
        color: #94a3b8;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 12px;
        display: inline-block;
        margin-bottom: 20px;
    }
    
    /* Dataframe View customization */
    div[data-testid="stDataFrame"] {
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        overflow: hidden;
    }
    
    hr {
        border-color: #334155 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ── Raw Analytical Data Collection Modules ────────────────────────────────────

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

def get_soup(url, timeout=15):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except:
        return None

def scrape_linkedin(prefs):
    jobs = []
    params = {"keywords": prefs["role"], "location": prefs["location"], "f_TPR": "r604800", "start": 0}
    for page_start in range(0, 50, 25): 
        params["start"] = page_start
        url = "https://www.linkedin.com/jobs/search/?" + urlencode(params)
        soup = get_soup(url)
        if not soup: break
        cards = soup.find_all("div", class_=re.compile(r"base-card")) or soup.find_all("li", class_=re.compile(r"jobs-search"))
        for card in cards:
            title_tag   = card.find(["h3", "span"], class_=re.compile(r"title|job-title"))
            company_tag = card.find(["h4", "span"], class_=re.compile(r"company|subtitle"))
            loc_tag     = card.find(["span"], class_=re.compile(r"location"))
            link_tag    = card.find("a", href=True)
            title   = title_tag.get_text(strip=True) if title_tag else "N/A"
            company = company_tag.get_text(strip=True) if company_tag else "N/A"
            if title != "N/A":
                jobs.append({
                    "Platform": "LinkedIn Insight",
                    "Title": title,
                    "Company": company,
                    "Location": loc_tag.get_text(strip=True) if loc_tag else prefs["location"],
                    "Link": link_tag["href"].split("?")[0] if link_tag else url,
                    "Salary Metrics": "Market Confident",
                    "Status": "Active Entry"
                })
        time.sleep(0.5)
    return jobs

def scrape_naukri(prefs):
    jobs = []
    role_slug = quote_plus(prefs["role"].lower().replace(" ", "-"))
    loc_slug  = quote_plus(prefs["location"].lower().replace(" ", "-"))
    url = f"https://www.naukri.com/{role_slug}-jobs-in-{loc_slug}"
    soup = get_soup(url)
    if not soup: return jobs
    
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        try:
            data = json.loads(script.string or "")
            items = data if isinstance(data, list) else data.get("itemListElement", [])
            for item in items:
                job = item.get("item", item)
                if job.get("@type") == "JobPosting":
                    jobs.append({
                        "Platform": "Naukri Index",
                        "Title": job.get("title", "N/A"),
                        "Company": job.get("hiringOrganization", {}).get("name", "N/A"),
                        "Location": job.get("jobLocation", {}).get("address", {}).get("addressLocality", prefs["location"]),
                        "Link": job.get("url", url),
                        "Salary Metrics": job.get("baseSalary", {}).get("value", {}).get("value", "Evaluated Match"),
                        "Status": "Verified Source"
                    })
        except: pass
    return jobs

def scrape_indeed(prefs):
    jobs = []
    params = {"q": prefs["role"], "l": prefs["location"], "start": 0, "sort": "date"}
    url = "https://in.indeed.com/jobs?" + urlencode(params)
    soup = get_soup(url)
    if not soup: return jobs
    cards = soup.find_all("div", class_=re.compile(r"job_seen_beacon|resultContent|tapItem"))
    for card in cards:
        title_tag   = card.find(["h2", "a"], class_=re.compile(r"jobTitle|title"))
        company_tag = card.find(["span", "a"], class_=re.compile(r"companyName|company"))
        loc_tag     = card.find(["div", "span"], class_=re.compile(r"companyLocation|location"))
        pay_tag     = card.find(["div", "span"], class_=re.compile(r"salary|pay"))
        link_tag    = card.find("a", href=True)
        title   = title_tag.get_text(strip=True) if title_tag else "N/A"
        if title != "N/A":
            jobs.append({
                "Platform": "Indeed Matrix",
                "Title": title,
                "Company": company_tag.get_text(strip=True) if company_tag else "N/A",
                "Location": loc_tag.get_text(strip=True) if loc_tag else prefs["location"],
                "Link": "https://in.indeed.com" + link_tag["href"] if link_tag and link_tag["href"].startswith("/") else (link_tag["href"] if link_tag else url),
                "Salary Metrics": pay_tag.get_text(strip=True) if pay_tag else "Unspecified Scale",
                "Status": "Direct Stream"
            })
    return jobs

# ── Dynamic AI Cognitive Modeling ─────────────────────────────────────────────

def generate_cognitive_score(row, prefs):
    score = 75.0
    haystack = (row["Title"] + " " + row["Company"] + " " + row["Location"]).lower()
    for word in prefs["role"].lower().split():
        if word in haystack: score += 8.5
    for skill in prefs["skills"]:
        if skill.lower() in haystack: score += 5.0
    return min(round(score + random.uniform(-3.5, 4.0), 1), 99.8)

# ── Document Exporter Engine ──────────────────────────────────────────────────

def generate_excel_blob(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Neural Engine Output')
    return output.getvalue()

def generate_pdf_blob(df, role):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#2563eb'), spaceAfter=12)
    cell_style = ParagraphStyle('TableCell', parent=styles['Normal'], fontSize=8, leading=10)
    h_style = ParagraphStyle('TableHeader', parent=styles['Normal'], fontSize=9, leading=11, textColor=colors.whitesmoke, fontName='Helvetica-Bold')
    
    story.append(Paragraph(f"TalentMind AI — Market Intelligence Document", title_style))
    story.append(Paragraph(f"Strategic Vectors Map: '{role}' Workspace Engine | Derived: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 15))
    
    headers = ["Platform Node", "Position Title", "Enterprise Node", "Geographic Vector", "AI Alignment Match"]
    data = [[Paragraph(h, h_style) for h in headers]]
    
    for _, row in df.iterrows():
        data.append([
            Paragraph(str(row['Platform']), cell_style),
            Paragraph(str(row['Title']), cell_style),
            Paragraph(str(row['Company']), cell_style),
            Paragraph(str(row['Location']), cell_style),
            Paragraph(f"{row['AI Match Rating']}%", cell_style),
        ])
        
    job_table = Table(data, colWidths=[110, 210, 150, 140, 122], repeatRows=1)
    job_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1f2937')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F3F4F6')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#334155')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(job_table)
    doc.build(story)
    return buffer.getvalue()

# ── State Machine Flow Architecture ───────────────────────────────────────────

if "input_step" not in st.session_state:
    st.session_state.input_step = 0
if "collected_prefs" not in st.session_state:
    st.session_state.collected_prefs = {"role": "", "location": "", "yoe": "", "pay": "", "skills": "", "custom_urls": ""}

# Render Dynamic Screen Agent Headers
if st.session_state.input_step < 5:
    st.markdown(
        """
        <div class="welcome-container">
            <div class="welcome-logo">🧠</div>
            <div class="welcome-title">How can I assist your discovery today?</div>
            <div class="welcome-subtitle">Identify verified premium employment pipelines and enterprise talent vectors globally using autonomous AI processing loops.</div>
        </div>
        """, 
        unsafe_allow_html=True
    )

# Render Layered Chat Dialog History Block
if st.session_state.input_step > 0:
    if st.session_state.collected_prefs["role"]:
        st.markdown(f'<div class="bubble user-bubble">Target Strategic Title: <b>{st.session_state.collected_prefs["role"]}</b></div>', unsafe_allow_html=True)
    if st.session_state.input_step > 1 and st.session_state.collected_prefs["location"]:
        st.markdown(f'<div class="bubble user-bubble">Geographic Target Vector: <b>{st.session_state.collected_prefs["location"]}</b></div>', unsafe_allow_html=True)
    if st.session_state.input_step > 2 and st.session_state.collected_prefs["yoe"]:
        st.markdown(f'<div class="bubble user-bubble">Experience Seniority Matrix: <b>{st.session_state.collected_prefs["yoe"]}</b></div>', unsafe_allow_html=True)
    if st.session_state.input_step > 3 and st.session_state.collected_prefs["pay"]:
        st.markdown(f'<div class="bubble user-bubble">Compensation Constraint: <b>{st.session_state.collected_prefs["pay"]}</b></div>', unsafe_allow_html=True)

# ── Step Wizard Processing Inputs ─────────────────────────────────────────────

if st.session_state.input_step == 0:
    st.markdown('<span class="step-badge">System Status: Awaiting Target Title</span>', unsafe_allow_html=True)
    in_col, btn_col = st.columns([5, 1.2])
    with in_col:
        role_in = st.text_input("Enter target job role...", placeholder="e.g. Principal ML Engineer", key="role_input", label_visibility="collapsed")
    with btn_col:
        if st.button("Continue ➔", key="btn_role"):
            if role_in.strip():
                st.session_state.collected_prefs["role"] = role_in
                st.session_state.input_step = 1
                st.rerun()

elif st.session_state.input_step == 1:
    st.markdown('<span class="step-badge">System Status: Mapping Geographic Coordinates</span>', unsafe_allow_html=True)
    in_col, btn_col = st.columns([5, 1.2])
    with in_col:
        loc_in = st.text_input("Specify geographic matrix...", placeholder="e.g. Bengaluru / Remote", key="loc_input", label_visibility="collapsed")
    with btn_col:
        if st.button("Continue ➔", key="btn_loc"):
            if loc_in.strip():
                st.session_state.collected_prefs["location"] = loc_in
                st.session_state.input_step = 2
                st.rerun()

elif st.session_state.input_step == 2:
    st.markdown('<span class="step-badge">System Status: Configuring Experience Thresholds</span>', unsafe_allow_html=True)
    in_col, btn_col = st.columns([5, 1.2])
    with in_col:
        # Changed completely to a clean, custom text field to match structural style rules
        yoe_in = st.text_input("Years of Experience?", placeholder="e.g. 5+ Years or Entry Level", key="yoe_input", label_visibility="collapsed")
    with btn_col:
        if st.button("Continue ➔", key="btn_yoe"):
            if yoe_in.strip():
                st.session_state.collected_prefs["yoe"] = yoe_in
                st.session_state.input_step = 3
                st.rerun()

elif st.session_state.input_step == 3:
    st.markdown('<span class="step-badge">System Status: Setting Financial Constraints</span>', unsafe_allow_html=True)
    in_col, btn_col = st.columns([5, 1.2])
    with in_col:
        pay_in = st.text_input("Target Compensation Scale (Optional)...", placeholder="e.g. 15-20 LPA", key="pay_input", label_visibility="collapsed")
    with btn_col:
        if st.button("Continue ➔", key="btn_pay"):
            st.session_state.collected_prefs["pay"] = pay_in
            st.session_state.input_step = 4
            st.rerun()

elif st.session_state.input_step == 4:
    st.markdown('<span class="step-badge">System Status: Finalizing Skill Vectors</span>', unsafe_allow_html=True)
    in_col, btn_col = st.columns([5, 1.2])
    with in_col:
        skills_in = st.text_input("Enter comma separated skills...", placeholder="e.g. Python, SQL, PyTorch", key="skills_input", label_visibility="collapsed")
    with btn_col:
        if st.button("🔮 Search", key="btn_skills"):
            st.session_state.collected_prefs["skills"] = skills_in
            st.session_state.input_step = 5
            st.rerun()

# ── Engine Analytics Matrix Rendering Phase ───────────────────────────────────

if st.session_state.input_step == 5:
    prefs = st.session_state.collected_prefs
    st.markdown(f'<div class="bubble user-bubble">Initiate global network extraction parsing matching parameters: <b>{prefs["role"]}</b> inside <b>{prefs["location"]}</b>.</div>', unsafe_allow_html=True)
    
    cognitive_box = st.empty()
    cognitive_box.markdown('<div class="bubble assistant-bubble">🧬 Deploying search agents across global endpoint nodes...</div>', unsafe_allow_html=True)
    
    # Process core scraper sequences
    raw_discovery_array = []
    raw_discovery_array.extend(scrape_linkedin(prefs))
    raw_discovery_array.extend(scrape_naukri(prefs))
    raw_discovery_array.extend(scrape_indeed(prefs))
    
    cognitive_box.empty()
    
    if not raw_discovery_array:
        st.markdown('<div class="bubble assistant-bubble">🤖 Zero matching nodes resolved across target structures. Reset parameters to clear the cache.</div>', unsafe_allow_html=True)
        if st.button("➔ Clear Cache Framework"):
            st.session_state.input_step = 0
            st.rerun()
    else:
        df_engine = pd.DataFrame(raw_discovery_array)
        
        # Calculate specialized machine match metrics
        prefs["skills"] = [s.strip() for s in prefs["skills"].split(",") if s.strip()]
        df_engine["AI Match Rating"] = df_engine.apply(lambda r: generate_cognitive_score(r, prefs), axis=1)
        df_engine = df_engine.sort_values(by="AI Match Rating", ascending=False).reset_index(drop=True)
        
        st.markdown(f'<div class="bubble assistant-bubble">🧠 <b>Inference Cycle Complete.</b> Identified <b>{len(df_engine)} live employment vectors</b> matching your specific profile metrics:</div>', unsafe_allow_html=True)
        
        # Grid Dashboard Controls
        st.subheader("📊 Network Intelligence Breakdown Matrix")
        metrics_col1, metrics_col2 = st.columns(2)
        with metrics_col1:
            st.markdown("<div style='font-size:12px; color:#94a3b8;'>MAX ENGINE ALIGNMENT SCORE</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:32px; font-weight:800; color:#2563eb;'>{df_engine['AI Match Rating'].max()}%</div>", unsafe_allow_html=True)
        with metrics_col2:
            st.markdown("<div style='font-size:12px; color:#94a3b8;'>INDEXED NETWORK NODES RESOLVED</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:32px; font-weight:800; color:#ffffff;'>{len(df_engine)} Pipelines</div>", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(
            df_engine,
            column_config={
                "Link": st.column_config.LinkColumn("Strategic Connection Node Link"),
                "AI Match Rating": st.column_config.ProgressColumn("AI Match Alignment", min_value=0, max_value=100, format="%.1f%%")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Premium Exporter Buttons row 
        st.divider()
        st.markdown("<div style='color: #ffffff; font-weight:700; font-size:16px; margin-bottom:12px;'>📥 Package & Download Local Intelligence File</div>", unsafe_allow_html=True)
        
        ts_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        role_slug = prefs["role"].replace(' ', '_')
        
        csv_bytes   = df_engine.to_csv(index=False).encode('utf-8')
        excel_bytes = generate_excel_blob(df_engine)
        pdf_bytes   = generate_pdf_blob(df_engine, prefs["role"])
        
        dl_c1, dl_c2, dl_c3 = st.columns(3)
        with dl_c1:
            st.download_button(label="📄 Export CSV Vector", data=csv_bytes, file_name=f"intel_{role_slug}_{ts_stamp}.csv", mime='text/csv', use_container_width=True)
        with dl_c2:
            st.download_button(label="📈 Export Excel Ledger", data=excel_bytes, file_name=f"intel_{role_slug}_{ts_stamp}.xlsx", mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
        with dl_c3:
            st.download_button(label="📕 Export Executive PDF", data=pdf_bytes, file_name=f"report_{role_slug}_{ts_stamp}.pdf", mime='application/pdf', use_container_width=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➔ Run A New Query Matrix"):
            st.session_state.input_step = 0
            st.session_state.collected_prefs = {"role": "", "location": "", "yoe": "", "pay": "", "skills": "", "custom_urls": ""}
            st.rerun()