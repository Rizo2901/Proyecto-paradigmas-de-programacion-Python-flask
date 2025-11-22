let clienteIdEliminar = null;

// Cargar clientes al iniciar
document.addEventListener('DOMContentLoaded', function() {
    cargarClientes();
});

// Cargar lista de clientes
async function cargarClientes() {
    try {
        const response = await fetch('/clientes');
        const clientes = await response.json();
        
        const tbody = document.getElementById('clientes-tbody');
        
        if (clientes.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="no-data">No hay clientes registrados</td></tr>';
            return;
        }
        
        tbody.innerHTML = clientes.map(cliente => `
            <tr>
                <td>${cliente.IdCliente}</td>
                <td>${cliente.Nombre}</td>
                <td>${cliente.Correo}</td>
                <td>${cliente.Telefono || '-'}</td>
                <td>${cliente.Direccion || '-'}</td>
                <td>${formatearFecha(cliente.FechaRegistro)}</td>
                <td class="actions">
                    <button class="btn-edit" onclick="abrirModalEditar(${cliente.IdCliente})" title="Editar">
                        ✏️
                    </button>
                    <button class="btn-delete" onclick="abrirModalEliminar(${cliente.IdCliente}, '${cliente.Nombre}')" title="Eliminar">
                        🗑️
                    </button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error al cargar clientes:', error);
        document.getElementById('clientes-tbody').innerHTML = 
            '<tr><td colspan="7" class="error">Error al cargar los clientes</td></tr>';
    }
}

// Abrir modal para crear
function abrirModalCrear() {
    document.getElementById('modalTitulo').textContent = 'Nuevo Cliente';
    document.getElementById('formCliente').reset();
    document.getElementById('clienteId').value = '';
    document.getElementById('modalCliente').style.display = 'block';
}

// Abrir modal para editar
async function abrirModalEditar(idCliente) {
    try {
        const response = await fetch(`/clientes/${idCliente}`);
        const cliente = await response.json();
        
        if (cliente.error) {
            alert('Error: ' + cliente.error);
            return;
        }
        
        document.getElementById('modalTitulo').textContent = 'Editar Cliente';
        document.getElementById('clienteId').value = cliente.IdCliente;
        document.getElementById('nombre').value = cliente.Nombre || '';
        document.getElementById('correo').value = cliente.Correo || '';
        document.getElementById('telefono').value = cliente.Telefono || '';
        document.getElementById('direccion').value = cliente.Direccion || '';
        
        document.getElementById('modalCliente').style.display = 'block';
    } catch (error) {
        console.error('Error al cargar cliente:', error);
        alert('Error al cargar los datos del cliente');
    }
}

// Abrir modal para eliminar
function abrirModalEliminar(idCliente, nombre) {
    clienteIdEliminar = idCliente;
    document.getElementById('nombreClienteEliminar').textContent = nombre;
    document.getElementById('modalEliminar').style.display = 'block';
}

// Cerrar modales
function cerrarModal() {
    document.getElementById('modalCliente').style.display = 'none';
}

function cerrarModalEliminar() {
    document.getElementById('modalEliminar').style.display = 'none';
    clienteIdEliminar = null;
}

// Manejar envío del formulario
document.getElementById('formCliente').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const clienteId = formData.get('IdCliente');
    const data = {
        Nombre: formData.get('Nombre'),
        Correo: formData.get('Correo'),
        Telefono: formData.get('Telefono') || null,
        Direccion: formData.get('Direccion') || null
    };
    
    try {
        const url = clienteId ? `/clientes/${clienteId}` : '/clientes';
        const method = clienteId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const resultado = await response.json();
        
        if (resultado.error) {
            alert('Error: ' + resultado.error);
            return;
        }
        
        alert(clienteId ? 'Cliente actualizado correctamente' : 'Cliente creado correctamente');
        cerrarModal();
        cargarClientes();
    } catch (error) {
        console.error('Error al guardar cliente:', error);
        alert('Error al guardar el cliente');
    }
});

// Confirmar eliminación
async function confirmarEliminar() {
    if (!clienteIdEliminar) return;
    
    try {
        const response = await fetch(`/clientes/${clienteIdEliminar}`, {
            method: 'DELETE'
        });
        
        const resultado = await response.json();
        
        if (resultado.error) {
            alert('Error: ' + resultado.error);
            return;
        }
        
        alert('Cliente eliminado correctamente');
        cerrarModalEliminar();
        cargarClientes();
    } catch (error) {
        console.error('Error al eliminar cliente:', error);
        alert('Error al eliminar el cliente');
    }
}

// Formatear fecha
function formatearFecha(fecha) {
    if (!fecha) return '-';
    const date = new Date(fecha);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

// Cerrar modal al hacer clic fuera
window.onclick = function(event) {
    const modalCliente = document.getElementById('modalCliente');
    const modalEliminar = document.getElementById('modalEliminar');
    
    if (event.target === modalCliente) {
        cerrarModal();
    }
    if (event.target === modalEliminar) {
        cerrarModalEliminar();
    }
}
