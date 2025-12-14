// =========================
// CARGAR CARTAS
// =========================
async function cargarCartas() {
    const tbody = document.getElementById("cartas-tbody");
    tbody.innerHTML = `<tr><td colspan="7">Cargando cartas...</td></tr>`;

    try {
        const res = await fetch("/productos");
        if (!res.ok) throw new Error("Error al obtener cartas");

        const cartas = await res.json();

        if (cartas.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7">No hay cartas registradas.</td></tr>`;
            return;
        }

        tbody.innerHTML = "";

        cartas.forEach(carta => {
            const tr = document.createElement("tr");
            const imagenHtml = carta.Imagen 
                ? `<img src="/static/img/cartas/${carta.Imagen}" alt="${carta.Nombre}" style="width: 50px; height: 70px; object-fit: cover; border-radius: 4px;">`
                : `<span style="color: #666;">Sin imagen</span>`;

            tr.innerHTML = `
                <td>${imagenHtml}</td>
                <td>${carta.Nombre}</td>
                <td>${carta.Descripcion || ''}</td>
                <td>₡${carta.Precio}</td>
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

                    <button class="btn btn-danger btn-sm btn-eliminar-carta"
                        data-id="${carta.IdProducto}"
                        data-nombre="${String(carta.Nombre).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;')}"
                        data-bs-toggle="modal" data-bs-target="#modalEliminar">
                        Eliminar
                    </button>
                </td>
            `;

            tbody.appendChild(tr);
        });

    } catch (err) {
        console.error(err);
        tbody.innerHTML = `<tr><td colspan="7">Error al cargar cartas</td></tr>`;
    }
}

// =========================
// VISTA PREVIA DE IMAGEN
// =========================
document.addEventListener("DOMContentLoaded", function() {
    const imagenInput = document.getElementById("imagen");
    const imagenPreview = document.getElementById("imagen-preview");
    
    if (imagenInput) {
        imagenInput.addEventListener("change", function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagenPreview.src = e.target.result;
                    imagenPreview.style.display = "block";
                };
                reader.readAsDataURL(file);
            } else {
                imagenPreview.src = "";
                imagenPreview.style.display = "none";
            }
        });
    }
});

// Variable para guardar la imagen actual
let imagenActual = null;

// =========================
// NUEVA CARTA
// =========================
function nuevaCarta() {
    document.getElementById("modalTitulo").textContent = "Nueva Carta";
    document.getElementById("formCarta").reset();
    document.getElementById("IdProducto").value = "";
    imagenActual = null;
    
    // Limpiar vista previa
    const imagenPreview = document.getElementById("imagen-preview");
    imagenPreview.src = "";
    imagenPreview.style.display = "none";

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
    document.getElementById("descripcion").value = carta.Descripcion || '';
    document.getElementById("precio").value = carta.Precio;
    document.getElementById("stock").value = carta.Stock;
    document.getElementById("activo").value = carta.Activo ? "true" : "false";
    
    // Mostrar imagen actual si existe
    const imagenPreview = document.getElementById("imagen-preview");
    if (carta.Imagen) {
        imagenPreview.src = `/static/img/cartas/${carta.Imagen}`;
        imagenPreview.style.display = "block";
        imagenActual = carta.Imagen;
    } else {
        imagenPreview.src = "";
        imagenPreview.style.display = "none";
        imagenActual = null;
    }
    
    // Limpiar input de imagen
    document.getElementById("imagen").value = "";

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
    document.getElementById("descripcion").value = carta.Descripcion || '';
    document.getElementById("precio").value = carta.Precio;
    document.getElementById("stock").value = carta.Stock;
    document.getElementById("activo").value = carta.Activo ? "true" : "false";
    
    // Mostrar imagen si existe
    const imagenPreview = document.getElementById("imagen-preview");
    if (carta.Imagen) {
        imagenPreview.src = `/static/img/cartas/${carta.Imagen}`;
        imagenPreview.style.display = "block";
    } else {
        imagenPreview.src = "";
        imagenPreview.style.display = "none";
    }

    document.querySelectorAll("#formCarta input, #formCarta textarea, #formCarta select")
        .forEach(el => el.disabled = true);
}


// =========================
// ELIMINAR
// =========================
let cartaEliminarId = null;

// Event listener para los botones de eliminar (delegación de eventos)
document.addEventListener('click', function(e) {
    const button = e.target.closest('.btn-eliminar-carta');
    if (button) {
        const id = button.getAttribute('data-id');
        const nombre = button.getAttribute('data-nombre');
        if (id && nombre) {
            setCartaEliminar(id, nombre);
        }
    }
});

function setCartaEliminar(id, nombre) {
    cartaEliminarId = parseInt(id); // Asegurar que sea un número
    if (isNaN(cartaEliminarId)) {
        console.error("Error: ID de carta inválido:", id);
        alert("Error: ID de carta inválido");
        return;
    }
    // El navegador decodifica automáticamente los atributos HTML
    document.getElementById("nombreCartaEliminar").textContent = nombre;
    console.log("Carta seleccionada para eliminar - ID:", cartaEliminarId, "Nombre:", nombre);
}

async function confirmarEliminar() {
    if (!cartaEliminarId) {
        alert("Error: No se ha seleccionado una carta para eliminar.");
        return;
    }

    try {
        const response = await fetch(`/productos/${cartaEliminarId}`, { method: "DELETE" });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || "Error al eliminar la carta");
        }
    
        const result = await response.json();
        bootstrap.Modal.getInstance(document.getElementById("modalEliminar")).hide();
        cartaEliminarId = null; // Limpiar el ID después de eliminar
        cargarCartas();
        alert("Carta eliminada correctamente.");
    } catch (err) {
        console.error("Error al eliminar carta:", err);
        alert(err.message || "Hubo un error al eliminar la carta.");
    }
}


// =========================
// GUARDAR CARTA
// =========================
document.getElementById("formCarta").addEventListener("submit", async (e) => {
    e.preventDefault();

    const id = document.getElementById("IdProducto").value;
    const imagenFile = document.getElementById("imagen").files[0];
    
    // Usar FormData para enviar datos incluyendo la imagen
    const formData = new FormData();
    formData.append("Nombre", document.getElementById("nombre").value);
    formData.append("Descripcion", document.getElementById("descripcion").value);
    formData.append("Precio", document.getElementById("precio").value);
    formData.append("Stock", document.getElementById("stock").value);
    formData.append("Activo", document.getElementById("activo").value);
    
    if (imagenFile) {
        formData.append("imagen", imagenFile);
    }

    const url = id ? `/productos/${id}` : "/productos";
    const method = id ? "PUT" : "POST";

    try {
        const res = await fetch(url, {
            method,
            body: formData
        });

        if (!res.ok) {
            const error = await res.json();
            alert(error.error || "Error al guardar carta");
            return;
        }

        bootstrap.Modal.getInstance(document.getElementById("modalCarta")).hide();
        cargarCartas();
    } catch (err) {
        console.error(err);
        alert("Error al guardar carta");
    }
});

// =========================
// INICIO
// =========================
document.addEventListener("DOMContentLoaded", cargarCartas);
