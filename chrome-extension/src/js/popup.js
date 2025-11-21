/**
 * Popup Script
 * 控制彈窗的邏輯
 */

document.addEventListener("DOMContentLoaded", () => {
  const activateBtn = document.getElementById("activateBtn");
  const settingsBtn = document.getElementById("settingsBtn");
  const settingsPanel = document.getElementById("settingsPanel");
  const saveSettingsBtn = document.getElementById("saveSettingsBtn");
  const apiUrlInput = document.getElementById("apiUrl");
  const modelTypeSelect = document.getElementById("modelType");

  // 啟動助手按鈕
  activateBtn.addEventListener("click", () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      chrome.tabs.sendMessage(tabs[0].id, {
        action: "toggleSidebar"
      });
    });
    window.close();
  });

  // 設定按鈕
  settingsBtn.addEventListener("click", () => {
    settingsPanel.classList.toggle("hidden");
  });

  // 保存設定
  saveSettingsBtn.addEventListener("click", () => {
    const apiUrl = apiUrlInput.value.trim() || "http://localhost:5000";
    const modelType = modelTypeSelect.value;

    chrome.storage.sync.set({
      apiUrl: apiUrl,
      modelType: modelType
    }, () => {
      alert("設定已保存！");
      settingsPanel.classList.add("hidden");
    });
  });

  // 載入已保存的設定
  chrome.storage.sync.get(["apiUrl", "modelType"], (data) => {
    if (data.apiUrl) {
      apiUrlInput.value = data.apiUrl;
    }
    if (data.modelType) {
      modelTypeSelect.value = data.modelType;
    }
  });

  // 鍵盤快捷鍵提示
  chrome.commands.getAll((commands) => {
    commands.forEach(cmd => {
      if (cmd.name === "toggle-sidebar" && cmd.shortcut) {
        activateBtn.title = `快捷鍵: ${cmd.shortcut}`;
      }
    });
  });
});
