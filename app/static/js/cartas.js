// =========================
// CARGAR CARTAS
// =========================
async function cargarCartas() {
    const tbody = document.getElementById("cartas-tbody");
    tbody.innerHTML = `<tr><td colspan="6">Cargando cartas...</td></tr>`;

    try {
        const res = await fetch("/productos");
        if (!res.ok) throw new Error("Error al obtener cartas");

        const cartas = await res.json();

        if (cartas.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6">No hay cartas registradas.</td></tr>`;
            return;
        }

        tbody.innerHTML = "";

        cartas.forEach(carta => {
            const tr = document.createElement("tr");

            tr.innerHTML = `
                <td>${carta.Nombre}</td>
                <td>${carta.Descripcion}</td>
                <td>${carta.Precio}</td>
                <td>${carta.Stock}</td>
                <td>${carta.Activo ? "Sí" : "No"}</td>
                <td>
                    <button class="btn btn-warning btn-sm"
                        onclick="editarCarta(${carta.IdProducto})"
                        data-bs-toggle="modal" data-bs-target="#modalCarta">
                        Editar
                    </button>

                    <button class="btn btn-info btn-sm"
                        onclick="verCarta(${carta.IdProducto})"
                        data-bs-toggle="modal" data-bs-target="#modalCarta">
                        Ver
                    </button>

                    <button class="btn btn-danger btn-sm"
                        onclick="setCartaEliminar(${carta.IdProducto}, '${carta.Nombre}')"
                        data-bs-toggle="modal" data-bs-target="#modalEliminar">
                        Eliminar
                    </button>
                </td>
            `;

            tbody.appendChild(tr);
        });

    } catch (err) {
        console.error(err);
        tbody.innerHTML = `<tr><td colspan="6">Error al cargar cartas</td></tr>`;
    }
}

// =========================
// NUEVA CARTA
// =========================
function nuevaCarta() {
    document.getElementById("modalTitulo").textContent = "Nueva Carta";
    document.getElementById("formCarta").reset();
    document.getElementById("IdProducto").value = "";

    document.querySelectorAll("#formCarta input, #formCarta textarea, #formCarta select")
        .forEach(el => el.disabled = false);
}


// =========================
// EDITAR CARTA
// =========================
async function editarCarta(id) {
    const res = await fetch(`/productos/${id}`);
    const carta = await res.json();

    document.getElementById("modalTitulo").textContent = "Editar Carta";

    document.getElementById("IdProducto").value = carta.IdProducto;
    document.getElementById("nombre").value = carta.Nombre;
    document.getElementById("descripcion").value = carta.Descripcion;
    document.getElementById("precio").value = carta.Precio;
    document.getElementById("stock").value = carta.Stock;
    document.getElementById("activo").value = carta.Activo ? "true" : "false";

    document.querySelectorAll("#formCarta input, #formCarta textarea, #formCarta select")
        .forEach(el => el.disabled = false);
}


// =========================
// VER CARTA
// =========================
async function verCarta(id) {
    const res = await fetch(`/productos/${id}`);
    const carta = await res.json();

    document.getElementById("modalTitulo").textContent = "Detalles de la Carta";

    document.getElementById("IdProducto").value = carta.IdProducto;
    document.getElementById("nombre").value = carta.Nombre;
    document.getElementById("descripcion").value = carta.Descripcion;
    document.getElementById("precio").value = carta.Precio;
    document.getElementById("stock").value = carta.Stock;
    document.getElementById("activo").value = carta.Activo ? "true" : "false";

    document.querySelectorAll("#formCarta input, #formCarta textarea, #formCarta select")
        .forEach(el => el.disabled = true);
}


// =========================
// ELIMINAR
// =========================
let cartaEliminarId = null;

function setCartaEliminar(id, nombre) {
    cartaEliminarId = id;
    document.getElementById("nombreCartaEliminar").textContent = nombre;
}

async function confirmarEliminar() {
    

    try {
        const response = await fetch(`/productos/${cartaEliminarId}`, { method: "DELETE" });
        if (!response.ok) throw new Error("Error al eliminar la carta");
    
        bootstrap.Modal.getInstance(document.getElementById("modalEliminar")).hide();
        cargarCartas();
      } catch (err) {
        console.error(err);
        alert("Hubo un error al eliminar la carta.");
      }
}


// =========================
// GUARDAR CARTA
// =========================
document.getElementById("formCarta").addEventListener("submit", async (e) => {
    e.preventDefault();

    const id = document.getElementById("IdProducto").value;
    const data = {
        Nombre: document.getElementById("nombre").value,
        Descripcion: document.getElementById("descripcion").value,
        Precio: document.getElementById("precio").value,
        Stock: document.getElementById("stock").value,
        Activo: document.getElementById("activo").value === "true"
    };

    const url = id ? `/productos/${id}` : "/productos";
    const method = id ? "PUT" : "POST";

    const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    if (!res.ok) {
        alert("Error al guardar carta");
        return;
    }

    bootstrap.Modal.getInstance(document.getElementById("modalCarta")).hide();
    cargarCartas();
});

// =========================
// INICIO
// =========================
document.addEventListener("DOMContentLoaded", cargarCartas);
