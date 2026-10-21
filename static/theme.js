const themeButtons = document.querySelectorAll("[data-theme-toggle]");

function applyTheme(theme) {
    const isDark = theme === "dark";
    document.documentElement.dataset.theme = isDark ? "dark" : "light";

    themeButtons.forEach((button) => {
        const label = isDark ? "Cambiar a modo claro" : "Cambiar a modo oscuro";
        button.setAttribute("aria-label", label);
        button.setAttribute("aria-pressed", String(isDark));
        button.title = label;
        button.textContent = button.dataset.lightText
            ? (isDark ? button.dataset.darkText : button.dataset.lightText)
            : (isDark ? "Modo claro" : "Modo oscuro");
    });
}

applyTheme(localStorage.getItem("atlas-theme") || "light");

themeButtons.forEach((button) => {
    button.addEventListener("click", () => {
        const nextTheme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
        localStorage.setItem("atlas-theme", nextTheme);
        applyTheme(nextTheme);
    });
});