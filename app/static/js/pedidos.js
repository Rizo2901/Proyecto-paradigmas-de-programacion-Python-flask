// Variables globales
let pedidos = [];
let clientes = [];
let productos = [];
let detallesPedido = [];
let pedidoEditandoId = null;
let detallesOriginales = []; // Para comparar al editar

// Inicialización cuando se carga la página
document.addEventListener("DOMContentLoaded", () => {
    cargarPedidos();
    cargarClientes();
    cargarProductos();
});

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
  

// Función para cargar pedidos
async function cargarPedidos() {
    try {
        const filtroEstado = document.getElementById("filtroEstado");
        const estado = filtroEstado ? filtroEstado.value : "";
        const url = estado && estado !== "" ? `/pedidos?estado=${estado}` : "/pedidos";
        
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        pedidos = data;
        renderizarPedidos();
    } catch (error) {
        console.error("Error al cargar pedidos:", error);
        mostrarError("Error al cargar los pedidos: " + error.message);
    }
}

// Función para cargar clientes
async function cargarClientes() {
    try {
        const response = await fetch("/clientes");
        const data = await response.json();
        clientes = data;
        
        const select = document.getElementById("idCliente");
        select.innerHTML = '<option value="">Seleccione un cliente</option>';
        data.forEach(cliente => {
            const option = document.createElement("option");
            option.value = cliente.IdCliente;
            option.textContent = `${cliente.Nombre} (${cliente.Correo})`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error("Error al cargar clientes:", error);
    }
}

// Función para cargar productos
async function cargarProductos() {
    try {
        const response = await fetch("/productos");
        const data = await response.json();
        productos = data.filter(p => p.Activo && p.Stock > 0);
    } catch (error) {
        console.error("Error al cargar productos:", error);
    }
}

// Función para renderizar pedidos en la tabla
function renderizarPedidos() {
    const tbody = document.getElementById("pedidos-tbody");
    
    if (pedidos.length === 0) {
        tbody.innerHTML = "<tr><td colspan='9' class='loading'>No hay pedidos registrados</td></tr>";
        return;
    }
    
    tbody.innerHTML = pedidos.map(pedido => {
        const fecha = new Date(pedido.FechaPedido).toLocaleDateString("es-ES");
        const total = pedido.Total.toFixed(2);
        const nombreCliente = pedido.NombreCliente || `Cliente #${pedido.IdCliente}`;
        const tiendaEnvio = pedido.TiendaEnvio || "";
        const notas = pedido.Notas || "";
        const notasCortas = notas.length > 30 ? notas.substring(0, 30) + "..." : notas;
        
        // Calcular cantidad total de cartas
        const cantidadCartas = pedido.Detalles && pedido.Detalles.length > 0 
            ? pedido.Detalles.reduce((sum, d) => sum + (d.Cantidad || 0), 0)
            : 0;
        
        return `
            <tr>
                <td>${pedido.IdPedido}</td>
                <td>${nombreCliente}</td>
                <td>${fecha}</td>
                <td style="text-align: center;">
                    <span style="background: #e3f2fd; color: #1565c0; padding: 4px 10px; border-radius: 12px; font-weight: bold;">
                        🃏 ${cantidadCartas}
                    </span>
                </td>
                <td>$${total}</td>
                <td><span class="estado-badge estado-${pedido.Estado.toLowerCase().replace(' ', '-')}">${pedido.Estado}</span></td>
                <td style="max-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${tiendaEnvio}">
                    ${tiendaEnvio ? `<span style="cursor: help;">🏪 ${tiendaEnvio}</span>` : '<span style="color: #999;">-</span>'}
                </td>
                <td title="${notas}" style="max-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                    ${notas ? `<span style="cursor: help;">📝 ${notasCortas}</span>` : '<span style="color: #999;">-</span>'}
                </td>
                <td class="acciones">
                    <button class="btn-icon" onclick="verDetalles(${pedido.IdPedido})" title="Ver detalles">👁️</button>
                    ${pedido.Estado === "Pendiente" ? `
                        <button class="btn-icon" onclick="editarPedido(${pedido.IdPedido})" title="Editar">✏️</button>
                        <button class="btn-icon" onclick="cambiarEstado(${pedido.IdPedido})" title="Cambiar estado">🔄</button>
                    ` : ""}
                    <button class="btn-icon btn-danger" onclick="abrirModalEliminar(${pedido.IdPedido})" title="Eliminar">🗑️</button>
                </td>
            </tr>
        `;
    }).join("");
}

// Función para abrir modal de crear pedido
function abrirModalCrear() {
    pedidoEditandoId = null;
    detallesPedido = [];
    detallesOriginales = [];
    document.getElementById("modalTitulo").textContent = "Nuevo Pedido";
    document.getElementById("pedidoId").value = "";
    document.getElementById("idCliente").value = "";
    document.getElementById("idCliente").disabled = false;
    document.getElementById("estado").value = "Pendiente";
    document.getElementById("totalPedido").textContent = "0.00";
    document.getElementById("detalles-list").innerHTML = "";
    document.getElementById("modalPedido").style.display = "block";
}

// Función para editar pedido
async function editarPedido(idPedido) {
    try {
        const response = await fetch(`/pedidos/${idPedido}`);
        const pedido = await response.json();
        
        if (pedido.error) {
            mostrarError(pedido.error);
            return;
        }
        
        // Validar que el pedido esté en estado Pendiente
        if (pedido.Estado !== "Pendiente") {
            mostrarError(`Solo se pueden editar pedidos en estado Pendiente. Estado actual: ${pedido.Estado}`);
            return;
        }
        
        pedidoEditandoId = idPedido;
        detallesPedido = JSON.parse(JSON.stringify(pedido.Detalles || [])); // Copia profunda
        detallesOriginales = JSON.parse(JSON.stringify(pedido.Detalles || [])); // Guardar originales para comparar
        
        document.getElementById("modalTitulo").textContent = `Editar Pedido #${idPedido}`;
        document.getElementById("pedidoId").value = idPedido;
        document.getElementById("idCliente").value = pedido.IdCliente;
        document.getElementById("estado").value = pedido.Estado;
        document.getElementById("idCliente").disabled = true; // No se puede cambiar el cliente
        
        renderizarDetalles();
        calcularTotal();
        
        document.getElementById("modalPedido").style.display = "block";
    } catch (error) {
        console.error("Error al cargar pedido:", error);
        mostrarError("Error al cargar el pedido");
    }
}

// Función para cerrar modal
function cerrarModal() {
    document.getElementById("modalPedido").style.display = "none";
    pedidoEditandoId = null;
    detallesPedido = [];
    detallesOriginales = [];
}

// Función para agregar detalle
function agregarDetalle() {
    detallesPedido.push({
        IdDetalle: null,
        IdProducto: "",
        Cantidad: 1,
        PrecioUnitario: 0,
        NombreProducto: ""
    });
    renderizarDetalles();
}

// Función para renderizar detalles
function renderizarDetalles() {
    const container = document.getElementById("detalles-list");
    
    // Si no hay detalles, mostrar mensaje informativo
    if (detallesPedido.length === 0) {
        container.innerHTML = `
            <div class="no-detalles-mensaje" style="
                background: #fff3cd;
                border: 1px solid #ffc107;
                border-radius: 8px;
                padding: 15px;
                text-align: center;
                color: #856404;
                margin-bottom: 10px;
            ">
                <p style="margin: 0 0 10px 0;"><strong>📦 No hay productos en este pedido</strong></p>
                <p style="margin: 0; font-size: 14px;">Haz clic en "+ Agregar Carta" para añadir productos al pedido.</p>
            </div>
        `;
        calcularTotal();
        return;
    }
    
    container.innerHTML = detallesPedido.map((detalle, index) => {
        const producto = productos.find(p => p.IdProducto == detalle.IdProducto);
        const stockDisponible = producto ? producto.Stock : 0;
        const nombreProducto = detalle.NombreProducto || (producto ? producto.Nombre : 'Producto desconocido');
        
        return `
            <div class="detalle-item" data-index="${index}" style="
                display: grid;
                grid-template-columns: 2fr 80px 100px 100px 40px;
                gap: 10px;
                align-items: center;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 8px;
                margin-bottom: 8px;
            ">
                <select class="producto-select" onchange="actualizarDetalleProducto(${index}, this.value)" style="padding: 8px; border-radius: 4px; border: 1px solid #ddd;">
                    <option value="">Seleccione una carta</option>
                    ${productos.map(p => {
                        const selected = p.IdProducto == detalle.IdProducto ? "selected" : "";
                        const stockWarning = p.Stock === 0 ? " (Sin stock)" : ` (Stock: ${p.Stock})`;
                        return `<option value="${p.IdProducto}" ${selected} ${p.Stock === 0 && !selected ? "disabled" : ""}>${p.Nombre} - $${p.Precio}${stockWarning}</option>`;
                    }).join("")}
                </select>
                <input type="number" class="cantidad-input" min="1" value="${detalle.Cantidad}" 
                       onchange="actualizarDetalleCantidad(${index}, this.value)"
                       max="${stockDisponible}"
                       style="padding: 8px; border-radius: 4px; border: 1px solid #ddd; text-align: center;">
                <span class="precio-unitario" style="text-align: right; color: #666;">$${detalle.PrecioUnitario ? detalle.PrecioUnitario.toFixed(2) : "0.00"}</span>
                <span class="subtotal" style="text-align: right; font-weight: bold; color: #28a745;">$${((detalle.Cantidad || 0) * (detalle.PrecioUnitario || 0)).toFixed(2)}</span>
                <button type="button" class="btn-icon btn-danger" onclick="eliminarDetalle(${index})" title="Eliminar" style="background: #dc3545; color: white; border: none; border-radius: 4px; padding: 5px 10px; cursor: pointer;">🗑️</button>
            </div>
        `;
    }).join("");
    calcularTotal();
}

// Función para actualizar producto en detalle
function actualizarDetalleProducto(index, idProducto) {
    const producto = productos.find(p => p.IdProducto == idProducto);
    if (producto) {
        detallesPedido[index].IdProducto = producto.IdProducto;
        detallesPedido[index].NombreProducto = producto.Nombre;
        detallesPedido[index].PrecioUnitario = producto.Precio;
        detallesPedido[index].Cantidad = Math.min(detallesPedido[index].Cantidad || 1, producto.Stock);
        renderizarDetalles();
    }
}

// Función para actualizar cantidad en detalle
function actualizarDetalleCantidad(index, cantidad) {
    const cantidadNum = parseInt(cantidad) || 1;
    const detalle = detallesPedido[index];
    const producto = productos.find(p => p.IdProducto == detalle.IdProducto);
    
    if (producto && cantidadNum > producto.Stock) {
        mostrarError(`Stock insuficiente. Disponible: ${producto.Stock}`);
        detallesPedido[index].Cantidad = producto.Stock;
    } else {
        detallesPedido[index].Cantidad = cantidadNum;
    }
    renderizarDetalles();
}

// Función para eliminar detalle
function eliminarDetalle(index) {
    detallesPedido.splice(index, 1);
    renderizarDetalles();
}

// Función para calcular total
function calcularTotal() {
    const total = detallesPedido.reduce((sum, detalle) => {
        return sum + ((detalle.Cantidad || 0) * (detalle.PrecioUnitario || 0));
    }, 0);
    document.getElementById("totalPedido").textContent = total.toFixed(2);
}

// Función para actualizar un pedido completo (información básica + detalles)
async function actualizarPedidoCompleto(idPedido, formData) {
    try {
        // 1. Actualizar información básica del pedido (Estado)
        const updateResponse = await fetch(`/pedidos/${idPedido}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                Estado: formData.Estado
            })
        });
        
        const updateResult = await updateResponse.json();
        if (updateResult.error) {
            return updateResult;
        }
        
        // 2. Obtener detalles actuales del servidor
        const detallesResponse = await fetch(`/pedidos/${idPedido}/detalles`);
        const detallesActuales = await detallesResponse.json();
        
        if (detallesActuales.error) {
            return detallesActuales;
        }
        
        // 3. Sincronizar detalles: comparar nuevos con actuales
        const detallesNuevos = formData.detalles || [];
        const detallesParaEliminar = [];
        const detallesParaCrear = [];
        const detallesParaActualizar = [];
        
        // Identificar detalles a eliminar (están en actuales pero no en nuevos)
        detallesActuales.forEach(detalleActual => {
            const existeEnNuevos = detallesNuevos.some(d => {
                // Buscar por IdDetalle si existe
                if (detalleActual.IdDetalle) {
                    return d.IdDetalle === detalleActual.IdDetalle;
                }
                return false;
            });
            
            if (!existeEnNuevos) {
                detallesParaEliminar.push(detalleActual);
            }
        });
        
        // Identificar detalles a crear/actualizar
        detallesNuevos.forEach(detalleNuevo => {
            // Buscar detalle existente por IdDetalle si está disponible
            let detalleExistente = null;
            if (detalleNuevo.IdDetalle) {
                detalleExistente = detallesActuales.find(d => d.IdDetalle === detalleNuevo.IdDetalle);
            }
            
            // Si no se encontró por IdDetalle, buscar por IdProducto
            if (!detalleExistente) {
                detalleExistente = detallesActuales.find(d => d.IdProducto === detalleNuevo.IdProducto);
            }
            
            if (!detalleExistente) {
                // Nuevo detalle a crear
                detallesParaCrear.push({
                    IdProducto: detalleNuevo.IdProducto,
                    Cantidad: detalleNuevo.Cantidad,
                    PrecioUnitario: detalleNuevo.PrecioUnitario
                });
            } else {
                // Verificar si necesita actualización
                const cambioCantidad = detalleExistente.Cantidad !== detalleNuevo.Cantidad;
                const cambioPrecio = Math.abs((detalleExistente.PrecioUnitario || 0) - (detalleNuevo.PrecioUnitario || 0)) > 0.01;
                const cambioProducto = detalleExistente.IdProducto !== detalleNuevo.IdProducto;
                
                if (cambioCantidad || cambioPrecio || cambioProducto) {
                    if (cambioProducto) {
                        // Si cambió el producto, eliminar el viejo y crear uno nuevo
                        detallesParaEliminar.push(detalleExistente);
                        detallesParaCrear.push({
                            IdProducto: detalleNuevo.IdProducto,
                            Cantidad: detalleNuevo.Cantidad,
                            PrecioUnitario: detalleNuevo.PrecioUnitario
                        });
                    } else {
                        // Actualizar detalle existente
                        detallesParaActualizar.push({
                            idDetalle: detalleExistente.IdDetalle,
                            data: {
                                Cantidad: detalleNuevo.Cantidad,
                                PrecioUnitario: detalleNuevo.PrecioUnitario
                            }
                        });
                    }
                }
            }
        });
        
        // 4. Ejecutar cambios: primero eliminar, luego crear, luego actualizar
        // Eliminar detalles
        for (const detalle of detallesParaEliminar) {
            const deleteResponse = await fetch(`/pedidos/${idPedido}/detalles/${detalle.IdDetalle}`, {
                method: "DELETE"
            });
            const deleteResult = await deleteResponse.json();
            if (deleteResult.error) {
                return deleteResult;
            }
        }
        
        // Crear nuevos detalles
        for (const detalle of detallesParaCrear) {
            const createResponse = await fetch(`/pedidos/${idPedido}/detalles`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(detalle)
            });
            const createResult = await createResponse.json();
            if (createResult.error) {
                return createResult;
            }
        }
        
        // Actualizar detalles existentes
        for (const { idDetalle, data } of detallesParaActualizar) {
            const updateResponse = await fetch(`/pedidos/${idPedido}/detalles/${idDetalle}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });
            const updateResult = await updateResponse.json();
            if (updateResult.error) {
                return updateResult;
            }
        }
        
        // 5. Obtener el pedido actualizado
        const finalResponse = await fetch(`/pedidos/${idPedido}`);
        return await finalResponse.json();
        
    } catch (error) {
        console.error("Error al actualizar pedido:", error);
        return { error: `Error al actualizar pedido: ${error.message}` };
    }
}

// Función para guardar pedido
document.getElementById("formPedido").addEventListener("submit", async (e) => {
    e.preventDefault();
    
    // Si estamos editando y no hay detalles, solo actualizar el estado
    const soloActualizarEstado = pedidoEditandoId && detallesPedido.length === 0;
    
    if (!pedidoEditandoId && detallesPedido.length === 0) {
        mostrarError("El pedido debe tener al menos un detalle");
        return;
    }
    
    // Validar stock antes de enviar (solo si hay detalles)
    if (detallesPedido.length > 0) {
        for (const detalle of detallesPedido) {
            if (!detalle.IdProducto) {
                mostrarError("Debe seleccionar un producto para cada detalle");
                return;
            }
            const producto = productos.find(p => p.IdProducto == detalle.IdProducto);
            if (!producto) {
                mostrarError(`Producto no encontrado: ${detalle.NombreProducto || detalle.IdProducto}`);
                return;
            }
            if (producto.Stock < detalle.Cantidad) {
                mostrarError(`Stock insuficiente para ${producto.Nombre}. Disponible: ${producto.Stock}, solicitado: ${detalle.Cantidad}`);
                return;
            }
        }
    }
    
    const formData = {
        IdCliente: parseInt(document.getElementById("idCliente").value),
        Estado: document.getElementById("estado").value,
        detalles: detallesPedido.map(d => ({
            IdDetalle: d.IdDetalle || null,
            IdProducto: parseInt(d.IdProducto),
            Cantidad: parseInt(d.Cantidad),
            PrecioUnitario: parseFloat(d.PrecioUnitario)
        }))
    };
    
    try {
        let resultado;
        if (pedidoEditandoId) {
            if (soloActualizarEstado) {
                // Solo actualizar el estado del pedido, sin tocar detalles
                const response = await fetch(`/pedidos/${pedidoEditandoId}`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ Estado: formData.Estado })
                });
                resultado = await response.json();
            } else {
                // Actualizar pedido existente con detalles
                resultado = await actualizarPedidoCompleto(pedidoEditandoId, formData);
            }
        } else {
            // Crear nuevo pedido
            const response = await fetch("/pedidos", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData)
            });
            resultado = await response.json();
        }
        
        if (resultado.error) {
            // Mostrar mensaje más amigable si es error de tabla
            if (resultado.error.includes("tabla") || resultado.error.includes("PedidosDetalle")) {
                mostrarError("No se pueden guardar los detalles porque la tabla PedidosDetalle no existe en la base de datos. El estado del pedido se actualizó correctamente.");
                cerrarModal();
                cargarPedidos();
            } else {
                mostrarError(resultado.error);
            }
        } else {
            cerrarModal();
            cargarPedidos();
            mostrarExito(pedidoEditandoId ? "Pedido actualizado correctamente" : "Pedido guardado correctamente");
        }
    } catch (error) {
        console.error("Error al guardar pedido:", error);
        mostrarError("Error al guardar el pedido: " + error.message);
    }
});

// Función para ver detalles del pedido
async function verDetalles(idPedido) {
    try {
        const response = await fetch(`/pedidos/${idPedido}`);
        const pedido = await response.json();
        
        if (pedido.error) {
            mostrarError(pedido.error);
            return;
        }
        
        document.getElementById("detallesPedidoId").textContent = idPedido;
        const contenido = document.getElementById("detalles-contenido");
        
        const nombreClienteDetalle = pedido.NombreCliente || `Cliente #${pedido.IdCliente}`;
        const tieneDetalles = pedido.Detalles && pedido.Detalles.length > 0;
        const tiendaEnvioPedido = pedido.TiendaEnvio || "";
        const notasPedido = pedido.Notas || "";
        
        contenido.innerHTML = `
            <div class="detalles-info" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <p style="margin: 5px 0;"><strong>👤 Cliente:</strong> ${nombreClienteDetalle}</p>
                <p style="margin: 5px 0;"><strong>📅 Fecha:</strong> ${new Date(pedido.FechaPedido).toLocaleString("es-ES")}</p>
                <p style="margin: 5px 0;"><strong>📊 Estado:</strong> <span style="background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 4px;">${pedido.Estado}</span></p>
                <p style="margin: 5px 0; font-size: 1.2em;"><strong>💰 Total:</strong> $${pedido.Total.toFixed(2)}</p>
            </div>
            ${tiendaEnvioPedido ? `
                <div style="background: #e8f5e9; border: 1px solid #4caf50; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
                    <p style="margin: 0 0 5px 0; font-weight: bold; color: #2e7d32;">🏪 Tienda de Envío:</p>
                    <p style="margin: 0; color: #2e7d32;">${tiendaEnvioPedido}</p>
                </div>
            ` : ''}
            ${notasPedido ? `
                <div style="background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
                    <p style="margin: 0 0 5px 0; font-weight: bold; color: #856404;">📝 Notas del Cliente:</p>
                    <p style="margin: 0; color: #856404;">${notasPedido}</p>
                </div>
            ` : ''}
            ${tieneDetalles ? `
                <h4 style="margin: 15px 0 10px 0; color: #333;">🛒 Productos del Pedido:</h4>
                <table class="detalles-table" style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: #f8f9fa;">
                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">Carta</th>
                            <th style="padding: 10px; text-align: center; border-bottom: 2px solid #ddd;">Cantidad</th>
                            <th style="padding: 10px; text-align: right; border-bottom: 2px solid #ddd;">Precio Unit.</th>
                            <th style="padding: 10px; text-align: right; border-bottom: 2px solid #ddd;">Subtotal</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${pedido.Detalles.map(d => `
                            <tr>
                                <td style="padding: 10px; border-bottom: 1px solid #eee;">${d.NombreProducto || 'Producto'}</td>
                                <td style="padding: 10px; text-align: center; border-bottom: 1px solid #eee;">${d.Cantidad}</td>
                                <td style="padding: 10px; text-align: right; border-bottom: 1px solid #eee;">$${(d.PrecioUnitario || 0).toFixed(2)}</td>
                                <td style="padding: 10px; text-align: right; border-bottom: 1px solid #eee; font-weight: bold; color: #28a745;">$${(d.Subtotal || 0).toFixed(2)}</td>
                            </tr>
                        `).join("")}
                    </tbody>
                </table>
            ` : `
                <div style="background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; padding: 20px; text-align: center; color: #856404;">
                    <p style="margin: 0 0 10px 0; font-size: 1.1em;"><strong>ℹ️ Sin detalles de productos</strong></p>
                    <p style="margin: 0; font-size: 14px;">
                        Este pedido no tiene detalles de productos registrados.<br>
                        La tabla PedidosDetalle puede no existir en la base de datos.
                    </p>
                </div>
            `}
        `;
        
        document.getElementById("modalDetalles").style.display = "block";
    } catch (error) {
        console.error("Error al cargar detalles:", error);
        mostrarError("Error al cargar los detalles del pedido");
    }
}

// Función para cerrar modal de detalles
function cerrarModalDetalles() {
    document.getElementById("modalDetalles").style.display = "none";
}

// Función para cambiar estado del pedido
async function cambiarEstado(idPedido) {
    // Estados válidos según el CHECK constraint de la base de datos
    const estados = ["Pendiente", "Enviado", "Entregado", "Pagado", "Cancelado"];
    const pedido = pedidos.find(p => p.IdPedido === idPedido);
    if (!pedido) return;
    
    const estadoActual = pedido.Estado;
    const indiceActual = estados.indexOf(estadoActual);
    const nuevoEstado = estados[(indiceActual + 1) % estados.length];
    
    try {
        const response = await fetch(`/pedidos/${idPedido}/estado`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ estado: nuevoEstado })
        });
        
        const resultado = await response.json();
        
        if (resultado.error) {
            mostrarError(resultado.error);
        } else {
            cargarPedidos();
            mostrarExito(`Estado cambiado a ${nuevoEstado}`);
        }
    } catch (error) {
        console.error("Error al cambiar estado:", error);
        mostrarError("Error al cambiar el estado del pedido");
    }
}

// Función para abrir modal de eliminar
let pedidoEliminarId = null;
function abrirModalEliminar(idPedido) {
    pedidoEliminarId = idPedido;
    document.getElementById("pedidoIdEliminar").textContent = idPedido;
    document.getElementById("modalEliminar").style.display = "block";
}

// Función para cerrar modal de eliminar
function cerrarModalEliminar() {
    document.getElementById("modalEliminar").style.display = "none";
    pedidoEliminarId = null;
}

// Función para confirmar eliminación
async function confirmarEliminar() {
    if (!pedidoEliminarId) return;
    
    try {
        const response = await fetch(`/pedidos/${pedidoEliminarId}`, {
            method: "DELETE"
        });
        
        const resultado = await response.json();
        
        if (resultado.error) {
            mostrarError(resultado.error);
        } else {
            cerrarModalEliminar();
            cargarPedidos();
            mostrarExito("Pedido eliminado correctamente");
        }
    } catch (error) {
        console.error("Error al eliminar pedido:", error);
        mostrarError("Error al eliminar el pedido");
    }
}

// Funciones de utilidad
function mostrarError(mensaje) {
    alert("Error: " + mensaje);
}

function mostrarExito(mensaje) {
    alert("Éxito: " + mensaje);
}

// Cerrar modales al hacer click fuera
window.onclick = function(event) {
    const modalPedido = document.getElementById("modalPedido");
    const modalDetalles = document.getElementById("modalDetalles");
    const modalEliminar = document.getElementById("modalEliminar");
    
    if (event.target === modalPedido) {
        cerrarModal();
    }
    if (event.target === modalDetalles) {
        cerrarModalDetalles();
    }
    if (event.target === modalEliminar) {
        cerrarModalEliminar();
    }
}

