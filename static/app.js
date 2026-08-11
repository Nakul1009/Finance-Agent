const API_BASE = '/api';

class FinBankApp {
    constructor() {
        this.currentView = 'dashboard';
        this.analyticsData = null;
        this.transactions = [];
        this.documents = [];
        this.chatHistory = [];
        this.filters = { search: '', category: '', type: '' };
        this.chartInstances = {};

        window.addEventListener('hashchange', () => this.handleHashChange());
        document.addEventListener('DOMContentLoaded', () => this.init());
    }

    async init() {
        this.handleHashChange();
        await this.checkHealth();
        await this.loadAllData();
    }

    handleHashChange() {
        const hash = window.location.hash.replace('#', '') || 'dashboard';
        this.navigate(hash);
    }

    navigate(view) {
        this.currentView = view;
        window.location.hash = view;

        // Update nav styling
        document.querySelectorAll('.nav-item').forEach(el => {
            el.classList.remove('bg-sky-50', 'text-sky-700', 'font-semibold');
            el.classList.add('text-slate-700');
        });
        const activeNav = document.getElementById(`nav-${view}`);
        if (activeNav) {
            activeNav.classList.add('bg-sky-50', 'text-sky-700', 'font-semibold');
        }

        this.render();
    }

    async checkHealth() {
        try {
            const res = await fetch(`${API_BASE}/health`);
            const data = await res.json();
            const badge = document.getElementById('llm-status-badge');
            if (badge) {
                if (data.llm_configured) {
                    badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-500"></span> Nemotron Active`;
                } else {
                    badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-amber-500"></span> Rules Engine`;
                }
            }
        } catch (e) {
            console.error('Health check failed', e);
        }
    }

    async loadAllData() {
        try {
            const [analyticsRes, txRes, docRes] = await Promise.all([
                fetch(`${API_BASE}/analytics`),
                fetch(`${API_BASE}/transactions`),
                fetch(`${API_BASE}/documents`)
            ]);

            if (analyticsRes.ok) this.analyticsData = await analyticsRes.json();
            if (txRes.ok) this.transactions = await txRes.json();
            if (docRes.ok) this.documents = await docRes.json();

            this.render();
        } catch (e) {
            console.error('Failed to load data', e);
        }
    }

    async loadDemoData() {
        const btn = document.getElementById('btn-load-demo');
        if (btn) btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin text-sky-600"></i> Loading...`;

        try {
            const res = await fetch(`${API_BASE}/documents/demo`, { method: 'POST' });
            if (res.ok) {
                await this.loadAllData();
                this.navigate('dashboard');
            }
        } catch (e) {
            alert('Failed to load demo statement.');
        } finally {
            if (btn) btn.innerHTML = `<i data-lucide="sparkles" class="w-4 h-4 text-sky-600"></i> Load Demo Statement`;
            lucide.createIcons();
        }
    }

    async handleFileUpload(file) {
        const formData = new FormData();
        formData.append('file', file);

        const container = document.getElementById('upload-status-zone');
        if (container) container.innerHTML = `<div class="text-sm text-sky-600 font-semibold flex items-center justify-center gap-2"><i data-lucide="loader-2" class="w-5 h-5 animate-spin"></i> Parsing and extracting transactions...</div>`;
        lucide.createIcons();

        try {
            const res = await fetch(`${API_BASE}/documents/upload`, {
                method: 'POST',
                body: formData
            });

            if (res.ok) {
                await this.loadAllData();
                this.navigate('dashboard');
            } else {
                const err = await res.json();
                alert(`Upload failed: ${err.detail || 'Invalid document'}`);
            }
        } catch (e) {
            alert('Error uploading document.');
        }
    }

    render() {
        const main = document.getElementById('main-view');
        if (!main) return;

        // Cleanup chart instances
        Object.values(this.chartInstances).forEach(c => c && c.destroy());
        this.chartInstances = {};

        switch (this.currentView) {
            case 'dashboard':
                main.innerHTML = this.renderDashboardHTML();
                this.initDashboardCharts();
                break;
            case 'documents':
                main.innerHTML = this.renderDocumentsHTML();
                break;
            case 'transactions':
                main.innerHTML = this.renderTransactionsHTML();
                break;
            case 'analytics':
                main.innerHTML = this.renderAnalyticsHTML();
                this.initAnalyticsCharts();
                break;
            case 'assistant':
                main.innerHTML = this.renderAssistantHTML();
                break;
            case 'report':
                main.innerHTML = this.renderReportHTML();
                break;
            default:
                main.innerHTML = this.renderDashboardHTML();
                this.initDashboardCharts();
        }

        lucide.createIcons();
    }

    renderDashboardHTML() {
        if (!this.transactions || this.transactions.length === 0) {
            return `
                <div class="space-y-6">
                    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                        <div>
                            <h2 class="text-xl font-bold text-slate-900">Financial Overview</h2>
                            <p class="text-xs text-slate-500">Real-time normalized statement intelligence & metrics</p>
                        </div>
                    </div>

                    <div class="bg-white p-12 rounded-xl border border-slate-200 shadow-sm text-center">
                        <div class="w-16 h-16 bg-sky-50 text-sky-600 rounded-full flex items-center justify-center mx-auto mb-4">
                            <i data-lucide="upload-cloud" class="w-8 h-8"></i>
                        </div>
                        <h3 class="text-lg font-bold text-slate-900 mb-1">No Financial Data Uploaded Yet</h3>
                        <p class="text-xs text-slate-500 max-w-md mx-auto mb-6">Upload your bank statement (PDF, CSV, or XLSX) to view real-time transaction categorizations, financial analytics, risk stability assessments, and AI assistant insights.</p>
                        <div class="flex flex-wrap items-center justify-center gap-3">
                            <button onclick="app.navigate('documents')" class="bg-sky-600 hover:bg-sky-700 text-white text-xs font-semibold px-5 py-2.5 rounded-lg transition shadow-sm flex items-center gap-2">
                                <i data-lucide="upload" class="w-4 h-4"></i> Upload Bank Statement
                            </button>
                            <button onclick="app.loadDemoData()" class="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold px-5 py-2.5 rounded-lg transition border border-slate-200 flex items-center gap-2">
                                <i data-lucide="sparkles" class="w-4 h-4 text-sky-600"></i> Load Demo Statement
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }

        const a = this.analyticsData || {};
        const assess = a.assessment || {};
        const rating = assess.rating || 'Needs Attention';

        const ratingColorClass = rating === 'Good' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
            (rating === 'Moderate' ? 'bg-amber-50 text-amber-700 border-amber-200' : 'bg-rose-50 text-rose-700 border-rose-200');

        return `
            <div class="space-y-6">
                <!-- Top Welcome Banner -->
                <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                    <div>
                        <h2 class="text-xl font-bold text-slate-900">Financial Overview</h2>
                        <p class="text-xs text-slate-500">Real-time normalized statement intelligence & metrics</p>
                    </div>
                    <div class="flex items-center gap-3">
                        <div class="px-3 py-1.5 rounded-lg border text-xs font-semibold flex items-center gap-1.5 ${ratingColorClass}">
                            <i data-lucide="shield-check" class="w-4 h-4"></i>
                            Financial Stability: ${rating}
                        </div>
                        <button onclick="app.navigate('documents')" class="bg-sky-600 hover:bg-sky-700 text-white text-xs font-semibold px-4 py-2 rounded-lg transition shadow-sm flex items-center gap-1.5">
                            <i data-lucide="upload" class="w-4 h-4"></i> Upload Statement
                        </button>
                    </div>
                </div>

                <!-- 4 Core Metric Cards -->
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                        <div class="flex justify-between items-center text-slate-500 mb-2">
                            <span class="text-xs font-semibold">Total Income</span>
                            <div class="w-8 h-8 rounded-lg bg-emerald-50 flex items-center justify-center text-emerald-600"><i data-lucide="trending-up" class="w-4 h-4"></i></div>
                        </div>
                        <div class="text-2xl font-bold text-slate-900">₹${(a.total_income || 0).toLocaleString('en-IN', {minimumFractionDigits:2})}</div>
                        <p class="text-[11px] text-emerald-600 font-medium mt-1">Verified Statement Inflow</p>
                    </div>

                    <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                        <div class="flex justify-between items-center text-slate-500 mb-2">
                            <span class="text-xs font-semibold">Total Expenses</span>
                            <div class="w-8 h-8 rounded-lg bg-rose-50 flex items-center justify-center text-rose-600"><i data-lucide="trending-down" class="w-4 h-4"></i></div>
                        </div>
                        <div class="text-2xl font-bold text-slate-900">₹${(a.total_expenses || 0).toLocaleString('en-IN', {minimumFractionDigits:2})}</div>
                        <p class="text-[11px] text-slate-500 font-medium mt-1">Expense Ratio: ${a.expense_to_income_ratio || 0}%</p>
                    </div>

                    <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                        <div class="flex justify-between items-center text-slate-500 mb-2">
                            <span class="text-xs font-semibold">Net Cash Flow</span>
                            <div class="w-8 h-8 rounded-lg bg-sky-50 flex items-center justify-center text-sky-600"><i data-lucide="wallet" class="w-4 h-4"></i></div>
                        </div>
                        <div class="text-2xl font-bold ${a.net_cash_flow >= 0 ? 'text-slate-900' : 'text-rose-600'}">₹${(a.net_cash_flow || 0).toLocaleString('en-IN', {minimumFractionDigits:2})}</div>
                        <p class="text-[11px] text-sky-600 font-medium mt-1">Savings Rate: ${a.savings_rate || 0}%</p>
                    </div>

                    <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                        <div class="flex justify-between items-center text-slate-500 mb-2">
                            <span class="text-xs font-semibold">Transactions</span>
                            <div class="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center text-slate-600"><i data-lucide="list" class="w-4 h-4"></i></div>
                        </div>
                        <div class="text-2xl font-bold text-slate-900">${a.transaction_count || 0}</div>
                        <p class="text-[11px] text-slate-500 font-medium mt-1">Avg: ₹${(a.avg_transaction_value || 0).toLocaleString('en-IN')}</p>
                    </div>
                </div>

                <!-- Charts Section -->
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <!-- Monthly Trend Chart -->
                    <div class="lg:col-span-2 bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col">
                        <h3 class="text-sm font-bold text-slate-900 mb-4 flex items-center justify-between">
                            <span>Income vs Expense Trend</span>
                            <span class="text-xs font-normal text-slate-400">Monthly breakdown</span>
                        </h3>
                        <div class="flex-1 relative min-h-[260px]">
                            <canvas id="chart-monthly-trend"></canvas>
                        </div>
                    </div>

                    <!-- Spending by Category Donut -->
                    <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col">
                        <h3 class="text-sm font-bold text-slate-900 mb-4">Top Spending Categories</h3>
                        <div class="flex-1 relative min-h-[260px]">
                            <canvas id="chart-category-donut"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Insights & Anomalies Quick Section -->
                <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                    <h3 class="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
                        <i data-lucide="alert-triangle" class="w-4 h-4 text-amber-500"></i>
                        <span>Detected Insights & Anomalies</span>
                    </h3>
                    <div class="space-y-3">
                        ${(a.anomalies || []).length > 0 ? a.anomalies.map(anom => `
                            <div class="p-3.5 rounded-lg border border-slate-100 bg-slate-50/70 flex items-start gap-3">
                                <span class="p-1.5 rounded-md ${anom.severity === 'high' ? 'bg-rose-100 text-rose-600' : 'bg-amber-100 text-amber-600'}">
                                    <i data-lucide="info" class="w-4 h-4"></i>
                                </span>
                                <div>
                                    <h4 class="text-xs font-bold text-slate-800">${anom.title}</h4>
                                    <p class="text-xs text-slate-600 mt-0.5">${anom.description}</p>
                                </div>
                            </div>
                        `).join('') : `
                            <p class="text-xs text-slate-500 italic">No unusual financial anomalies detected in the statement.</p>
                        `}
                    </div>
                </div>
            </div>
        `;
    }

    initDashboardCharts() {
        if (!this.transactions || this.transactions.length === 0) return;
        const a = this.analyticsData || {};
        const trends = a.monthly_trends || [];
        const cats = (a.top_categories || []).slice(0, 5);

        // Monthly Trend
        const ctxTrend = document.getElementById('chart-monthly-trend');
        if (ctxTrend) {
            this.chartInstances.trend = new Chart(ctxTrend, {
                type: 'bar',
                data: {
                    labels: trends.map(t => t.month),
                    datasets: [
                        { label: 'Income', data: trends.map(t => t.income), backgroundColor: '#10b981', borderRadius: 4 },
                        { label: 'Expense', data: trends.map(t => t.expense), backgroundColor: '#f43f5e', borderRadius: 4 }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'top', labels: { boxWidth: 12, font: { size: 11 } } } },
                    scales: {
                        x: { grid: { display: false }, ticks: { font: { size: 11 } } },
                        y: { grid: { color: '#f1f5f9' }, ticks: { font: { size: 11 } } }
                    }
                }
            });
        }

        // Category Donut
        const ctxDonut = document.getElementById('chart-category-donut');
        if (ctxDonut) {
            this.chartInstances.donut = new Chart(ctxDonut, {
                type: 'doughnut',
                data: {
                    labels: cats.map(c => c.category),
                    datasets: [{
                        data: cats.map(c => c.amount),
                        backgroundColor: ['#0284c7', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#64748b']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 10 } } } }
                }
            });
        }
    }

    renderDocumentsHTML() {
        return `
            <div class="max-w-4xl mx-auto space-y-6">
                <div>
                    <h2 class="text-xl font-bold text-slate-900">Upload Bank Statement</h2>
                    <p class="text-xs text-slate-500">Supports PDF, CSV, and XLSX statement parsing with automatic column normalization</p>
                </div>

                <!-- Drag and Drop Upload Zone -->
                <div class="bg-white p-8 rounded-xl border-2 border-dashed border-slate-300 hover:border-sky-500 transition text-center" id="drop-zone">
                    <div id="upload-status-zone">
                        <div class="w-12 h-12 rounded-full bg-sky-50 text-sky-600 flex items-center justify-center mx-auto mb-3">
                            <i data-lucide="cloud-upload" class="w-6 h-6"></i>
                        </div>
                        <h3 class="text-sm font-bold text-slate-900 mb-1">Upload Bank Statement File</h3>
                        <p class="text-xs text-slate-500 mb-4">PDF, CSV, or Excel XLSX files up to 25MB</p>
                        
                        <label class="inline-flex items-center gap-2 bg-sky-600 hover:bg-sky-700 text-white text-xs font-semibold px-5 py-2.5 rounded-lg cursor-pointer transition shadow-sm">
                            <i data-lucide="file-plus" class="w-4 h-4"></i> Browse Files
                            <input type="file" class="hidden" accept=".pdf,.csv,.xlsx,.xls" onchange="app.handleFileUpload(this.files[0])">
                        </label>
                    </div>
                </div>

                <!-- Or Load Synthetic Demo -->
                <div class="bg-gradient-to-r from-sky-50 to-indigo-50 border border-sky-200 p-5 rounded-xl flex items-center justify-between">
                    <div>
                        <h4 class="text-sm font-bold text-sky-900">Recruiter Demo Mode</h4>
                        <p class="text-xs text-slate-600">No bank statement handy? Immediately test with realistic synthetic multi-month financial statement data.</p>
                    </div>
                    <button onclick="app.loadDemoData()" class="bg-sky-600 hover:bg-sky-700 text-white text-xs font-semibold px-4 py-2.5 rounded-lg transition shadow-sm flex items-center gap-2 flex-shrink-0">
                        <i data-lucide="sparkles" class="w-4 h-4"></i> Load Demo Data
                    </button>
                </div>

                <!-- Processed Documents History -->
                <div class="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
                    <h3 class="text-sm font-bold text-slate-900 mb-4">Uploaded Document History</h3>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs border-collapse">
                            <thead>
                                <tr class="border-b border-slate-200 text-slate-500 font-semibold bg-slate-50">
                                    <th class="p-3">Filename</th>
                                    <th class="p-3">Format</th>
                                    <th class="p-3">Uploaded At</th>
                                    <th class="p-3">Transactions</th>
                                    <th class="p-3">Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${(this.documents || []).length > 0 ? this.documents.map(d => `
                                    <tr class="border-b border-slate-100 hover:bg-slate-50/50">
                                        <td class="p-3 font-semibold text-slate-800 flex items-center gap-2">
                                            <i data-lucide="file-text" class="w-4 h-4 text-sky-600"></i> ${d.filename}
                                        </td>
                                        <td class="p-3 uppercase text-slate-500">${d.file_type}</td>
                                        <td class="p-3 text-slate-500">${new Date(d.upload_date).toLocaleDateString()}</td>
                                        <td class="p-3 font-medium text-slate-700">${d.transaction_count}</td>
                                        <td class="p-3">
                                            <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold ${d.status === 'completed' ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'}">
                                                ${d.status}
                                            </span>
                                        </td>
                                    </tr>
                                `).join('') : `
                                    <tr>
                                        <td colspan="5" class="p-6 text-center text-slate-400">No documents processed yet. Click "Load Demo Statement" to test instantly.</td>
                                    </tr>
                                `}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
    }

    renderTransactionsHTML() {
        const filtered = this.transactions.filter(t => {
            const matchesSearch = !this.filters.search ||
                t.description.toLowerCase().includes(this.filters.search.toLowerCase()) ||
                t.merchant.toLowerCase().includes(this.filters.search.toLowerCase());
            const matchesCategory = !this.filters.category || t.category === this.filters.category;
            const matchesType = !this.filters.type || t.transaction_type === this.filters.type;
            return matchesSearch && matchesCategory && matchesType;
        });

        return `
            <div class="space-y-6">
                <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div>
                        <h2 class="text-xl font-bold text-slate-900">Extracted & Normalized Transactions</h2>
                        <p class="text-xs text-slate-500">Categorized via Hybrid Rules & Nemotron LLM with full explainability</p>
                    </div>
                    <div class="text-xs text-slate-500 font-semibold bg-white px-3 py-2 rounded-lg border border-slate-200">
                        Showing ${filtered.length} of ${this.transactions.length} transactions
                    </div>
                </div>

                <!-- Filter Controls -->
                <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row gap-3">
                    <div class="flex-1 relative">
                        <i data-lucide="search" class="w-4 h-4 text-slate-400 absolute left-3 top-3"></i>
                        <input type="text" placeholder="Search merchant or narration..." value="${this.filters.search}" oninput="app.setFilter('search', this.value)" class="w-full pl-9 pr-3 py-2 text-xs border border-slate-200 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500">
                    </div>
                    <div class="w-full md:w-48">
                        <select onchange="app.setFilter('category', this.value)" class="w-full p-2 text-xs border border-slate-200 rounded-lg focus:ring-2 focus:ring-sky-500">
                            <option value="">All Categories</option>
                            ${(this.analyticsData?.top_categories || []).map(c => `<option value="${c.category}" ${this.filters.category === c.category ? 'selected' : ''}>${c.category}</option>`).join('')}
                        </select>
                    </div>
                    <div class="w-full md:w-36">
                        <select onchange="app.setFilter('type', this.value)" class="w-full p-2 text-xs border border-slate-200 rounded-lg focus:ring-2 focus:ring-sky-500">
                            <option value="">All Types</option>
                            <option value="income" ${this.filters.type === 'income' ? 'selected' : ''}>Income</option>
                            <option value="expense" ${this.filters.type === 'expense' ? 'selected' : ''}>Expense</option>
                        </select>
                    </div>
                </div>

                <!-- Transactions Table -->
                <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs border-collapse">
                            <thead>
                                <tr class="border-b border-slate-200 text-slate-500 font-semibold bg-slate-50">
                                    <th class="p-3">Date</th>
                                    <th class="p-3">Merchant / Narration</th>
                                    <th class="p-3">Category</th>
                                    <th class="p-3">Method</th>
                                    <th class="p-3 text-right">Amount</th>
                                    <th class="p-3 text-center">Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${filtered.length > 0 ? filtered.map(t => `
                                    <tr class="border-b border-slate-100 hover:bg-slate-50/50">
                                        <td class="p-3 font-medium text-slate-600 whitespace-nowrap">${t.date}</td>
                                        <td class="p-3">
                                            <div class="font-bold text-slate-800">${t.merchant}</div>
                                            <div class="text-[11px] text-slate-400 truncate max-w-xs">${t.description}</div>
                                        </td>
                                        <td class="p-3">
                                            <span class="inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-semibold bg-sky-50 text-sky-700 border border-sky-100">
                                                ${t.category}
                                            </span>
                                        </td>
                                        <td class="p-3">
                                            <span class="inline-flex items-center gap-1 text-[11px] font-medium text-slate-500 capitalize">
                                                <i data-lucide="${t.categorization_method === 'nemotron' ? 'cpu' : (t.categorization_method === 'manual' ? 'user-check' : 'check-circle')}" class="w-3.5 h-3.5 text-sky-600"></i>
                                                ${t.categorization_method} (${Math.round(t.confidence * 100)}%)
                                            </span>
                                        </td>
                                        <td class="p-3 text-right font-bold whitespace-nowrap ${t.transaction_type === 'income' ? 'text-emerald-600' : 'text-slate-900'}">
                                            ${t.transaction_type === 'income' ? '+' : '-'}₹${t.amount.toLocaleString('en-IN', {minimumFractionDigits:2})}
                                        </td>
                                        <td class="p-3 text-center">
                                            <button onclick="app.openCategoryModal('${t.id}', '${t.merchant.replace(/'/g, "\\'")}', '${t.category}')" class="text-sky-600 hover:text-sky-800 font-semibold p-1 hover:bg-sky-50 rounded transition" title="Edit Category">
                                                <i data-lucide="edit-2" class="w-3.5 h-3.5"></i>
                                            </button>
                                        </td>
                                    </tr>
                                `).join('') : `
                                    <tr>
                                        <td colspan="6" class="p-6 text-center text-slate-400">No matching transactions found.</td>
                                    </tr>
                                `}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
    }

    setFilter(key, val) {
        this.filters[key] = val;
        this.render();
    }

    openCategoryModal(txId, desc, currentCat) {
        document.getElementById('modal-tx-id').value = txId;
        document.getElementById('modal-tx-desc').innerText = `Transaction: ${desc}`;
        document.getElementById('modal-category-select').value = currentCat;
        document.getElementById('category-modal').classList.remove('hidden');
    }

    closeCategoryModal() {
        document.getElementById('category-modal').classList.add('hidden');
    }

    async saveCategoryEdit() {
        const txId = document.getElementById('modal-tx-id').value;
        const newCat = document.getElementById('modal-category-select').value;

        try {
            const res = await fetch(`${API_BASE}/transactions/${txId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ category: newCat })
            });

            if (res.ok) {
                this.closeCategoryModal();
                await this.loadAllData();
            }
        } catch (e) {
            alert('Failed to update category.');
        }
    }

    renderAnalyticsHTML() {
        if (!this.transactions || this.transactions.length === 0) {
            return `
                <div class="space-y-6">
                    <div>
                        <h2 class="text-xl font-bold text-slate-900">Financial Patterns & Analytics</h2>
                        <p class="text-xs text-slate-500">Deterministic statistical calculation of recurring commitments & anomalies</p>
                    </div>
                    <div class="bg-white p-12 rounded-xl border border-slate-200 shadow-sm text-center">
                        <div class="w-16 h-16 bg-sky-50 text-sky-600 rounded-full flex items-center justify-center mx-auto mb-4">
                            <i data-lucide="pie-chart" class="w-8 h-8"></i>
                        </div>
                        <h3 class="text-lg font-bold text-slate-900 mb-1">No Financial Data Available</h3>
                        <p class="text-xs text-slate-500 max-w-md mx-auto mb-6">Upload a bank statement (PDF, CSV, or XLSX) to view category distributions, top merchants, and detected recurring commitments.</p>
                        <button onclick="app.navigate('documents')" class="bg-sky-600 hover:bg-sky-700 text-white text-xs font-semibold px-5 py-2.5 rounded-lg transition shadow-sm inline-flex items-center gap-2">
                            <i data-lucide="upload" class="w-4 h-4"></i> Upload Bank Statement
                        </button>
                    </div>
                </div>
            `;
        }

        const a = this.analyticsData || {};
        const recurs = a.recurring_payments || [];

        return `
            <div class="space-y-6">
                <div>
                    <h2 class="text-xl font-bold text-slate-900">Financial Patterns & Analytics</h2>
                    <p class="text-xs text-slate-500">Deterministic statistical calculation of recurring commitments & anomalies</p>
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <!-- Detailed Bar Chart -->
                    <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                        <h3 class="text-sm font-bold text-slate-900 mb-4">Category Spending Distribution</h3>
                        <div class="h-64 relative">
                            <canvas id="chart-analytics-bar"></canvas>
                        </div>
                    </div>

                    <!-- Top Merchants Table -->
                    <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col">
                        <h3 class="text-sm font-bold text-slate-900 mb-4">Top Merchant Expenses</h3>
                        <div class="overflow-y-auto max-h-64 custom-scrollbar flex-1">
                            <table class="w-full text-left text-xs">
                                <thead>
                                    <tr class="border-b border-slate-200 text-slate-400 font-semibold bg-slate-50">
                                        <th class="p-2">Merchant</th>
                                        <th class="p-2">Category</th>
                                        <th class="p-2 text-right">Total Spent</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${(a.top_merchants || []).map(m => `
                                        <tr class="border-b border-slate-100">
                                            <td class="p-2 font-bold text-slate-800">${m.merchant}</td>
                                            <td class="p-2 text-slate-500">${m.category}</td>
                                            <td class="p-2 text-right font-semibold text-slate-900">₹${m.amount.toLocaleString('en-IN', {minimumFractionDigits:2})}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- Recurring Payments Table -->
                <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                    <h3 class="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
                        <i data-lucide="repeat" class="w-4 h-4 text-sky-600"></i>
                        <span>Detected Recurring Financial Commitments</span>
                    </h3>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs border-collapse">
                            <thead>
                                <tr class="border-b border-slate-200 text-slate-500 font-semibold bg-slate-50">
                                    <th class="p-3">Merchant</th>
                                    <th class="p-3">Category</th>
                                    <th class="p-3">Est. Monthly Amount</th>
                                    <th class="p-3">Frequency</th>
                                    <th class="p-3">Last Payment Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${recurs.length > 0 ? recurs.map(r => `
                                    <tr class="border-b border-slate-100">
                                        <td class="p-3 font-bold text-slate-800">${r.merchant}</td>
                                        <td class="p-3 text-slate-600">${r.category}</td>
                                        <td class="p-3 font-bold text-slate-900">₹${r.estimated_amount.toLocaleString('en-IN', {minimumFractionDigits:2})}</td>
                                        <td class="p-3 text-slate-500 capitalize">${r.frequency}</td>
                                        <td class="p-3 text-slate-500">${r.last_date}</td>
                                    </tr>
                                `).join('') : `
                                    <tr><td colspan="5" class="p-4 text-center text-slate-400">No recurring payments detected.</td></tr>
                                `}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
    }

    initAnalyticsCharts() {
        if (!this.transactions || this.transactions.length === 0) return;
        const a = this.analyticsData || {};
        const cats = a.top_categories || [];

        const ctxBar = document.getElementById('chart-analytics-bar');
        if (ctxBar) {
            this.chartInstances.analyticsBar = new Chart(ctxBar, {
                type: 'bar',
                data: {
                    labels: cats.map(c => c.category),
                    datasets: [{
                        label: 'Total Spent (₹)',
                        data: cats.map(c => c.amount),
                        backgroundColor: '#0ea5e9',
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: { x: { grid: { display: false } }, y: { grid: { color: '#f1f5f9' } } }
                }
            });
        }
    }

    renderAssistantHTML() {
        return `
            <div class="max-w-3xl mx-auto space-y-4 flex flex-col h-[calc(100vh-140px)]">
                <div>
                    <h2 class="text-xl font-bold text-slate-900">AI Financial Assistant</h2>
                    <p class="text-xs text-slate-500">Ask questions grounded strictly in your processed bank statement context</p>
                </div>

                <!-- Quick Prompt Buttons -->
                <div class="flex flex-wrap gap-2">
                    <button onclick="app.sendAssistantMessage('How much did I spend on food?')" class="bg-white hover:bg-sky-50 text-slate-700 text-xs px-3 py-1.5 rounded-lg border border-slate-200 shadow-sm transition">
                        🍔 How much did I spend on food?
                    </button>
                    <button onclick="app.sendAssistantMessage('What were my largest expenses?')" class="bg-white hover:bg-sky-50 text-slate-700 text-xs px-3 py-1.5 rounded-lg border border-slate-200 shadow-sm transition">
                        💎 What were my largest expenses?
                    </button>
                    <button onclick="app.sendAssistantMessage('What are my recurring payments?')" class="bg-white hover:bg-sky-50 text-slate-700 text-xs px-3 py-1.5 rounded-lg border border-slate-200 shadow-sm transition">
                        🔄 What are my recurring payments?
                    </button>
                    <button onclick="app.sendAssistantMessage('Summarize my financial activity.')" class="bg-white hover:bg-sky-50 text-slate-700 text-xs px-3 py-1.5 rounded-lg border border-slate-200 shadow-sm transition">
                        📊 Summarize my financial activity
                    </button>
                </div>

                <!-- Chat Box Area -->
                <div class="flex-1 bg-white rounded-xl border border-slate-200 shadow-sm p-4 overflow-y-auto space-y-4 custom-scrollbar" id="chat-box">
                    <div class="flex gap-3 items-start">
                        <div class="w-8 h-8 rounded-lg bg-sky-600 text-white flex items-center justify-center font-bold text-xs">AI</div>
                        <div class="bg-slate-100 p-3 rounded-xl rounded-tl-none text-xs text-slate-800 max-w-xl">
                            Hello! I am your FinBank AI assistant. Ask me anything about your uploaded bank statement (e.g. food spending, top expenses, savings rate, recurring payments).
                        </div>
                    </div>

                    ${this.chatHistory.map(m => `
                        <div class="flex gap-3 items-start ${m.role === 'user' ? 'justify-end' : ''}">
                            ${m.role === 'assistant' ? '<div class="w-8 h-8 rounded-lg bg-sky-600 text-white flex items-center justify-center font-bold text-xs">AI</div>' : ''}
                            <div class="${m.role === 'user' ? 'bg-sky-600 text-white rounded-tr-none' : 'bg-slate-100 text-slate-800 rounded-tl-none'} p-3 rounded-xl text-xs max-w-xl">
                                ${m.content.replace(/\n/g, '<br>')}
                            </div>
                        </div>
                    `).join('')}
                </div>

                <!-- Input Controls -->
                <form onsubmit="app.handleChatSubmit(event)" class="flex gap-2">
                    <input type="text" id="chat-input" placeholder="Type your financial question..." class="flex-1 text-xs border border-slate-200 rounded-lg p-3 focus:ring-2 focus:ring-sky-500 focus:border-sky-500 shadow-sm">
                    <button type="submit" class="bg-sky-600 hover:bg-sky-700 text-white text-xs font-semibold px-5 rounded-lg transition shadow-sm flex items-center gap-1.5">
                        <i data-lucide="send" class="w-4 h-4"></i> Send
                    </button>
                </form>
            </div>
        `;
    }

    async sendAssistantMessage(msg) {
        const input = document.getElementById('chat-input');
        if (input) input.value = msg;
        this.handleChatSubmit(new Event('submit'));
    }

    async handleChatSubmit(e) {
        if (e) e.preventDefault();
        const input = document.getElementById('chat-input');
        if (!input || !input.value.trim()) return;

        const userMsg = input.value.trim();
        input.value = '';

        this.chatHistory.push({ role: 'user', content: userMsg });
        this.render();

        const box = document.getElementById('chat-box');
        if (box) box.scrollTop = box.scrollHeight;

        try {
            const res = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMsg, history: this.chatHistory })
            });

            if (res.ok) {
                const data = await res.json();
                this.chatHistory.push({ role: 'assistant', content: data.reply });
            } else {
                this.chatHistory.push({ role: 'assistant', content: 'Sorry, I failed to process your question.' });
            }
        } catch (e) {
            this.chatHistory.push({ role: 'assistant', content: 'Network error communicating with AI service.' });
        } finally {
            this.render();
            const box = document.getElementById('chat-box');
            if (box) box.scrollTop = box.scrollHeight;
        }
    }

    renderReportHTML() {
        if (!this.transactions || this.transactions.length === 0) {
            return `
                <div class="max-w-4xl mx-auto space-y-6">
                    <div>
                        <h2 class="text-xl font-bold text-slate-900">Exportable Financial Intelligence Report</h2>
                        <p class="text-xs text-slate-500">Download a clean ReportLab PDF statement analysis for records or review</p>
                    </div>
                    <div class="bg-white p-12 rounded-xl border border-slate-200 shadow-sm text-center">
                        <div class="w-16 h-16 bg-sky-50 text-sky-600 rounded-full flex items-center justify-center mx-auto mb-4">
                            <i data-lucide="file-bar-chart" class="w-8 h-8"></i>
                        </div>
                        <h3 class="text-lg font-bold text-slate-900 mb-1">No Report Available Yet</h3>
                        <p class="text-xs text-slate-500 max-w-md mx-auto mb-6">Upload a bank statement (PDF, CSV, or XLSX) to generate and download exportable PDF financial intelligence reports.</p>
                        <button onclick="app.navigate('documents')" class="bg-sky-600 hover:bg-sky-700 text-white text-xs font-semibold px-5 py-2.5 rounded-lg transition shadow-sm inline-flex items-center gap-2">
                            <i data-lucide="upload" class="w-4 h-4"></i> Upload Bank Statement
                        </button>
                    </div>
                </div>
            `;
        }

        const a = this.analyticsData || {};
        const assess = a.assessment || {};

        return `
            <div class="max-w-4xl mx-auto space-y-6">
                <div class="flex justify-between items-center">
                    <div>
                        <h2 class="text-xl font-bold text-slate-900">Exportable Financial Intelligence Report</h2>
                        <p class="text-xs text-slate-500">Download a clean ReportLab PDF statement analysis for records or review</p>
                    </div>
                    <a href="${API_BASE}/reports/generate" target="_blank" class="bg-sky-600 hover:bg-sky-700 text-white text-xs font-semibold px-5 py-2.5 rounded-lg transition shadow-sm flex items-center gap-2">
                        <i data-lucide="download" class="w-4 h-4"></i> Download PDF Report
                    </a>
                </div>

                <!-- Preview Card -->
                <div class="bg-white rounded-xl border border-slate-200 p-8 shadow-sm space-y-6">
                    <div class="border-b border-slate-100 pb-4 flex justify-between items-start">
                        <div>
                            <h1 class="text-lg font-bold text-slate-900">FinBank AI — Financial Intelligence Summary</h1>
                            <p class="text-xs text-slate-500">Analysis Period: Multi-Month Statement | Mode: Hybrid Rule + Nemotron</p>
                        </div>
                        <span class="px-3 py-1 bg-slate-100 text-slate-700 rounded-lg text-xs font-semibold">PDF Ready</span>
                    </div>

                    <!-- Stability Assessment Box -->
                    <div class="bg-slate-50 p-5 rounded-xl border border-slate-200">
                        <h3 class="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">Financial Stability Assessment</h3>
                        <div class="text-sm font-bold text-slate-900 mb-1">
                            Status: <span class="${assess.rating === 'Good' ? 'text-emerald-600' : 'text-amber-600'}">${assess.rating || 'N/A'}</span>
                        </div>
                        <p class="text-xs text-slate-600 leading-relaxed">${assess.summary_explanation || ''}</p>
                        <p class="text-[11px] text-slate-400 italic mt-3">Notice: AI-assisted financial analysis — not a lending decision.</p>
                    </div>

                    <!-- Summary Grid -->
                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
                        <div class="p-3 bg-slate-50 rounded-lg border border-slate-100">
                            <span class="text-slate-400">Total Income</span>
                            <div class="font-bold text-slate-900 text-sm mt-1">₹${(a.total_income || 0).toLocaleString('en-IN', {minimumFractionDigits:2})}</div>
                        </div>
                        <div class="p-3 bg-slate-50 rounded-lg border border-slate-100">
                            <span class="text-slate-400">Total Expenses</span>
                            <div class="font-bold text-slate-900 text-sm mt-1">₹${(a.total_expenses || 0).toLocaleString('en-IN', {minimumFractionDigits:2})}</div>
                        </div>
                        <div class="p-3 bg-slate-50 rounded-lg border border-slate-100">
                            <span class="text-slate-400">Net Cash Flow</span>
                            <div class="font-bold text-slate-900 text-sm mt-1">₹${(a.net_cash_flow || 0).toLocaleString('en-IN', {minimumFractionDigits:2})}</div>
                        </div>
                        <div class="p-3 bg-slate-50 rounded-lg border border-slate-100">
                            <span class="text-slate-400">Savings Rate</span>
                            <div class="font-bold text-slate-900 text-sm mt-1">${a.savings_rate || 0}%</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
}

const app = new FinBankApp();
