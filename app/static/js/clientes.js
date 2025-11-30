// =========================
// VALIDACIONES FORM CLIENTE
// =========================
// Validación Bootstrap
(() => {
    'use strict';
    const forms = document.querySelectorAll('.needs-validation');
  
    Array.from(forms).forEach(form => {
      form.addEventListener('submit', event => {
        if (!form.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();
        }
        // Activa estilos de error
        form.classList.add('was-validated');
      }, false);
    });
  })();
  
  // =========================
  // CARGA DE CLIENTES EN TABLA
  // =========================
  async function cargarClientes() {
    const tbody = document.getElementById("clientes-tbody");
    tbody.innerHTML = `<tr><td colspan="7" class="loading">Cargando clientes...</td></tr>`;
  
    try {
      // Llama a tu API (ajusta la URL según tu backend)
      const response = await fetch("/clientes");
      if (!response.ok) throw new Error("Error al obtener clientes");
  
      const clientes = await response.json();
  
      if (clientes.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7">No hay clientes registrados.</td></tr>`;
        return;
      }
  
      // Renderizar filas
      tbody.innerHTML = "";
      clientes.forEach(cliente => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${cliente.IdCliente}</td>
          <td>${cliente.Nombre}</td>
          <td>${cliente.Correo}</td>
          <td>${cliente.Telefono || ""}</td>
          <td>${cliente.Direccion || ""}</td>
          <td>${cliente.FechaRegistro}</td>
          <td class="actions">
            <!-- Botón Editar -->
            <button 
              class="btn btn-sm btn-warning" 
              data-bs-toggle="modal" 
              data-bs-target="#modalCliente" 
              onclick="editarCliente(${cliente.IdCliente})" 
              title="Editar">
              <i class="bi bi-pencil-square"></i>
            </button>
  
            <!-- Botón Eliminar -->
            <button 
              class="btn btn-sm btn-danger" 
              data-bs-toggle="modal" 
              data-bs-target="#modalEliminar" 
              onclick="setClienteEliminar(${cliente.IdCliente}, '${cliente.Nombre}')" 
              title="Eliminar">
              <i class="bi bi-trash"></i>
            </button>
  
            <!-- Botón Ver Detalles -->
            <button 
              class="btn btn-sm btn-info" 
              data-bs-toggle="modal" 
              data-bs-target="#modalCliente" 
              onclick="verCliente(${cliente.IdCliente})" 
              title="Ver Detalles">
              <i class="bi bi-eye"></i>
            </button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    } catch (error) {
      tbody.innerHTML = `<tr><td colspan="7" class="error">Error al cargar clientes</td></tr>`;
      console.error(error);
    }
  }
  
  // =========================
  // CREAR / EDITAR CLIENTE
  // =========================
  document.getElementById("formCliente").addEventListener("submit", async function (e) {
    e.preventDefault();
  
    if (!this.checkValidity()) {
      this.classList.add("was-validated");
      return;
    }
  
    const clienteId = document.getElementById("clienteId").value;
    const data = {
      IdCliente: clienteId || null,
      Nombre: document.getElementById("nombre").value,
      Correo: document.getElementById("correo").value,
      Telefono: document.getElementById("telefono").value,
      Direccion: document.getElementById("direccion").value
    };
  
    try {
      const url = clienteId ? `/clientes/${clienteId}` : `/clientes`;
      const method = clienteId ? "PUT" : "POST";
  
      const response = await fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });
  
      if (!response.ok) throw new Error("Error al guardar cliente");
  
      // Cerrar modal y recargar tabla
      bootstrap.Modal.getInstance(document.getElementById("modalCliente")).hide();
      cargarClientes();
    } catch (err) {
      console.error(err);
      alert("Hubo un error al guardar el cliente.");
    }
  });
  
  // =========================
  // ELIMINAR CLIENTE
  // =========================
  let clienteEliminarId = null;
  
  function setClienteEliminar(id, nombre) {
    clienteEliminarId = id;
    document.getElementById("nombreClienteEliminar").textContent = nombre;
  }
  
  async function confirmarEliminar() {
    try {
      const response = await fetch(`/clientes/${clienteEliminarId}`, { method: "DELETE" });
      if (!response.ok) throw new Error("Error al eliminar cliente");
  
      bootstrap.Modal.getInstance(document.getElementById("modalEliminar")).hide();
      cargarClientes();
    } catch (err) {
      console.error(err);
      alert("Hubo un error al eliminar el cliente.");
    }
  }
  
  // =========================
  // EDITAR CLIENTE
  // =========================
  async function editarCliente(id) {
    try {
      const response = await fetch(`/clientes/${id}`);
      if (!response.ok) throw new Error("Error al obtener cliente");
  
      const cliente = await response.json();
  
      // Cambiar título del modal
      document.getElementById("modalTitulo").textContent = "Editar Cliente";
  
      // Llenar campos
      document.getElementById("clienteId").value = cliente.IdCliente;
      document.getElementById("nombre").value = cliente.Nombre;
      document.getElementById("correo").value = cliente.Correo;
      document.getElementById("telefono").value = cliente.Telefono || "";
      document.getElementById("direccion").value = cliente.Direccion || "";
  
      // Habilitar inputs
      document.querySelectorAll("#formCliente input, #formCliente textarea").forEach(el => el.disabled = false);
    } catch (err) {
      console.error(err);
      alert("Error al cargar datos del cliente.");
    }
  }
  
  // =========================
  // VER DETALLES CLIENTE
  // =========================
  async function verCliente(id) {
    try {
      const response = await fetch(`/clientes/${id}`);
      if (!response.ok) throw new Error("Error al obtener cliente");
  
      const cliente = await response.json();
  
      // Mostrar datos en un modal de detalles
      document.getElementById("modalTitulo").textContent = "Detalles Cliente";
      document.getElementById("clienteId").value = cliente.IdCliente;
      document.getElementById("nombre").value = cliente.Nombre;
      document.getElementById("correo").value = cliente.Correo;
      document.getElementById("telefono").value = cliente.Telefono || "";
      document.getElementById("direccion").value = cliente.Direccion || "";
  
      // Deshabilitar inputs si es solo lectura
      document.querySelectorAll("#formCliente input, #formCliente textarea").forEach(el => el.disabled = true);
    } catch (err) {
      console.error(err);
      alert("Error al cargar detalles del cliente.");
    }
  }
  
  // =========================
  // INICIALIZACIÓN
  // =========================
  document.addEventListener("DOMContentLoaded", cargarClientes);