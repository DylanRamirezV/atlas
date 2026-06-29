(function () {
  var toggle = document.getElementById("sidebar-toggle");
  var sidebar = document.getElementById("sidebar");
  var backdrop = document.getElementById("sidebar-backdrop");
  var body = document.body;
  var desktopMin = 901;

  function openSidebar() {
    body.classList.add("sidebar-open");
    if (sidebar) {
      sidebar.setAttribute("aria-hidden", "false");
    }
    if (backdrop) {
      backdrop.setAttribute("aria-hidden", "false");
    }
  }

  function closeSidebar() {
    body.classList.remove("sidebar-open");
    if (sidebar) {
      sidebar.setAttribute("aria-hidden", "true");
    }
    if (backdrop) {
      backdrop.setAttribute("aria-hidden", "true");
    }
  }

  function setInitialState() {
    if (window.innerWidth >= desktopMin) {
      openSidebar();
    } else {
      closeSidebar();
    }
  }

  if (toggle) {
    toggle.addEventListener("click", function () {
      if (body.classList.contains("sidebar-open")) {
        closeSidebar();
      } else {
        openSidebar();
      }
    });
  }

  if (backdrop) {
    backdrop.addEventListener("click", closeSidebar);
  }

  window.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      closeSidebar();
    }
  });

  var sidebarLinks = sidebar ? sidebar.querySelectorAll("a") : [];
  sidebarLinks.forEach(function (link) {
    link.addEventListener("click", function () {
      if (window.innerWidth < desktopMin) {
        closeSidebar();
      }
    });
  });

  var screens = document.querySelectorAll(".screen[data-section]");

  function showSelectedScreen() {
    if (!screens.length) {
      return;
    }

    var selectedId = window.location.hash.replace("#", "") || "institucional";
    var selectedScreen = document.getElementById(selectedId);

    if (!selectedScreen || !selectedScreen.matches(".screen[data-section]")) {
      selectedId = "institucional";
    }

    screens.forEach(function (screen) {
      screen.style.display = screen.id === selectedId ? "block" : "none";
    });
  }

  window.addEventListener("resize", setInitialState);
  window.addEventListener("hashchange", showSelectedScreen);
  setInitialState();
  showSelectedScreen();
})();
