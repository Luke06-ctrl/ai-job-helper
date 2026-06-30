/**
 * 职途星 — 全局前端工具
 */

// 通用 Markdown 渲染（带安全处理）
function renderMarkdown(text) {
    if (typeof marked === 'undefined') return text;
    // marked.js 默认会将文本渲染为 HTML
    return marked.parse(text);
}

// Toast 消息提示
function showToast(message, type) {
    type = type || 'info';
    var toast = document.createElement('div');
    toast.className = 'toast toast-' + type;
    toast.textContent = message;
    toast.style.cssText = [
        'position: fixed',
        'top: 20px',
        'right: 20px',
        'padding: 12px 20px',
        'background: ' + (type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#4f46e5'),
        'color: #fff',
        'border-radius: 8px',
        'font-size: .9rem',
        'z-index: 9999',
        'animation: slideIn .3s ease',
        'box-shadow: 0 4px 12px rgba(0,0,0,.2)',
    ].join(';');
    document.body.appendChild(toast);
    setTimeout(function() {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity .3s';
        setTimeout(function() { toast.remove(); }, 300);
    }, 2500);
}

// 加载动画
function showLoading(el) {
    el.innerHTML = '<div class="spinner"></div><p>加载中...</p>';
    el.style.display = 'flex';
    el.style.flexDirection = 'column';
    el.style.alignItems = 'center';
    el.style.justifyContent = 'center';
}

// 自动调整 textarea 高度
document.addEventListener('DOMContentLoaded', function() {
    var textareas = document.querySelectorAll('textarea');
    textareas.forEach(function(ta) {
        ta.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });
});
