const BACKEND_URL = "http://127.0.0.1:8000";

// ============ PAGE NAVIGATION ============
function showPage(pageId, event) {
  // Hide all pages
  document.querySelectorAll(".page").forEach((page) => {
    page.classList.remove("active");
  });

  // Remove active class from all nav buttons
  document.querySelectorAll(".nav-btn").forEach((btn) => {
    btn.classList.remove("active");
  });

  // Show selected page
  document.getElementById(pageId).classList.add("active");

  // Add active class to clicked button
  if (event) {
    event.target.classList.add("active");
  }
}

// ============ COURSE GENERATOR ============
async function generateCurriculum() {
  let courseTitle = document.getElementById("courseTitle").value;
  let courseLevel = document.getElementById("courseLevel").value;
  let duration = document.getElementById("duration").value;
  let audience = document.getElementById("audience").value;
  let requirements = document.getElementById("requirements").value;
  let description = document.getElementById("description").value;

  let imageType = document.getElementById("imageType")
    ? document.getElementById("imageType").value
    : "photo";

  if (!courseTitle || !duration || !audience || !requirements || !description) {
    alert("⚠️ Please fill all fields!");
    return;
  }

  document.getElementById("outputText").innerText =
    "⏳ Generating curriculum... Please wait...";

  try {
    const response = await fetch(`${BACKEND_URL}/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        courseTitle: courseTitle,
        courseLevel: courseLevel,
        duration: duration,
        audience: audience,
        requirements: requirements,
        description: description,
        imageType: imageType,
      }),
    });

    const data = await response.json();

    if (data.output) {
      document.getElementById("outputText").innerText = data.output;

      // Show a sample cover image based on selected image type
      const img = document.getElementById("courseImage");

      if (img) {
        let query = "education";

        if (imageType === "illustration") query = "illustration,education";
        else if (imageType === "diagram") query = "diagram,education";
        else if (imageType === "icon") query = "icon,education";

        img.src = `https://source.unsplash.com/800x400/?${encodeURIComponent(
          query
        )}`;
        img.style.display = "block";
      }
    } else if (data.error) {
      document.getElementById("outputText").innerText = `❌ Error: ${data.error}`;
    } else {
      document.getElementById("outputText").innerText = "❌ No output received.";
    }
  } catch (error) {
    document.getElementById(
      "outputText"
    ).innerText = `❌ Error connecting to backend: ${error.message}`;
    console.error(error);
  }
}

// ============ TEXT SUMMARIZER ============
async function summarizeText() {
  let text = document.getElementById("summarizeText").value;
  let maxLength = parseInt(document.getElementById("maxLength").value) || 150;
  let minLength = parseInt(document.getElementById("minLength").value) || 50;

  if (!text.trim()) {
    alert("⚠️ Please enter text to summarize!");
    return;
  }

  document.getElementById("originalText").innerText = "⏳ Processing...";
  document.getElementById("summaryText").innerText = "⏳ Summarizing...";

  try {
    const response = await fetch(`${BACKEND_URL}/huggingface/summarize`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text: text,
        max_length: maxLength,
        min_length: minLength,
      }),
    });

    const data = await response.json();

    if (data.summary) {
      document.getElementById("originalText").innerText = data.original_text;
      document.getElementById(
        "summaryText"
      ).innerText = `[${data.tool}]\n\n${data.summary}`;
    } else if (data.error) {
      document.getElementById("summaryText").innerText = `❌ Error: ${data.error}`;
    } else {
      document.getElementById("summaryText").innerText = "❌ No summary received.";
    }
  } catch (error) {
    document.getElementById(
      "summaryText"
    ).innerText = `❌ Error connecting to backend: ${error.message}`;
    console.error(error);
  }
}

// ============ FEEDBACK SUBMISSION ============
function submitFeedback() {
  let name = document.getElementById("feedbackName").value;
  let email = document.getElementById("feedbackEmail").value;

  let message = document.getElementById("feedbackMessage").value;

  if (!name || !email || !message) {
    alert("⚠️ Please fill all required fields!");
    return;
  }

  console.log({
    name: name,
    email: email,
    message: message,
    timestamp: new Date().toISOString(),
  });

  alert(`✅ Thank you ${name}! Your feedback has been received.`);

  // Clear form
  document.getElementById("feedbackName").value = "";
  document.getElementById("feedbackEmail").value = "";
  document.getElementById("feedbackMessage").value = "";
}

// ============ BACKEND HEALTH CHECK ============
async function checkBackendHealth() {
  document.getElementById("healthStatus").innerText =
    "🔄 Checking backend...";

  try {
    const response = await fetch(`${BACKEND_URL}/health`);
    const data = await response.json();

    let status = "Backend Status:\n\n";
    status += `Status: ${data.status}\n`;
    status += `Gemini AI: ${data.gemini}\n`;
    status += `Hugging Face: ${data.huggingface}\n`;
    status += `IBM Watson: ${data.ibm_watson}\n\n`;
    status += `✅ All services checked at ${new Date().toLocaleTimeString()}`;

    document.getElementById("healthStatus").innerText = status;
  } catch (error) {
    document.getElementById(
      "healthStatus"
    ).innerText = `❌ Cannot connect to backend at ${BACKEND_URL}\n\nError: ${error.message}\n\nMake sure the backend is running!`;
  }
}

// ============ Initialize on Page Load ============
document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("welcome").classList.add("active");
  console.log("✅ script.js loaded successfully");
});
