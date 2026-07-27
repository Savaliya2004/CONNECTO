/**
 * CONNECTO Admin Dashboard — Chart.js Integration
 * Interactive analytics charts with dynamic data loading
 */

'use strict';

// ─── Chart Defaults ───────────────────────────────────────────────────────────
const CHART_COLORS = {
  accent: '#4a6a4a',
  accentHover: '#8aa88a',
  success: '#10B981',
  warning: '#F59E0B',
  danger: '#EF4444',
  blue: '#3B82F6',
  pink: '#EC4899',
  teal: '#14B8A6',
};

function applyChartDefaults() {
  if (typeof Chart === 'undefined') return;
  Chart.defaults.color = '#6a7a6a';
  Chart.defaults.borderColor = 'rgba(30,40,30,0.5)';
  Chart.defaults.font.family = "'Inter', sans-serif";
  Chart.defaults.font.size = 12;
  Chart.defaults.plugins.legend.labels.boxWidth = 12;
  Chart.defaults.plugins.legend.labels.padding = 16;
  Chart.defaults.plugins.tooltip.backgroundColor = '#1E293B';
  Chart.defaults.plugins.tooltip.borderColor = '#2D3748';
  Chart.defaults.plugins.tooltip.borderWidth = 1;
  Chart.defaults.plugins.tooltip.titleColor = '#E2E8F0';
  Chart.defaults.plugins.tooltip.bodyColor = '#94A3B8';
  Chart.defaults.plugins.tooltip.padding = 12;
  Chart.defaults.plugins.tooltip.cornerRadius = 8;
}

function makeGradient(ctx, color, alpha1 = 0.3, alpha2 = 0) {
  const gradient = ctx.createLinearGradient(0, 0, 0, 300);
  gradient.addColorStop(0, color.replace(')', `, ${alpha1})`).replace('rgb', 'rgba'));
  gradient.addColorStop(1, color.replace(')', `, ${alpha2})`).replace('rgb', 'rgba'));
  return gradient;
}

function hexToRgb(hex) {
  const r = parseInt(hex.slice(1,3), 16);
  const g = parseInt(hex.slice(3,5), 16);
  const b = parseInt(hex.slice(5,7), 16);
  return `${r}, ${g}, ${b}`;
}

// ─── Chart Instances Registry ─────────────────────────────────────────────────
const charts = {};

function destroyChart(id) {
  if (charts[id]) {
    charts[id].destroy();
    delete charts[id];
  }
}

// ─── Main Growth Chart ─────────────────────────────────────────────────────────
function initGrowthChart(labels, usersData, postsData) {
  const canvas = document.getElementById('growth-chart');
  if (!canvas || typeof Chart === 'undefined') return;

  destroyChart('growth');
  const ctx = canvas.getContext('2d');

  const userGrad = ctx.createLinearGradient(0, 0, 0, 280);
  userGrad.addColorStop(0, `rgba(${hexToRgb(CHART_COLORS.accent)}, 0.25)`);
  userGrad.addColorStop(1, `rgba(${hexToRgb(CHART_COLORS.accent)}, 0)`);

  const postGrad = ctx.createLinearGradient(0, 0, 0, 280);
  postGrad.addColorStop(0, `rgba(${hexToRgb(CHART_COLORS.success)}, 0.2)`);
  postGrad.addColorStop(1, `rgba(${hexToRgb(CHART_COLORS.success)}, 0)`);

  charts['growth'] = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'New Users',
          data: usersData,
          borderColor: CHART_COLORS.accent,
          backgroundColor: userGrad,
          borderWidth: 2.5,
          pointRadius: 4,
          pointHoverRadius: 6,
          pointBackgroundColor: CHART_COLORS.accent,
          fill: true,
          tension: 0.4,
        },
        {
          label: 'New Posts',
          data: postsData,
          borderColor: CHART_COLORS.success,
          backgroundColor: postGrad,
          borderWidth: 2.5,
          pointRadius: 4,
          pointHoverRadius: 6,
          pointBackgroundColor: CHART_COLORS.success,
          fill: true,
          tension: 0.4,
        },
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: { legend: { position: 'top' } },
      scales: {
        x: { grid: { color: 'rgba(45,55,72,0.5)' } },
        y: { grid: { color: 'rgba(45,55,72,0.5)' }, beginAtZero: true }
      }
    }
  });
}

// ─── Engagement Chart ──────────────────────────────────────────────────────────
function initEngagementChart(labels, likesData, commentsData) {
  const canvas = document.getElementById('engagement-chart');
  if (!canvas || typeof Chart === 'undefined') return;

  destroyChart('engagement');
  const ctx = canvas.getContext('2d');

  charts['engagement'] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Likes',
          data: likesData,
          backgroundColor: `rgba(${hexToRgb(CHART_COLORS.warning)}, 0.8)`,
          borderRadius: 6,
          borderSkipped: false,
        },
        {
          label: 'Comments',
          data: commentsData,
          backgroundColor: `rgba(${hexToRgb(CHART_COLORS.blue)}, 0.8)`,
          borderRadius: 6,
          borderSkipped: false,
        },
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: { legend: { position: 'top' } },
      scales: {
        x: { grid: { display: false } },
        y: { grid: { color: 'rgba(45,55,72,0.5)' }, beginAtZero: true }
      }
    }
  });
}

// ─── Content Distribution Chart ────────────────────────────────────────────────
function initContentChart(postsCount, storiesCount, reelsCount) {
  const canvas = document.getElementById('content-chart');
  if (!canvas || typeof Chart === 'undefined') return;

  destroyChart('content');
  const ctx = canvas.getContext('2d');

  charts['content'] = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Posts', 'Stories', 'Reels'],
      datasets: [{
        data: [postsCount, storiesCount, reelsCount],
        backgroundColor: [
          CHART_COLORS.accent,
          CHART_COLORS.success,
          CHART_COLORS.pink,
        ],
        borderColor: '#1E293B',
        borderWidth: 3,
        hoverOffset: 8,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '68%',
      plugins: {
        legend: { position: 'bottom' },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.label}: ${ctx.raw.toLocaleString()}`
          }
        }
      }
    }
  });
}

// ─── User Activity Chart ───────────────────────────────────────────────────────
function initActivityChart(labels, data) {
  const canvas = document.getElementById('activity-chart');
  if (!canvas || typeof Chart === 'undefined') return;

  destroyChart('activity');
  const ctx = canvas.getContext('2d');

  const gradient = ctx.createLinearGradient(0, 0, 0, 250);
  gradient.addColorStop(0, `rgba(${hexToRgb(CHART_COLORS.accentHover)}, 0.3)`);
  gradient.addColorStop(1, `rgba(${hexToRgb(CHART_COLORS.accentHover)}, 0)`);

  charts['activity'] = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Active Users',
        data,
        borderColor: CHART_COLORS.accentHover,
        backgroundColor: gradient,
        borderWidth: 2.5,
        pointRadius: 3,
        pointHoverRadius: 6,
        fill: true,
        tension: 0.4,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: 'rgba(45,55,72,0.5)' } },
        y: { grid: { color: 'rgba(45,55,72,0.5)' }, beginAtZero: true }
      }
    }
  });
}

// ─── Dynamic Chart Data Loading ────────────────────────────────────────────────
let currentPeriod = 'weekly';

async function loadChartData(period) {
  currentPeriod = period;
  const url = `/control/api/analytics/?period=${period}`;

  // Update tab UI
  document.querySelectorAll('.chart-tab').forEach(t => {
    t.classList.toggle('active', t.dataset.period === period);
  });

  try {
    const resp = await fetch(url, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });
    if (!resp.ok) throw new Error('Network error');
    const data = await resp.json();

    const { labels, datasets } = data;
    initGrowthChart(labels, datasets.users, datasets.posts);
    initEngagementChart(labels, datasets.likes, datasets.comments);
    initActivityChart(labels, datasets.users);

  } catch (err) {
    console.warn('Chart data load error:', err);
  }
}

// ─── Mini Sparkline ───────────────────────────────────────────────────────────
function initSparkline(canvasId, data, color = CHART_COLORS.accent) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || typeof Chart === 'undefined') return;

  new Chart(canvas.getContext('2d'), {
    type: 'line',
    data: {
      labels: data.map((_, i) => i),
      datasets: [{
        data,
        borderColor: color,
        borderWidth: 2,
        pointRadius: 0,
        fill: false,
        tension: 0.4,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
      scales: { x: { display: false }, y: { display: false } },
      animation: { duration: 600 }
    }
  });
}

// ─── Init All Charts ──────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  if (typeof Chart === 'undefined') return;

  applyChartDefaults();

  // Init period tab buttons
  document.querySelectorAll('.chart-tab').forEach(btn => {
    btn.addEventListener('click', () => loadChartData(btn.dataset.period || 'weekly'));
  });

  // Load initial chart data if chart containers are present
  if (document.getElementById('growth-chart') || document.getElementById('engagement-chart')) {
    loadChartData('weekly');
  }

  // Content distribution from data attributes
  const contentCanvas = document.getElementById('content-chart');
  if (contentCanvas) {
    initContentChart(
      parseInt(contentCanvas.dataset.posts || 0),
      parseInt(contentCanvas.dataset.stories || 0),
      parseInt(contentCanvas.dataset.reels || 0),
    );
  }
});

// Expose
window.loadChartData = loadChartData;
window.initSparkline = initSparkline;
