import os
import shutil
import re

# 0. Copy ipclub.ico to rustdesk resources
if os.path.exists('ipclub.ico'):
    shutil.copyfile('ipclub.ico', 'rustdesk/res/icon.ico')
    shutil.copyfile('ipclub.ico', 'rustdesk/res/tray-icon.ico')
    print("COPIED_IPCLUB_ICO_TO_RES")

# Fix inline-sciter.py to always read and write files with encoding='utf-8' on Windows
inline_sciter_path = 'rustdesk/res/inline-sciter.py'
if os.path.exists(inline_sciter_path):
    with open(inline_sciter_path, 'r', encoding='utf-8') as f:
        sciter_script = f.read()
    
    # Force utf-8 on all open() calls
    sciter_script = sciter_script.replace("open('src/ui/inline.rs', 'wt')", "open('src/ui/inline.rs', 'wt', encoding='utf-8')")
    sciter_script = re.sub(r"open\((['\"][^'\"]+['\"])\)\.read\(\)", r"open(\1, encoding='utf-8').read()", sciter_script)
    
    with open(inline_sciter_path, 'w', encoding='utf-8') as f:
        f.write(sciter_script)
    print("FIXED_INLINE_SCITER_ENCODING_COMPREHENSIVE")

with open('ipclub_logo_128_b64.txt', 'r', encoding='utf-8') as f:
    logo_b64 = f.read().strip()

# 1. Update ui.rs with official IPClub icon
with open('rustdesk/src/ui.rs', 'r', encoding='utf-8') as f:
    ui_code = f.read()

new_ui_code = re.sub(r'\"data:image/png;base64,[A-Za-z0-9+/=]+\"\.into\(\)', f'\"data:image/png;base64,{logo_b64}\".into()', ui_code)
with open('rustdesk/src/ui.rs', 'w', encoding='utf-8') as f:
    f.write(new_ui_code)
print("UPDATED_UI_RS_ICON")

# 2. Update index.css
with open('rustdesk/src/ui/index.css', 'r', encoding='utf-8') as f:
    index_css = f.read()

custom_css = """
/* IPClub Official Custom Styles */
div.ipclub-top-logo {
    flow: horizontal;
    border-spacing: 12px;
    margin-bottom: 1.2em;
    padding-bottom: 0.8em;
    border-bottom: 1px solid #e0e0e0;
}
div.ipclub-top-logo img {
    size: 42px;
}
div.ipclub-top-logo .brand-title {
    font-size: 1.3em;
    font-weight: bold;
    color: #0f172a;
    line-height: 1.2em;
}
div.ipclub-top-logo .brand-sub {
    font-size: 0.75em;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Custom UAC Card */
div.install-me {
    background: linear-gradient(135deg, #1e3a8a, #2563eb) !important;
    border-radius: 8px !important;
    padding: 14px !important;
    margin-top: 1em !important;
}
div.install-me .button {
    background: white !important;
    color: #1e3a8a !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 6px 16px !important;
    cursor: pointer !important;
}
div.install-me .button:hover {
    background: #f1f5f9 !important;
}

/* Custom Footer Links */
div.connect-status {
    flow: horizontal;
    border-spacing: 10px;
    font-size: 0.85em;
}
div.connect-status a.footer-link, div.connect-status span.footer-link {
    color: #2563eb;
    text-decoration: underline;
    cursor: pointer;
}
div.connect-status a.footer-link:hover, div.connect-status span.footer-link:hover {
    color: #1d4ed8;
}
"""
index_css += custom_css
with open('rustdesk/src/ui/index.css', 'w', encoding='utf-8') as f:
    f.write(index_css)
print("UPDATED_INDEX_CSS")

# 3. Update index.tis
with open('rustdesk/src/ui/index.tis', 'r', encoding='utf-8') as f:
    index_tis = f.read()

# Replace InstallMe text using safe HTML entities so Sciter renders UTF-8 flawlessly on any OS
install_me_old = "<div>{translate('install_tip')}</div>"
install_me_new = "<div><strong>Permiss&#xe3;o de Administrador (UAC):</strong><br/>Para que o suporte t&#xe9;cnico da IPClub responda &#xe0;s confirma&#xe7;&#xf5;es do Windows e instale programas sem travar a tela, clique no bot&#xe3;o abaixo:</div>"
if install_me_old in index_tis:
    index_tis = index_tis.replace(install_me_old, install_me_new)
    print("REPLACED_INSTALL_ME_TEXT")
else:
    print("WARNING: install_me_old not found!")

# Add Top Logo
logo_html = f'''<div .ipclub-top-logo>
                        <img src="data:image/png;base64,{logo_b64}" />
                        <div>
                            <div .brand-title>IPClub</div>
                            <div .brand-sub>Remote Control</div>
                        </div>
                    </div>'''

# Match <div .left-pane ...>
left_pane_regex = r'(<div \.left-pane[^>]*>)'
if re.search(left_pane_regex, index_tis):
    index_tis = re.sub(left_pane_regex, r'\1\n                    ' + logo_html, index_tis, count=1)
    print("INJECTED_TOP_LOGO")
else:
    print("WARNING: left-pane not found!")

# Replace ConnectStatus footer with safe ASCII / HTML-entities
status_code = """    function getConnectStatusStr() {
        if (service_stopped) {
            return translate("Service is not running");
        } else if (connect_status == -1) {
            return translate('not_ready_status');
        } else if (connect_status == 0) {
            return translate('connecting_status');
        }
        return <span>{translate("Ready")} | <span .footer-link #link-site>ipclub.com.br</span> | <span .footer-link #link-zap>WhatsApp: 0800 305 7300</span> | <span .footer-link #link-planos>Planos</span></span>;
    }

    event click $(#link-site) () {
        handler.open_url("https://ipclub.com.br");
    }

    event click $(#link-zap) () {
        handler.open_url("https://wa.me/5508003057300");
    }

    event click $(#link-planos) () {
        handler.open_url("https://remote.ipclub.com.br/planos");
    }
}"""

old_status_regex = r'function getConnectStatusStr\(\) \{[\s\S]*?event click \$\(#setup-server\) \(\) \{[\s\S]*?\}\r?\n\}'
if re.search(old_status_regex, index_tis):
    index_tis = re.sub(old_status_regex, status_code, index_tis, count=1)
    print("REPLACED_FOOTER_STATUS")
else:
    print("WARNING: old_status_regex not matched!")

with open('rustdesk/src/ui/index.tis', 'w', encoding='utf-8') as f:
    f.write(index_tis)

# 4. Also update Portuguese translation in rustdesk/src/lang/pt_BR.rs
pt_lang_path = 'rustdesk/src/lang/pt_BR.rs'
if os.path.exists(pt_lang_path):
    with open(pt_lang_path, 'r', encoding='utf-8') as f:
        pt_content = f.read()
    pt_content = pt_content.replace('RustDesk', 'IPClub Remote')
    pt_content = pt_content.replace('rustdesk.com', 'ipclub.com.br')
    with open(pt_lang_path, 'w', encoding='utf-8') as f:
        f.write(pt_content)
    print("UPDATED_PT_BR_LANG")

print("ALL_CUSTOMIZATIONS_SUCCESS")
