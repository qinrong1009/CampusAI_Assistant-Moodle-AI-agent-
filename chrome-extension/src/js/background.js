/**
 * Background Service Worker
 * 處理插件的後台邏輯和訊息傳遞
 */

console.log("[Background] Service Worker 已啟動");

// 儲存視窗 ID，避免重複創建
let chatWindowId = null;

// 監聽擴展圖標點擊
chrome.action.onClicked.addListener(() => {
  console.log("[Background] 圖標被點擊");
  openChatWindow();
});

// 監聽快捷鍵命令
chrome.commands.onCommand.addListener((command) => {
  console.log("[Background] 命令:", command);
  if (command === "toggle-sidebar") {
    // 改為創建獨立視窗
    openChatWindow();
  }
});

// 創建或聚焦聊天視窗
async function openChatWindow() {
  try {
    // 檢查視窗是否已存在
    if (chatWindowId !== null) {
      try {
        const existingWindow = await chrome.windows.get(chatWindowId);
        // 視窗存在，聚焦它
        await chrome.windows.update(chatWindowId, { focused: true });
        console.log("[Background] 聚焦現有視窗");
        return;
      } catch (e) {
        // 視窗不存在了，清除 ID
        chatWindowId = null;
      }
    }
    
    // 創建新視窗（不指定位置，讓系統自動決定）
    const window = await chrome.windows.create({
      url: chrome.runtime.getURL("src/html/sidebar.html"),
      type: "popup",
      width: 500,
      height: 700
    });
    
    chatWindowId = window.id;
    console.log("[Background] 創建新視窗, ID:", chatWindowId);
    
    // 監聽視窗關閉
    chrome.windows.onRemoved.addListener((windowId) => {
      if (windowId === chatWindowId) {
        chatWindowId = null;
        console.log("[Background] 視窗已關閉");
      }
    });
  } catch (error) {
    console.error("[Background] 創建視窗失敗:", error);
  }
}

// 處理來自 Content Script 的訊息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log("[Background] 收到訊息:", request.action);
  
  if (request.action === "captureScreenshot") {
    // 截圖請求 - 需要截取當前活躍的標籤頁，而不是發送者的視窗
    captureActiveTabScreenshot().then(screenshot => {
      sendResponse({ 
        success: true, 
        screenshot: screenshot 
      });
    }).catch(error => {
      console.error("[Background] 截圖失敗:", error);
      sendResponse({ 
        success: false, 
        error: error.message 
      });
    });
    return true; // 異步回應
  }
  
  if (request.action === "apiCall") {
    // 從儲存空間取得 API 設定
    chrome.storage.sync.get(["apiUrl", "modelType"], (data) => {
      const apiUrl = data.apiUrl || "http://localhost:5001";
      const model = data.modelType || "qwen2.5vl:7b";
      
      console.log("[Background] 呼叫 API:", apiUrl);
      
      // 呼叫後端 API
      fetch(`${apiUrl}/api/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          screenshot: request.screenshot,
          question: request.question,
          model: model
        })
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log("[Background] API 成功:", data);
        sendResponse({ success: true, data: data });
      })
      .catch(error => {
        console.error("[Background] API 錯誤:", error);
        sendResponse({ 
          success: false, 
          error: error.message || "API 連接失敗"
        });
      });
    });
    
    // 異步發送回應
    return true;
  }
});

// 截取當前活躍標籤頁的截圖（用於獨立視窗）
async function captureActiveTabScreenshot() {
  try {
    // 獲取當前活躍的標籤頁（排除 popup 視窗）
    const tabs = await chrome.tabs.query({ active: true, currentWindow: false });
    
    if (tabs.length === 0) {
      // 如果沒有活躍標籤，嘗試獲取最近使用的普通視窗
      const windows = await chrome.windows.getAll({ populate: true, windowTypes: ['normal'] });
      
      for (const window of windows) {
        const activeTab = window.tabs.find(tab => tab.active);
        if (activeTab) {
          return await captureScreenshotFromWindow(window.id);
        }
      }
      
      throw new Error("找不到可截圖的標籤頁");
    }
    
    // 使用第一個活躍標籤的視窗進行截圖
    return await captureScreenshotFromWindow(tabs[0].windowId);
  } catch (error) {
    console.error("[Background] 截取活躍標籤失敗:", error);
    throw error;
  }
}

// 從指定視窗截圖
async function captureScreenshotFromWindow(windowId) {
  try {
    // 使用 Chrome 的 captureVisibleTab API
    const canvas = await chrome.tabs.captureVisibleTab(windowId, {
      format: "jpeg",
      quality: 80
    });
    
    console.log("[Background] 截圖成功");
    return canvas;
  } catch (error) {
    console.error("[Background] Chrome API 截圖失敗，使用備用方案:", error);
    
    // 備用方案：使用簡單的白色圖片
    const c = document.createElement("canvas");
    c.width = 1280;
    c.height = 720;
    const ctx = c.getContext("2d");
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, c.width, c.height);
    ctx.fillStyle = "#666";
    ctx.font = "20px Arial";
    ctx.fillText("截圖失敗，請重試", 50, 100);
    
    return c.toDataURL("image/jpeg", 0.8);
  }
}

// 使用 Chrome 的截圖 API（舊版，保留以防需要）
async function captureScreenshotFromTab(tabId) {
  try {
    // 使用 Chrome 的 captureVisibleTab API
    const canvas = await chrome.tabs.captureVisibleTab(null, {
      format: "jpeg",
      quality: 80
    });
    
    console.log("[Background] 截圖成功");
    return canvas;
  } catch (error) {
    console.error("[Background] Chrome API 截圖失敗，使用備用方案:", error);
    
    // 備用方案：使用簡單的白色圖片
    const c = document.createElement("canvas");
    c.width = 1280;
    c.height = 720;
    const ctx = c.getContext("2d");
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, c.width, c.height);
    ctx.fillStyle = "#666";
    ctx.font = "20px Arial";
    ctx.fillText("截圖失敗，請重試", 50, 100);
    
    return c.toDataURL("image/jpeg", 0.8);
  }
}

// 插件安裝時初始化設定
chrome.runtime.onInstalled.addListener(() => {
  console.log("[Background] 插件已安裝，初始化設定");
  chrome.storage.sync.set({
    apiUrl: "http://localhost:5001",
    modelType: "qwen2.5vl:7b"
  });
});

console.log("[Background] 所有監聽器已註冊");
