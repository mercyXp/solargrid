document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const toggle = document.getElementById('sidebarToggle');

    if (toggle && sidebar && overlay) {
        toggle.addEventListener('click', function () {
            sidebar.classList.toggle('show');
            overlay.classList.toggle('show');
        });
        overlay.addEventListener('click', function () {
            sidebar.classList.remove('show');
            overlay.classList.remove('show');
        });
    }

    document.querySelectorAll('[data-confirm]').forEach(function (el) {
        el.addEventListener('click', function (e) {
            if (!confirm(el.getAttribute('data-confirm'))) {
                e.preventDefault();
            }
        });
    });

    setTimeout(function () {
        document.querySelectorAll('.alert-auto-dismiss').forEach(function (alert) {
            alert.classList.add('fade');
            setTimeout(function () { alert.remove(); }, 300);
        });
    }, 5000);
});

function statusBadgeClass(status) {
    const map = {
        Completed: 'bg-success-custom',
        Paid: 'bg-success-custom',
        Resolved: 'bg-success-custom',
        Active: 'bg-success-custom',
        Cancelled: 'bg-danger-custom',
        Critical: 'bg-danger-custom',
        Overdue: 'bg-danger-custom',
        Faulty: 'bg-danger-custom',
        'In Progress': 'bg-info-custom',
        Open: 'bg-warning-custom',
        Scheduled: 'bg-warning-custom',
        Draft: 'bg-secondary',
    };
    return map[status] || 'bg-secondary';
}
