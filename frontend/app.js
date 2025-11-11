const API_BASE = "/api/crawlers";

const tableBody = document.querySelector("#crawler-table-body");
const rowTemplate = document.querySelector("#row-template");
const form = document.querySelector("#crawler-form");
const formTitle = document.querySelector("#form-title");
const toast = document.querySelector("#toast");
const refreshButton = document.querySelector("#refresh-btn");
const resetButton = document.querySelector("#reset-btn");

const formFields = {
  id: document.querySelector("#crawler-id"),
  name: document.querySelector("#name"),
  target_url: document.querySelector("#target_url"),
  schedule: document.querySelector("#schedule"),
  enabled: document.querySelector("#enabled"),
  notes: document.querySelector("#notes"),
};

function showToast(message, isError = false) {
  toast.textContent = message;
  toast.style.background = isError ? "#d32f2f" : "#323232";
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2200);
}

function toFormData() {
  return {
    name: formFields.name.value.trim(),
    target_url: formFields.target_url.value.trim(),
    schedule: formFields.schedule.value.trim() || null,
    enabled: formFields.enabled.checked,
    notes: formFields.notes.value.trim() || null,
  };
}

function resetForm() {
  form.reset();
  formFields.id.value = "";
  formFields.enabled.checked = true;
  formTitle.textContent = "新增爬虫";
}

async function fetchJSON(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "请求失败");
  }
  if (response.status === 204) {
    return null;
  }
  return response.json();
}

function renderTable(crawlers) {
  tableBody.innerHTML = "";
  if (!crawlers.length) {
    tableBody.innerHTML = '<tr><td colspan="7" class="empty">暂无数据</td></tr>';
    return;
  }

  crawlers.forEach((crawler) => {
    const clone = rowTemplate.content.firstElementChild.cloneNode(true);
    clone.dataset.id = crawler.id;
    clone.querySelector(".crawler-name").textContent = crawler.name;
    clone.querySelector(".crawler-url").textContent = crawler.target_url;
    clone.querySelector(".crawler-schedule").textContent = crawler.schedule || "-";
    clone.querySelector(".crawler-status").textContent = `${
      crawler.enabled ? "启用" : "停用"
    } / ${crawler.last_run_status}`;
    clone.querySelector(".crawler-last-run").textContent = crawler.last_run_at
      ? new Date(crawler.last_run_at).toLocaleString()
      : "从未执行";
    clone.querySelector(".crawler-notes").textContent = crawler.notes || "-";

    clone.querySelector(".edit").addEventListener("click", () => fillForm(crawler));
    clone.querySelector(".delete").addEventListener("click", () => removeCrawler(crawler.id));
    clone.querySelector(".run").addEventListener("click", () => triggerRun(crawler.id));

    tableBody.appendChild(clone);
  });
}

function fillForm(crawler) {
  formFields.id.value = crawler.id;
  formFields.name.value = crawler.name;
  formFields.target_url.value = crawler.target_url;
  formFields.schedule.value = crawler.schedule || "";
  formFields.enabled.checked = crawler.enabled;
  formFields.notes.value = crawler.notes || "";
  formTitle.textContent = `编辑：${crawler.name}`;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function loadCrawlers() {
  try {
    const crawlers = await fetchJSON(API_BASE);
    renderTable(crawlers);
  } catch (error) {
    console.error(error);
    showToast(error.message, true);
  }
}

async function removeCrawler(id) {
  if (!confirm("确定要删除该爬虫配置吗？")) {
    return;
  }
  try {
    await fetchJSON(`${API_BASE}/${id}`, { method: "DELETE" });
    showToast("已删除爬虫配置");
    await loadCrawlers();
    resetForm();
  } catch (error) {
    console.error(error);
    showToast(error.message, true);
  }
}

async function triggerRun(id) {
  try {
    await fetchJSON(`${API_BASE}/${id}/run`, { method: "POST" });
    showToast("已触发模拟执行");
    await loadCrawlers();
  } catch (error) {
    console.error(error);
    showToast(error.message, true);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = toFormData();

  if (!payload.name || !payload.target_url) {
    showToast("请填写完整信息", true);
    return;
  }

  const id = formFields.id.value;
  const method = id ? "PUT" : "POST";
  const url = id ? `${API_BASE}/${id}` : API_BASE;

  try {
    await fetchJSON(url, { method, body: JSON.stringify(payload) });
    showToast(id ? "已更新爬虫" : "已创建爬虫");
    await loadCrawlers();
    resetForm();
  } catch (error) {
    console.error(error);
    showToast(error.message, true);
  }
});

refreshButton.addEventListener("click", loadCrawlers);
resetButton.addEventListener("click", resetForm);

document.addEventListener("DOMContentLoaded", loadCrawlers);
