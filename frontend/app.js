async function fetchJson(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

function pretty(data) {
  return JSON.stringify(data, null, 2);
}

async function loadUsers() {
  const users = await fetchJson('/api/users');
  const select = document.getElementById('userSelect');
  select.innerHTML = '';
  users.forEach((user) => {
    const option = document.createElement('option');
    option.value = user.user_id;
    option.textContent = `${user.display_name} (${user.role})`;
    select.appendChild(option);
  });
  select.value = 'architect_1';
}

async function refreshMetrics() {
  document.getElementById('metricsBox').textContent = pretty(await fetchJson('/api/metrics'));
}

async function refreshQueue() {
  document.getElementById('reviewBox').textContent = pretty(await fetchJson('/api/review-queue'));
}

async function refreshTraces() {
  const traces = await fetchJson('/api/traces');
  document.getElementById('traceBox').textContent = pretty(traces.slice(0, 8));
}

async function runQuery() {
  const payload = {
    user_id: document.getElementById('userSelect').value,
    query: document.getElementById('queryInput').value,
    requested_tool: document.getElementById('toolSelect').value || null,
  };
  const result = await fetchJson('/api/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  document.getElementById('resultBox').textContent = pretty(result);
  await refreshMetrics();
  await refreshQueue();
  await refreshTraces();
}

async function runBenchmarks() {
  const result = await fetchJson('/api/benchmarks/run', { method: 'POST' });
  document.getElementById('traceBox').textContent = pretty(result);
  await refreshMetrics();
  await refreshQueue();
}

document.getElementById('runButton').addEventListener('click', runQuery);
document.getElementById('refreshMetrics').addEventListener('click', refreshMetrics);
document.getElementById('refreshQueue').addEventListener('click', refreshQueue);
document.getElementById('refreshTraces').addEventListener('click', refreshTraces);
document.getElementById('runBenchmarks').addEventListener('click', runBenchmarks);

loadUsers().then(() => Promise.all([refreshMetrics(), refreshQueue(), refreshTraces()]));
