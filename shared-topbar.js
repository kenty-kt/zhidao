(function () {
  const LOGIN_STORAGE_KEY = "zhidao_login_v1";
  const AUTH_STORAGE_KEY = "zhidao_authorizations_v1";
  const UI_THEME_STORAGE_KEY = "zhidao_trade2_theme_v1";
  const UI_LANG_STORAGE_KEY = "zhidao_trade2_lang_v1";
  const AUTH_META = {
    binance: {
      title: "Binance",
      remarkLabel: "账户备注名(选填)",
      remarkPlaceholder: "可不填，输入以便管理",
      quickTitle: "一键连接你的授权币安账户。无需提供 API Key，数据能更多",
      quickSteps: [
        "点击下方【前往开启即时授权币安账户】按钮",
        "登录你的币安账户，并授权 知道Ai 访问权限",
        "授权完成后，系统将自动获取你的账户信息",
        "返回本页面，即可开始使用 AI 交易助手"
      ],
      quickButton: "前往在线即时授权币安账户",
      quickUrl: "https://accounts.binance.com/zh-CN/login",
      keyLabel: "API密钥",
      keyPlaceholder: "填写 Binance API密钥",
      secretLabel: "密钥",
      secretPlaceholder: "填写 Binance 密钥",
      passLabel: "",
      passPlaceholder: "",
      hidePass: true,
      tutorialTitle: "授权教程",
      tutorialSteps: [
        "1. 访问【币安】，并完成登录账号；",
        "2. 点击【个人中心】→【API管理】→【创建API】→【系统生成API】；",
        "3. 【备注】为您需要记忆；【创建】，然后【安装设置API-KEY申请限制】",
        "4. 输入【文件上是否开启“现货及杠杆交易”】，其它选项【API交易】选项都须进行；",
        "5. 从提款账号ID导出，输入【你设定的API】密钥信息；",
        "6. 保存到记录需要本窗口开一个安全档案对外进行完毕授权下载等级。"
      ]
    },
    okx: {
      title: "OKX",
      remarkLabel: "账户备注名(选填)",
      remarkPlaceholder: "可不填，输入以便管理",
      quickTitle: "一键连接你的授权欧易账户。无需提供 API Key，数据能更多",
      quickSteps: [
        "点击下方【前往开启即时授权欧易账户】按钮",
        "登录你的欧易账户，并授权 知道Ai 访问权限",
        "授权完成后，系统将自动获取你的账户信息",
        "返回本页面，即可开始使用 AI 交易助手"
      ],
      quickButton: "前往在线即时授权欧易账户",
      quickUrl: "https://www.okx.com/",
      keyLabel: "API Key",
      keyPlaceholder: "填写 OKX API Key",
      secretLabel: "密钥",
      secretPlaceholder: "填写 OKX 密钥",
      passLabel: "密码 (Passphrase)",
      passPlaceholder: "填写 OKX Passphrase",
      tutorialTitle: "授权教程",
      tutorialSteps: [
        "1. 访问【欧易】，并完成登录账号；",
        "2. 点击【个人中心】→【API管理】→【创建API】；",
        "3. 选择只读或交易权限，不要开启提币权限；",
        "4. 复制 API Key、Secret、Passphrase 回到本页面；"
      ]
    },
    hyper: {
      title: "Hyperliquid",
      remarkLabel: "账户备注名",
      remarkPlaceholder: "填写账户备注名",
      quickTitle: "Hyperliquid 当前仅支持 API 授权",
      quickSteps: [
        "1. 访问 Hyperliquid 并登录；",
        "2. 在 API 页面生成 API 钱包地址与私钥；",
        "3. 返回本页面填写主钱包地址、API 钱包地址和私钥；"
      ],
      quickButton: "前往 Hyperliquid",
      quickUrl: "https://hyperliquid.xyz/",
      keyLabel: "主钱包地址",
      keyPlaceholder: "填写主钱包地址",
      secretLabel: "API钱包地址",
      secretPlaceholder: "填写 API 钱包地址",
      passLabel: "API钱包私钥",
      passPlaceholder: "填写 API 钱包私钥",
      tutorialTitle: "授权教程",
      tutorialSteps: [
        "1. 访问【Hyperliquid】，并完成登录账号；",
        "2. 创建 API 钱包地址与私钥；",
        "3. 填写信息并保存授权。"
      ],
      quickDisabled: true
    }
  };

  const style = document.createElement("style");
  style.textContent = `
    .shared-user-menu{position:fixed;z-index:125;min-width:320px;border-radius:18px;border:1px solid rgba(255,255,255,.08);background:#23272f;box-shadow:0 24px 60px rgba(0,0,0,.4);overflow:hidden;display:none}
    .shared-user-menu.open{display:block}
    .shared-user-head{display:flex;align-items:center;gap:14px;padding:18px;border-bottom:1px solid rgba(255,255,255,.08)}
    .shared-user-avatar{width:44px;height:44px;border-radius:14px;background:#4c6ecb;color:#fff;display:inline-flex;align-items:center;justify-content:center;font-size:24px}
    .shared-user-name{font-size:20px;color:#f3f4f6}
    .shared-user-body{padding:12px 0;border-bottom:1px solid rgba(255,255,255,.08)}
    .shared-user-item{width:100%;height:56px;padding:0 18px;border:0;background:transparent;color:#f3f4f6;display:flex;align-items:center;gap:14px;font-size:17px;text-align:left;cursor:pointer}
    .shared-user-item:hover{background:rgba(255,255,255,.04)}
    .shared-user-icon{width:24px;text-align:center;color:#d4dae4}
    .shared-user-logout{width:100%;height:56px;padding:0 18px;border:0;background:transparent;color:#ff647a;display:flex;align-items:center;gap:14px;font-size:17px;text-align:left;cursor:pointer}
    .shared-user-logout:hover{background:rgba(255,255,255,.04)}
    .shared-confirm-modal{position:fixed;inset:0;z-index:150;display:none;align-items:center;justify-content:center;padding:20px;background:rgba(7,10,14,.64);backdrop-filter:blur(10px)}
    .shared-confirm-modal.open{display:flex}
    .shared-confirm-panel{width:min(100%,420px);border-radius:18px;border:1px solid rgba(255,255,255,.08);background:#252b34;box-shadow:0 28px 90px rgba(0,0,0,.42);padding:22px}
    .shared-confirm-title{font-size:20px;font-weight:800;color:#f8fafc;margin-bottom:10px}
    .shared-confirm-text{font-size:14px;line-height:1.7;color:#a8b1c1;margin-bottom:18px}
    .shared-confirm-actions{display:flex;justify-content:flex-end;gap:10px}
    .shared-confirm-btn{height:40px;padding:0 16px;border-radius:12px;border:1px solid rgba(255,255,255,.08);background:#313845;color:#f3f4f6;font-size:14px;font-weight:800;cursor:pointer}
    .shared-confirm-btn.danger{border-color:#ff4d71;color:#ff647a;background:transparent}
    .shared-account-modal{position:fixed;inset:0;z-index:130;display:none;align-items:center;justify-content:center;padding:48px;background:rgba(7,10,14,.62);backdrop-filter:blur(18px)}
    .shared-account-modal.open{display:flex}
    .shared-account-panel{width:min(720px,58vw);height:min(600px,72vh);border-radius:18px;border:1px solid rgba(255,255,255,.06);background:#22272f;box-shadow:0 30px 100px rgba(0,0,0,.42);display:flex;flex-direction:column;overflow:hidden}
    .shared-account-content{display:flex;flex-direction:column;min-width:0}
    .shared-account-head{height:48px;display:flex;align-items:center;justify-content:space-between;padding:0 14px;border-bottom:1px solid rgba(255,255,255,.08)}
    .shared-account-title{font-size:14px;font-weight:800;color:#f8fafc}
    .shared-account-close{width:26px;height:26px;border:0;background:transparent;color:#9199aa;font-size:20px;cursor:pointer}
    .shared-account-scroll{padding:8px 12px 12px;overflow:auto;background:#22272f}
    .shared-profile-card,.shared-exchange-card,.shared-security-card{border-radius:12px;border:1px solid rgba(255,255,255,.06);background:#303743;padding:8px}
    .shared-profile-card{display:flex;align-items:center;gap:10px;margin-bottom:8px}
    .shared-profile-avatar{width:42px;height:42px;border-radius:12px;background:#4967b6;display:inline-flex;align-items:center;justify-content:center;color:#fff;font-size:24px;flex:0 0 auto}
    .shared-profile-name{font-size:14px;color:#f8fafc}
    .shared-profile-meta{margin-top:2px;font-size:10px;color:#9aa4b5}
    .shared-section-title{font-size:13px;font-weight:800;color:#f8fafc;margin-bottom:6px}
    .shared-exchange-list{display:grid;gap:6px}
    .shared-exchange-card{margin-bottom:0}
    .shared-exchange-top{display:flex;align-items:center;justify-content:space-between;gap:10px;padding-bottom:6px;border-bottom:1px solid rgba(255,255,255,.05)}
    .shared-exchange-left{display:flex;align-items:center;gap:10px}
    .shared-exchange-logo{width:40px;height:40px;border-radius:12px;background:#ffffff;display:inline-flex;align-items:center;justify-content:center;font-size:15px;font-weight:800;color:#111827;overflow:hidden}
    .shared-exchange-logo.dark{background:#090c12;color:#fff}
    .shared-exchange-name{font-size:14px;color:#f8fafc}
    .shared-exchange-tag{display:inline-flex;height:18px;padding:0 6px;border-radius:6px;background:rgba(255,255,255,.06);align-items:center;font-size:9px;color:#d4dae4;margin-left:6px}
    .shared-exchange-address{margin-top:2px;font-size:9px;color:#9aa4b5}
    .shared-exchange-status{height:26px;padding:0 9px;border-radius:14px;border:1px solid rgba(0,213,138,.48);background:rgba(0,213,138,.1);color:#00d58a;display:inline-flex;align-items:center;gap:4px;font-size:10px;font-weight:800}
    .shared-exchange-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:4px;padding:6px 0;border-bottom:1px solid rgba(255,255,255,.05)}
    .shared-kv-label{font-size:9px;color:#9aa4b5;margin-bottom:2px}
    .shared-kv-value{font-size:13px;color:#f8fafc}
    .shared-kv-value.green{color:#00d58a}
    .shared-exchange-actions{display:flex;gap:8px;padding-top:6px}
    .shared-exchange-btn{height:28px;padding:0 10px;border-radius:9px;border:1px solid rgba(255,255,255,.08);background:#232831;color:#f3f4f6;font-size:10px;font-weight:800;cursor:pointer}
    .shared-exchange-btn.danger{border-color:#ff4d71;color:#ff4d71;background:transparent}
    .shared-exchange-row{display:flex;align-items:center;justify-content:space-between;gap:16px}
    .shared-exchange-row .shared-exchange-left{gap:12px}
    .shared-authorize-btn{height:28px;padding:0 10px;border-radius:9px;border:0;background:#f3f4f6;color:#111827;font-size:10px;font-weight:800;cursor:pointer}
    .shared-security-card{margin-top:6px;background:#15c97d;border-color:#15c97d;padding:8px 10px}
    .shared-security-title{font-size:12px;color:#f2fff8;font-weight:800;margin-bottom:4px}
    .shared-security-text{font-size:10px;line-height:1.4;color:#f2fff8}
    .shared-login-modal{position:fixed;inset:0;z-index:120;display:none;align-items:center;justify-content:center;padding:20px;background:rgba(4,8,15,.62);backdrop-filter:blur(8px)}
    .shared-login-modal.open{display:flex}
    .shared-login-panel{width:min(100%,480px);border-radius:22px;border:1px solid rgba(255,255,255,.08);background:#1d232c;box-shadow:0 24px 70px rgba(0,0,0,.42);padding:22px}
    .shared-login-head{display:flex;align-items:center;justify-content:space-between;padding-bottom:16px;border-bottom:1px solid rgba(255,255,255,.08);margin-bottom:18px}
    .shared-login-title{font-size:22px;font-weight:800;color:#f8fafc}
    .shared-login-close{width:34px;height:34px;border-radius:999px;border:0;background:transparent;color:#8f99aa;font-size:24px;cursor:pointer}
    .shared-login-label{display:block;font-size:14px;font-weight:700;color:#eef2f7;margin-bottom:8px}
    .shared-login-field,.shared-login-code{width:100%;min-height:58px;border-radius:16px;border:1px solid rgba(255,255,255,.04);background:#333b48;display:flex;align-items:center;padding:0 18px;margin-bottom:16px}
    .shared-login-field input,.shared-login-code input{width:100%;border:0;outline:0;background:transparent;color:#f8fafc;font-size:18px;font-family:inherit}
    .shared-login-field input::placeholder,.shared-login-code input::placeholder{color:rgba(255,255,255,.34)}
    .shared-login-code{justify-content:space-between;gap:12px}
    .shared-login-send{border:0;background:transparent;color:rgba(255,255,255,.56);font-size:16px;cursor:pointer;flex:0 0 auto}
    .shared-login-submit{width:100%;height:58px;border-radius:16px;border:0;background:#f3f4f6;color:#1f2937;font-size:22px;font-weight:800;cursor:pointer;margin-top:6px}
    .shared-login-or{text-align:center;color:rgba(255,255,255,.4);font-size:16px;margin:14px 0}
    .shared-login-socials{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
    .shared-login-social{height:58px;border-radius:16px;border:1px solid rgba(255,255,255,.04);background:#333b48;color:#f3f4f6;display:inline-flex;align-items:center;justify-content:center;gap:10px;font-size:18px;cursor:pointer}
    .shared-auth-modal{position:fixed;inset:0;z-index:140;display:none;align-items:center;justify-content:center;padding:28px;background:rgba(7,10,14,.68);backdrop-filter:blur(14px)}
    .shared-auth-modal.open{display:flex}
    .shared-auth-modal[data-exchange="hyper"] [data-auth-mode="quick"]{display:none !important}
    .shared-auth-modal[data-exchange="hyper"] #sharedQuickView{display:none !important}
    .shared-auth-modal[data-exchange="hyper"] .shared-auth-right{display:none !important}
    .shared-auth-modal[data-exchange="hyper"] .shared-auth-body{grid-template-columns:minmax(0,1fr)}
    .shared-auth-panel{width:min(1180px,92vw);height:min(760px,80vh);border-radius:24px;border:1px solid rgba(255,255,255,.08);background:#23272f;overflow:hidden;box-shadow:0 28px 90px rgba(0,0,0,.46);display:flex;flex-direction:column}
    .shared-auth-top{height:88px;display:flex;align-items:center;justify-content:space-between;padding:0 22px;border-bottom:1px solid rgba(255,255,255,.08)}
    .shared-auth-exchanges{display:flex;gap:14px}
    .shared-auth-tab{height:48px;padding:0 24px;border-radius:16px;border:1px solid rgba(255,255,255,.08);background:#303744;color:#c5ccd8;font-size:18px;cursor:pointer}
    .shared-auth-tab.active{background:#f3f4f6;color:#1f2937}
    .shared-auth-close{width:36px;height:36px;border:0;background:transparent;color:#97a0b1;font-size:30px;cursor:pointer}
    .shared-auth-modebar{height:72px;display:flex;align-items:flex-end;gap:28px;padding:0 22px;border-bottom:1px solid rgba(255,255,255,.08)}
    .shared-auth-mode{height:100%;display:inline-flex;align-items:center;border:0;background:transparent;color:#aeb6c3;font-size:18px;font-weight:800;cursor:pointer;border-bottom:3px solid transparent}
    .shared-auth-mode.active{color:#f3f4f6;border-bottom-color:#f3f4f6}
    .shared-auth-body{display:grid;grid-template-columns:minmax(0,.8fr) minmax(360px,.7fr);flex:1;min-height:0}
    .shared-auth-body.api-only{grid-template-columns:minmax(0,1fr)}
    .shared-auth-body.api-only .shared-auth-right{display:none}
    .shared-auth-body.quick-only{grid-template-columns:minmax(0,1fr)}
    .shared-auth-body.quick-only .shared-auth-right{display:none}
    .shared-auth-left{padding:16px;border-right:1px solid rgba(255,255,255,.08);overflow:auto;scrollbar-width:none;-ms-overflow-style:none;display:flex;justify-content:center}
    .shared-auth-right{padding:20px;background:#171d21;overflow:auto;scrollbar-width:none;-ms-overflow-style:none}
    .shared-auth-left::-webkit-scrollbar,.shared-auth-right::-webkit-scrollbar{display:none}
    .shared-auth-quick-center{width:min(100%,560px);margin:0 auto}
    .shared-auth-notice{display:flex;align-items:center;gap:14px;padding:18px 22px;border-radius:18px;background:rgba(20,118,78,.42);color:#00d58a;font-size:16px;font-weight:700;margin-bottom:18px}
    .shared-auth-card{border-radius:20px;border:1px solid rgba(255,255,255,.06);background:#313845;padding:18px;margin-bottom:18px}
    .shared-auth-brand{display:flex;align-items:center;justify-content:center;gap:18px;padding:20px 0 14px}
    .shared-auth-brand-logo{width:86px;height:86px;border-radius:22px;background:#1d232c;color:#fff;display:inline-flex;align-items:center;justify-content:center;font-size:34px;font-weight:800}
    .shared-auth-brand-link{display:flex;align-items:center;gap:18px;color:#00d58a;font-size:18px}
    .shared-auth-card-title{text-align:center;color:#cfd5df;font-size:16px;margin-bottom:8px}
    .shared-auth-steps{margin:0;padding-left:26px;color:#cfd5df;font-size:16px;line-height:1.8}
    .shared-auth-options{display:grid;gap:10px;margin:18px 0;color:#e2e8f0;font-size:15px}
    .shared-auth-primary{width:100%;height:34px;border-radius:12px;border:0;background:#ff9c1a;color:#1f2937;font-size:18px;font-weight:800;cursor:pointer}
    .shared-auth-footwarn{margin-top:18px;border-radius:18px;background:#4a4034;color:#ff9c1a;padding:16px 18px;font-size:15px;line-height:1.7}
    .shared-auth-form{display:grid;gap:16px}
    .shared-auth-label{font-size:16px;color:#f3f4f6}
    .shared-auth-input{width:100%;height:48px;border-radius:14px;border:1px solid rgba(255,255,255,.04);background:#39414e;color:#f8fafc;padding:0 16px;font-size:16px}
    .shared-auth-input::placeholder{color:rgba(255,255,255,.35)}
    .shared-auth-checks{display:grid;gap:12px;color:#e2e8f0;font-size:14px;margin:10px 0}
    .shared-auth-add{width:100%;height:34px;border-radius:12px;border:0;background:#ff9c1a;color:#1f2937;font-size:18px;font-weight:800;cursor:pointer;margin-top:8px}
    .shared-auth-side-title{font-size:20px;font-weight:800;color:#f3f4f6;margin-bottom:14px}
    .shared-auth-side-steps{margin:0;padding-left:28px;color:#e2e8f0;font-size:16px;line-height:1.75}
    .shared-auth-side-shot{margin-top:20px;height:320px;border-radius:16px;background:linear-gradient(135deg, rgba(255,255,255,.08), rgba(255,255,255,.02)), url('https://images.unsplash.com/photo-1520607162513-77705c0f0d4a?auto=format&fit=crop&w=900&q=80') center/cover no-repeat;border:1px solid rgba(255,255,255,.06)}
    .shared-global-controls{position:fixed;top:12px;right:16px;z-index:160;display:flex;align-items:center;gap:10px}
    .shared-global-btn{width:36px;height:36px;border-radius:999px;border:1px solid rgba(255,255,255,.12);background:rgba(19,27,39,.72);color:#eef2f7;display:inline-flex;align-items:center;justify-content:center;cursor:pointer;backdrop-filter:blur(12px);box-shadow:0 10px 24px rgba(15,23,42,.18)}
    .shared-global-btn:hover{filter:brightness(1.05)}
    .shared-global-select{height:36px;min-width:98px;padding:0 30px 0 12px;border-radius:999px;border:1px solid rgba(255,255,255,.12);background:linear-gradient(45deg, transparent 50%, #94a3b8 50%) calc(100% - 14px) calc(50% - 2px)/6px 6px no-repeat,linear-gradient(135deg, #94a3b8 50%, transparent 50%) calc(100% - 10px) calc(50% - 2px)/6px 6px no-repeat,rgba(19,27,39,.72);color:#eef2f7;font-size:12px;font-weight:700;appearance:none;outline:none;backdrop-filter:blur(12px)}
    .shared-global-select:focus{border-color:rgba(56,189,248,.38)}
    .shared-global-avatar{width:36px;height:36px;border-radius:999px;border:1px solid rgba(255,255,255,.12);background:linear-gradient(180deg, rgba(76,110,203,.95), rgba(59,130,246,.82));color:#fff;display:inline-flex;align-items:center;justify-content:center;font-size:16px;font-weight:800;cursor:pointer;box-shadow:0 8px 20px rgba(59,130,246,.22)}
    body.light-theme .shared-global-btn, body.light-theme .shared-global-select{background-color:rgba(255,255,255,.92);color:#111827;border-color:rgba(15,23,42,.10);box-shadow:0 8px 18px rgba(15,23,42,.08)}
    .shared-rail-logo{position:fixed;top:8px;left:15px;z-index:170;width:40px;height:40px;display:inline-flex;align-items:center;justify-content:center;filter:drop-shadow(0 6px 18px rgba(0,0,0,.28))}
    .shared-rail-logo svg{width:34px;height:34px;display:block}
    .nav-logo,.rail-logo{visibility:hidden !important}
    @media (max-width: 768px){.shared-global-controls{top:10px;right:12px;gap:8px}.shared-global-select{min-width:88px;font-size:11px}}
  `;
  document.head.appendChild(style);

  function updateThemeIcon(button) {
    if (!button) return;
    button.innerHTML = document.body.classList.contains("light-theme")
      ? '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="12" cy="12" r="5" stroke="currentColor" stroke-width="1.8"></circle><path d="M12 2v2.2M12 19.8V22M4.93 4.93l1.56 1.56M17.5 17.5l1.57 1.57M2 12h2.2M19.8 12H22M4.93 19.07l1.56-1.56M17.5 6.5l1.57-1.57" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"></path></svg>'
      : '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3c0 .34-.02.68-.02 1.03A7.98 7.98 0 0 0 19.97 13c.35 0 .69-.02 1.03-.21Z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  }

  function applyGlobalTheme(theme) {
    const next = theme === "light" ? "light" : "dark";
    document.body.classList.toggle("light-theme", next === "light");
    localStorage.setItem(UI_THEME_STORAGE_KEY, next);
    const btn = document.getElementById("sharedThemeToggle");
    updateThemeIcon(btn);
    document.dispatchEvent(new CustomEvent("zhidao-ui-change", { detail: { theme: next, language: localStorage.getItem(UI_LANG_STORAGE_KEY) || "zh" } }));
  }

  function applyGlobalLanguage(language) {
    const next = language === "en" ? "en" : "zh";
    localStorage.setItem(UI_LANG_STORAGE_KEY, next);
    const select = document.getElementById("sharedLanguageSelect");
    if (select) select.value = next;
    document.documentElement.lang = next === "en" ? "en" : "zh-CN";
    document.dispatchEvent(new CustomEvent("zhidao-ui-change", { detail: { theme: localStorage.getItem(UI_THEME_STORAGE_KEY) || "dark", language: next } }));
  }

  function ensureGlobalControls() {
    let controls = document.getElementById("sharedGlobalControls");
    if (controls) return controls;
    controls = document.createElement("div");
    controls.id = "sharedGlobalControls";
    controls.className = "shared-global-controls";
    controls.innerHTML = `
      <button id="sharedThemeToggle" class="shared-global-btn" type="button" aria-label="切换亮暗色"></button>
      <select id="sharedLanguageSelect" class="shared-global-select" aria-label="语言切换">
        <option value="zh">中文</option>
        <option value="en">English</option>
      </select>
      <button class="shared-global-avatar avatar-pill" type="button" data-login-avatar aria-label="登录与授权">d</button>
    `;
    document.body.appendChild(controls);
    const themeBtn = controls.querySelector("#sharedThemeToggle");
    const languageSelect = controls.querySelector("#sharedLanguageSelect");
    updateThemeIcon(themeBtn);
    themeBtn.addEventListener("click", () => {
      const current = document.body.classList.contains("light-theme") ? "light" : "dark";
      applyGlobalTheme(current === "light" ? "dark" : "light");
    });
    languageSelect.addEventListener("change", () => applyGlobalLanguage(languageSelect.value));
    return controls;
  }

  function ensureRailLogo() {
    let logo = document.getElementById("sharedRailLogo");
    if (logo) return logo;
    logo = document.createElement("a");
    logo.id = "sharedRailLogo";
    logo.className = "shared-rail-logo";
    logo.href = "index.html";
    logo.setAttribute("aria-label", "返回首页");
    logo.innerHTML = `
      <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <defs>
          <linearGradient id="sharedLogoLeft" x1="9" y1="44" x2="31" y2="17" gradientUnits="userSpaceOnUse">
            <stop stop-color="#2AA7FF"/>
            <stop offset="1" stop-color="#8A3FFC"/>
          </linearGradient>
          <linearGradient id="sharedLogoRight" x1="30" y1="43" x2="54" y2="18" gradientUnits="userSpaceOnUse">
            <stop stop-color="#FF5B7F"/>
            <stop offset="1" stop-color="#FF9F1C"/>
          </linearGradient>
        </defs>
        <path d="M11.5 42.5c-2.7-2.7-2.7-7.1 0-9.8l10.1-10.1c2.7-2.7 7.1-2.7 9.8 0l7.1 7.1-6.3 6.3-5.4-5.4a2.3 2.3 0 0 0-3.2 0l-5.7 5.7a2.3 2.3 0 0 0 0 3.2l5.4 5.4-6.3 6.3-7.5-7.5Z" fill="url(#sharedLogoLeft)"/>
        <path d="M52.5 42.5c2.7-2.7 2.7-7.1 0-9.8L42.4 22.6c-2.7-2.7-7.1-2.7-9.8 0l-7.1 7.1 6.3 6.3 5.4-5.4a2.3 2.3 0 0 1 3.2 0l5.7 5.7a2.3 2.3 0 0 1 0 3.2l-5.4 5.4 6.3 6.3 7.5-7.5Z" fill="url(#sharedLogoRight)"/>
        <rect x="45.5" y="9" width="9" height="9" rx="2.2" transform="rotate(45 45.5 9)" fill="#FF9F1C"/>
      </svg>
    `;
    document.body.appendChild(logo);
    return logo;
  }

  function normalizeLeftNavPlaceholders() {
    document.querySelectorAll(".nav-logo,.rail-logo,.global-nav > .nav-logo").forEach((el) => {
      if (el.id !== "sharedRailLogo") el.style.display = "none";
    });
    document.querySelectorAll("aside").forEach((aside) => {
      const first = aside.firstElementChild;
      if (!first) return;
      if (first.matches('.w-10.h-10.rounded-xl.bg-white\\/5.border.border-white\\/10')) {
        first.style.display = "none";
      }
    });
  }

  function readLoginState() {
    try {
      const raw = localStorage.getItem(LOGIN_STORAGE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (error) {
      return null;
    }
  }

  function writeLoginState(payload) {
    localStorage.setItem(LOGIN_STORAGE_KEY, JSON.stringify(payload));
  }

  function readAuthStore() {
    try {
      const raw = localStorage.getItem(AUTH_STORAGE_KEY);
      const parsed = raw ? JSON.parse(raw) : {};
      return Array.isArray(parsed.connections) ? parsed : { connections: [] };
    } catch (error) {
      return { connections: [] };
    }
  }

  function saveAuthConnection(exchange) {
    const meta = AUTH_META[exchange];
    if (!meta) return;
    const store = readAuthStore();
    const rest = store.connections.filter((item) => item.exchange !== exchange);
    rest.forEach((item) => { item.isDefault = false; });
    const entry = {
      exchange,
      title: meta.title,
      mode: "quick",
      remark: `${meta.title}授权`,
      envType: "live",
      status: "connected",
      isDefault: exchange === "binance",
      createdAt: Date.now()
    };
    localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify({ connections: [entry].concat(rest), updatedAt: Date.now() }));
  }

  function ensureModal() {
    let modal = document.getElementById("sharedLoginModal");
    if (modal) return modal;
    modal = document.createElement("div");
    modal.id = "sharedLoginModal";
    modal.className = "shared-login-modal";
    modal.setAttribute("aria-hidden", "true");
    modal.innerHTML = `
      <div class="shared-login-panel">
        <div class="shared-login-head">
          <div class="shared-login-title">登入</div>
          <button id="sharedLoginClose" class="shared-login-close" type="button" aria-label="关闭">×</button>
        </div>
        <label class="shared-login-label">邮箱</label>
        <div class="shared-login-field"><input id="sharedLoginEmail" type="email" placeholder="电子邮件地址"></div>
        <label class="shared-login-label">验证码</label>
        <div class="shared-login-code">
          <input type="text" placeholder="">
          <button class="shared-login-send" type="button">发送</button>
        </div>
        <button id="sharedLoginSubmit" class="shared-login-submit" type="button">登录</button>
        <div class="shared-login-or">或</div>
        <div class="shared-login-socials">
          <button class="shared-login-social" type="button"><span style="color:#fbbc05;">G</span><span>Google</span></button>
          <button class="shared-login-social" type="button"><span style="font-size:22px;"></span><span>Apple</span></button>
        </div>
      </div>`;
    document.body.appendChild(modal);
    return modal;
  }

  function ensureUserMenu() {
    let menu = document.getElementById("sharedUserMenu");
    if (menu) return menu;
    menu = document.createElement("div");
    menu.id = "sharedUserMenu";
    menu.className = "shared-user-menu";
    menu.innerHTML = `
      <div class="shared-user-head">
        <div id="sharedUserAvatar" class="shared-user-avatar">d</div>
        <div id="sharedUserName" class="shared-user-name">Djdjefelkdjj</div>
      </div>
      <div class="shared-user-body">
        <button id="sharedUserAccountBtn" class="shared-user-item" type="button"><span class="shared-user-icon">◔</span><span>账户</span></button>
      </div>
      <button id="sharedUserLogout" class="shared-user-logout" type="button"><span class="shared-user-icon" style="color:#ff647a;">↪</span><span>退出登录</span></button>
    `;
    document.body.appendChild(menu);
    return menu;
  }

  function ensureAccountModal() {
    let modal = document.getElementById("sharedAccountModal");
    if (modal) return modal;
    modal = document.createElement("div");
    modal.id = "sharedAccountModal";
    modal.className = "shared-account-modal";
    modal.setAttribute("aria-hidden", "true");
    modal.innerHTML = `
      <div class="shared-account-panel">
        <section class="shared-account-content">
          <div class="shared-account-head">
            <div class="shared-account-title">账户</div>
            <button id="sharedAccountClose" class="shared-account-close" type="button" aria-label="关闭">×</button>
          </div>
          <div class="shared-account-scroll">
            <div class="shared-profile-card">
              <div id="sharedAccountProfileAvatar" class="shared-profile-avatar">d</div>
              <div>
                <div id="sharedAccountProfileName" class="shared-profile-name">Djdjefelkdjj</div>
                <div class="shared-profile-meta">UID: 58623196</div>
              </div>
            </div>
            <div class="shared-section-title">已绑定交易所账号</div>
            <div class="shared-exchange-list">
              <div id="sharedHyperCard" class="shared-exchange-card">
                <div class="shared-exchange-top">
                  <div class="shared-exchange-left">
                    <div class="shared-exchange-logo" style="background:#073b35;color:#8af5de">~</div>
                    <div>
                      <div class="shared-exchange-name">Hyperliquid <span class="shared-exchange-tag">主账户</span></div>
                      <div class="shared-exchange-address">0×742d...3f9a</div>
                    </div>
                  </div>
                  <div class="shared-exchange-status">◔ 已授权</div>
                </div>
                <div class="shared-exchange-grid">
                  <div><div class="shared-kv-label">账户净值</div><div class="shared-kv-value">$53,473.82</div></div>
                  <div><div class="shared-kv-label">可用保证金</div><div class="shared-kv-value">$48,392.10</div></div>
                  <div><div class="shared-kv-label">未实现盈亏</div><div class="shared-kv-value green">+$2,847.35</div></div>
                  <div><div class="shared-kv-label">持仓数量</div><div class="shared-kv-value">334.33</div></div>
                </div>
                <div class="shared-exchange-actions">
                  <button id="sharedHyperDetailsBtn" class="shared-exchange-btn" type="button">查看详情</button>
                  <button id="sharedHyperUnbindBtn" class="shared-exchange-btn danger" type="button">解绑</button>
                </div>
              </div>
              <div class="shared-exchange-card">
                <div class="shared-exchange-row">
                  <div class="shared-exchange-left">
                    <div class="shared-exchange-logo">◈</div>
                    <div class="shared-exchange-name">币安</div>
                  </div>
                  <button class="shared-authorize-btn" type="button">＋ 授权</button>
                </div>
              </div>
              <div class="shared-exchange-card">
                <div class="shared-exchange-row">
                  <div class="shared-exchange-left">
                    <div class="shared-exchange-logo dark">✣</div>
                    <div class="shared-exchange-name">OKX</div>
                  </div>
                  <button class="shared-authorize-btn" type="button">＋ 授权</button>
                </div>
              </div>
            </div>
            <div class="shared-security-card">
              <div class="shared-security-title">◔ 安全提示</div>
              <div class="shared-security-text">您的 API 密钥经过高强度加密存储，知道Ai 仅用于读取账户信息和执行授权交易，不会进行任何未授权操作。</div>
            </div>
          </div>
        </section>
      </div>
    `;
    document.body.appendChild(modal);
    return modal;
  }

  function ensureAuthorizeModal() {
    let modal = document.getElementById("sharedAuthorizeModal");
    if (modal) return modal;
    modal = document.createElement("div");
    modal.id = "sharedAuthorizeModal";
    modal.className = "shared-auth-modal";
    modal.setAttribute("aria-hidden", "true");
    modal.innerHTML = `
      <div class="shared-auth-panel">
        <div class="shared-auth-top">
          <div class="shared-auth-exchanges">
            <button class="shared-auth-tab active" type="button" data-auth-exchange="binance">Binance</button>
            <button class="shared-auth-tab" type="button" data-auth-exchange="okx">OKX</button>
            <button class="shared-auth-tab" type="button" data-auth-exchange="hyper">Hyperliquid</button>
          </div>
          <button id="sharedAuthClose" class="shared-auth-close" type="button" aria-label="关闭">×</button>
        </div>
        <div class="shared-auth-modebar">
          <button class="shared-auth-mode active" type="button" data-auth-mode="quick">快速授权</button>
          <button class="shared-auth-mode" type="button" data-auth-mode="api">API 授权</button>
        </div>
        <div class="shared-auth-body">
          <section class="shared-auth-left">
            <div id="sharedQuickView">
              <div class="shared-auth-quick-center">
                <div id="sharedAuthNotice" class="shared-auth-notice"></div>
                <div class="shared-auth-card">
                  <div class="shared-auth-brand">
                    <div class="shared-auth-brand-logo">⟲</div>
                    <div class="shared-auth-brand-link"><span>•</span><span>⛓</span><span>•</span></div>
                    <div id="sharedAuthTargetLogo" class="shared-auth-brand-logo">◈</div>
                  </div>
                  <div class="shared-auth-card-title">官方直接授权地址 查询账号信息</div>
                </div>
                <div class="shared-auth-card">
                  <div style="font-size:18px;color:#f3f4f6;margin-bottom:12px;">完成首次授权流程：</div>
                  <ol id="sharedAuthQuickSteps" class="shared-auth-steps"></ol>
                </div>
                <div class="shared-auth-options">
                  <label><input type="checkbox" checked> 开启资产统计</label>
                  <label><input type="checkbox"> 设为默认账户</label>
                </div>
                <button id="sharedAuthQuickBtn" class="shared-auth-primary" type="button">前往在线即时授权币安账户</button>
                <div class="shared-auth-footwarn">API密钥经过多重加密且仅保存在您的浏览器中，不会存储在服务器。请放心使用。 查看授权说明</div>
              </div>
            </div>
            <div id="sharedApiView" hidden>
              <div class="shared-auth-body" style="display:grid;grid-template-columns:minmax(0,1fr) 420px;min-height:auto">
                <section style="padding-right:18px;border-right:1px solid rgba(255,255,255,.08)">
                  <div class="shared-auth-notice" style="background:#4a4034;color:#ff9c1a;">为了保障交易安全，请务必在授权前：请导致你要进行。</div>
                  <div class="shared-auth-form">
                    <div>
                      <div id="sharedRemarkLabel" class="shared-auth-label">账户备注名(选填)</div>
                      <input id="sharedAuthRemark" class="shared-auth-input" placeholder="可不填，输入以便管理">
                    </div>
                    <div>
                      <div id="sharedKeyLabel" class="shared-auth-label">API Key+ *</div>
                      <input id="sharedAuthKey" class="shared-auth-input" placeholder="">
                    </div>
                    <a href="#" style="color:#5d8eff;font-size:14px;">查看说明</a>
                    <div>
                      <div id="sharedSecretLabel" class="shared-auth-label">密钥 *</div>
                      <input id="sharedAuthSecret" class="shared-auth-input" placeholder="">
                    </div>
                    <div id="sharedPassWrap">
                      <div id="sharedPassLabel" class="shared-auth-label">密码(Passphrase) *</div>
                      <input id="sharedAuthPass" class="shared-auth-input" placeholder="">
                    </div>
                    <div class="shared-auth-checks">
                      <label><input type="checkbox"> 开启资产统计</label>
                      <label><input type="checkbox"> 设为默认账户</label>
                    </div>
                    <button id="sharedAuthAddBtn" class="shared-auth-add" type="button">添加</button>
                  </div>
                </section>
                <aside style="padding-left:18px">
                  <div id="sharedTutorialTitle" class="shared-auth-side-title">授权教程</div>
                  <ol id="sharedTutorialSteps" class="shared-auth-side-steps"></ol>
                  <div class="shared-auth-side-shot"></div>
                </aside>
              </div>
            </div>
          </section>
          <aside class="shared-auth-right">
            <div id="sharedAuthTutorialTitle" class="shared-auth-side-title">授权教程</div>
            <ol id="sharedAuthTutorialSteps" class="shared-auth-side-steps"></ol>
            <div class="shared-auth-side-shot"></div>
          </aside>
        </div>
      </div>`;
    document.body.appendChild(modal);
    return modal;
  }

  function ensureConfirmModal() {
    let modal = document.getElementById("sharedConfirmModal");
    if (modal) return modal;
    modal = document.createElement("div");
    modal.id = "sharedConfirmModal";
    modal.className = "shared-confirm-modal";
    modal.innerHTML = `
      <div class="shared-confirm-panel">
        <div class="shared-confirm-title">确认解绑</div>
        <div class="shared-confirm-text">解绑后，该交易所将从已绑定列表中移除，你可以稍后重新授权。</div>
        <div class="shared-confirm-actions">
          <button id="sharedConfirmCancel" class="shared-confirm-btn" type="button">取消</button>
          <button id="sharedConfirmOk" class="shared-confirm-btn danger" type="button">确认解绑</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
    return modal;
  }

  function openSharedAccountModal() {
    const modal = ensureAccountModal();
    modal.classList.add("open");
    modal.setAttribute("aria-hidden", "false");
  }

  function closeSharedAccountModal() {
    const modal = ensureAccountModal();
    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
  }

  function registerGlobalUIActions() {
    if (!window.ZhidaoUI) window.ZhidaoUI = {};
    window.ZhidaoUI.openAccountModal = openSharedAccountModal;
    window.ZhidaoUI.closeAccountModal = closeSharedAccountModal;
  }

  function bindLogin(avatarBtn) {
    const modal = ensureModal();
    const menu = ensureUserMenu();
    const accountModal = ensureAccountModal();
    const authModal = ensureAuthorizeModal();
    const confirmModal = ensureConfirmModal();
    const closeBtn = modal.querySelector("#sharedLoginClose");
    const submitBtn = modal.querySelector("#sharedLoginSubmit");
    const emailInput = modal.querySelector("#sharedLoginEmail");
    const logoutBtn = menu.querySelector("#sharedUserLogout");
    const accountBtn = menu.querySelector("#sharedUserAccountBtn");
    const userAvatar = menu.querySelector("#sharedUserAvatar");
    const userName = menu.querySelector("#sharedUserName");
    const accountCloseBtn = accountModal.querySelector("#sharedAccountClose");
    const accountProfileAvatar = accountModal.querySelector("#sharedAccountProfileAvatar");
    const accountProfileName = accountModal.querySelector("#sharedAccountProfileName");
    const hyperCard = accountModal.querySelector("#sharedHyperCard");
    const hyperDetailsBtn = accountModal.querySelector("#sharedHyperDetailsBtn");
    const hyperUnbindBtn = accountModal.querySelector("#sharedHyperUnbindBtn");
    const authCloseBtn = authModal.querySelector("#sharedAuthClose");
    const authTabs = Array.from(authModal.querySelectorAll("[data-auth-exchange]"));
    const authModes = Array.from(authModal.querySelectorAll("[data-auth-mode]"));
    const authBody = authModal.querySelector(".shared-auth-body");
    const quickView = authModal.querySelector("#sharedQuickView");
    const apiView = authModal.querySelector("#sharedApiView");
    const authRight = authModal.querySelector(".shared-auth-right");
    const authNotice = authModal.querySelector("#sharedAuthNotice");
    const authTargetLogo = authModal.querySelector("#sharedAuthTargetLogo");
    const quickSteps = authModal.querySelector("#sharedAuthQuickSteps");
    const quickBtn = authModal.querySelector("#sharedAuthQuickBtn");
    const authTutorialTitle = authModal.querySelector("#sharedAuthTutorialTitle");
    const authTutorialSteps = authModal.querySelector("#sharedAuthTutorialSteps");
    const tutorialTitle = authModal.querySelector("#sharedTutorialTitle");
    const tutorialSteps = authModal.querySelector("#sharedTutorialSteps");
    const keyLabel = authModal.querySelector("#sharedKeyLabel");
    const secretLabel = authModal.querySelector("#sharedSecretLabel");
    const passLabel = authModal.querySelector("#sharedPassLabel");
    const passWrap = authModal.querySelector("#sharedPassWrap");
    const remarkLabel = authModal.querySelector("#sharedRemarkLabel");
    const keyInput = authModal.querySelector("#sharedAuthKey");
    const secretInput = authModal.querySelector("#sharedAuthSecret");
    const passInput = authModal.querySelector("#sharedAuthPass");
    const authRemarkInput = authModal.querySelector("#sharedAuthRemark");
    const authAddBtn = authModal.querySelector("#sharedAuthAddBtn");
    const confirmCancelBtn = confirmModal.querySelector("#sharedConfirmCancel");
    const confirmOkBtn = confirmModal.querySelector("#sharedConfirmOk");
    let activeAuthExchange = "binance";
    const quickModeBtn = authModal.querySelector('[data-auth-mode="quick"]');
    const apiModeBtn = authModal.querySelector('[data-auth-mode="api"]');

    const syncAvatar = () => {
      const state = readLoginState();
      avatarBtn.textContent = state?.name || "d";
      userAvatar.textContent = state?.name || "d";
      userName.textContent = state?.email ? state.email.split("@")[0] : "Djdjefelkdjj";
       accountProfileAvatar.textContent = state?.name || "d";
       accountProfileName.textContent = state?.email ? state.email.split("@")[0] : "Djdjefelkdjj";
    };

    const openModal = () => {
      modal.classList.add("open");
      modal.setAttribute("aria-hidden", "false");
    };

    const closeModal = () => {
      modal.classList.remove("open");
      modal.setAttribute("aria-hidden", "true");
    };

    const closeMenu = () => {
      menu.classList.remove("open");
    };

    const openAccountModal = () => {
      accountModal.classList.add("open");
      accountModal.setAttribute("aria-hidden", "false");
    };

    const closeAccountModal = () => {
      accountModal.classList.remove("open");
      accountModal.setAttribute("aria-hidden", "true");
    };

    const openAuthModal = (exchange) => {
      activeAuthExchange = exchange || "binance";
      setAuthExchange(activeAuthExchange);
      const meta = AUTH_META[activeAuthExchange] || AUTH_META.binance;
      setAuthMode(meta.quickDisabled ? "api" : "quick");
      authModal.classList.add("open");
      authModal.setAttribute("aria-hidden", "false");
    };

    const closeAuthModal = () => {
      authModal.classList.remove("open");
      authModal.setAttribute("aria-hidden", "true");
    };

    const openConfirmModal = () => {
      confirmModal.classList.add("open");
    };

    const closeConfirmModal = () => {
      confirmModal.classList.remove("open");
    };

    const setAuthMode = (mode) => {
      authModes.forEach((btn) => {
        if (btn.hidden) {
          btn.classList.remove("active");
          return;
        }
        btn.classList.toggle("active", btn.dataset.authMode === mode);
      });
      quickView.hidden = mode !== "quick";
      apiView.hidden = mode !== "api";
      authRight.hidden = mode !== "api";
      authBody.classList.toggle("api-only", mode === "api");
      authBody.classList.toggle("quick-only", mode === "quick");
    };

    const setAuthExchange = (exchange) => {
      activeAuthExchange = exchange;
      const meta = AUTH_META[exchange] || AUTH_META.binance;
      authModal.dataset.exchange = exchange;
      authTabs.forEach((btn) => btn.classList.toggle("active", btn.dataset.authExchange === exchange));
      authNotice.innerHTML = `◔ ${meta.quickTitle}`;
      authTargetLogo.textContent = exchange === "binance" ? "◈" : exchange === "okx" ? "✣" : "◉";
      quickSteps.innerHTML = meta.quickSteps.map((step) => `<li>${step}</li>`).join("");
      quickBtn.textContent = meta.quickButton;
      authTutorialTitle.textContent = meta.tutorialTitle;
      authTutorialSteps.innerHTML = meta.tutorialSteps.map((step) => `<li>${step}</li>`).join("");
      tutorialTitle.textContent = meta.tutorialTitle;
      tutorialSteps.innerHTML = meta.tutorialSteps.map((step) => `<li>${step}</li>`).join("");
      remarkLabel.textContent = meta.remarkLabel || "账户备注名(选填)";
      authRemarkInput.placeholder = meta.remarkPlaceholder || "可不填，输入以便管理";
      keyLabel.textContent = `${meta.keyLabel} *`;
      secretLabel.textContent = `${meta.secretLabel} *`;
      passLabel.textContent = meta.passLabel ? `${meta.passLabel} *` : "";
      keyInput.placeholder = meta.keyPlaceholder;
      secretInput.placeholder = meta.secretPlaceholder;
      passInput.placeholder = meta.passPlaceholder;
      if (passWrap) passWrap.hidden = !!meta.hidePass;
      authAddBtn.textContent = "添加";
      authAddBtn.disabled = false;
      authAddBtn.style.opacity = "1";
      authModes.forEach((btn) => {
        btn.hidden = false;
        btn.classList.remove("active");
      });
      if (meta.quickDisabled) {
        if (quickModeBtn) quickModeBtn.hidden = true;
        setAuthMode("api");
        return;
      }
      if (quickModeBtn) quickModeBtn.hidden = false;
      if (apiModeBtn) apiModeBtn.hidden = false;
      setAuthMode("quick");
    };

    const openMenu = () => {
      const rect = avatarBtn.getBoundingClientRect();
      menu.style.top = `${rect.bottom + 10}px`;
      menu.style.left = `${Math.max(16, rect.right - 320)}px`;
      menu.classList.add("open");
    };

    if (!avatarBtn.dataset.loginBound) {
      avatarBtn.dataset.loginBound = "1";
      avatarBtn.addEventListener("click", (event) => {
        event.stopPropagation();
        if (!readLoginState()) {
          openModal();
        } else {
          const isOpen = menu.classList.contains("open");
          closeMenu();
          if (!isOpen) openMenu();
        }
      });
    }

    if (!modal.dataset.bound) {
      modal.dataset.bound = "1";
      closeBtn.addEventListener("click", closeModal);
      modal.addEventListener("click", (event) => {
        if (event.target === modal) closeModal();
      });
      submitBtn.addEventListener("click", () => {
        const email = emailInput.value.trim();
        const name = email ? email[0].toLowerCase() : "d";
        writeLoginState({ name, email, loggedInAt: Date.now() });
        document.querySelectorAll(".shared-topbar-avatar,[data-login-avatar]").forEach((el) => {
          el.textContent = name;
        });
        syncAvatar();
        closeModal();
      });
      document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && modal.classList.contains("open")) closeModal();
        if (event.key === "Escape" && menu.classList.contains("open")) closeMenu();
        if (event.key === "Escape" && authModal.classList.contains("open")) closeAuthModal();
        if (event.key === "Escape" && confirmModal.classList.contains("open")) closeConfirmModal();
      });
      document.addEventListener("click", (event) => {
        if (!menu.contains(event.target) && !event.target.closest(".shared-topbar-avatar,[data-login-avatar],.avatar-pill,.avatar-btn")) {
          closeMenu();
        }
        if (event.target === accountModal) closeAccountModal();
        if (event.target === authModal) closeAuthModal();
        if (event.target === confirmModal) closeConfirmModal();
      });
      accountBtn.addEventListener("click", () => {
        closeMenu();
        openAccountModal();
      });
      accountCloseBtn.addEventListener("click", closeAccountModal);
      confirmCancelBtn.addEventListener("click", closeConfirmModal);
      authCloseBtn.addEventListener("click", closeAuthModal);
      authTabs.forEach((btn) => btn.addEventListener("click", () => setAuthExchange(btn.dataset.authExchange)));
      authModes.forEach((btn) => btn.addEventListener("click", () => setAuthMode(btn.dataset.authMode)));
      accountModal.querySelectorAll(".shared-authorize-btn").forEach((btn, index) => {
        const exchange = index === 0 ? "binance" : "okx";
        btn.addEventListener("click", () => {
          closeAccountModal();
          openAuthModal(exchange);
        });
      });
      hyperDetailsBtn.addEventListener("click", () => {
        closeAccountModal();
        openAuthModal("hyper");
      });
      hyperUnbindBtn.addEventListener("click", openConfirmModal);
      confirmOkBtn.addEventListener("click", () => {
        closeConfirmModal();
        hyperCard.innerHTML = `
          <div class="shared-exchange-row">
            <div class="shared-exchange-left">
              <div class="shared-exchange-logo" style="background:#073b35;color:#8af5de">~</div>
              <div class="shared-exchange-name">Hyperliquid</div>
            </div>
            <button class="shared-authorize-btn" type="button">＋ 授权</button>
          </div>
        `;
        const btn = hyperCard.querySelector(".shared-authorize-btn");
        btn.addEventListener("click", () => {
          closeAccountModal();
          openAuthModal("hyper");
        });
      });
      quickBtn.addEventListener("click", () => {
        saveAuthConnection(activeAuthExchange);
        closeAuthModal();
      });
      authAddBtn.addEventListener("click", () => {
        saveAuthConnection(activeAuthExchange);
        closeAuthModal();
      });
      logoutBtn.addEventListener("click", () => {
        localStorage.removeItem(LOGIN_STORAGE_KEY);
        localStorage.removeItem(AUTH_STORAGE_KEY);
        document.querySelectorAll(".shared-topbar-avatar,[data-login-avatar],.avatar-pill,.avatar-btn").forEach((el) => {
          el.textContent = "d";
        });
        syncAvatar();
        closeMenu();
        closeAccountModal();
        closeAuthModal();
      });
    }

    syncAvatar();
  }

  function bindExistingAvatars() {
    document.querySelectorAll("#chatAvatarBtn,#threadAvatarBtn,.avatar-pill,.avatar-btn,[data-login-avatar]").forEach((avatar) => {
      bindLogin(avatar);
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    ensureRailLogo();
    normalizeLeftNavPlaceholders();
    ensureGlobalControls();
    registerGlobalUIActions();
    applyGlobalTheme(localStorage.getItem(UI_THEME_STORAGE_KEY) || "dark");
    applyGlobalLanguage(localStorage.getItem(UI_LANG_STORAGE_KEY) || "zh");
    bindExistingAvatars();
  });

  document.addEventListener("zhidao-open-account-modal", () => {
    openSharedAccountModal();
  });
})();
