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
  // 保存設定（改為友好提示並讓按鈕在請求時鎖定）
  saveSettingsBtn.addEventListener("click", () => {
    const apiUrl = apiUrlInput.value.trim() || "http://localhost:5000";
    const modelType = modelTypeSelect.value;

    saveSettingsBtn.disabled = true;
    saveSettingsBtn.textContent = '儲存中...';

    // 先嘗試透過 background 呼叫 /api/set_model，如果成功，再保存到 storage
    chrome.runtime.sendMessage({ action: 'setModel', model: modelType }, (resp) => {
      chrome.storage.sync.set({ apiUrl: apiUrl, modelType: modelType }, () => {
        if (resp && resp.success) {
          // 輕量提示
          saveSettingsBtn.textContent = '已保存';
          setTimeout(() => {
            saveSettingsBtn.textContent = '保存';
            saveSettingsBtn.disabled = false;
            settingsPanel.classList.add("hidden");
          }, 800);
        } else {
          saveSettingsBtn.textContent = '已保存 (本地)';
          setTimeout(() => {
            saveSettingsBtn.textContent = '保存';
            saveSettingsBtn.disabled = false;
            settingsPanel.classList.add("hidden");
          }, 1200);
        }
      });
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
