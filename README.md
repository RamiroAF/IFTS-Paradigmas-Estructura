# IFTS-Estructura-Paradigmas

Esta es una aplicación Web para consultar la base de datos en donde están almacenadas las Ventas del local "Farmacia".

A grandes rasgos, ¿cómo será el flujo del programa?

El core de la aplicación se encuentra en el archivo "app.py", donde tiene definidas todas las clases y las URLs. Cuando el usuario se loguee, tendrá acceso a todas las URLs, las cuales tienen cada una un archivo .HTML específico, que le envía al navegador la información que se mostrará, y la estructura que tendrá que tener.

¿Qué estructura se utilizará para representar la información del archivo?

La información está guardada en archivos con formato .CSV, y es mostrada de la misma manera en la página web, está estructurada en tablas, donde la primera línea es la cabecera de las columnas, y el resto es la información.

¿Cómo se usa el programa?

Primero de todo, el usuario deberá ir al link "register", donde lo llevará a una página que le permitirá crear su usuario y luego loguearse con el mismo. Al loguearse, la página automáticamente lo va a redirigir a la url "Ventas", donde le mostrará una tabla con todas las ventas registradas en el archivo .csv. Si desea volver a esta página, simplemente debe hacer click en "Ventas", que se encuentra en la barra superior de la página.
En caso de que desee buscar por alguna línea específica, deberá filtrar la información, para esto, deberá hacer click en el link correspondiente a su consulta, que también se encuentran en la barra superior. Si desea consultar por "Cliente", deberá hacer click en "Filtrar por Cliente", y así para el resto de las consultas.

¿Qué clases se diseñaron?¿Por qué?

Para esta aplicación, las clases creadas son todas formularios, cuales son utilizados cada vez que la aplicación necesite información del usuario. En los formularios se utilizó un validator que es el "DataRequired", para que sea obligatorio rellenar los campos.
Cada consulta tiene su formulario específico, ya que se hardcodeo en cada uno el mensaje que se mostrará acompañando el campo para que ingrese los datos.
