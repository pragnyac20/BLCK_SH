const API_BASE = ''; // same origin (Flask serves everything)


document.addEventListener('DOMContentLoaded', () => {
  initUI();
  checkHealth();
});

function qs(sel){ return document.querySelector(sel) }
function qsa(sel){ return document.querySelectorAll(sel) }

function initUI(){
  qs('#studentForm').addEventListener('submit', async (e)=>{
    e.preventDefault();
    await addStudent();
  });

  qs('#issueForm').addEventListener('submit', async (e)=>{
    e.preventDefault();
    await issueRecord();
  });

  qs('#btnGetRecord').addEventListener('click', getEncryptedRecord);
  qs('#btnDecryptRecord').addEventListener('click', decryptRecord);
  qs('#btnVerify').addEventListener('click', verifyRecord);
  qs('#btnLoadTx').addEventListener('click', loadTransactions);
}

async function checkHealth(){
  const healthEl = qs('#health');
  try {
    const res = await fetch(`${API_BASE}/api/health`);
    const j = await res.json();
    if (res.ok) {
      healthEl.textContent = 'Online';
      healthEl.classList.remove('offline');
      healthEl.classList.add('online');
    } else {
      healthEl.textContent = 'Unhealthy';
      healthEl.classList.add('offline');
    }
  } catch(err){
    healthEl.textContent = 'Offline';
    healthEl.classList.add('offline');
  }
}

// --------------- Students ----------------
async function addStudent(){
  const id = qs('#studentId').value.trim();
  const name = qs('#studentName').value.trim();
  const email = qs('#studentEmail').value.trim();
  let meta = qs('#studentMeta').value.trim();
  let parsedMeta = {};
  if(meta) {
    try { parsedMeta = JSON.parse(meta) } catch(e){
      qs('#studentMsg').textContent = 'Invalid JSON in metadata';
      return;
    }
  }

  try {
    qs('#studentMsg').textContent = 'Creating...'
    const res = await fetch(`${API_BASE}/api/students`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        student_id: id,
        name, email,
        public_metadata: parsedMeta
      })
    });
    const j = await res.json();
    if(res.ok){
      qs('#studentMsg').textContent = 'Student created: ' + (j.student && j.student.student_id);
      // copy id to issue form for convenience
      qs('#issueStudentId').value = id;
    } else {
      qs('#studentMsg').textContent = j.error || 'Error creating student';
    }
  } catch (err){
    qs('#studentMsg').textContent = 'Network error: ' + err.message;
  }
}

// --------------- Issue records ----------------
async function issueRecord(){
  const studentId = qs('#issueStudentId').value.trim();
  const course = qs('#issueCourse').value.trim();
  const grade = qs('#issueGrade').value.trim();
  let extra = qs('#issuePayload').value.trim(); let extraObj = {};
  if(extra){
    try { extraObj = JSON.parse(extra) } catch(e){
      qs('#issueMsg').textContent = 'Invalid JSON in payload';
      return;
    }
  }
  if(!studentId || !course || !grade){
    qs('#issueMsg').textContent = 'Missing required fields';
    return;
  }

  const payload = Object.assign({course, grade}, extraObj);

  try {
    qs('#issueMsg').textContent = 'Issuing...';
    const res = await fetch(`${API_BASE}/api/issue`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({student_id: studentId, payload})
    });
    const j = await res.json();
    if(res.ok){
      qs('#issueMsg').textContent = `Issued: ${j.record_id} (tx: ${j.tx_id})`;
      qs('#recordIdInput').value = j.record_id;
    } else {
      qs('#issueMsg').textContent = j.error || 'Error issuing record';
    }
  } catch(err){
    qs('#issueMsg').textContent = 'Network error: ' + err.message;
  }
}

// --------------- Records & Verify ----------------
async function getEncryptedRecord(){
  const rid = qs('#recordIdInput').value.trim();
  if(!rid){ qs('#recordResult').textContent = 'Enter record id'; return; }
  try {
    qs('#recordResult').textContent = 'Loading...';
    const res = await fetch(`${API_BASE}/api/records/${encodeURIComponent(rid)}`);
    const j = await res.json();
    if(res.ok){
      qs('#recordResult').textContent = JSON.stringify(j, null, 2);
    } else qs('#recordResult').textContent = j.error || 'Not found';
  } catch(err){
    qs('#recordResult').textContent = 'Network error: ' + err.message;
  }
}

async function decryptRecord(){
  const rid = qs('#recordIdInput').value.trim();
  if(!rid){ qs('#recordResult').textContent = 'Enter record id'; return; }
  try {
    qs('#recordResult').textContent = 'Decrypting...';
    const res = await fetch(`${API_BASE}/api/records/${encodeURIComponent(rid)}/decrypt`);
    const j = await res.json();
    if(res.ok) qs('#recordResult').textContent = JSON.stringify(j, null, 2);
    else qs('#recordResult').textContent = j.error || 'Error';
  } catch(err){
    qs('#recordResult').textContent = 'Network error: ' + err.message;
  }
}

async function verifyRecord(){
  const rid = qs('#recordIdInput').value.trim();
  if(!rid){ qs('#recordResult').textContent = 'Enter record id'; return; }
  try {
    qs('#recordResult').textContent = 'Verifying...';
    const res = await fetch(`${API_BASE}/api/verify/${encodeURIComponent(rid)}`);
    const j = await res.json();
    if(res.ok) qs('#recordResult').textContent = JSON.stringify(j, null, 2);
    else qs('#recordResult').textContent = j.error || 'Error verifying';
  } catch(err){
    qs('#recordResult').textContent = 'Network error: ' + err.message;
  }
}

// --------------- Transactions ----------------
async function loadTransactions(){
  try {
    const res = await fetch(`${API_BASE}/api/transactions`);
    const j = await res.json();
    if(!res.ok){ qs('#txList').innerHTML = `<li>${j.error || 'error'}</li>`; return; }
    const html = j.transactions.map(t => {
      return `<li><strong>${t.operation}</strong> ${t.tx_id} — ${t.merkle_root || ''}<div style="font-size:12px;color:var(--muted)">${t.timestamp}</div></li>`;
    }).join('');
    qs('#txList').innerHTML = html || '<li>No transactions</li>';
  } catch(err){
    qs('#txList').innerHTML = `<li>Network error: ${err.message}</li>`;
  }
}
