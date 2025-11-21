/**
 * Sidebar Script
 * 在獨立視窗中運行，控制聊天交互
 * 支持聊天氣泡 UI
 */

let currentScreenshot = null;

document.addEventListener("DOMContentLoaded", () => {
  const closeSidebarBtn = document.getElementById("closeSidebarBtn");
  const submitBtn = document.getElementById("submitBtn");
  const questionInput = document.getElementById("questionInput");
  const charCount = document.getElementById("charCount");
  const chatArea = document.getElementById("chatArea");

  // 關閉按鈕 - 在獨立視窗中直接關閉視窗
  if (closeSidebarBtn) {
    closeSidebarBtn.addEventListener("click", () => {
      window.close();
    });
  }

  // 提交按鈕 - 自動截圖然後提交
  submitBtn.addEventListener("click", () => {
    if (questionInput.value.trim()) {
      submitQuestionWithScreenshot();
    }
  });

  // 問題輸入監聽
  questionInput.addEventListener("input", () => {
    charCount.textContent = questionInput.value.length;
    updateSubmitButtonState();
  });

  // 支持 Enter 鍵提交
  questionInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (questionInput.value.trim() && !submitBtn.disabled) {
        submitBtn.click();
      }
    }
  });

  // 初始化提交按鈕狀態
  updateSubmitButtonState();
});

// 添加聊天訊息到聊天區域
function addChatMessage(text, isUser = false) {
  const chatArea = document.getElementById("chatArea");
  
  const messageDiv = document.createElement("div");
  messageDiv.className = `chat-message ${isUser ? "user" : "ai"}`;
  
  const bubble = document.createElement("div");
  bubble.className = "message-bubble";
  bubble.textContent = text;
  
  messageDiv.appendChild(bubble);
  chatArea.appendChild(messageDiv);
  
  // 自動捲動到最下面
  chatArea.scrollTop = chatArea.scrollHeight;
}

// 帶截圖的提交問題
async function submitQuestionWithScreenshot() {
  const questionInput = document.getElementById("questionInput");
  const question = questionInput.value.trim();

  if (!question) {
    alert("請輸入問題");
    return;
  }

  // 添加用戶訊息到聊天區域
  addChatMessage(question, true);
  
  // 清空輸入框
  questionInput.value = "";
  document.getElementById("charCount").textContent = "0";

  // 顯示加載狀態
  document.getElementById("loadingArea").classList.remove("hidden");
  document.getElementById("submitBtn").disabled = true;

  try {
    // 🎯 在獨立視窗中，直接透過 chrome.runtime 請求截圖
    console.log("[Sidebar] 請求截圖...");
    
    const response = await chrome.runtime.sendMessage({
      action: "captureScreenshot"
    });
    
    if (response && response.success) {
      currentScreenshot = response.screenshot;
      console.log("[Sidebar] 截圖成功，長度:", currentScreenshot.length);
      
      // 截圖成功後提交問題
      await submitQuestion(question);
    } else {
      throw new Error(response?.error || "截圖失敗");
    }
  } catch (error) {
    console.error("[Sidebar] 錯誤:", error);
    document.getElementById("loadingArea").classList.add("hidden");
    document.getElementById("submitBtn").disabled = false;
    addChatMessage(`❌ 錯誤: ${error.message}`, false);
  }
}

// 提交問題到 API
async function submitQuestion(question) {
  if (!currentScreenshot) {
    throw new Error("沒有截圖");
  }

  try {
    console.log("[Sidebar] 呼叫 API...");
    
    // 🎯 直接透過 chrome.runtime 呼叫 API
    const response = await chrome.runtime.sendMessage({
      action: "apiCall",
      question: question,
      screenshot: currentScreenshot
    });
    
    console.log("[Sidebar] API 回應:", response);
    handleApiResponse(response);
  } catch (error) {
    console.error("[Sidebar] API 錯誤:", error);
    handleApiResponse({
      success: false,
      error: error.message || "API 連接失敗"
    });
  }
}

// 處理 API 回應
function handleApiResponse(response) {
  document.getElementById("loadingArea").classList.add("hidden");
  document.getElementById("submitBtn").disabled = false;

  if (response.success && response.data) {
    // 格式化回應內容
    let content = response.data.response || response.data;
    if (typeof content === "object") {
      content = JSON.stringify(content, null, 2);
    }

    // 添加 AI 訊息到聊天區域
    addChatMessage(content, false);
  } else {
    // 添加錯誤訊息
    const errorMsg = response.error || "AI 處理失敗，請重試";
    addChatMessage(`❌ ${errorMsg}`, false);
  }
}

// 更新提交按鈕狀態
function updateSubmitButtonState() {
  const questionInput = document.getElementById("questionInput");
  const submitBtn = document.getElementById("submitBtn");
  
  if (questionInput.value.trim()) {
    submitBtn.disabled = false;
  } else {
    submitBtn.disabled = true;
  }
}
