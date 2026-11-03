"""Patient Experience Dashboard: Administration & Support Services (MFU-MCH)."""
import html
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

st.set_page_config(page_title='Patient Experience | Administration & Support', layout='wide')
pio.templates.default = 'plotly_white'

SHEET_ID = '1Y-eivhlobS1e0otAxcoGW3yZZ8JT--TH4zVUGHxoFk4'
SHEET_GID = '1379757400'
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={SHEET_GID}'
BACKUP = 'admin_support.xlsx'

LOGO_URL = 'https://raw.githubusercontent.com/HOIARRTool/hoiarr/main/logo1.png'
BRAND_URLS = [
    'https://github.com/HOIARRTool/appqtbi/blob/main/messageImage_1763018963411.jpg?raw=true',
    'https://github.com/HOIARRTool/appqtbi/blob/main/csm_logo_mfu_3d_colour_15e5a7a50f.png?raw=true',
]

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap');
:root{color-scheme:light!important}
html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"],
[data-testid="stMain"],[data-testid="stSidebar"],[data-testid="stHeader"]{
 background:#ffffff!important;color:#172033!important;font-family:'Kanit',sans-serif!important}
[data-testid="stMarkdownContainer"],[data-testid="stWidgetLabel"],
[data-testid="stSidebar"] label{color:#172033!important;font-family:'Kanit',sans-serif!important}
[data-testid="stMetric"]{background:#f8fafc;border:1px solid #e2e8f0;border-radius:14px;padding:12px}
.metric-box{border:1px solid #e5e7eb;border-radius:14px;padding:14px;min-height:112px;
text-align:center;box-shadow:0 2px 6px rgba(0,0,0,.05);color:#334155}
.metric-box .label{font-size:1rem;font-weight:600}.metric-box .value{font-size:2.15rem;font-weight:700;margin-top:8px}
.metric-1{background:#e0f7fa}.metric-2{background:#e8f5e9}.metric-3{background:#e3f2fd}
.metric-4{background:#fce4ec}.metric-5{background:#fffde7}.metric-6{background:#f3e5f5}
.gauge-head{font-weight:600;font-size:1rem;color:#172033;min-height:52px;line-height:1.35}
.gauge-sub{color:#475569;font-size:.9rem}
.gradient-text{background:linear-gradient(45deg,#007bff,#6610f2,#d63384);background-clip:text;
-webkit-background-clip:text;color:transparent;font-weight:700}
[data-testid="stDataFrame"]{color-scheme:light}
</style>''', unsafe_allow_html=True)

st.sidebar.markdown(f'<div style="display:flex;align-items:center;gap:10px"><img src="{LOGO_URL}" style="height:40px"><b class="gradient-text">Patient Experience | ADMIN</b></div>', unsafe_allow_html=True)
st.markdown(f'<div style="display:flex;justify-content:flex-end;gap:16px;align-items:center"><img src="{BRAND_URLS[0]}" style="height:62px"><img src="{BRAND_URLS[1]}" style="height:75px"></div>', unsafe_allow_html=True)

# The 14 items follow the actual column titles and order in the source Sheet.
ITEMS = [
    ('การบริการรวดเร็วประทับใจ', 'การบริการรวดเร็วประทับใจ'),
    ('มีขั้นตอนการให้บริการที่ชัดเจน', 'ขั้นตอนการให้บริการชัดเจน'),
    ('ท่านได้รับบริการตรงความต้องการ', 'ได้รับบริการตรงตามความต้องการ'),
    ('เจ้าหน้าที่มีพฤติกรรมบริการที่ดี กระตือรือร้น เต็มใจให้การต้อนรับ', 'ความกระตือรือร้นและการต้อนรับ'),
    ('เจ้าหน้าที่ให้บริการด้วยกริยา วาจาที่สุภาพ มีกิริยามารยาทเรียบร้อย เต็มใจให้บริการ', 'ความสุภาพและเต็มใจบริการ'),
    ('เจ้าหน้าที่รับฟังและอธิบาย ตอบข้อซักถามอย่างชัดเจนตรงประเด็น', 'การรับฟังและการตอบข้อซักถาม'),
    ('เจ้าหน้าที่บริการด้วยความเสมอภาค เป็นธรรม ไม่เลือกปฏิบัติ', 'ความเสมอภาคและเป็นธรรม'),
    ('สถานที่มีความพร้อม สะอาด เป็นระเบียบ เหมาะสมกับการปฏิบัติงาน', 'ความพร้อมและความสะอาดของสถานที่'),
    ('มีสิ่งอำนวยความสะดวกเหมาะสม/พร้อมใช้งาน เช่น น้ำดื่ม ห้องน้ำ ทางเดิน ที่จอดรถ', 'สิ่งอำนวยความสะดวก'),
    ('มีการเตรียมตัว ให้ข้อมูล กับผู้รับบริการ', 'การเตรียมตัวและให้ข้อมูล'),
    ('การประสานและดำเนินการ มีความเหมาะสมและรวดเร็ว', 'การประสานงานและความรวดเร็ว'),
    ('บริการที่ได้รับเป็นประโยชน์ต่อท่าน', 'ประโยชน์จากบริการ'),
    ('ความมั่นใจในระบบความปลอดภัยต่อชีวิตและทรัพย์สิน', 'ความมั่นใจในความปลอดภัย'),
    ('ระยะเวลาการรอคอยสำหรับมารับบริการจนถึงเสร็จสิ้นกระบวนการ', 'ระยะเวลารอคอยจนเสร็จสิ้นบริการ'),
]

FIELD_HINTS = {
    'หน่วยงาน': ['หน่วยงานที่ท่านเข้ารับบริการ'],
    'ผู้ตอบแบบสอบถาม': ['ผู้ตอบแบบสอบถาม'],
    'ประเภทการมา': ['ท่านมาใช้บริการ'],
    'เหตุผลที่เลือก': ['เหตุผลที่เลือกใช้บริการ'],
    'อายุ': ['อายุ'],
    'ภูมิลำเนา': ['ภูมิลำเนา'],
    'อาชีพ': ['อาชีพ'],
    'วันที่รับบริการ': ['วันที่มารับบริการ'],
    'ความพึงพอใจโดยรวม': ['ความพึงพอใจต่อบริการของโรงพยาบาลในภาพรวม'],
    'กลับมารับบริการหรือไม่': ['ท่านจะกลับมารับบริการอีกครั้งหรือไม่'],
    'แนะนำผู้อื่นหรือไม่': ['ท่านจะแนะนำผู้อื่นให้มารับบริการหรือไม่'],
    'มีความไม่พึงพอใจหรือไม่': ['ท่านมีความไม่พึงพอใจในการมาใช้บริการกับหน่วยงานนี้หรือไม่'],
    'รายละเอียดความไม่พึงพอใจ': ['(หากมี) ความไม่พึงพอใจกรุณาระบุรายละเอียด'],
    'ความเชื่อมั่น': ['ความเชื่อมั่นที่มีต่อบริการทางการแพทย์ของโรงพยาบาลในภาพรวม'],
    'การจัดการข้อร้องเรียน': ['หากท่านเคยระบุความไม่พึงพอใจหรือส่งเรื่องร้องเรียน'],
}

LIKERT = {
 'มากที่สุด':5,'มาก':4,'ปานกลาง':3,'น้อย':2,'น้อยมาก':1,
 'ดีมาก':5,'ดี':4,'พอใช้':3,'ควรปรับปรุง':2,'ต้องปรับปรุง':1,
 'สะดวกมาก':5,'สะดวก':4,'ชัดเจนมาก':5,'ชัดเจน':4,'เหมาะสมมาก':5,'เหมาะสม':4,
}

def normalize_score(value):
    if pd.isna(value):
        return np.nan
    s = str(value).strip()
    if not s or s.lower() in {'null','nan','none','n/a','-'}:
        return np.nan
    if s in LIKERT:
        return float(LIKERT[s])
    if re.fullmatch(r'[1-5](?:\.0+)?', s):
        return float(s)
    return np.nan  # Never infer arbitrary numbers from free text.


def cleaned_text(series):
    s = series.astype('string').str.strip()
    return s.mask(s.str.lower().isin(['', 'null', 'nan', 'none', 'n/a', '-']).fillna(True))


def find_column(columns, fragments):
    for fragment in fragments:
        candidates = [c for c in columns if fragment in str(c)]
        if candidates:
            return candidates[0]
    return None


def parse_thai_dates(col):
    s = col.astype('string').str.strip()
    # Timestamp source uses dd/mm/yyyy HH:MM:SS; avoid month-first ambiguity.
    parsed = pd.to_datetime(s, format='%d/%m/%Y %H:%M:%S', errors='coerce')
    missing = parsed.isna() & s.notna()
    if missing.any():
        parsed.loc[missing] = pd.to_datetime(s.loc[missing], dayfirst=True, errors='coerce')
    # BE correction for unexpected Buddhist-year input, if present.
    be = parsed.notna() & (parsed.dt.year > 2400)
    if be.any():
        parsed.loc[be] = parsed.loc[be] - pd.DateOffset(years=543)
    return parsed


def prepare(df):
    df = df.copy()
    df.columns = [re.sub(r'\s+', ' ', str(x)).strip() for x in df.columns]
    for target, fragments in FIELD_HINTS.items():
        source = find_column(df.columns, fragments)
        df[target] = df[source] if source else pd.NA
    for i, (question, _) in enumerate(ITEMS, 1):
        source = find_column(df.columns, [f'แบบประเมิน [{question}]', question])
        df[f'Q{i}'] = df[source].map(normalize_score) if source else np.nan
    for c in ['ความพึงพอใจโดยรวม','ความเชื่อมั่น','การจัดการข้อร้องเรียน']:
        df[c + '_score'] = df[c].map(normalize_score)
    for c in ['หน่วยงาน','ผู้ตอบแบบสอบถาม','ประเภทการมา','รายละเอียดความไม่พึงพอใจ','เหตุผลที่เลือก']:
        df[c] = cleaned_text(df[c])
    time_col = find_column(df.columns, ['Timestamp','ประทับเวลา'])
    df['date_col'] = parse_thai_dates(df[time_col]) if time_col else pd.NaT
    df['ปี'] = df['date_col'].dt.year
    df['ไตรมาส'] = df['date_col'].dt.quarter
    df['เดือน'] = df['date_col'].dt.month
    return df

@st.cache_data(ttl=300, show_spinner=False)
def load_data(source):
    df = pd.read_excel(source) if str(source).lower().endswith('.xlsx') else pd.read_csv(source)
    return prepare(df)

try:
    source_label = 'Google Sheets (อัปเดตทุก 5 นาที)'
    data = load_data(SHEET_URL)
    if data.empty:
        raise ValueError('Google Sheets returned no responses')
except Exception as exc:
    if Path(BACKUP).exists():
        try:
            data = load_data(BACKUP)
            source_label = f'ไฟล์สำรอง {BACKUP}'
            st.sidebar.warning(f'ไม่สามารถอ่าน Google Sheets ได้ ใช้ข้อมูลสำรองแทน: {exc}')
        except Exception as backup_exc:
            st.error(f'อ่านข้อมูลไม่ได้: {backup_exc}')
            st.stop()
    else:
        st.error('อ่านข้อมูลจาก Google Sheets ไม่สำเร็จ และไม่พบ admin_support.xlsx สำหรับสำรอง')
        st.caption(str(exc))
        st.stop()

st.sidebar.markdown('---')
st.sidebar.caption(source_label)
if data['date_col'].notna().any():
    st.sidebar.caption('ช่วงข้อมูล: ' + data['date_col'].min().strftime('%d/%m/%Y') + ' – ' + data['date_col'].max().strftime('%d/%m/%Y'))

st.sidebar.header('ตัวกรองข้อมูล (Filter)')
unit_list = sorted(data['หน่วยงาน'].dropna().unique().tolist())
unit = st.sidebar.selectbox('เลือกหน่วยงาน:', ['ภาพรวมทั้งหมด'] + unit_list, key='admin_unit')
period = st.sidebar.selectbox('เลือกช่วงเวลา:', ['ทั้งหมด','เลือกตามปี','เลือกตามไตรมาส','เลือกตามเดือน'], key='admin_period')
subset = data.copy()
if period != 'ทั้งหมด' and data['ปี'].notna().any():
    year_options = sorted(data['ปี'].dropna().astype(int).unique().tolist(), reverse=True)
    year = st.sidebar.selectbox('เลือกปี:', year_options, key='admin_year')
    subset = subset[subset['ปี'] == year]
    if period == 'เลือกตามไตรมาส':
        options = sorted(subset['ไตรมาส'].dropna().astype(int).unique().tolist())
        if options:
            quarter = st.sidebar.selectbox('เลือกไตรมาส:', options, key='admin_quarter')
            subset = subset[subset['ไตรมาส'] == quarter]
    elif period == 'เลือกตามเดือน':
        options = sorted(subset['เดือน'].dropna().astype(int).unique().tolist())
        if options:
            month_labels = {1:'ม.ค.',2:'ก.พ.',3:'มี.ค.',4:'เม.ย.',5:'พ.ค.',6:'มิ.ย.',7:'ก.ค.',8:'ส.ค.',9:'ก.ย.',10:'ต.ค.',11:'พ.ย.',12:'ธ.ค.'}
            month = st.sidebar.selectbox('เลือกเดือน:', options, format_func=lambda x: month_labels.get(x,str(x)), key='admin_month')
            subset = subset[subset['เดือน'] == month]
if unit != 'ภาพรวมทั้งหมด':
    subset = subset[subset['หน่วยงาน'] == unit]
if subset.empty:
    st.warning('ไม่พบข้อมูลสำหรับตัวกรองที่เลือก')
    st.stop()


def pct_count(column, positive):
    answers = cleaned_text(subset[column]).dropna()
    n = len(answers)
    return (100.0 * answers.eq(positive).sum() / n if n else np.nan), n

def fmt_pct(x):
    return f'{x:.1f}%' if pd.notna(x) else 'N/A'

def metric(label,value,klass):
    return f'<div class="metric-box {klass}"><div class="label">{html.escape(label)}</div><div class="value">{html.escape(str(value))}</div></div>'

def gauge(scores, title, key, low_good=False, percentage=False, n_display=None):
    series = pd.to_numeric(scores, errors='coerce').dropna()
    st.markdown(f'<div class="gauge-head">{html.escape(title)}</div><div class="gauge-sub">n = {(n_display if n_display is not None else len(series)):,}</div>', unsafe_allow_html=True)
    if series.empty:
        st.info('ยังไม่มีข้อมูลสำหรับคำถามนี้')
        return
    avg = float(series.mean())
    if percentage:
        brackets = [0, 5, 10, 20, 100] if low_good else [0,50,65,80,100]
        colors = ['#16A34A','#F59E0B','#EA580C','#DC2626'] if low_good else ['#DC2626','#EA580C','#F59E0B','#16A34A']
    else:
        brackets=[1,2,3,4,5]
        colors=['#DC2626','#EA580C','#F59E0B','#16A34A']
    steps=[dict(range=[brackets[i],brackets[i+1]],color=colors[i]) for i in range(4)]
    fig=go.Figure(go.Indicator(mode='gauge',value=avg,gauge={
        'axis':{'range':[brackets[0],brackets[-1]]},'bar':{'color':'#111827'},
        'steps':steps,'threshold':{'line':{'color':'#111827','width':2},'value':avg}}))
    fig.add_annotation(x=.5,y=.35,xref='paper',yref='paper',showarrow=False,
                       text=f'{avg:.1f}%' if percentage else f'{avg:.2f}',
                       font={'size':42,'color':'#475569'})
    fig.update_layout(height=230,margin=dict(t=10,b=10,l=15,r=15),paper_bgcolor='white',plot_bgcolor='white',font_color='#172033')
    st.plotly_chart(fig,use_container_width=True,key=key)


def pct_gauge(title, percentage, n, key, low_good=False):
    if n == 0:
        st.markdown(f'**{title}**')
        st.info('ยังไม่มีคำตอบ')
    else:
        # A single numeric observation is supplied so the gauge can reuse its formatter.
        gauge(pd.Series([percentage]),title,key,low_good=low_good,percentage=True,n_display=n)
        st.caption(f'ผู้ตอบคำถามนี้ {n:,} ราย')

st.title(f'DASHBOARD: {unit}')
st.caption('Patient Experience Program | Administration & Support Services')
return_pct, return_n=pct_count('กลับมารับบริการหรือไม่','ใช่')
refer_pct, refer_n=pct_count('แนะนำผู้อื่นหรือไม่','ใช่')
dissat_pct, dissat_n=pct_count('มีความไม่พึงพอใจหรือไม่','มี')
mean_score=subset['ความพึงพอใจโดยรวม_score'].mean()

st.markdown('##### ภาพรวม')
boxes=[
 ('จำนวนผู้ตอบ',f'{len(subset):,}','metric-1'),
 ('คะแนนพึงพอใจเฉลี่ย', f'{mean_score:.2f}' if pd.notna(mean_score) else 'N/A','metric-2'),
 ('จำนวนหน่วยงาน',str(subset['หน่วยงาน'].dropna().nunique()),'metric-3'),
 ('% กลับมาใช้บริการ',fmt_pct(return_pct),'metric-4'),
 ('% การบอกต่อ',fmt_pct(refer_pct),'metric-5'),
 ('% ไม่พึงพอใจ',fmt_pct(dissat_pct),'metric-6')]
for offset in [0,3]:
    cols=st.columns(3)
    for i,(label,value,klass) in enumerate(boxes[offset:offset+3]):
        cols[i].markdown(metric(label,value,klass),unsafe_allow_html=True)
st.markdown('---')
if unit=='ภาพรวมทั้งหมด':
    st.subheader('สรุปจำนวนการประเมินตามหน่วยงาน')
    counts=subset['หน่วยงาน'].value_counts().rename_axis('หน่วยงาน').reset_index(name='จำนวน')
    st.dataframe(counts,use_container_width=True,hide_index=True)

st.subheader('ความพึงพอใจโดยรวม')
left,right=st.columns(2)
with left:
    st.markdown(f'### ❤️ {mean_score:.2f} / 5' if pd.notna(mean_score) else '### ❤️ ยังไม่มีคะแนน')
    st.caption(f'จำนวนผู้ตอบที่มีคะแนน {subset["ความพึงพอใจโดยรวม_score"].count():,} ราย')
with right:
    dist=subset['ความพึงพอใจโดยรวม_score'].dropna().astype(int).value_counts().reindex([1,2,3,4,5],fill_value=0)
    fig=go.Figure(go.Bar(x=dist.index.tolist(),y=dist.values.tolist(),text=dist.values.tolist(),textposition='auto',marker_color=['#DC2626','#EA580C','#F59E0B','#22C55E','#16A34A']))
    fig.update_layout(title='Distribution ของคะแนน (1–5)',height=260,paper_bgcolor='white',plot_bgcolor='white',font_color='#172033',xaxis={'dtick':1})
    st.plotly_chart(fig,use_container_width=True,key='admin_overall_dist')

st.markdown('---')
st.header('ส่วนที่ 2: ความพึงพอใจต่อบริการ (14 หัวข้อ)')
for i in range(0,len(ITEMS),2):
    c1,c2=st.columns(2)
    for col,j in zip([c1,c2],[i,i+1]):
        if j < len(ITEMS):
            with col:
                gauge(subset[f'Q{j+1}'],f'{j+1}. {ITEMS[j][1]}',f'admin_q{j+1}')

st.markdown('---')
st.header('ส่วนที่ 3: ความตั้งใจในอนาคต')
cols=st.columns(3)
for col,title,pct,n,key,low in zip(cols,['1. กลับมารับบริการ (ใช่)','2. แนะนำผู้อื่น (ใช่)','3. ไม่พึงพอใจ (มี)'],
                                   [return_pct,refer_pct,dissat_pct],[return_n,refer_n,dissat_n],
                                   ['admin_return','admin_refer','admin_dissat'],[False,False,True]):
    with col:
        pct_gauge(title,pct,n,key,low_good=low)

st.markdown('---')
st.header('ส่วนที่ 4: ความเชื่อมั่นและการจัดการข้อร้องเรียน')
c1,c2=st.columns(2)
with c1:
    gauge(subset['ความเชื่อมั่น_score'],'1. ความเชื่อมั่นต่อบริการทางการแพทย์', 'admin_confidence')
with c2:
    gauge(subset['การจัดการข้อร้องเรียน_score'],'2. ความพึงพอใจต่อการจัดการข้อร้องเรียน', 'admin_complaint')
st.caption('คะแนนอิงจำนวนผู้ตอบที่ให้คะแนนจริงในแต่ละข้อ ไม่ถือว่าคำตอบว่างเป็นศูนย์')

st.markdown('---')
st.header('เสียงสะท้อนจากผู้รับบริการ')
for key,title in [('รายละเอียดความไม่พึงพอใจ','รายละเอียดความไม่พึงพอใจ'),('เหตุผลที่เลือก','เหตุผลที่เลือกใช้บริการ')]:
    st.subheader(title)
    lines=subset[['หน่วยงาน',key]].dropna(subset=[key]).copy()
    if lines.empty:
        st.info('ยังไม่มีข้อมูล')
    else:
        st.dataframe(lines,use_container_width=True,hide_index=True)

# Do not show direct respondent identifiers, timestamps, or any sensitive raw fields in public tables.
