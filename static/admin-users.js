function filterAdminUsers() {
    const roleFilter = document.querySelector('[data-user-filter="role"]');
    const groupFilter = document.querySelector('[data-user-filter="group"]');
    const rows = document.querySelectorAll("#usuarios-area [data-user-role]");
    const emptyMessage = document.getElementById("usuarios-filtro-vacio");
    let visibleCount = 0;

    rows.forEach((row) => {
        const matchesRole = !roleFilter.value || row.dataset.userRole === roleFilter.value;
        const matchesGroup = !groupFilter.value || row.dataset.userGroup === groupFilter.value;
        row.hidden = !(matchesRole && matchesGroup);
        if (!row.hidden) visibleCount += 1;
    });

    emptyMessage.hidden = visibleCount > 0 || rows.length === 0;
}

document.addEventListener("change", (event) => {
    if (event.target.matches("[data-user-filter]")) filterAdminUsers();
});