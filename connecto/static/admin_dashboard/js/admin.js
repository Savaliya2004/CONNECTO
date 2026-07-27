/**
 * CONNECTO Admin Dashboard — JavaScript
 * Handles: Sidebar toggle, Dark/Light mode, Toast system,
 *          Action dropdowns, Modals, Confirm dialogs, AJAX helpers
 */

'use strict';

// ─── Theme ────────────────────────────────────────────────────────────────────
const ThemeManager = {
  init() {
    const saved = localStorage.getItem('admin_theme') || 'dark';
    this.apply(saved);
  },
  apply(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('admin_theme', theme);
    const btn = document.getElementById('theme-toggle');
    if (btn) {
      btn.textContent = theme === 'dark' ? '☀️' : '🌙';
      btn.title = theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode';
    }
  },
  toggle() {
    const current = localStorage.getItem('admin_theme') || 'dark';
    this.apply(current === 'dark' ? 'light' : 'dark');
  }
};

// ─── Sidebar ──────────────────────────────────────────────────────────────────
const Sidebar = {
  init() {
    this.sidebar = document.getElementById('sidebar');
    this.mainContent = document.getElementById('main-content');
    this.toggleBtn = document.getElementById('sidebar-toggle');

    if (!this.sidebar) return;

    // Restore collapsed state
    if (localStorage.getItem('sidebar_collapsed') === 'true') {
      this.collapse();
    }

    if (this.toggleBtn) {
      this.toggleBtn.addEventListener('click', () => this.toggle());
    }

    // Mobile overlay
    const overlay = document.getElementById('sidebar-overlay');
    if (overlay) {
      overlay.addEventListener('click', () => this.closeMobile());
    }

    // Window resize
    window.addEventListener('resize', () => {
      if (window.innerWidth > 768) {
        this.closeMobile();
      }
    });
  },
  toggle() {
    if (window.innerWidth <= 768) {
      this.toggleMobile();
    } else {
      this.sidebar.classList.toggle('collapsed');
      this.mainContent?.classList.toggle('sidebar-collapsed');
      localStorage.setItem('sidebar_collapsed', this.sidebar.classList.contains('collapsed'));
    }
  },
  collapse() {
    this.sidebar?.classList.add('collapsed');
    this.mainContent?.classList.add('sidebar-collapsed');
  },
  expand() {
    this.sidebar?.classList.remove('collapsed');
    this.mainContent?.classList.remove('sidebar-collapsed');
  },
  toggleMobile() {
    this.sidebar?.classList.toggle('mobile-open');
    document.getElementById('sidebar-overlay')?.classList.toggle('active');
  },
  closeMobile() {
    this.sidebar?.classList.remove('mobile-open');
    document.getElementById('sidebar-overlay')?.classList.remove('active');
  }
};

// ─── Toast Notifications ──────────────────────────────────────────────────────
const Toast = {
  container: null,
  init() {
    this.container = document.querySelector('.toast-container');
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.className = 'toast-container';
      document.body.appendChild(this.container);
    }
  },
  show(msg, type = 'info', title = null, duration = 4000) {
    const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
    const titles = { success: 'Success', error: 'Error', warning: 'Warning', info: 'Info' };

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <span class="toast-icon">${icons[type] || icons.info}</span>
      <div class="toast-content">
        <div class="toast-title">${title || titles[type]}</div>
        <div class="toast-msg">${msg}</div>
      </div>
      <button class="toast-close" onclick="this.closest('.toast').remove()">×</button>
    `;
    this.container.appendChild(toast);

    if (duration > 0) {
      setTimeout(() => {
        toast.classList.add('removing');
        setTimeout(() => toast.remove(), 300);
      }, duration);
    }
    return toast;
  },
  success(msg, title) { return this.show(msg, 'success', title); },
  error(msg, title) { return this.show(msg, 'error', title); },
  warning(msg, title) { return this.show(msg, 'warning', title); },
  info(msg, title) { return this.show(msg, 'info', title); },
};

// ─── Modals ───────────────────────────────────────────────────────────────────
const Modal = {
  open(id) {
    const modal = document.getElementById(id);
    if (modal) {
      modal.classList.add('open');
      document.body.style.overflow = 'hidden';
    }
  },
  close(id) {
    const modal = document.getElementById(id);
    if (modal) {
      modal.classList.remove('open');
      document.body.style.overflow = '';
    }
  },
  init() {
    // Close modal on overlay click
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
          overlay.classList.remove('open');
          document.body.style.overflow = '';
        }
      });
    });

    // Escape key closes modal
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        document.querySelectorAll('.modal-overlay.open').forEach(m => {
          m.classList.remove('open');
          document.body.style.overflow = '';
        });
      }
    });
  }
};

// ─── Action Dropdowns ─────────────────────────────────────────────────────────
const Dropdown = {
  init() {
    document.addEventListener('click', (e) => {
      const toggle = e.target.closest('[data-dropdown-toggle]');
      if (toggle) {
        e.stopPropagation();
        const menu = toggle.closest('.action-menu');
        const isOpen = menu.classList.contains('open');
        // Close all
        document.querySelectorAll('.action-menu.open').forEach(m => m.classList.remove('open'));
        if (!isOpen) menu.classList.add('open');
        return;
      }
      // Click outside closes all
      document.querySelectorAll('.action-menu.open').forEach(m => m.classList.remove('open'));
    });
  }
};

// ─── Confirm Dialog ───────────────────────────────────────────────────────────
const Confirm = {
  show(message, onConfirm, title = 'Confirm Action') {
    const existing = document.getElementById('confirm-modal');
    if (existing) existing.remove();

    const modal = document.createElement('div');
    modal.id = 'confirm-modal';
    modal.className = 'modal-overlay open';
    modal.innerHTML = `
      <div class="modal" style="max-width: 440px;">
        <div class="modal-header">
          <span class="modal-title">⚠️ ${title}</span>
          <button class="modal-close" onclick="document.getElementById('confirm-modal').remove()">×</button>
        </div>
        <div class="modal-body">
          <p style="color: var(--text); font-size: 14px; line-height: 1.6;">${message}</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" onclick="document.getElementById('confirm-modal').remove()">Cancel</button>
          <button class="btn btn-danger" id="confirm-ok">Confirm</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
    document.getElementById('confirm-ok').addEventListener('click', () => {
      modal.remove();
      onConfirm();
    });
  }
};

// ─── Bulk Actions ─────────────────────────────────────────────────────────────
const BulkActions = {
  init() {
    const selectAll = document.getElementById('select-all');
    if (!selectAll) return;

    selectAll.addEventListener('change', () => {
      document.querySelectorAll('.row-checkbox').forEach(cb => {
        cb.checked = selectAll.checked;
      });
      this.updateBulkBar();
    });

    document.querySelectorAll('.row-checkbox').forEach(cb => {
      cb.addEventListener('change', () => this.updateBulkBar());
    });
  },
  updateBulkBar() {
    const checked = document.querySelectorAll('.row-checkbox:checked');
    const bar = document.getElementById('bulk-action-bar');
    const count = document.getElementById('bulk-count');
    if (bar) bar.style.display = checked.length > 0 ? 'flex' : 'none';
    if (count) count.textContent = checked.length;
  },
  getSelected() {
    return Array.from(document.querySelectorAll('.row-checkbox:checked')).map(cb => cb.value);
  }
};

// ─── Table Sort ───────────────────────────────────────────────────────────────
const TableSort = {
  init() {
    document.querySelectorAll('th.sortable').forEach(th => {
      th.addEventListener('click', () => {
        const field = th.dataset.sort;
        const url = new URL(window.location.href);
        const current = url.searchParams.get('sort');
        url.searchParams.set('sort', current === field ? `-${field}` : field);
        window.location.href = url.toString();
      });
    });
  }
};

// ─── Loading Skeleton ─────────────────────────────────────────────────────────
const Skeleton = {
  show(containerId) {
    const el = document.getElementById(containerId);
    if (!el) return;
    el.innerHTML = `
      <div class="skeleton skeleton-card mb-4"></div>
      <div class="skeleton skeleton-line"></div>
      <div class="skeleton skeleton-line short"></div>
      <div class="skeleton skeleton-line xshort"></div>
    `;
  }
};

// ─── Search Debounce ──────────────────────────────────────────────────────────
function debounce(fn, delay) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

const initLiveSearch = () => {
  const input = document.getElementById('live-search-input');
  if (!input) return;

  const handler = debounce(() => {
    const form = input.closest('form');
    if (form) form.submit();
  }, 500);

  input.addEventListener('input', handler);
};

// ─── CSRF Helper ──────────────────────────────────────────────────────────────
function getCsrfToken() {
  return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
    document.cookie.split('; ').find(r => r.startsWith('csrftoken='))?.split('=')[1] || '';
}

// ─── Action Form Submit Helper ─────────────────────────────────────────────────
function submitActionForm(formId) {
  const form = document.getElementById(formId);
  if (form) form.submit();
}

function confirmDelete(message, formId) {
  Confirm.show(message, () => submitActionForm(formId), 'Delete Confirmation');
}

function confirmAction(message, formId) {
  Confirm.show(message, () => submitActionForm(formId));
}

// ─── Date Formatter ───────────────────────────────────────────────────────────
function timeAgo(dateStr) {
  const date = new Date(dateStr);
  const now = new Date();
  const diff = Math.floor((now - date) / 1000);

  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
  return date.toLocaleDateString();
}

// ─── Tab System ───────────────────────────────────────────────────────────────
const Tabs = {
  init() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const group = btn.closest('.tabs-wrapper');
        const target = btn.dataset.tab;

        group?.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        group?.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

        btn.classList.add('active');
        document.getElementById(`tab-${target}`)?.classList.add('active');
      });
    });
  }
};

// ─── Init ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  ThemeManager.init();
  Sidebar.init();
  Toast.init();
  Modal.init();
  Dropdown.init();
  BulkActions.init();
  TableSort.init();
  Tabs.init();
  initLiveSearch();

  // Theme toggle button
  const themeBtn = document.getElementById('theme-toggle');
  if (themeBtn) themeBtn.addEventListener('click', () => ThemeManager.toggle());

  // Auto-dismiss Django messages as toasts
  document.querySelectorAll('[data-toast]').forEach(el => {
    const type = el.dataset.toast;
    const msg = el.dataset.message;
    if (msg) Toast.show(msg, type);
    el.remove();
  });

  // Confirm delete buttons
  document.querySelectorAll('[data-confirm]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const msg = btn.dataset.confirm;
      const href = btn.href || btn.dataset.href;
      const formId = btn.dataset.form;

      if (formId) {
        Confirm.show(msg, () => submitActionForm(formId));
      } else if (href) {
        Confirm.show(msg, () => window.location.href = href);
      }
    });
  });

  // Auto-close alerts after 5s
  document.querySelectorAll('.alert-auto-close').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity 0.4s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 400);
    }, 5000);
  });
});

// Expose to window for inline use
window.Modal = Modal;
window.Toast = Toast;
window.Confirm = Confirm;
window.ThemeManager = ThemeManager;
window.confirmDelete = confirmDelete;
window.confirmAction = confirmAction;
