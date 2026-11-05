(() => {
  const subjects = {
    tb_carts:'el carrito de compras', tb_logs:'el evento de auditoría',
    tb_order_cancellations:'la solicitud de cancelación del pedido', tb_orders:'el pedido',
    tb_payment_methods:'el método de pago', tb_payment_transaction:'la transacción de pago',
    tb_payments:'el pago', tb_people:'la ficha de datos personales', tb_products:'el producto',
    tb_refunds:'el reembolso', tb_returns:'la devolución de producto', tb_shipments:'el envío',
    tb_user_addresses:'la dirección de usuario', tb_users:'la cuenta de usuario',
    tbc_categories:'la categoría de producto', tbc_payment_methods_types:'el tipo de método de pago',
    tbd_address_components:'el componente de dirección', tbd_cancellation_items:'el artículo de pedido cancelado',
    tbd_cart_items:'la línea del carrito', tbd_order_items:'la línea del pedido',
    tbd_products_categories:'la asociación entre producto y categoría',
    tbd_products_users_providers:'la relación entre proveedor y producto',
    tbd_return_items:'el artículo devuelto', tbd_user_payment_methods:'el medio de pago asociado a usuario',
    tbd_users_wishlist_products:'el producto guardado en lista de deseos'
  };

  const meanings = {
    email:'correo electrónico registrado para identificar o contactar la cuenta',
    nickname:'alias visible de la cuenta', password:'credencial de acceso asociada a la cuenta; el DDL no especifica si se almacena cifrada o como hash',
    key:'clave textual alternativa del pedido; el SQL no explica su uso fuera de la base de datos',
    total_products:'cantidad total de productos contabilizados en el pedido', total_cost:'importe total heredado del pedido',
    buyer_order_ID:'identificador de pedido de comprador vinculado por nombre; el DDL de cancelaciones no declara esta columna como FK',
    subtotal:'importe de los artículos antes de sumar el envío', shipping_cost:'importe cobrado por transportar el pedido o paquete',
    fulfillment_status:'la etapa de preparación y entrega del pedido', status_string:'el estado general del pedido conservado por el modelo anterior',
    title:'tratamiento o título personal de la persona', given_names:'nombres de pila de la persona', family_names:'apellidos de la persona',
    gender_ID:'la categoría de género registrada para la persona', birth_date:'fecha de nacimiento de la persona',
    phone:'número telefónico de contacto', country_code:'código de país asociado al dato',
    current_price:'precio vigente del producto', current_stock:'existencias disponibles registradas para el producto',
    SKU:'código de referencia comercial del producto; su unicidad depende del índice declarado en el esquema',
    reason_code:'código interno que clasifica el motivo', reason_detail:'explicación textual del motivo',
    cancellation_scope:'el alcance de la cancelación: pedido completo o artículos seleccionados', internal_notes:'observaciones internas del proceso',
    amount:'importe monetario del movimiento', currency:'código de moneda de tres caracteres',
    provider:'proveedor externo que procesa o transporta la operación', provider_reference:'referencia asignada por el proveedor externo',
    provider_transaction_id:'identificador de la transacción en el sistema del proveedor', idempotency_key:'clave para reconocer reintentos de una misma solicitud',
    response_code:'código devuelto por el proveedor', response_message:'mensaje de respuesta recibido del proveedor',
    transaction_type:'la clase de movimiento financiero', operation:'la acción auditada en la base de datos',
    table_name:'nombre textual de la tabla afectada; el DDL no lo declara como clave foránea',
    db_users:'nombre de la cuenta de base de datos anotado en la bitácora; se guarda como texto y no tiene FK',
    operation_status:'resultado binario registrado para la operación auditada',
    payment_status:'el estado del pago según el flujo de procesamiento', refund_status:'el estado del reembolso según su procesamiento',
    cancellation_status:'el estado de revisión y resolución de la cancelación', return_status:'la etapa de autorización, recepción y cierre de la devolución',
    shipment_status:'la etapa de preparación, tránsito o entrega del envío', item_status:'el estado de revisión y resolución del artículo devuelto',
    item_condition:'la condición física declarada al recibir el artículo devuelto', disposition:'el destino previsto para el artículo devuelto',
    approved_refund_amount:'importe del reembolso autorizado para este artículo',
    recipient_name:'nombre de la persona que debe recibir el paquete', recipient_phone:'teléfono de contacto de quien recibe el paquete',
    address_line_1:'primera línea de la dirección de entrega', address_line_2:'segunda línea opcional de la dirección de entrega',
    city:'ciudad de destino', state_region:'estado, provincia o región de destino', postal_code:'código postal de destino',
    country_code:'código del país de destino', carrier:'empresa transportista del paquete', service_level:'servicio o nivel de entrega contratado',
    tracking_number:'número de seguimiento asignado por el transportista', tracking_url:'enlace para consultar el seguimiento del paquete',
    return_carrier:'empresa transportista que gestiona la devolución', return_tracking_number:'número de seguimiento del paquete devuelto',
    address_label:'nombre corto para distinguir la dirección, por ejemplo casa o trabajo',
    delivery_instructions:'indicaciones para entregar el paquete en la dirección', latitude:'coordenada de latitud de la dirección',
    longitude:'coordenada de longitud de la dirección', is_default:'indicador que señala si el registro se selecciona como opción predeterminada',
    code:'código corto del tipo de método de pago', value:'valor textual del componente de dirección',
    component_type:'clase de componente que representa el valor de dirección',
    address_sup_ID:'identificador del componente superior en la jerarquía de dirección',
    label:'nombre elegido para reconocer el método de pago guardado', last_four:'últimos cuatro caracteres de la referencia del medio de pago',
    provider_method_ref:'referencia del medio de pago guardado en el proveedor; no contiene necesariamente el número completo',
    type_ownership:'el papel del usuario respecto del producto', avalaible_date:'fecha desde la que se declara disponible la relación proveedor-producto',
    quantity:'unidades del producto incluidas en esta línea', provider_ID:'identificador del proveedor asociado con la línea; el DDL no declara una FK para este campo',
    unit_price:'precio por unidad registrado para esta línea',
    product_name:'nombre del producto copiado al detalle del pedido',
    total_products:'cantidad total de productos contabilizados en el pedido',
    description:'texto descriptivo que amplía la información funcional del registro; el DDL no fija una plantilla de contenido'
  };

  const times = {
    last_login:'fecha y hora del último acceso registrado para la cuenta',
    operation_date:'fecha y hora en que ocurrió la operación auditada',
    requested_at:'fecha y hora en que se envió la solicitud', reviewed_at:'fecha y hora de revisión de la solicitud',
    completed_at:'fecha y hora en que concluyó la cancelación', processed_at:'fecha y hora de procesamiento del reembolso',
    request_date:'fecha y hora de envío de la solicitud al proveedor', response_date:'fecha y hora de recepción de la respuesta del proveedor',
    paid_date:'fecha y hora en que se registró el pago como realizado', authorized_at:'fecha y hora en que se autorizó la devolución',
    received_at:'fecha y hora en que el artículo devuelto llegó al destino de recepción', closed_at:'fecha y hora de cierre de la devolución',
    shipped_at:'fecha y hora en que el paquete salió hacia el transportista',
    estimated_delivery_at:'fecha y hora estimadas para la entrega', delivered_at:'fecha y hora de entrega registrada',
    birth_date:'fecha de nacimiento registrada para la persona', avalaible_date:'fecha desde la que se declara disponible la relación'
  };

  const tableTimes = {
    'tb_order_cancellations.requested_at':'fecha y hora en que se solicitó cancelar el pedido',
    'tb_returns.requested_at':'fecha y hora en que se solicitó devolver el producto'
  };

  function enumValues(type) {
    const match=type.match(/^enum\((.*)\)$/i);
    if(!match)return '';
    return [...match[1].matchAll(/'((?:\\.|[^'])*)'/g)].map(item=>item[1]).join(', ');
  }

  function explain(column,table) {
    const subject=subjects[table.name]||`registro de ${table.name}`;
    const key=`${table.name}.${column.name}`;
    const refTables=[...new Set(column.references.map(reference=>reference.split('.')[0]))];
    const primary=column.keys.includes('PK');

    if(key==='tb_logs.db_users')return 'Nombre de la cuenta de base de datos consignado en el evento de auditoría. Se almacena como texto y no está relacionado mediante una clave foránea.';
    if(key==='tb_orders.status_string')return `Estado general codificado del pedido. Se diferencia de fulfillment_status, que describe su etapa de preparación y entrega. Valores permitidos por el DDL: ${enumValues(column.type)}.`;
    if(key==='tb_orders.total_cost')return 'Importe total conservado en el pedido. El DDL no define cómo se calcula respecto de subtotal y shipping_cost.';
    if(key==='tb_people.country_code')return 'Código de país asociado a la ficha personal; el DDL no especifica si representa nacionalidad, residencia u otra relación.';
    if(key==='tb_user_addresses.country_code')return 'Código del país al que pertenece la dirección registrada.';
    if(key==='tb_shipments.country_code')return 'Código del país de destino del envío.';
    if(key==='tb_orders.subtotal')return 'Importe de los productos del pedido antes de sumar shipping_cost; el DDL no declara una fórmula de cálculo.';
    if(key==='tbd_order_items.subtotal')return 'Importe total de esta línea del pedido; el DDL no declara una fórmula entre quantity y unit_price.';
    if(key==='tbd_cart_items.quantity')return 'Número de unidades del producto que el usuario mantiene en el carrito.';
    if(key==='tbd_order_items.quantity')return 'Número de unidades del producto registradas en la línea comprada.';
    if(key==='tbd_cancellation_items.quantity')return 'Número de unidades de la línea del pedido que se solicita cancelar.';
    if(key==='tbd_return_items.quantity')return 'Número de unidades de la línea del pedido incluidas en la devolución.';
    if(key==='tb_refunds.reason')return `Motivo clasificado del reembolso. Valores permitidos por el DDL: ${enumValues(column.type)}.`;
    if(refTables.length){
      const targets=refTables.map(name=>subjects[name]||`tabla ${name}`);
      const relation=targets.length===1?`establece el vínculo con ${targets[0]}`:`participa en relaciones con ${targets.join(' y ')}`;
      const roles=[];
      if(primary)roles.push('también forma parte de la clave primaria compuesta');
      if(column.keys.some(role=>role.startsWith('UNIQUE ')))roles.push('un índice único limita sus valores repetidos');
      return `El campo ${column.name} en ${subject} ${relation} mediante la clave foránea declarada${roles.length?`; ${roles.join('; ')}`:''}.`;
    }
    if(primary)return column.name==='ID'?`Identificador primario que identifica ${subject}.`:`Componente de la clave primaria compuesta de la fila de ${subject}.`;
    if(column.name==='creation_date')return `Fecha y hora en que se creó ${subject}${column.default?' en la base de datos':''}.`;
    if(column.name==='last_update')return `Fecha y hora de la última modificación de ${subject}${column.onUpdate?'; el DDL actualiza este valor automáticamente al modificar la fila':''}.`;
    if(tableTimes[key]||times[column.name])return `${tableTimes[key]||times[column.name]}.`;

    if(column.name==='operation_status')return `En ${subject}, registra en formato binario el resultado de la operación auditada; el SQL no documenta qué valor representa éxito o error.`;
    if(column.name==='status'||column.name.endsWith('_status')){
      const values=enumValues(column.type);
      if(values)return `En ${subject}, indica ${meanings[column.name]||'el estado actual del proceso'}. Valores permitidos por el DDL: ${values}.`;
      if(/^bit|^tinyint\(1\)/i.test(column.type))return `En ${subject}, es una bandera binaria de estado. Por convención del nombre, 1 se interpreta como activo y 0 como inactivo; confirma este significado con las reglas de negocio.`;
    }
    const values=enumValues(column.type);
    if(values)return `En ${subject}, el campo ${column.name} representa ${meanings[column.name]||`la clasificación «${column.name.replace(/_/g,' ')}»`}. Valores permitidos por el DDL: ${values}.`;

    if(column.name==='ID')return `Identificador técnico del ${subject}; revisa las claves declaradas para confirmar si es primario.`;
    if(meanings[column.name])return `En ${subject}, almacena ${meanings[column.name]}.`;
    if(column.name==='name')return `Nombre visible utilizado para reconocer ${subject}.`;
    if(column.name==='description')return `Texto que describe ${subject}; el DDL no define una plantilla ni un vocabulario controlado.`;
    if(column.name==='status')return `Indicador de estado del ${subject}; los valores y su significado de negocio no están documentados en el SQL.`;

    const label=column.name.replace(/_/g,' ').replace(/\bID\b/g,'identificador');
    return `En ${subject}, almacena el dato «${label}». El respaldo define el tipo ${column.type}${column.nullable? ' y permite NULL':' como obligatorio'}, pero no especifica una regla de negocio adicional.`;
  }

  window.COLUMN_GUIDE={explain};
})();
