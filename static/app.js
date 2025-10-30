// === BASE URL ===
// Change to your Flask address if different
const BASE_URL = "http://127.0.0.1:5000";

// === Toast helper ===
function showToast(message, isError = false) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.style.background = isError
    ? "linear-gradient(135deg, #ff4b4b, #ff8080)"
    : "linear-gradient(135deg, #00ffb3, #008cff)";
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 3000);
}

// === Health check ===
async function checkHealth() {
  try {
    const res = await fetch(`${BASE_URL}/api/health`);
    const data = await res.json();
    const el = document.getElementById("health");
    if (data.status === "healthy") {
      el.textContent = "Online";
      el.classList.remove("offline");
      el.classList.add("online");
    } else {
      el.textContent = "Offline";
    }
  } catch (err) {
    const el = document.getElementById("health");
    el.textContent = "Offline";
    el.classList.remove("online");
    el.classList.add("offline");
  }
}
checkHealth();

// === Create Student ===
document.getElementById("studentForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const studentData = {
    student_id: document.getElementById("studentId").value.trim(),
    name: document.getElementById("studentName").value.trim(),
    email: document.getElementById("studentEmail").value.trim(),
    public_metadata: JSON.parse(document.getElementById("studentMeta").value || "{}"),
  };

  try {
    const res = await fetch(`${BASE_URL}/api/students`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(studentData),
    });

    const data = await res.json();
    if (res.ok) {
      showToast("✅ Student Created Successfully!");
      document.getElementById("studentMsg").textContent = JSON.stringify(data, null, 2);
    } else {
      showToast(data.error || "Failed to create student", true);
    }
  } catch (err) {
    showToast("Network error: Failed to reach backend", true);
  }
});

// === Issue Record ===
document.getElementById("issueForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const recordData = {
    student_id: document.getElementById("issueStudentId").value.trim(),
    payload: {
      course: document.getElementById("issueCourse").value.trim(),
      grade: document.getElementById("issueGrade").value.trim(),
      ...JSON.parse(document.getElementById("issuePayload").value || "{}"),
    },
  };

  try {
    const res = await fetch(`${BASE_URL}/api/issue`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(recordData),
    });

    const data = await res.json();
    if (res.ok) {
      showToast("📜 Record Issued Successfully!");
      document.getElementById("issueMsg").textContent = JSON.stringify(data, null, 2);
    } else {
      showToast(data.error || "Failed to issue record", true);
    }
  } catch (err) {
    showToast("Network error: Failed to reach backend", true);
  }
});

// === Get Encrypted Record ===
document.getElementById("btnGetRecord").addEventListener("click", async () => {
  const recordId = document.getElementById("recordIdInput").value.trim();
  if (!recordId) return showToast("Please enter a Record ID", true);

  try {
    const res = await fetch(`${BASE_URL}/api/records/${recordId}`);
    const data = await res.json();
    if (res.ok) {
      showToast("Encrypted record fetched!");
      document.getElementById("recordResult").textContent = JSON.stringify(data, null, 2);
    } else {
      showToast(data.error || "Record not found", true);
    }
  } catch (err) {
    showToast("Network error: Failed to fetch record", true);
  }
});

// === Decrypt Record ===
document.getElementById("btnDecryptRecord").addEventListener("click", async () => {
  const recordId = document.getElementById("recordIdInput").value.trim();
  if (!recordId) return showToast("Please enter a Record ID", true);

  try {
    const res = await fetch(`${BASE_URL}/api/records/${recordId}/decrypt`);
    const data = await res.json();
    if (res.ok) {
      showToast("🔓 Record decrypted successfully!");
      document.getElementById("recordResult").textContent = JSON.stringify(data, null, 2);
    } else {
      showToast(data.error || "Failed to decrypt record", true);
    }
  } catch (err) {
    showToast("Network error: Failed to fetch record", true);
  }
});

// === Verify Record ===
document.getElementById("btnVerify").addEventListener("click", async () => {
  const recordId = document.getElementById("recordIdInput").value.trim();
  if (!recordId) return showToast("Please enter a Record ID", true);

  try {
    const res = await fetch(`${BASE_URL}/api/verify/${recordId}`);
    const data = await res.json();
    if (res.ok) {
      showToast(data.verified ? "✅ Record is VALID!" : "❌ Record INVALID", !data.verified);
      document.getElementById("recordResult").textContent = JSON.stringify(data, null, 2);
    } else {
      showToast(data.error || "Verification failed", true);
    }
  } catch (err) {
    showToast("Network error: Failed to reach backend", true);
  }
});

// === Load Transactions ===
document.getElementById("btnLoadTx").addEventListener("click", async () => {
  try {
    const res = await fetch(`${BASE_URL}/api/transactions`);
    const data = await res.json();
    const list = document.getElementById("txList");
    list.innerHTML = "";

    if (data.transactions && data.transactions.length > 0) {
      data.transactions.forEach((tx) => {
        const li = document.createElement("li");
        li.textContent = `${tx.tx_id} — ${tx.operation}`;
        list.appendChild(li);
      });
      showToast("🔄 Transactions loaded!");
    } else {
      list.innerHTML = "<li>No transactions found.</li>";
    }
  } catch (err) {
    showToast("Network error: Could not fetch transactions", true);
  }
});
