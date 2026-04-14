(function () {
  const AUTH_STORAGE_KEY = "zhidao_authorizations_v1";
  const quickModal = document.getElementById("authEmbedModal");
  const quickFrame = document.getElementById("authEmbedFrame");
  const quickTitle = document.getElementById("authEmbedTitle");
  const quickOpenNew = document.getElementById("authEmbedOpenNew");
  const quickClose = document.getElementById("authEmbedClose");
  const apiModal = document.getElementById("apiAuthModal");
  const apiClose = document.getElementById("apiAuthClose");
  const apiTabs = Array.from(document.querySelectorAll("[data-api-tab]"));
  const apiModeTabs = Array.from(document.querySelectorAll("[data-api-mode]"));
  const apiContent = document.querySelector(".api-content");
  const apiTutorialList = document.getElementById("apiTutorialList");
  const apiTutorialBtn = document.getElementById("apiTutorialBtn");
  const apiGlobalNotice = document.getElementById("apiGlobalNotice");
  const apiLeftTitle = document.getElementById("apiLeftTitle");
  const apiKeyLabel = document.getElementById("apiKeyLabel");
  const apiSecretLabel = document.getElementById("apiSecretLabel");
  const apiPassphraseLabel = document.getElementById("apiPassphraseLabel");
  const apiBindAccountOption = document.getElementById("apiBindAccountOption");
  const apiAuthKeyInput = document.getElementById("apiAuthKeyInput");
  const apiAuthSecretInput = document.getElementById("apiAuthSecretInput");
  const apiAuthPassphraseInput = document.getElementById("apiAuthPassphraseInput");
  const apiRemarkInput = document.getElementById("apiRemarkInput");
  const apiEnableStatsInput = document.getElementById("apiEnableStatsInput");
  const apiDefaultInput = document.getElementById("apiDefaultInput");
  const apiBindAccountInput = document.getElementById("apiBindAccountInput");
  const apiAddBtn = document.getElementById("apiAddBtn");
  const apiSignupLink = document.getElementById("apiSignupLink");
  const quickExchangeName = document.getElementById("quickExchangeName");
  const quickAuthGoBtn = document.getElementById("quickAuthGoBtn");
  const quickEnableStatsInput = document.getElementById("quickEnableStatsInput");
  const quickDefaultInput = document.getElementById("quickDefaultInput");
  const quickTargetLogo = document.getElementById("quickTargetLogo");
  const quickStepList = document.getElementById("quickStepList");
  const quickBanner = document.querySelector(".quick-banner");
  const quickBannerClose = document.querySelector(".quick-banner-close");
  const remarkSuffix = document.querySelector(".api-input-suffix");
  let activeApiTab = "okx";

  const META = {
    okx: {
      title: "欧易OKX",
      keyLabel: "API Key",
      secretLabel: "密钥",
      passphraseLabel: "密码<br>(Passphrase)",
      keyPlaceholder: "前往欧易OKX创建API，获取后填写",
      secretPlaceholder: "前往欧易OKX创建API，获取后填写",
      passPlaceholder: "创建API时设置，获取后填写",
      tutorialBtn: "欧易OKX授权教程",
      tutorialSteps: [
        "访问 OKX 官网并完成登录。",
        "进入 API 管理并创建 API。",
        "勾选交易权限，不要开启提币权限。",
        "复制 API Key、Secret 和 Passphrase 到左侧表单。"
      ],
      signupText: "欧易OKX 注册",
      signupHref: "https://www.okx.com/",
      quickSteps: [
        "点击下面按钮，前往欧易官网。",
        "登录你的欧易账户。",
        "同意快捷 API 授权。"
      ],
      quickUrl:
        "https://www.okx.com/zh-hans/account/authlogin?access_type=offline&client_id=3fe1ee51d88a4c1cab8694faf7752e95Q2XtBWdH&redirect_uri=https%3A%2F%2Fwww.aicoin.com%2Flink%2Fmain%2Foauth%2Fokex&response_type=code&scope=fast_api",
      quickLogoHtml: "✣",
      quickLogoClass: "",
      showPassphrase: true,
      showBindAccount: true,
      hideModeSwitch: false,
      envType: "simulated"
    },
    binance: {
      title: "币安",
      keyLabel: "API密钥",
      secretLabel: "密钥",
      passphraseLabel: "",
      keyPlaceholder: "前往币安创建API，获取后填写",
      secretPlaceholder: "前往币安创建API，获取后填写",
      passPlaceholder: "",
      tutorialBtn: "币安授权教程",
      tutorialSteps: [
        "访问币安官网并完成登录。",
        "进入 API 管理并创建 API。",
        "勾选交易权限，不要开启提币权限。",
        "复制 API Key 和 Secret 到左侧表单。"
      ],
      signupText: "币安注册",
      signupHref: "https://www.binance.com/",
      quickSteps: [
        "点击下面按钮，前往币安官网。",
        "登录你的币安账户。",
        "同意快捷 API 授权。"
      ],
      quickUrl: "https://accounts.binance.com/zh-CN/login",
      quickLogoHtml: "◆",
      quickLogoClass: "binance",
      showPassphrase: false,
      showBindAccount: false,
      hideModeSwitch: false,
      envType: "live"
    },
    hyper: {
      title: "Hyperliquid",
      keyLabel: "主钱包地址",
      secretLabel: "API钱包地址",
      passphraseLabel: "API钱包私钥",
      keyPlaceholder: "填写主钱包地址",
      secretPlaceholder: "填写 API 钱包地址",
      passPlaceholder: "填写 API 钱包私钥",
      tutorialBtn: "Hyperliquid授权教程",
      tutorialSteps: [
        "访问 Hyperliquid 官网并完成登录。",
        "在 API 页面生成 API 钱包地址和私钥。",
        "复制主钱包地址、API 钱包地址和私钥到左侧表单。",
        "首次可能需要钱包签名完成授权。"
      ],
      signupText: "Hyperliquid注册",
      signupHref: "https://hyperliquid.xyz/",
      quickSteps: ["Hyperliquid 当前仅支持 API 表单授权。"],
      quickUrl: "",
      quickLogoHtml: "◉",
      quickLogoClass: "",
      showPassphrase: true,
      showBindAccount: false,
      hideModeSwitch: true,
      globalNotice: "Hyperliquid 为链上 DEX，授权流程与中心化交易所不同。",
      leftTitle: "添加API账户",
      envType: "live"
    }
  };

  function readStore() {
    try {
      const raw = localStorage.getItem(AUTH_STORAGE_KEY);
      const parsed = raw ? JSON.parse(raw) : {};
      return Array.isArray(parsed.connections) ? parsed : { connections: [] };
    } catch (err) {
      return { connections: [] };
    }
  }

  function writeStore(data) {
    localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(data));
  }

  function saveConnection(entry) {
    const store = readStore();
    const rest = store.connections.filter((item) => item.exchange !== entry.exchange);
    if (entry.isDefault) {
      rest.forEach((item) => {
        item.isDefault = false;
      });
    }
    writeStore({ connections: [entry].concat(rest), updatedAt: Date.now() });
  }

  function updateRemarkCounter() {
    if (remarkSuffix && apiRemarkInput) {
      remarkSuffix.textContent = String((apiRemarkInput.value || "").length) + "/15";
    }
  }

  function buildQuickDoc(exchange) {
    return [
      "<!doctype html>",
      "<html lang='zh-CN'><head><meta charset='UTF-8'><style>",
      "body{margin:0;background:#f8fafc;color:#0f172a;font-family:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;display:grid;place-items:center;height:100vh;padding:24px;box-sizing:border-box}",
      ".card{max-width:520px;border:1px solid #e2e8f0;border-radius:18px;background:#fff;padding:28px;box-shadow:0 20px 40px rgba(15,23,42,.08)}",
      "h1{margin:0 0 12px;font-size:28px}p{margin:0 0 12px;line-height:1.7;color:#475569}",
      ".tag{display:inline-flex;height:28px;align-items:center;padding:0 12px;border-radius:999px;background:#e0f2fe;color:#0369a1;font-size:12px;font-weight:700;margin-bottom:14px}",
      "</style></head><body><div class='card'><div class='tag'>虚拟模式</div>",
      "<h1>" + exchange + " 已进入演示授权流程</h1>",
      "<p>当前项目已切换为纯虚拟数据模式，不会向真实交易所发起授权请求。</p>",
      "<p>本次操作只会在本地保存一条模拟授权记录，用于账户页展示连接状态、模拟资产和模拟持仓。</p>",
      "<p>关闭弹窗后可前往账户页查看结果。</p>",
      "</div></body></html>"
    ].join("");
  }

  function openQuickModal(exchange, url) {
    if (!quickModal || !quickFrame || !quickTitle || !quickOpenNew) return;
    quickTitle.textContent = exchange + " · 虚拟快捷授权";
    quickOpenNew.href = url || "#";
    quickFrame.srcdoc = buildQuickDoc(exchange);
    quickModal.classList.add("show");
    quickModal.setAttribute("aria-hidden", "false");
  }

  function closeQuickModal() {
    if (!quickModal || !quickFrame) return;
    quickModal.classList.remove("show");
    quickModal.setAttribute("aria-hidden", "true");
    quickFrame.src = "about:blank";
    quickFrame.srcdoc = "";
  }

  function openApiModal() {
    if (!apiModal) return;
    apiModal.classList.add("show");
    apiModal.setAttribute("aria-hidden", "false");
  }

  function closeApiModal() {
    if (!apiModal) return;
    apiModal.classList.remove("show");
    apiModal.setAttribute("aria-hidden", "true");
  }

  function setApiMode(mode) {
    const meta = META[activeApiTab] || META.okx;
    apiModeTabs.forEach((tab) => {
      const isApi = tab.getAttribute("data-api-mode") === "api";
      tab.classList.toggle(
        "active",
        meta.hideModeSwitch ? isApi : tab.getAttribute("data-api-mode") === mode
      );
    });
    if (!apiContent) return;
    apiContent.classList.toggle("quick-mode", !meta.hideModeSwitch && mode === "quick");
    apiContent.classList.toggle("hyper-mode", !!meta.hideModeSwitch);
    if (quickBanner) quickBanner.style.display = meta.hideModeSwitch ? "none" : "flex";
  }

  function setApiTab(tabName) {
    const meta = META[tabName] || META.okx;
    activeApiTab = tabName;
    apiTabs.forEach((tab) => {
      tab.classList.toggle("active", tab.getAttribute("data-api-tab") === tabName);
    });
    if (apiTutorialBtn) apiTutorialBtn.textContent = meta.tutorialBtn;
    if (apiTutorialList) {
      apiTutorialList.innerHTML = meta.tutorialSteps.map((item) => "<li>" + item + "</li>").join("");
    }
    if (apiGlobalNotice) {
      apiGlobalNotice.textContent = meta.globalNotice || "";
      apiGlobalNotice.classList.toggle("show", !!meta.globalNotice);
    }
    if (apiLeftTitle) apiLeftTitle.textContent = meta.leftTitle || "";
    if (apiKeyLabel) apiKeyLabel.innerHTML = meta.keyLabel + ' <span class="req">*</span>';
    if (apiSecretLabel) apiSecretLabel.innerHTML = meta.secretLabel + ' <span class="req">*</span>';
    if (apiPassphraseLabel && apiAuthPassphraseInput) {
      apiPassphraseLabel.style.display = meta.showPassphrase ? "" : "none";
      apiAuthPassphraseInput.style.display = meta.showPassphrase ? "" : "none";
      apiPassphraseLabel.innerHTML = meta.passphraseLabel
        ? meta.passphraseLabel + ' <span class="req">*</span>'
        : "";
    }
    if (apiBindAccountOption) apiBindAccountOption.style.display = meta.showBindAccount ? "" : "none";
    if (apiAuthKeyInput) apiAuthKeyInput.placeholder = meta.keyPlaceholder;
    if (apiAuthSecretInput) apiAuthSecretInput.placeholder = meta.secretPlaceholder;
    if (apiAuthPassphraseInput) apiAuthPassphraseInput.placeholder = meta.passPlaceholder;
    if (apiSignupLink) {
      apiSignupLink.textContent = meta.signupText;
      apiSignupLink.href = meta.signupHref;
    }
    if (quickExchangeName) quickExchangeName.textContent = meta.title;
    if (quickAuthGoBtn) {
      quickAuthGoBtn.textContent = "前往连接我的" + meta.title + "账户";
      quickAuthGoBtn.disabled = !meta.quickUrl;
      quickAuthGoBtn.style.opacity = meta.quickUrl ? "1" : "0.5";
      quickAuthGoBtn.style.cursor = meta.quickUrl ? "pointer" : "not-allowed";
    }
    if (quickStepList) {
      quickStepList.innerHTML = meta.quickSteps.map((item) => "<li>" + item + "</li>").join("");
    }
    if (quickTargetLogo) {
      quickTargetLogo.className = "quick-brand-logo";
      if (meta.quickLogoClass) quickTargetLogo.classList.add(meta.quickLogoClass);
      quickTargetLogo.innerHTML = meta.quickLogoHtml;
    }
    if (apiRemarkInput) apiRemarkInput.value = "";
    if (apiAuthKeyInput) apiAuthKeyInput.value = "";
    if (apiAuthSecretInput) apiAuthSecretInput.value = "";
    if (apiAuthPassphraseInput) apiAuthPassphraseInput.value = "";
    if (apiDefaultInput) apiDefaultInput.checked = false;
    if (apiBindAccountInput) apiBindAccountInput.checked = false;
    updateRemarkCounter();
    setApiMode("api");
  }

  function validateAndSaveApi() {
    const meta = META[activeApiTab] || META.okx;
    const key = apiAuthKeyInput ? apiAuthKeyInput.value.trim() : "";
    const secret = apiAuthSecretInput ? apiAuthSecretInput.value.trim() : "";
    const passphrase = apiAuthPassphraseInput ? apiAuthPassphraseInput.value.trim() : "";
    if (!key) return window.alert(meta.keyLabel + "不能为空");
    if (!secret) return window.alert(meta.secretLabel + "不能为空");
    if (meta.showPassphrase && !passphrase) {
      return window.alert((meta.passphraseLabel || "Passphrase") + "不能为空");
    }
    saveConnection({
      exchange: activeApiTab,
      title: meta.title,
      mode: "api",
      remark: (apiRemarkInput && apiRemarkInput.value.trim()) || (meta.title + "账户"),
      keyMasked: key.slice(0, 4) + "****",
      secretMasked: secret.slice(0, 3) + "***",
      hasPassphrase: !!passphrase,
      enableStats: !!(apiEnableStatsInput && apiEnableStatsInput.checked),
      isDefault: !!(apiDefaultInput && apiDefaultInput.checked),
      bindAccount: !!(apiBindAccountInput && apiBindAccountInput.checked),
      envType: meta.envType,
      status: "manual_connected",
      createdAt: Date.now()
    });
    closeApiModal();
    window.alert(meta.title + " 授权信息已保存。");
    window.location.href = "account.html";
  }

  function saveQuickAuth() {
    const meta = META[activeApiTab] || META.okx;
    saveConnection({
      exchange: activeApiTab,
      title: meta.title,
      mode: "quick",
      remark: meta.title + "快捷授权",
      keyMasked: "",
      secretMasked: "",
      hasPassphrase: false,
      enableStats: !!(quickEnableStatsInput && quickEnableStatsInput.checked),
      isDefault: !!(quickDefaultInput && quickDefaultInput.checked),
      bindAccount: false,
      envType: meta.envType,
      status: "quick_connected",
      createdAt: Date.now()
    });
  }

  document.querySelectorAll("[data-quick-auth]").forEach((button) => {
    button.addEventListener("click", function () {
      openQuickModal(button.getAttribute("data-exchange") || "交易所", button.getAttribute("data-url") || "#");
    });
  });

  document.querySelectorAll("[data-api-auth]").forEach((button) => {
    button.addEventListener("click", function () {
      openApiModal();
      setApiTab(button.getAttribute("data-api-open-tab") || "okx");
    });
  });

  apiTabs.forEach((tab) => {
    tab.addEventListener("click", function () {
      setApiTab(tab.getAttribute("data-api-tab") || "okx");
    });
  });

  apiModeTabs.forEach((tab) => {
    tab.addEventListener("click", function () {
      setApiMode(tab.getAttribute("data-api-mode") || "api");
    });
  });

  if (quickAuthGoBtn) {
    quickAuthGoBtn.addEventListener("click", function () {
      const meta = META[activeApiTab] || META.okx;
      if (!meta.quickUrl) return;
      saveQuickAuth();
      openQuickModal(meta.title, meta.quickUrl);
    });
  }

  if (apiAddBtn) apiAddBtn.addEventListener("click", validateAndSaveApi);
  if (apiRemarkInput) apiRemarkInput.addEventListener("input", updateRemarkCounter);

  if (quickBannerClose && quickBanner) {
    quickBannerClose.addEventListener("click", function () {
      quickBanner.style.display = "none";
    });
  }

  if (quickClose) quickClose.addEventListener("click", closeQuickModal);
  if (apiClose) apiClose.addEventListener("click", closeApiModal);

  if (quickModal) {
    quickModal.addEventListener("click", function (event) {
      if (event.target === quickModal) closeQuickModal();
    });
  }

  if (apiModal) {
    apiModal.addEventListener("click", function (event) {
      if (event.target === apiModal) closeApiModal();
    });
  }

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      closeQuickModal();
      closeApiModal();
    }
  });

  setApiTab("okx");
  updateRemarkCounter();
})();
