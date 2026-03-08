import streamlit as st
import re
import sys
import os

# ── Path setup so backend is importable regardless of CWD ─────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from api_client import (
    load_accounts,
    transfer_funds,
    get_account_transactions,
    authenticate_user,
    register_user,
    setup_2fa,
    verify_2fa,
    create_account,
    deposit_amount,
    withdraw_amount,
    delete_account,
    load_transactions,
    link_account
)

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG  (must be the very first Streamlit call)
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="NexaBank",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center;'>🏦 NexaBank Portal</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            totp_code = st.text_input("2FA Code (if enabled)", key="login_2fa")
            
            if st.button("Login", use_container_width=True):
                success, data = authenticate_user(username.strip(), password.strip(), totp_code.strip() if totp_code else None)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.token = data["access_token"]
                    st.session_state.role = data["role"]
                    st.session_state.username = username.strip()
                    st.rerun()
                else:
                    st.error(f"Login failed: {data}")
                    
        with tab2:
            new_username = st.text_input("Choose Username", key="reg_user")
            new_email = st.text_input("Email", key="reg_email")
            new_password = st.text_input("Create Password", type="password", key="reg_pass")
            
            if st.button("Register", use_container_width=True):
                email_val = new_email.strip() if new_email.strip() else None
                success, data = register_user(new_username.strip(), new_password.strip(), email_val)
                if success:
                    st.success("Registration successful! You can now log in.")
                else:
                    st.error(f"Registration failed: {data}")

    st.stop()  # Stop execution here if not authenticated

# ══════════════════════════════════════════════════════════════════════════════
#  DYNAMIC CSS & GLASSMORPHISM THEME
# ══════════════════════════════════════════════════════════════════════════════
theme_role = st.session_state.get("role", "customer")

# Define Role-Based Accents
if theme_role == "manager":
    primary_color = "#9333ea" # Premium Purple
    gradient_bg = "linear-gradient(135deg, #1e0b35 0%, #110720 100%)"
    accent_gradient = "linear-gradient(135deg, #a855f7 0%, #7e22ce 100%)"
    hover_gradient = "linear-gradient(135deg, #d8b4fe 0%, #a855f7 100%)"
    glow_color = "rgba(168, 85, 247, 0.4)"
elif theme_role == "teller":
    primary_color = "#0ea5e9" # Vibrant Teal/Cyan
    gradient_bg = "linear-gradient(135deg, #072a38 0%, #03151c 100%)"
    accent_gradient = "linear-gradient(135deg, #38bdf8 0%, #0284c7 100%)"
    hover_gradient = "linear-gradient(135deg, #7dd3fc 0%, #0ea5e9 100%)"
    glow_color = "rgba(14, 165, 233, 0.4)"
else:
    primary_color = "#3b82f6" # Ocean Blue (Customer)
    gradient_bg = "linear-gradient(135deg, #091326 0%, #050a14 100%)"
    accent_gradient = "linear-gradient(135deg, #60a5fa 0%, #2563eb 100%)"
    hover_gradient = "linear-gradient(135deg, #93c5fd 0%, #3b82f6 100%)"
    glow_color = "rgba(59, 130, 246, 0.4)"

css = f"""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

h1, h2, h3, h4, h5, h6, .brand {{
    font-family: 'Outfit', sans-serif !important;
}}

/* ── App background ── */
.stApp {{
    background: {gradient_bg};
    color: #e6edf3;
}}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
    background: rgba(13, 17, 23, 0.6) !important;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}}
section[data-testid="stSidebar"] * {{ color: #e6edf3 !important; }}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header {{ visibility: hidden; }}

/* ── Metric cards (Glassmorphism) ── */
[data-testid="metric-container"] {{
    background: rgba(22, 27, 39, 0.4);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 20px 24px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
}}
[data-testid="metric-container"]:hover {{
    transform: translateY(-5px);
    box-shadow: 0 12px 40px {glow_color};
    border-color: {primary_color};
}}
[data-testid="metric-container"] label {{ color: #8b949e !important; font-size: 13px; font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase; }}
[data-testid="metric-container"] [data-testid="stMetricValue"] {{ 
    color: #ffffff !important; 
    font-size: 32px; 
    font-weight: 700; 
    font-family: 'Outfit', sans-serif;
    background: {accent_gradient};
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

/* ── Buttons (Animated & Glowing) ── */
.stButton > button {{
    background: {accent_gradient};
    color: #ffffff !important;
    border: none;
    border-radius: 12px;
    padding: 12px 24px;
    font-weight: 600;
    font-family: 'Outfit', sans-serif;
    font-size: 15px;
    letter-spacing: 0.5px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px {glow_color};
    width: 100%;
}}
.stButton > button:hover {{
    background: {hover_gradient};
    box-shadow: 0 8px 25px {glow_color};
    transform: translateY(-2px);
}}
.stButton > button:active {{
    transform: translateY(1px);
}}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div {{
    background: rgba(22, 27, 39, 0.6) !important;
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    font-size: 15px;
    transition: all 0.3s ease;
}}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {{
    border-color: {primary_color} !important;
    box-shadow: 0 0 0 3px {glow_color} !important;
    background: rgba(22, 27, 39, 0.8) !important;
}}

/* ── DataFrames / Tables ── */
.stDataFrame {{
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(22, 27, 39, 0.3);
    backdrop-filter: blur(10px);
}}

/* ── Success / Error / Warning banners ── */
.stAlert {{ border-radius: 12px; backdrop-filter: blur(8px); padding: 16px; border: 1px solid rgba(255, 255, 255, 0.1); }}
div[data-baseweb="notification"] {{ border-radius: 12px; backdrop-filter: blur(8px); }}

/* ── Radio & Selectbox labels ── */
.stRadio label, .stSelectbox label {{ color: #a1aab5 !important; font-size: 14px; font-weight: 500; }}

/* ── Section divider ── */
hr {{ border-color: rgba(255, 255, 255, 0.08); margin: 24px 0; }}

/* ── Page title pill ── */
.page-title {{
    background: rgba(22, 27, 39, 0.5);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-left: 4px solid {primary_color};
    border-radius: 0 16px 16px 0;
    padding: 16px 24px;
    margin-bottom: 32px;
    font-size: 24px;
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    color: #ffffff;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    display: inline-block;
}}

/* ── Card wrapper (Glassmorphism) ── */
.card {{
    background: rgba(22, 27, 39, 0.3);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 20px;
    padding: 32px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    transition: border-color 0.3s ease;
}}
.card:hover {{
    border-color: rgba(255,255,255,0.15);
}}

/* ── Chat bubbles ── */
.chat-user {{
    background: {accent_gradient};
    color: #fff;
    padding: 12px 18px;
    border-radius: 18px 18px 4px 18px;
    margin: 6px 0 6px 60px;
    font-size: 15px;
    max-width: 90%;
    float: right;
    clear: both;
    box-shadow: 0 4px 15px {glow_color};
}}
.chat-ai {{
    background: rgba(33, 38, 45, 0.8);
    backdrop-filter: blur(8px);
    color: #e6edf3;
    padding: 12px 18px;
    border-radius: 18px 18px 18px 4px;
    margin: 6px 60px 6px 0;
    font-size: 15px;
    max-width: 90%;
    border: 1px solid rgba(255,255,255,0.08);
    float: left;
    clear: both;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}}
.chat-wrap {{ overflow: hidden; }}

/* ── Sidebar nav label ── */
.sidebar-logo {{
    text-align: center;
    padding: 24px 0 32px 0;
}}
.sidebar-logo .brand {{
    font-size: 32px;
    font-weight: 800;
    background: {accent_gradient};
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}}
.sidebar-logo .tagline {{ font-size: 12px; color: #8b949e; margin-top: 6px; font-weight: 500; }}

/* ── Transaction type badge ── */
.badge-deposit  {{ background: rgba(35, 134, 54, 0.2); color: #3fb950; padding: 4px 12px; border-radius: 20px; font-size: 12px; border: 1px solid rgba(63, 185, 80, 0.3); font-weight: 600; }}
.badge-withdraw {{ background: rgba(185, 28, 28, 0.2); color: #f85149; padding: 4px 12px; border-radius: 20px; font-size: 12px; border: 1px solid rgba(248, 81, 73, 0.3); font-weight: 600; }}
.badge-transfer {{ background: rgba(31, 111, 235, 0.2); color: #58a6ff; padding: 4px 12px; border-radius: 20px; font-size: 12px; border: 1px solid rgba(88, 166, 255, 0.3); font-weight: 600; }}

/* ── Role Badge ── */
.role-badge {{
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 8px;
    background: {glow_color};
    color: #ffffff;
    border: 1px solid {primary_color};
    box-shadow: 0 0 10px {glow_color};
}}

/* ── Hero Banner ── */
.hero-banner {{
    background: url('https://images.unsplash.com/photo-1557683311-eac922347aa1?q=80&w=2629&auto=format&fit=crop') center/cover;
    border-radius: 20px;
    padding: 40px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
}}
.hero-overlay {{
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(90deg, {primary_color} 0%, transparent 100%);
    opacity: 0.8;
}}
.hero-content {{
    position: relative;
    z-index: 1;
}}
.hero-title {{
    font-size: 36px;
    font-family: 'Outfit', sans-serif;
    font-weight: 800;
    margin: 0 0 8px 0;
    color: #ffffff;
}}
.hero-subtitle {{
    font-size: 16px;
    color: #e6edf3;
    margin: 0;
    max-width: 600px;
    line-height: 1.5;
}}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR NAVIGATION
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    role_display = st.session_state.role.capitalize() if st.session_state.role else "Customer"
    st.markdown(
        f'<div class="sidebar-logo">'
        f'<div class="brand">🏦 NexaBank</div>'
        f'<div class="tagline">Smart Banking, Simplified</div>'
        f'<div class="role-badge">{role_display}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    if st.session_state.role == "customer":
        nav_items = [
            "🏠  Dashboard",
            "🔗  Link Existing Account",
            "🔄  Fund Transfer",
            "🔍  Balance Enquiry",
            "📜  Transaction History",
            "🤖  AI Assistant",
            "🛡️  Security Profile"
        ]
    elif st.session_state.role == "teller":
        nav_items = [
            "🏠  Dashboard",
            "➕  New Account",
            "💰  Deposit",
            "💸  Withdraw",
            "📋  All Accounts",
            "🔍  Balance Enquiry",
            "📜  Transaction History",
            "🛡️  Security Profile"
        ]
    elif st.session_state.role == "manager":
        nav_items = [
            "🏠  Dashboard",
            "➕  New Account",
            "💰  Deposit",
            "💸  Withdraw",
            "📋  All Accounts",
            "✏️  Modify Account",
            "🗑️  Delete Account",
            "🔍  Balance Enquiry",
            "📜  Transaction History",
            "🛡️  Security Profile"
        ]

    page = st.radio(
        "Navigation",
        nav_items,
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        "<div style='font-size:11px;color:#8b949e;text-align:center;'>NexaBank v2.0<br>Built with Streamlit</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.token = None
        st.session_state.role = None
        st.session_state.username = None
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  HELPER UTILITIES
# ══════════════════════════════════════════════════════════════════════════════
def page_header(title: str, icon: str = ""):
    st.markdown(
        f'<div class="page-title">{icon}&nbsp; {title}</div>',
        unsafe_allow_html=True,
    )


def find_account(acno: int):
    """Return account dict or None."""
    for acc in load_accounts(st.session_state.token, st.session_state.role):
        if acc["acno"] == acno:
            return acc
    return None

def account_selector(label: str, key_suffix: str):
    """Render a smart drop-down for Customers, or manual input for Staff."""
    if st.session_state.role == "customer":
        accounts = load_accounts(st.session_state.token, st.session_state.role)
        if not accounts:
            st.warning("No active accounts available.")
            return None
        options = {f"{a['name']} - ₹{a['deposit']:,.2f} (Acct: {a['acno']})": a['acno'] for a in accounts}
        selected = st.selectbox(label, options=list(options.keys()), key=f"sel_{key_suffix}")
        return options[selected]
    else:
        return st.number_input(label, min_value=1000000000, step=1, format="%d", key=f"num_{key_suffix}")


def format_currency(amount):
    return f"₹ {amount:,.2f}"


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 1 – DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠  Dashboard":
    # ── Hero Banner ──
    user_display = st.session_state.username.capitalize() if st.session_state.username else "User"
    st.markdown(f"""
    <div class="hero-banner">
        <div class="hero-overlay"></div>
        <div class="hero-content">
            <h1 class="hero-title">Welcome back, {user_display}! 👋</h1>
            <p class="hero-subtitle">Here is your financial overview. You are logged in with <strong>{st.session_state.role.capitalize() if st.session_state.role else 'Customer'}</strong> privileges.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    accounts = load_accounts(st.session_state.token, st.session_state.role)
    total_accounts = len(accounts)
    total_deposits = sum(a["deposit"] for a in accounts)
    savings_count = sum(1 for a in accounts if a["acc_type"] == "S")
    current_count = sum(1 for a in accounts if a["acc_type"] == "C")

    # KPI Row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📂 Total Accounts", total_accounts)
    c2.metric("💵 Total Deposits", format_currency(total_deposits))
    c3.metric("🏷️ Savings Accounts", savings_count)
    c4.metric("🏢 Current Accounts", current_count)

    st.markdown("<br>", unsafe_allow_html=True)

    # Recent accounts table
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 👤 Recent Accounts")
        if accounts:
            import pandas as pd

            df = pd.DataFrame(accounts[-10:][::-1])
            df = df[["acno", "name", "acc_type", "deposit"]]
            df.columns = ["Account No", "Name", "Type", "Balance (₹)"]
            df["Type"] = df["Type"].map({"S": "Savings", "C": "Current"})
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No accounts found. Create one to get started!")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### 📊 Account Distribution")
        if accounts:
            import pandas as pd

            chart_data = pd.DataFrame(
                {"Type": ["Savings", "Current"], "Count": [savings_count, current_count]}
            )
            st.bar_chart(chart_data.set_index("Type"), color="#58a6ff")
        else:
            st.info("No data to display yet.")
        st.markdown("</div>", unsafe_allow_html=True)

    # Quick transaction summary
    # Only fetch global txns if staff, otherwise we don't display global recent txns easily (would require a different endpoint)
    if st.session_state.role in ["teller", "manager"]:
        txns = load_transactions(st.session_state.token)
    else:
        txns = [] # Customers only see their own accounts in dashboard

    if txns:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### ⚡ Recent Transactions")
        import pandas as pd

        df_txn = pd.DataFrame(txns[-8:][::-1])
        df_txn = df_txn[["timestamp", "acno", "trans_type", "amount"]]
        df_txn.columns = ["Timestamp", "Account No", "Type", "Amount (₹)"]
        st.dataframe(df_txn, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 2 – NEW ACCOUNT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "➕  New Account":
    page_header("Open New Account", "➕")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(
        f"<p style='color:#8b949e;font-size:13px;'>Account No will be "
        f"<strong style='color:#58a6ff;'>Auto-generated</strong></p>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", placeholder="e.g. Ravi Kumar")
        acc_type = st.selectbox("Account Type", ["Savings (S)", "Current (C)"])

    with col2:
        acc_code = "S" if acc_type.startswith("S") else "C"
        min_dep = 500 if acc_code == "S" else 1000
        deposit = st.number_input(
            f"Initial Deposit (Min ₹{min_dep})", min_value=0, step=100
        )

    if st.button("✅ Create Account"):
        error = None
        if not name.strip():
            error = "Name cannot be empty."
        elif deposit < min_dep:
            error = f"Minimum deposit for {acc_type} is ₹{min_dep}."
        else:
            resp = create_account(st.session_state.token, name.strip(), acc_code, deposit)
            if "detail" in resp:
                error = resp["detail"]
            else:
                new_acno = resp.get("acno", "Unknown")

        if error:
            st.error(f"❌ {error}")
        else:
            st.success(f"🎉 Account created successfully! Account No: **{new_acno}**")
            st.balloons()

    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 2.5 – LINK ACCOUNT (Customer Only)
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔗  Link Existing Account":
    page_header("Link Existing Account", "🔗")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#8b949e;font-size:14px;'>If you opened an account at a branch, "
        "you can link it to your online profile here.</p>",
        unsafe_allow_html=True,
    )

    link_acno = st.number_input("Account Number", min_value=1000000000, step=1, format="%d", key="link_acno")
    link_name = st.text_input("Account Holder Name (exactly as registered at branch)", placeholder="e.g. John Doe", key="link_name")

    if st.button("🔗 Link Account"):
        if not link_name.strip():
            st.error("❌ Account Holder Name is required.")
        else:
            success, msg = link_account(st.session_state.token, int(link_acno), link_name.strip())
            if success:
                st.success(f"🎉 **Success!** Account **{link_acno}** has been securely linked to your profile.")
                st.balloons()
            else:
                st.error(f"❌ **Linking Failed:** {msg}")
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 3 – DEPOSIT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💰  Deposit":
    page_header("Deposit Funds", "💰")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    acno = st.number_input("Account Number", min_value=1000000000, step=1, format="%d")
    amount = st.number_input("Deposit Amount (₹)", min_value=1, step=100)

    if st.button("💰 Deposit"):
        acc_data = find_account(int(acno))
        if not acc_data:
            st.error("❌ Account not found.")
        else:
            success, data = deposit_amount(st.session_state.token, int(acno), amount)
            if success:
                st.success(
                    f"✅ **₹{amount:,}** deposited to account **{acno}**. "
                    f"New Balance: **{format_currency(data['deposit'])}**"
                )
            else:
                st.error("❌ Deposit failed.")
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 4 – WITHDRAW
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💸  Withdraw":
    page_header("Withdraw Funds", "💸")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    acno = st.number_input("Account Number", min_value=1000000000, step=1, format="%d")
    amount = st.number_input("Withdrawal Amount (₹)", min_value=1, step=100)

    if st.button("💸 Withdraw"):
        acc_data = find_account(int(acno))
        if not acc_data:
            st.error("❌ Account not found.")
        else:
            success, data = withdraw_amount(st.session_state.token, int(acno), amount)
            if success:
                st.success(
                    f"✅ **₹{amount:,}** withdrawn from account **{acno}**. "
                    f"New Balance: **{format_currency(data['deposit'])}**"
                )
            else:
                st.error(f"❌ {data}")
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 5 – FUND TRANSFER
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔄  Fund Transfer":
    page_header("Fund Transfer", "🔄")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        from_acno = account_selector("From Account No", "transfer_from")
    with col2:
        to_acno = st.number_input("To Account No (Destination)", min_value=1000000000, step=1, format="%d", key="transfer_to")

    amount = st.number_input("Transfer Amount (₹)", min_value=1, step=100)

    if from_acno is not None and st.button("🔄 Transfer"):
        if from_acno == to_acno:
            st.error("❌ Source and destination accounts cannot be the same.")
        else:
            success, msg = transfer_funds(st.session_state.token, int(from_acno), int(to_acno), int(amount))
            if success:
                st.success(f"✅ {msg} — **₹{amount:,}** transferred from **{from_acno}** → **{to_acno}**")
            else:
                st.error(f"❌ {msg}")
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 6 – BALANCE ENQUIRY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍  Balance Enquiry":
    page_header("Balance Enquiry", "🔍")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    acno = account_selector("Account Number", "balance_enquiry")

    if acno is not None and st.button("🔍 Check Balance"):
        acc = find_account(int(acno))
        if not acc:
            st.error("❌ Account not found.")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Account No", str(acc["acno"]))
            col2.metric("Account Holder", acc["name"])
            col3.metric(
                "Available Balance",
                format_currency(acc["deposit"]),
            )
            acc_type_label = "Savings" if acc["acc_type"] == "S" else "Current"
            st.info(f"📋 Account Type: **{acc_type_label}**")
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 7 – TRANSACTION HISTORY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📜  Transaction History":
    page_header("Transaction History", "📜")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    acno = account_selector("Account Number", "txn_history")

    if acno is not None and st.button("📜 View History"):
        acc = find_account(int(acno))
        if not acc:
            st.error("❌ Account not found.")
        else:
            txns = get_account_transactions(st.session_state.token, int(acno))
            if not txns:
                st.warning("No transactions found for this account.")
            else:
                import pandas as pd

                st.success(f"Showing **{len(txns)}** transaction(s) for account **{acno}**")
                df = pd.DataFrame(txns[::-1])
                df = df[["timestamp", "trans_type", "amount", "related_acno"]]
                df.columns = ["Timestamp", "Type", "Amount (₹)", "Related Account"]
                df["Related Account"] = df["Related Account"].fillna("—")
                st.dataframe(df, use_container_width=True, hide_index=True)

                # Simple chart
                st.markdown("##### Amount Trend")
                chart_df = pd.DataFrame({"Amount": [t["amount"] for t in txns]})
                st.area_chart(chart_df, color="#58a6ff")
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 8 – ALL ACCOUNTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋  All Accounts":
    page_header("All Accounts", "📋")

    accounts = load_accounts(st.session_state.token, st.session_state.role)
    if not accounts:
        st.info("No accounts yet. Create one first!")
    else:
        import pandas as pd

        # Filter controls
        col1, col2, col3 = st.columns([2, 1, 1])
        search = col1.text_input("🔎 Search by name", placeholder="Type a name...")
        type_filter = col2.selectbox("Filter by Type", ["All", "Savings", "Current"])
        sort_by = col3.selectbox("Sort by", ["Balance ↓", "Balance ↑", "Name"])

        df = pd.DataFrame(accounts)
        if not df.empty and "acno" in df.columns:
            df = df[["acno", "name", "acc_type", "deposit"]]
        df.columns = ["Account No", "Name", "Type", "Balance (₹)"]
        df["Type Label"] = df["Type"].map({"S": "Savings", "C": "Current"})

        if search:
            df = df[df["Name"].str.contains(search, case=False, na=False)]
        if type_filter != "All":
            df = df[df["Type Label"] == type_filter]
        if sort_by == "Balance ↓":
            df = df.sort_values("Balance (₹)", ascending=False)
        elif sort_by == "Balance ↑":
            df = df.sort_values("Balance (₹)", ascending=True)
        else:
            df = df.sort_values("Name")

        st.markdown(f"<p style='color:#8b949e;font-size:13px;'>Showing **{len(df)}** account(s)</p>", unsafe_allow_html=True)
        st.dataframe(
            df[["Account No", "Name", "Type Label", "Balance (₹)"]].rename(columns={"Type Label": "Type"}),
            use_container_width=True,
            hide_index=True,
        )

        # Download CSV
        csv = df.to_csv(index=False)
        st.download_button(
            "⬇️ Download as CSV",
            data=csv,
            file_name="accounts.csv",
            mime="text/csv",
        )


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 9 – MODIFY ACCOUNT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "✏️  Modify Account":
    page_header("Modify Account", "✏️")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    acno = st.number_input("Enter Account Number to modify", min_value=1000000000, step=1, format="%d")

    if st.button("🔍 Load Account"):
        acc = find_account(int(acno))
        if not acc:
            st.error("❌ Account not found.")
        else:
            st.session_state["modify_acc"] = acc

    if "modify_acc" in st.session_state:
        acc = st.session_state["modify_acc"]
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Name", value=acc["name"])
            new_type = st.selectbox(
                "Account Type",
                ["Savings (S)", "Current (C)"],
                index=0 if acc["acc_type"] == "S" else 1,
            )
        with col2:
            new_type_code = "S" if new_type.startswith("S") else "C"
            min_dep = 500 if new_type_code == "S" else 1000
            new_deposit = st.number_input(
                f"Balance (Min ₹{min_dep})",
                value=acc["deposit"],
                min_value=0,
                step=100,
            )

        if st.button("💾 Save Changes"):
            if not new_name.strip():
                st.error("Name cannot be empty.")
            elif new_deposit < min_dep:
                st.error(f"Minimum balance for this account type is ₹{min_dep}.")
            else:
                success = update_account(st.session_state.token, acc["acno"], new_name.strip(), new_type_code, new_deposit)
                if success:
                    st.success("✅ Account updated successfully!")
                    del st.session_state["modify_acc"]
                else:
                    st.error("❌ Update failed.")
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 10 – DELETE ACCOUNT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🗑️  Delete Account":
    page_header("Delete Account", "🗑️")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    acno = st.number_input("Account Number to delete", min_value=1000000000, step=1, format="%d")

    if st.button("🔍 Lookup Account"):
        acc = find_account(int(acno))
        if not acc:
            st.error("❌ Account not found.")
        else:
            st.session_state["delete_acc"] = acc

    if "delete_acc" in st.session_state:
        acc = st.session_state["delete_acc"]
        st.warning(
            f"⚠️ You are about to permanently delete:\n\n"
            f"**Name:** {acc['name']}  |  **Balance:** {format_currency(acc['deposit'])}  |  **Type:** {'Savings' if acc['acc_type']=='S' else 'Current'}"
        )
        col1, col2 = st.columns(2)
        if col1.button("🗑️ Confirm Delete", type="primary"):
            success = delete_account(st.session_state.token, acc["acno"])
            if success:
                st.success("✅ Account deleted.")
                del st.session_state["delete_acc"]
            else:
                st.error("❌ Error deleting account.")
        if col2.button("❌ Cancel"):
            del st.session_state["delete_acc"]
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 11 – AI ASSISTANT (Advanced Chatbot)
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🤖  AI Assistant":
    import datetime
    import pandas as pd
    from api_client import load_transactions

    page_header("AI Banking Assistant", "🤖")

    # ── Extra CSS for advanced chat UI ────────────────────────────────────────
    st.markdown("""
    <style>
    .chat-container { max-height: 520px; overflow-y: auto; padding: 10px 0; }
    .chat-meta { font-size: 10px; color: #8b949e; margin-bottom: 2px; }
    .chat-meta-right { text-align: right; }
    .chip-row { display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0; }
    .chip {
        background: #1c2333; border: 1px solid #30363d; border-radius: 20px;
        padding: 5px 14px; font-size: 12px; color: #58a6ff; cursor: pointer;
        transition: background 0.2s;
    }
    .intent-badge {
        display: inline-block; padding: 2px 8px; border-radius: 12px;
        font-size: 10px; font-weight: 600; margin-bottom: 4px;
    }
    .intent-finance  { background: #1a4a2a; color: #3fb950; }
    .intent-transfer { background: #1a2a4a; color: #58a6ff; }
    .intent-info     { background: #2a1a4a; color: #a78bfa; }
    .intent-action   { background: #4a2a1a; color: #f0883e; }
    .chat-table { width:100%; border-collapse:collapse; font-size:12px; margin-top:6px; }
    .chat-table th { background:#21262d; padding:5px 10px; text-align:left; color:#8b949e; }
    .chat-table td { padding:5px 10px; border-top:1px solid #21262d; color:#e6edf3; }
    .chat-table tr:hover td { background:#1c2333; }
    </style>
    """, unsafe_allow_html=True)

    # ── Session state init ────────────────────────────────────────────────────
    now = datetime.datetime.now()
    hour = now.hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        st.session_state.chat_context = {}   # stores last_acno, pending_action, etc.
        welcome = (
            f"👋 **{greeting}!** I'm your NexaBank AI Assistant.\n\n"
            "Here's what I understand:\n"
            "| Command | Example |\n"
            "|---|---|\n"
            "| Balance enquiry | *balance for 1000000001* |\n"
            "| Transaction history | *history for 1000000001* |\n"
            "| Mini statement | *mini statement 1000000001* |\n"
            "| Fund transfer | *transfer 500 from 1000000001 to 1000000002* |\n"
            "| Deposit | *deposit 300 to 1000000001* |\n"
            "| Withdraw | *withdraw 200 from 1000000001* |\n"
            "| Account info | *info 1000000001* |\n"
            "| Search by name | *find accounts ravi* |\n"
            "| Account stats | *account stats* |\n"
            "| Transaction summary | *transaction summary* |\n"
            "| Create account | *create savings account john doe 5000* |\n"
            "| Delete account | *delete account 1000000001* |"
        )
        st.session_state.chat_history.append({
            "role": "ai", "text": welcome, "intent": "info",
            "time": now.strftime("%H:%M")
        })

    if "chat_context" not in st.session_state:
        st.session_state.chat_context = {}

    # ── Advanced NLP intent engine ────────────────────────────────────────────
    def advanced_chatbot_response(text: str) -> tuple[str, str]:
        """Returns (response_markdown, intent_label)."""
        t = text.strip().lower()
        ctx = st.session_state.chat_context

        # ── 1. Greeting ───────────────────────────────────────────────────────
        if re.match(r"^(hi|hello|hey|good\s*(morning|afternoon|evening|night)|howdy)[\s!.]*$", t):
            return f"👋 {greeting}! How can I assist you today? Type **help** to see all commands.", "info"

        # ── 2. Help ───────────────────────────────────────────────────────────
        if re.search(r"\bhelp\b", t):
            return (
                "🤖 **Available Commands:**\n\n"
                "| Command | Example |\n|---|---|\n"
                "| Balance | *balance for {acno}* |\n"
                "| History | *history for {acno}* |\n"
                "| Mini-statement | *mini statement {acno}* |\n"
                "| Transfer | *transfer {amt} from {acno} to {acno}* |\n"
                "| Deposit | *deposit {amt} to {acno}* |\n"
                "| Withdraw | *withdraw {amt} from {acno}* |\n"
                "| Account info | *info {acno}* |\n"
                "| Search name | *find accounts {name}* |\n"
                "| Global stats | *account stats* |\n"
                "| Txn summary | *transaction summary* |\n"
                "| Create | *create savings account {name} {deposit}* |\n"
                "| Delete | *delete account {acno}* |"
            ), "info"

        # ── 3. Balance enquiry ────────────────────────────────────────────────
        m = re.search(r"(balance|money|funds).{0,20}?(\d{10})", t)
        if m:
            acno = int(m.group(2))
            ctx["last_acno"] = acno
            acc = find_account(acno)
            if acc:
                txns = get_account_transactions(st.session_state.token, acno)
                last_txn = f", last txn: **{txns[-1]['trans_type']} ₹{txns[-1]['amount']:,}** on {txns[-1]['timestamp']}" if txns else ""
                return (
                    f"💰 **Balance Summary**\n\n"
                    f"| Field | Value |\n|---|---|\n"
                    f"| Account No | {acc['acno']} |\n"
                    f"| Name | {acc['name']} |\n"
                    f"| Type | {'Savings' if acc['acc_type'] == 'S' else 'Current'} |\n"
                    f"| **Balance** | **{format_currency(acc['deposit'])}** |"
                    f"{last_txn}"
                ), "finance"
            return f"❌ Account **{acno}** not found.", "finance"

        # ── 4. Transaction history ────────────────────────────────────────────
        m = re.search(r"(history|transactions?|statement).{0,20}?(\d{10})", t)
        if m and "mini" not in t:
            acno = int(m.group(2))
            ctx["last_acno"] = acno
            txns = get_account_transactions(st.session_state.token, acno)
            if not txns:
                return f"📭 No transactions found for account **{acno}**.", "info"
            recent = txns[-10:][::-1]
            rows = "\n".join(
                f"| {tx['timestamp']} | `{tx['trans_type']}` | ₹{tx['amount']:,} | {tx['related_acno'] or '—'} |"
                for tx in recent
            )
            return (
                f"📜 **Last {len(recent)} Transactions** for account **{acno}**\n\n"
                f"| Timestamp | Type | Amount | Ref |\n|---|---|---|---|\n{rows}"
            ), "finance"

        # ── 5. Mini statement (last 3 txns + balance) ────────────────────────
        m = re.search(r"mini.{0,10}(statement|stmt).{0,10}?(\d{10})", t)
        if m:
            acno = int(m.group(2))
            ctx["last_acno"] = acno
            acc = find_account(acno)
            if not acc:
                return f"❌ Account **{acno}** not found.", "finance"
            txns = get_account_transactions(st.session_state.token, acno)
            last3 = txns[-3:][::-1]
            rows = "\n".join(
                f"| {tx['timestamp']} | `{tx['trans_type']}` | ₹{tx['amount']:,} |"
                for tx in last3
            ) or "| — | No transactions | — |"
            return (
                f"🧾 **Mini Statement** — Account **{acno}** ({acc['name']})\n\n"
                f"**Balance:** {format_currency(acc['deposit'])}\n\n"
                f"| Timestamp | Type | Amount |\n|---|---|---|\n{rows}"
            ), "finance"

        # ── 6. Fund transfer ──────────────────────────────────────────────────
        m = re.search(r"transfer\s+(\d+)\s+(?:from\s+)?(\d{10})\s+(?:to\s+)?(\d{10})", t)
        if m:
            amount, from_acc, to_acc = int(m.group(1)), int(m.group(2)), int(m.group(3))
            ctx["last_acno"] = from_acc
            if from_acc == to_acc:
                return "❌ Source and destination accounts cannot be the same.", "transfer"
            success, msg = transfer_funds(st.session_state.token, from_acc, to_acc, amount)
            if success:
                fa = find_account(from_acc)
                return (
                    f"✅ **Transfer Successful!**\n\n"
                    f"| Detail | Value |\n|---|---|\n"
                    f"| Amount | ₹{amount:,} |\n"
                    f"| From | {from_acc} |\n"
                    f"| To | {to_acc} |\n"
                    f"| New Balance (sender) | {format_currency(fa['deposit'] if fa else 0)} |"
                ), "transfer"
            return f"❌ Transfer failed: **{msg}**", "transfer"

        # ── 7. Deposit ────────────────────────────────────────────────────────
        m = re.search(r"deposit\s+(\d+)\s+(?:to\s+|into\s+)?(\d{10})", t)
        if m:
            amount, acno = int(m.group(1)), int(m.group(2))
            ctx["last_acno"] = acno
            success, data = deposit_amount(st.session_state.token, acno, amount)
            if success:
                return (
                    f"✅ **Deposit Successful!**\n\n"
                    f"Deposited **{format_currency(amount)}** to account **{acno}**.\n"
                    f"New Balance: **{format_currency(data['deposit'])}**"
                ), "finance"
            return f"❌ Account **{acno}** not found or error occurred.", "finance"

        # ── 8. Withdraw ───────────────────────────────────────────────────────
        m = re.search(r"withdraw\s+(\d+)\s+(?:from\s+)?(\d{10})", t)
        if m:
            amount, acno = int(m.group(1)), int(m.group(2))
            ctx["last_acno"] = acno
            success, data = withdraw_amount(st.session_state.token, acno, amount)
            if success:
                return (
                    f"✅ **Withdrawal Successful!**\n\n"
                    f"Withdrew **{format_currency(amount)}** from account **{acno}**.\n"
                    f"Remaining Balance: **{format_currency(data['deposit'])}**"
                ), "finance"
            else:
                return (
                    f"❌ **Withdrawal Failed.**\n\n"
                    f"Reason: {data}"
                ), "finance"

        # ── 9. Account info ───────────────────────────────────────────────────
        m = re.search(r"(info|details?|show|lookup)\s+(\d{10})", t)
        if m:
            acno = int(m.group(2))
            ctx["last_acno"] = acno
            acc = find_account(acno)
            if not acc:
                return f"❌ Account **{acno}** not found.", "info"
            txns = get_account_transactions(st.session_state.token, acno)
            total_deposited = sum(tx["amount"] for tx in txns if tx["trans_type"] == "DEPOSIT")
            total_withdrawn = sum(tx["amount"] for tx in txns if tx["trans_type"] == "WITHDRAW")
            return (
                f"📋 **Account Details**\n\n"
                f"| Field | Value |\n|---|---|\n"
                f"| Account No | {acc['acno']} |\n"
                f"| Name | {acc['name']} |\n"
                f"| Type | {'Savings' if acc['acc_type'] == 'S' else 'Current'} |\n"
                f"| Balance | {format_currency(acc['deposit'])} |\n"
                f"| Total Deposited | {format_currency(total_deposited)} |\n"
                f"| Total Withdrawn | {format_currency(total_withdrawn)} |\n"
                f"| No. of Transactions | {len(txns)} |"
            ), "info"

        # ── 10. Search accounts by name ───────────────────────────────────────
        m = re.search(r"(?:find|search|lookup)\s+(?:accounts?\s+(?:for\s+)?)?(.+)", t)
        if m and not re.search(r"\d{10}", m.group(1)):
            name_query = m.group(1).strip()
            accounts = load_accounts(st.session_state.token, st.session_state.role)
            matches = [a for a in accounts if name_query.lower() in a["name"].lower()]
            if not matches:
                return f"🔍 No accounts found matching **\"{name_query}\"**.", "info"
            rows = "\n".join(
                f"| {a['acno']} | {a['name']} | {'Savings' if a['acc_type']=='S' else 'Current'} | {format_currency(a['deposit'])} |"
                for a in matches
            )
            return (
                f"🔍 Found **{len(matches)}** account(s) matching **\"{name_query}\"**\n\n"
                f"| Account No | Name | Type | Balance |\n|---|---|---|---|\n{rows}"
            ), "info"

        # ── 11. Global account stats ──────────────────────────────────────────
        if re.search(r"(account\s+stats?|statistics|overview|summary\s+of\s+accounts?)", t):
            accounts = load_accounts(st.session_state.token, st.session_state.role)
            if not accounts:
                return "📭 No accounts found in the system.", "info"
            total = len(accounts)
            savings = [a for a in accounts if a["acc_type"] == "S"]
            current = [a for a in accounts if a["acc_type"] == "C"]
            total_bal = sum(a["deposit"] for a in accounts)
            avg_bal = total_bal / total if total else 0
            richest = max(accounts, key=lambda x: x["deposit"])
            return (
                f"📊 **Bank Account Statistics**\n\n"
                f"| Metric | Value |\n|---|---|\n"
                f"| Total Accounts | {total} |\n"
                f"| Savings Accounts | {len(savings)} |\n"
                f"| Current Accounts | {len(current)} |\n"
                f"| Total Deposits | {format_currency(total_bal)} |\n"
                f"| Average Balance | {format_currency(avg_bal)} |\n"
                f"| Highest Balance | {richest['name']} — {format_currency(richest['deposit'])} |"
            ), "info"

        # ── 12. Transaction summary (bank-wide) ───────────────────────────────
        if re.search(r"transaction\s+summary|txn\s+summary|all\s+transactions", t):
            txns = load_transactions(st.session_state.token) if st.session_state.role in ["teller", "manager"] else []
            if not txns:
                return "📭 No transactions recorded yet.", "info"
            deposits = [tx for tx in txns if tx["trans_type"] == "DEPOSIT"]
            withdraws = [tx for tx in txns if tx["trans_type"] == "WITHDRAW"]
            transfers = [tx for tx in txns if "TRANSFER" in tx["trans_type"]]
            return (
                f"📈 **Bank-wide Transaction Summary**\n\n"
                f"| Type | Count | Total Amount |\n|---|---|---|\n"
                f"| Deposits | {len(deposits)} | {format_currency(sum(x['amount'] for x in deposits))} |\n"
                f"| Withdrawals | {len(withdraws)} | {format_currency(sum(x['amount'] for x in withdraws))} |\n"
                f"| Transfers | {len(transfers)//2 if transfers else 0} | {format_currency(sum(x['amount'] for x in transfers)//2)} |\n"
                f"| **Total** | **{len(txns)}** | — |"
            ), "info"

        # ── 13. Create account via chat ───────────────────────────────────────
        m = re.search(r"create\s+(savings?|current)\s+account\s+(.+?)\s+(\d+)$", t)
        if m:
            acc_type_raw = m.group(1)
            name = m.group(2).strip().title()
            deposit = int(m.group(3))
            acc_code = "S" if "sav" in acc_type_raw else "C"
            min_dep = 500 if acc_code == "S" else 1000
            if deposit < min_dep:
                return (
                    f"❌ Minimum deposit for {'Savings' if acc_code=='S' else 'Current'} account is ₹{min_dep:,}.\n"
                    f"You entered: ₹{deposit:,}."
                ), "action"
            resp = create_account(st.session_state.token, name, acc_code, deposit)
            new_acno = resp.get("acno", "Unknown")
            ctx["last_acno"] = new_acno
            return (
                f"🎉 **Account Created Successfully!**\n\n"
                f"| Field | Value |\n|---|---|\n"
                f"| Account No | **{new_acno}** |\n"
                f"| Name | {name} |\n"
                f"| Type | {'Savings' if acc_code=='S' else 'Current'} |\n"
                f"| Opening Balance | {format_currency(deposit)} |"
            ), "action"

        # ── 14. Delete account via chat ───────────────────────────────────────
        m = re.search(r"delete\s+account\s+(\d{10})", t)
        if m:
            acno = int(m.group(1))
            acc = find_account(acno)
            if not acc:
                return f"❌ Account **{acno}** not found.", "action"
            success = delete_account(st.session_state.token, acno)
            if success:
                return (
                    f"🗑️ Account **{acno}** ({acc['name']}) has been **permanently deleted**.\n"
                    f"Final balance was {format_currency(acc['deposit'])}."
                ), "action"
            return f"❌ Failed to delete account **{acno}**.", "action"

        # ── 15. Context-aware: use last account number ────────────────────────
        if ctx.get("last_acno") and re.search(r"\b(balance|info|history|statement)\b", t):
            acno = ctx["last_acno"]
            if "balance" in t:
                acc = find_account(acno)
                return (f"💰 Balance for your last account **{acno}**: **{format_currency(acc['deposit'])}**"
                        if acc else f"❌ Account **{acno}** no longer exists."), "finance"
            if "info" in t or "detail" in t:
                acc = find_account(acno)
                if acc:
                    return (
                        f"📋 Quick info for **{acno}**: **{acc['name']}** | "
                        f"{'Savings' if acc['acc_type']=='S' else 'Current'} | "
                        f"{format_currency(acc['deposit'])}"
                    ), "info"

        # ── Fallback ──────────────────────────────────────────────────────────
        suggestions = [
            "balance for", "history for", "mini statement", "transfer",
            "deposit", "withdraw", "account stats", "transaction summary", "help"
        ]
        did_you_mean = ""
        for s in suggestions:
            if any(word in t for word in s.split()):
                did_you_mean = f"\n\nDid you mean: **{s} ...**?"
                break
        return (
            f"🤔 I couldn't understand that command.{did_you_mean}\n\n"
            "Type **help** to see all available commands."
        ), "info"

    # ── Intent badge HTML ─────────────────────────────────────────────────────
    INTENT_CSS = {
        "finance":  "intent-finance",
        "transfer": "intent-transfer",
        "info":     "intent-info",
        "action":   "intent-action",
    }
    INTENT_LABELS = {
        "finance":  "💰 Finance",
        "transfer": "🔄 Transfer",
        "info":     "ℹ️ Info",
        "action":   "⚙️ Action",
    }

    # ── Render chat ───────────────────────────────────────────────────────────
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        ts = msg.get("time", "")
        if msg["role"] == "user":
            st.markdown(
                f'<div class="chat-meta chat-meta-right">You · {ts}</div>'
                f'<div class="chat-wrap"><div class="chat-user">{msg["text"]}</div></div>',
                unsafe_allow_html=True,
            )
        else:
            intent = msg.get("intent", "info")
            badge_cls = INTENT_CSS.get(intent, "intent-info")
            badge_lbl = INTENT_LABELS.get(intent, "ℹ️ Info")
            st.markdown(
                f'<div class="chat-meta">🤖 NexaBank AI · {ts}'
                f'<span class="intent-badge {badge_cls}" style="margin-left:8px;">{badge_lbl}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown(msg["text"])
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Quick-reply chips ─────────────────────────────────────────────────────
    st.markdown("**💡 Quick suggestions:**")
    chips = [
        "account stats", "transaction summary", "help",
        "find accounts ", "mini statement ",
    ]
    chip_cols = st.columns(len(chips))
    for col, chip in zip(chip_cols, chips):
        if col.button(chip, key=f"chip_{chip}"):
            ts_now = datetime.datetime.now().strftime("%H:%M")
            st.session_state.chat_history.append({
                "role": "user", "text": chip, "time": ts_now
            })
            reply, intent = advanced_chatbot_response(chip)
            st.session_state.chat_history.append({
                "role": "ai", "text": reply, "intent": intent, "time": ts_now
            })
            st.rerun()

    st.markdown("---")

    # ── Input row ─────────────────────────────────────────────────────────────
    col_input, col_btn = st.columns([6, 1])
    user_input = col_input.text_input(
        "Message",
        placeholder="e.g. 'balance for 1000000001' or 'transfer 500 from … to …'",
        label_visibility="collapsed",
        key="chat_input",
    )
    send = col_btn.button("Send ➤", use_container_width=True)

    if send and user_input.strip():
        ts_now = datetime.datetime.now().strftime("%H:%M")
        st.session_state.chat_history.append({
            "role": "user", "text": user_input.strip(), "time": ts_now
        })
        reply, intent = advanced_chatbot_response(user_input.strip())
        st.session_state.chat_history.append({
            "role": "ai", "text": reply, "intent": intent, "time": ts_now
        })
        st.rerun()

    # ── Footer tools ──────────────────────────────────────────────────────────
    col_clear, col_export, _ = st.columns([1, 1, 4])
    if col_clear.button("🗑️ Clear Chat"):
        intro = st.session_state.chat_history[0]
        st.session_state.chat_history = [intro]
        st.session_state.chat_context = {}
        st.rerun()

    if col_export.button("📥 Export Chat"):
        lines = []
        for msg in st.session_state.chat_history:
            role = "You" if msg["role"] == "user" else "AI"
            lines.append(f"[{msg.get('time','')}] {role}: {msg['text']}\n")
        st.download_button(
            "⬇️ Download transcript",
            data="\n".join(lines),
            file_name="nexa_chat_export.txt",
            mime="text/plain",
        )

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 12 – SECURITY PROFILE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🛡️  Security Profile":
    page_header("Security Settings", "🛡️")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    st.markdown("### Two-Factor Authentication (2FA)")
    if getattr(st.session_state, "is_2fa_enabled", False):
        st.success("✅ 2FA is successfully enabled on your account.")
    else:
        st.warning("⚠️ 2FA is currently disabled. We highly recommend enabling it to secure your transactions.")
        
        if st.button("Generate Setup Key"):
            success, data = setup_2fa(st.session_state.token)
            if success:
                st.session_state["2fa_secret"] = data["secret"]
                st.session_state["2fa_uri"] = data["uri"]
            else:
                st.error("Could not generate setup key.")
                
        if "2fa_secret" in st.session_state:
            st.info(f"**Manual Secret Key:** `{st.session_state['2fa_secret']}`")
            st.markdown("Enter this key into Google Authenticator or Authy to configure 2FA.")
            
            verify_code = st.text_input("Enter 6-digit Code to Verify")
            if st.button("Verify & Enable 2FA"):
                if verify_code.strip():
                    success, msg = verify_2fa(st.session_state.token, verify_code.strip())
                    if success:
                        st.success("✅ " + msg)
                        st.session_state.is_2fa_enabled = True
                    else:
                        st.error("❌ " + msg)
                else:
                    st.error("Please enter the code.")
                
    st.markdown("</div>", unsafe_allow_html=True)
