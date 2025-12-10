document.addEventListener("DOMContentLoaded", () => {
    const menuBtn = document.getElementById("menuBtn");
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebarOverlay");

    // Hacer que el sidebar sea focusable
    sidebar.setAttribute("tabindex", "-1");

    // Función para abrir el sidebar y hacer focus
    const abrirSidebar = () => {
        sidebar.classList.add("show");
        overlay.classList.add("show");
        // Hacer focus en el sidebar después de la animación
        setTimeout(() => {
            sidebar.focus();
        }, 100);
    };

    // Función para cerrar el sidebar
    const cerrarSidebar = () => {
        sidebar.classList.remove("show");
        overlay.classList.remove("show");
        sidebar.blur();
    };

    // Abrir/cerrar sidebar con el botón del menú
    menuBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        if (sidebar.classList.contains("show")) {
            cerrarSidebar();
        } else {
            abrirSidebar();
        }
    });

    // Cerrar sidebar al hacer click en el overlay
    overlay.addEventListener("click", () => {
        cerrarSidebar();
    });

    // Cerrar sidebar al hacer click fuera de él
    document.addEventListener("click", (e) => {
        // Si el sidebar está abierto
        if (sidebar.classList.contains("show")) {
            // Si el click NO fue dentro del sidebar ni en el botón del menú
            if (!sidebar.contains(e.target) && !menuBtn.contains(e.target)) {
                cerrarSidebar();
            }
        }
    });

    // Evitar que el click dentro del sidebar cierre el menú
    sidebar.addEventListener("click", (e) => {
        e.stopPropagation();
    });
});