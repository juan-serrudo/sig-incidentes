"""Technological incident templates for the UOIT operations environment.

Covers 40 independent operational families across 5 technological categories:
- applications_services (8 families)
- databases (8 families)
- networks_connectivity (8 families)
- infrastructure_storage (8 families)
- security_access (8 families)
"""

FAMILIES = {
    "applications_services": [
        # app-01: Caida de portal web institucional
        {
            "family_id": "app-01",
            "titles": [
                "Portal web institucional fuera de servicio con error 502",
                "Indisponibilidad del portal de tramites en servidores web",
                "Caida del servicio web principal por error de gateway",
                "El portal institucional no responde y devuelve HTTP 502 Bad Gateway",
            ],
            "descriptions": [
                "Los usuarios reportan pantalla en blanco y error 502 Bad Gateway al intentar consultar el portal de tramites.",
                "El balanceador Nginx devuelve error 502 indicando que el backend de la aplicacion web no responde a las solicitudes.",
                "El servicio web institucional se encuentra caido, impidiendo la atencion de tramites digitales a los usuarios externos.",
                "Las instancias del portal web quedaron inaccesibles tras un reinicio del proceso de aplicacion en los servidores web.",
            ],
        },
        # app-02: Falla en API Gateway / microservicios
        {
            "family_id": "app-02",
            "titles": [
                "Error 500 en endpoint central del API Gateway institucional",
                "Falla en microservicio de integracion y excepciones HTTP 500",
                "Respuestas HTTP 500 masivas en la pasarela de servicios API",
                "Microservicio de gestion reporta excepciones internas no controladas",
            ],
            "descriptions": [
                "El API Gateway institucional devuelve respuestas HTTP 500 Internal Server Error en los endpoints de integracion.",
                "Los sistemas clientes no logran consumir los servicios REST debido a excepciones internas en la pasarela central.",
                "Se detectan fallas recurrentes en el microservicio de integracion, arrojando errores 500 en llamadas sincronas.",
                "Los logs del servidor de aplicaciones evidencian desbordamiento de pila y respuestas HTTP 500 al recibir peticiones JSON.",
            ],
        },
        # app-03: Fallas en modulo de reportes y facturacion del ERP
        {
            "family_id": "app-03",
            "titles": [
                "Falla en generacion de reportes y exportacion en sistema ERP",
                "Modulo de liquidacion y nommina en aplicacion ERP congelado",
                "Error al emitir reportes contables en el sistema de gestion institucional",
                "Aplicacion ERP se cuelga al procesar solicitudes de exportacion masiva",
            ],
            "descriptions": [
                "Los operadores reportan que la aplicacion ERP deja de responder al solicitar reportes consolidados del mes.",
                "La funcionalidad de exportacion de planillas en el ERP institucional arroja timeout y aborta la sesion del usuario.",
                "El modulo contable del aplicativo no finaliza el calculo de liquidaciones y congela la interfaz grafica.",
                "Al intentar descargar informes financieros en el ERP, el sistema arroja error de procesamiento y no genera el archivo.",
            ],
        },
        # app-04: Timeout en pasarela de pagos / cobros
        {
            "family_id": "app-04",
            "titles": [
                "Timeout recurrente en pasarela de pagos en linea",
                "Transacciones de cobro fallidas por interrupcion en el modulo de pagos",
                "Lentitud extrema y fallos de timeout en cobros digitales del aplicativo",
                "Servicio de recaudacion web aborta transacciones por timeout de confirmacion",
            ],
            "descriptions": [
                "Los cobros en linea quedan en estado pendiente y se abortan por timeout con el servicio bancario.",
                "El aplicativo de pagos en linea no logra procesar confirmaciones de transacciones, generando timeouts recurrentes.",
                "Se observan demoras criticas y cancelaciones de pago en la plataforma web al intentar procesar transacciones de clientes.",
                "La comunicacion con la pasarela de recaudacion digital se interrumpe y los comprobantes no se emiten.",
            ],
        },
        # app-05: Tarea programada batch fallida
        {
            "family_id": "app-05",
            "titles": [
                "Fallo en ejecucion de tarea batch nocturna de sincronizacion",
                "Proceso programado de cierre diario abortado en servidor de aplicaciones",
                "Error en cron de integracion de datos entre sistemas institucionales",
                "La tarea por lotes de consolidacion de expedientes termino con codigo de error",
            ],
            "descriptions": [
                "La tarea programada de la madrugada finalizo inesperadamente dejando pendientes los lotes de sincronizacion de expedientes.",
                "El script batch nocturno se detuvo con codigo de error impidiendo la consolidacion diaria en el sistema institucional.",
                "El cron de exportacion periodica fallo al procesar los archivos de intercambio entre plataformas de gestion.",
                "El proceso por lotes en segundo plano arrojo excepciones y no cargo los registros diarios de expedientes.",
            ],
        },
        # app-06: Fuga de memoria / OutOfMemoryError en servidor de aplicaciones
        {
            "family_id": "app-06",
            "titles": [
                "Agotamiento de memoria Java y OutOfMemoryError en servidor Tomcat",
                "Fuga de memoria detectada en contenedor de aplicaciones empresariales",
                "Proceso Java consumiendo 100% de heap memory en servidor de produccion",
                "Reinicio forzado del servidor de aplicaciones por error de falta de memoria",
            ],
            "descriptions": [
                "La maquina virtual Java del servidor Tomcat arrojo java.lang.OutOfMemoryError Java heap space y quedo sin responder.",
                "El consumo de memoria heap en el contenedor de aplicaciones supero el 99%, degradando totalmente el servicio web.",
                "El proceso Java dejo de atender peticiones debido a una fuga de memoria detectada en el modulo de procesamiento documental.",
                "Monitoreo de APM alerta sobre agotamiento de memoria en la JVM provocando pausas de garbage collection mayores a 30 segundos.",
            ],
        },
        # app-07: Cola de mensajeria RabbitMQ/Kafka saturada
        {
            "family_id": "app-07",
            "titles": [
                "Saturacion critica de cola de mensajeria en broker RabbitMQ",
                "Mensajes represados y demora en procesamiento de eventos asincronos",
                "Desbordamiento de mensajes en topico de eventos de la plataforma",
                "Consumidores de cola de mensajeria detenidos y mensajes acumulandose",
            ],
            "descriptions": [
                "La cola de notificaciones en RabbitMQ acumula mas de 50.000 mensajes sin procesar por caida de consumidores.",
                "Los eventos asincronos entre microservicios no se estan entregando debido a saturacion critica en el broker de mensajes.",
                "El broker de mensajeria reporta umbral de memoria superado y bloqueo de publicacion de nuevos mensajes de transacciones.",
                "Se detecta paralizacion en el procesamiento de eventos en cola, demorando el despacho de correos y avisos del sistema.",
            ],
        },
        # app-08: Falla tras despliegue de version de software
        {
            "family_id": "app-08",
            "titles": [
                "Inestabilidad y errores 404/500 tras despliegue de nueva version",
                "Fallo en pase a produccion de release de aplicacion institucional",
                "Incompatibilidad de librerias tras actualizacion de modulo de software",
                "Rollback solicitado por fallo general tras despliegue de version 2.4",
            ],
            "descriptions": [
                "Inmediatamente despues del despliegue de la ultima actualizacion, el sistema arroja errores 404 en rutas criticas.",
                "La nueva version de la aplicacion desplegada esta manana presenta incompatibilidad con los paquetes del servidor web.",
                "Se reportan fallos generalizados tras la liberacion del parche, requiriendo analisis inmediato o rollback del artefacto.",
                "La aplicacion no arranca tras la actualizacion de dependencias en el servidor web de produccion.",
            ],
        },
    ],
    "databases": [
        # db-01: Agotamiento de pool de conexiones PostgreSQL
        {
            "family_id": "db-01",
            "titles": [
                "Agotamiento del pool de conexiones en base de datos PostgreSQL",
                "Servidor de base de datos rechaza conexiones por limite superado",
                "Error FATAL: remaining connection slots are reserved en base de datos",
                "Pool de PgBouncer saturado y aplicaciones sin conexion al motor relacional",
            ],
            "descriptions": [
                "Las aplicaciones no logran abrir nuevas sesiones porque PostgreSQL alcanzo el maximo de conexiones permitidas.",
                "El pooler de base de datos reporta clientes en espera y rechaza peticiones con mensaje de error de conexiones agotadas.",
                "El motor de base de datos rechaza nuevas conexiones de servicios arrojando error FATAL too many clients already.",
                "Las aplicaciones web quedan bloqueadas al intentar obtener un handle de conexion hacia el servidor principal de base de datos.",
            ],
        },
        # db-02: Bloqueo de transacciones (Deadlock)
        {
            "family_id": "db-02",
            "titles": [
                "Bloqueo masivo de tablas y transacciones en base de datos",
                "Deadlock detectado entre procesos concurrentes en motor relacional",
                "Consultas bloqueadas por transaccion abierta sin commit en base de datos",
                "Alertas de lock wait timeout excedido en tablas maestras del sistema",
            ],
            "descriptions": [
                "Multiples procesos de escritura se encuentran en espera prolongada debido a un bloqueo exclusivo en la tabla de facturacion.",
                "El motor de base de datos arrojo alerta de deadlock al competir dos transacciones concurrentes por los mismos registros.",
                "Una transaccion no confirmada mantiene bloqueadas las tablas principales, frenando las operaciones del sistema de gestion.",
                "Se registran decenas de consultas en estado lock wait, paralizando la actualizacion de estados en el motor relacional.",
            ],
        },
        # db-03: Desincronizacion de replica secundaria
        {
            "family_id": "db-03",
            "titles": [
                "Lag critico y desincronizacion en replica de base de datos",
                "Falla en streaming replication de nodo secundario de base de datos",
                "Replica de lectura de base de datos desactualizada por retraso en WAL",
                "Nodo esclavo de base de datos perdio sincronismo con el nodo maestro",
            ],
            "descriptions": [
                "La replica de base de datos presenta un retraso de mas de dos horas en la aplicacion de registros de transacciones.",
                "El proceso de replicacion continua se interrumpio arrojando error de conexion entre el nodo primario y secundario.",
                "Los reportes consultados en el nodo de solo lectura devuelven informacion desactualizada por caida del proceso de streaming.",
                "El cluster de base de datos reporta perdida de redundancia por desconexion y lag acumulado en la replica pasiva.",
            ],
        },
        # db-04: Corrupcion de indices o tablas
        {
            "family_id": "db-04",
            "titles": [
                "Corrupcion de indice b-tree detectada en tabla de transacciones",
                "Error de lectura I/O por bloque corrupto en motor de base de datos",
                "Inconsistencia de datos y error de checksum en tabla relacional",
                "Fallo en consulta SELECT por indice danado en base de datos productiva",
            ],
            "descriptions": [
                "Una consulta rutinaria arroja error de bloque corrupto en pagina de datos al leer el indice de la tabla principal.",
                "El log del servidor de base de datos reporta invalid page checksum en el archivo fisico de la tabla de auditoria.",
                "Las consultas sobre expedientes historicos fallan de inmediato requiriendo reconstruccion (REINDEX) de indices corruptos.",
                "El motor de datos detiene la ejecucion de sentencias sobre una tabla debido a inconsistencias estructurales detectadas.",
            ],
        },
        # db-05: Tablespace o espacio de base de datos agotado
        {
            "family_id": "db-05",
            "titles": [
                "Tablespace principal de base de datos al 99% de capacidad",
                "Agotamiento de espacio en disco asignado al motor de base de datos",
                "Base de datos no permite inserciones por falta de espacio en tablespace",
                "Alerta de disco lleno en volumen de datos del cluster de base de datos",
            ],
            "descriptions": [
                "El volumen asignado al tablespace de datos alcanzo su capacidad maxima e impide la insercion de nuevos registros.",
                "Las operaciones de INSERT fallan con error de disco lleno en la particion de almacenamiento de la base de datos.",
                "El crecimiento acelerado de tablas temporales provoco el llenado completo del tablespace del motor relacional.",
                "Se requiere ampliacion urgente de almacenamiento en el cluster de base de datos para reanudar operaciones de escritura.",
            ],
        },
        # db-06: CPU al 100% por consultas sin indice / queries lentas
        {
            "family_id": "db-06",
            "titles": [
                "Saturacion de CPU al 100% en servidor de base de datos por query lenta",
                "Consultas costosas sin indexar degradan el rendimiento del motor de base de datos",
                "Alto consumo de recursos en base de datos provocado por full table scans",
                "Servidor de base de datos no responde por sobrecarga de procesos SQL",
            ],
            "descriptions": [
                "Una secuencia de consultas analiticas pesadas sin indices adecuados saturo todos los procesadores del servidor de base de datos.",
                "El motor de base de datos mantiene una carga promedio excesiva debido a lecturas completas de tablas no optimizadas.",
                "El tiempo de respuesta de las consultas generales se disparo a mas de 40 segundos por sobrecarga de procesamiento en el motor.",
                "Monitoreo detecta tres procesos SQL consumiendo la totalidad del procesamiento del servidor maestro de datos.",
            ],
        },
        # db-07: Falla en archivos de registro de transacciones (WAL/Redo Log)
        {
            "family_id": "db-07",
            "titles": [
                "Falla en rotacion y archivo de registros WAL en base de datos",
                "Particion de transacciones WAL saturada impidiendo operaciones de base de datos",
                "Error en proceso de archivado continuo de logs en motor relacional",
                "El motor de base de datos entra en modo panico por no poder escribir transacciones",
            ],
            "descriptions": [
                "La particion designada para almacenar los archivos WAL de transacciones se lleno al 100%, deteniendo la base de datos.",
                "El comando de archivado continuo de registros de base de datos falla y acumula cientos de ficheros pendientes en disco.",
                "El servidor de base de datos se cerro de forma preventiva al no poder asegurar la persistencia del log de transacciones.",
                "Las transacciones quedan retenidas debido a que el directorio pg_wal no dispone de espacio para nuevos segmentos.",
            ],
        },
        # db-08: Error de migracion o script DDL fallido
        {
            "family_id": "db-08",
            "titles": [
                "Script de migracion DDL de base de datos interrumpido a la mitad",
                "Inconsistencia en esquema de base de datos tras alter table fallido",
                "Fallo en actualizacion de estructura de tablas de base de datos",
                "Error de sintaxis y bloqueo en migracion automatizada de base de datos",
            ],
            "descriptions": [
                "Un script de migracion de esquema fallo al modificar columnas con claves foraneas, dejando la base de datos en estado inconsistente.",
                "La sentencia ALTER TABLE sobre la tabla de usuarios se interrumpio por timeout, dejando bloqueos residuales en el catalogo.",
                "El proceso automatizado de actualizacion DDL arrojo violacion de restricciones y no pudo aplicar el rollback correspondiente.",
                "La estructura del esquema productivo discrepa de la version de la aplicacion tras fallar el despliegue de base de datos.",
            ],
        },
    ],
    "networks_connectivity": [
        # net-01: Caida de enlace WAN principal
        {
            "family_id": "net-01",
            "titles": [
                "Caida de enlace WAN principal de fibra optica con el proveedor",
                "Perdida de conectividad externa por corte de enlace de internet troncal",
                "Enlace metropolitano entre sede central y datacenter fuera de servicio",
                "Alerta de enlace de fibra optica caido en puerto de enrutador perimetral",
            ],
            "descriptions": [
                "El enlace de fibra optica principal con el proveedor de telecomunicaciones se cayo, dejando a la sede sin salida a internet.",
                "Monitoreo de red reporta que la interfaz WAN troncal paso a estado DOWN, requiriendo conmutacion hacia el enlace de respaldo.",
                "La conexion WAN entre los dos centros de datos se encuentra interrumpida impidiendo la comunicacion de red corporativa.",
                "Se constata perdida de enlace fisico en el puerto del router de borde que conecta con el proveedor de internet.",
            ],
        },
        # net-02: Problemas de enrutamiento BGP/OSPF
        {
            "family_id": "net-02",
            "titles": [
                "Flapping e inestabilidad en sesion BGP con proveedor de red",
                "Perdida de rutas y reconvergencia constante en protocolo OSPF interno",
                "Tablas de enrutamiento vacias por falla en sesion BGP de frontera",
                "Desconexion intermitente de prefijos IP corporativos en tabla de rutas",
            ],
            "descriptions": [
                "La sesion BGP perimetral experimenta caidas sucesivas, provocando cortes intermitentes y perdida de rutas hacia internet.",
                "Los routers de distribucion reportan cambios continuos de topologia OSPF por una interfaz de red con fallos intermitentes.",
                "El enrutador de borde perdio los anuncios de prefijos IP institucionales debido a la caida de la adyacencia BGP.",
                "Se detecta perdida de paquetes a nivel de capa 3 por bucles de enrutamiento dinamico no estabilizados.",
            ],
        },
        # net-03: Bucle de switching / broadcast storm
        {
            "family_id": "net-03",
            "titles": [
                "Tormenta de broadcast y bucle de switching en red de distribucion",
                "Colapso de switches de acceso por falla en protocolo Spanning Tree",
                "Saturacion de puertos de red por bucle fisico en switch departamental",
                "Caida de segmento LAN debido a trafico masivo de broadcast no controlado",
            ],
            "descriptions": [
                "Un bucle fisico en el switch del piso 2 provoco una tormenta de broadcast que saturo todos los enlaces de la red local.",
                "El protocolo Spanning Tree fallo en bloquear un enlace redundante, elevando el uso de CPU de los conmutadores al 100%.",
                "Los puertos de red de los conmutadores parpadean masivamente y ningun equipo del edificio logra comunicarse por LAN.",
                "Se observa caida generalizada del segmento Ethernet corporativo debido a paquetes de broadcast multiplicandose en bucle.",
            ],
        },
        # net-04: Falla en servidor DNS institucional
        {
            "family_id": "net-04",
            "titles": [
                "Falla en resolucion de nombres por caida de servidor DNS interno",
                "Servidor DNS corporativo no responde a consultas de nombres de dominio",
                "Error Server Failure en resolucion de nombres locales institucionales",
                "Equipos de la red no pueden acceder a sistemas por timeout en servidor DNS",
            ],
            "descriptions": [
                "Las estaciones de trabajo no logran resolver nombres de servidores internos debido a que el servicio DNS principal no responde.",
                "El servicio BIND en el servidor DNS corporativo se detuvo, provocando fallos de resolucion para todos los dominios de la entidad.",
                "Las consultas DNS internas arrojan timeout, imposibilitando la navegacion hacia recursos institucionales por nombre.",
                "Monitoreo alerta que el puerto UDP 53 del servidor DNS de la infraestructura no procesa peticiones de los puestos de red.",
            ],
        },
        # net-05: Falla en concentrador VPN corporativo
        {
            "family_id": "net-05",
            "titles": [
                "Caida de concentrador VPN impidiendo el acceso a usuarios remotos",
                "Falla en tuneles VPN IPsec corporativos entre sedes remotas",
                "Usuarios de teletrabajo reportan desconexion masiva del cliente VPN",
                "El servicio de acceso VPN corporativo rechaza el establecimiento de tuneles",
            ],
            "descriptions": [
                "El concentrador VPN no permite el inicio de sesiones remotas y expulsa a todos los usuarios conectados desde fuera.",
                "El tunel VPN IPsec que conecta la sucursal regional con el datacenter central se cayo y no logra renegociar las llaves.",
                "El servicio de red privada virtual corporativa no responde, impidiendo el acceso seguro a los operadores en teletrabajo.",
                "Se reporta interrupcion total en el acceso remoto por caida del demonio VPN en la pasarela de conectividad.",
            ],
        },
        # net-06: Saturacion y perdida de paquetes en interfaz de red
        {
            "family_id": "net-06",
            "titles": [
                "Saturacion de ancho de banda y descarte de paquetes en enlace de red",
                "Latencia extrema de red superior a 400ms en el troncal corporativo",
                "Descarte masivo de tramas en interfaz GigabitEthernet del switch central",
                "Trafico anomalo satura el enlace de comunicacion de red entre sedes",
            ],
            "descriptions": [
                "La interfaz troncal de red presenta un uso continuo del 99%, provocando descarte de tramas y lentitud generalizada.",
                "Se registra una latencia anormalmente alta y 30% de perdida de paquetes de red en el enlace interdepartamental.",
                "El trafico en el enlace de red supera el ancho de banda contratado, generando cola de espera y retransmisiones masivas.",
                "Los equipos de red reportan errores de buffer overflow y perdida de paquetes en los puertos de comunicacion interna.",
            ],
        },
        # net-07: Falla de controlador Wi-Fi / Access Points
        {
            "family_id": "net-07",
            "titles": [
                "Controlador Wi-Fi institucional desconecto todos los puntos de acceso",
                "Caida de red inalambrica institucional en edificio de administracion",
                "Puntos de acceso Wi-Fi desasociados del controlador central de red",
                "Falla en autenticacion y asignacion de red inalambrica corporativa",
            ],
            "descriptions": [
                "Todos los Access Points del edificio perdieron conexion con el controlador central de Wi-Fi, dejando sin senal a la sede.",
                "La red inalambrica corporativa no permite conexion de nuevos clientes tras un reinicio del controlador de acceso.",
                "Los puntos de acceso inalambricos de las plantas 3 y 4 se encuentran apagados o desasociados de la red de gestion.",
                "Se reporta ausencia total de cobertura de red Wi-Fi institucional en las salas de reuniones y oficinas de direccion.",
            ],
        },
        # net-08: Fallo en pasarela predeterminada / gateway de VLAN
        {
            "family_id": "net-08",
            "titles": [
                "Gateway predeterminado de VLAN de servidores no responde a ping",
                "Perdida de comunicacion inter-VLAN por caida de interfaz virtual SVI",
                "Aislamiento de segmento de red por falla en la direccion IP de gateway",
                "Servidores de una VLAN especifica pierden comunicacion con el resto de la red",
            ],
            "descriptions": [
                "Los servidores alojados en la VLAN de produccion no logran alcanzar su puerta de enlace predeterminada en el switch core.",
                "La interfaz virtual SVI de la VLAN de monitoreo cayo, impidiendo el enrutamiento hacia otros segmentos de red.",
                "Ningun equipo del segmento de red logra enviar trafico fuera de su subred local por indisponibilidad de la IP del router.",
                "Se detecta una caida de la direccion IP de gateway en el switch de capa 3, aislando completamente el segmento de red.",
            ],
        },
    ],
    "infrastructure_storage": [
        # inf-01: Hipervisor de virtualizacion en estado Not Responding
        {
            "family_id": "inf-01",
            "titles": [
                "Hipervisor de virtualizacion en estado Not Responding en el cluster",
                "Host fisico de maquinas virtuales se congelo y desconecto del vCenter",
                "Falla critica en servidor hipervisor afectando a diez maquinas virtuales",
                "Reinicio imprevisto de nodo fisico de computo en cluster de virtualizacion",
            ],
            "descriptions": [
                "El servidor hipervisor fisico quedo en estado no responde, dejando congeladas todas las maquinas virtuales que alojaba.",
                "El gestor de virtualizacion perdio comunicacion con el host de computo, activando alertas de alta disponibilidad HA.",
                "Un fallo critico en el sistema operativo base del hipervisor provoco la interrupcion de servidores virtuales de produccion.",
                "El servidor fisico que hospeda maquinas virtuales sufrio un kernel panic de hardware y reinicio sin previo aviso.",
            ],
        },
        # inf-02: Disco degradado en arreglo RAID
        {
            "family_id": "inf-02",
            "titles": [
                "Disco fisico fallido en arreglo RAID de servidor de infraestructura",
                "Arreglo RAID 5 en estado DEGRADED por averia en unidad de disco",
                "Controladora de almacenamiento alerta fallo inminente en disco de servidor",
                "Perdida de redundancia en volumen RAID por desconexion de disco rigido",
            ],
            "descriptions": [
                "La controladora RAID del servidor principal reporta un disco en estado failed y el volumen operando en modo degradado.",
                "Uno de los discos mecanicos del arreglo de almacenamiento presento sectores danados y fue expulsado del volumen RAID.",
                "El servidor de almacenamiento masivo perdio la tolerancia a fallos tras la rotura de una unidad de disco SAS.",
                "Se requiere reemplazo fisico de disco rigido en servidor de infraestructura tras alerta roja de la controladora RAID.",
            ],
        },
        # inf-03: Falla en copias de seguridad / backup nocturno
        {
            "family_id": "inf-03",
            "titles": [
                "Fallo en trabajo nocturno de copias de seguridad de servidores",
                "Job de backup programado abortado con error de escritura en destino",
                "Copias de respaldo de maquinas virtuales incompletas y con error",
                "Servidor de backups reporta error de comunicacion con el repositorio de almacenamiento",
            ],
            "descriptions": [
                "El trabajo de respaldo nocturno de las maquinas virtuales fallo al no poder escribir en el repositorio de backup.",
                "La tarea programada de copia de seguridad termino con codigo de error y los puntos de restauracion no se generaron.",
                "El software de copias de seguridad alerta que el job de snapshot de servidores criticos fue abortado por timeout.",
                "Las copias de respaldo de la infraestructura quedaron truncadas debido a un corte en la comunicacion con el servidor de cintas/SAN.",
            ],
        },
        # inf-04: LUN o volumen de cabina SAN desconectado
        {
            "family_id": "inf-04",
            "titles": [
                "Datastore LUN de cabina SAN desasociado de servidores de computo",
                "Perdida de conectividad Fiber Channel hacia volumen de almacenamiento SAN",
                "Volumen compartido iSCSI desconectado en los nodos de virtualizacion",
                "Cabina de almacenamiento SAN no responde a solicitudes de lectura y escritura",
            ],
            "descriptions": [
                "El volumen LUN compartido de la cabina de discos SAN se desconecto, provocando que los datastores queden inaccesibles.",
                "Los hipervisores perdieron acceso a los discos por Fibre Channel, dejando a los sistemas virtuales sin almacenamiento de lectura.",
                "Se detecta perdida de paths en la red SAN de almacenamiento, ocasionando timeouts de entrada y salida en las maquinas.",
                "La controladora de la cabina de discos SAN entro en mantenimiento imprevisto y desmonto los volumenes de produccion.",
            ],
        },
        # inf-05: Falla de hardware de servidor (memoria RAM o fuente)
        {
            "family_id": "inf-05",
            "titles": [
                "Falla en modulo de memoria RAM fisica en servidor de infraestructura",
                "Averia en fuente de alimentacion redundante de servidor blade",
                "Alerta de error ECC no corregible en memoria del servidor de produccion",
                "Sensor de hardware reporta perdida de energia en fuente secundaria de rack",
            ],
            "descriptions": [
                "El modulo de control iLO/iDRAC alerta sobre errores irrecuperables en el banco de memoria RAM del servidor de base.",
                "La fuente de alimentacion numero dos del servidor de infraestructura se apago y no entrega energia electrica.",
                "El servidor de infraestructura experimento un reinicio automatico por falla de paridad detectada en la memoria fisica.",
                "El chasis de servidores emite alarma por desconfiguracion de hardware y fallo en el sistema de alimentacion redundante.",
            ],
        },
        # inf-06: Particion de sistema o root llena en servidor
        {
            "family_id": "inf-06",
            "titles": [
                "Particion root al 100% de ocupacion en servidor de infraestructura",
                "Almacenamiento de sistema operativo lleno por acumulacion de logs",
                "Servidor no permite creacion de archivos temporales por disco lleno al 100%",
                "Alerta critica de espacio agotado en volumen /var/log de servidor base",
            ],
            "descriptions": [
                "El disco del sistema operativo llego al 100% de uso en la particion root, impidiendo el inicio de servicios y creacion de sockets.",
                "La acumulacion desmedida de registros de sistema en /var/log lleno el almacenamiento del servidor de infraestructura.",
                "Los servicios del sistema operativo se detienen debido a que no pueden escribir archivos de estado en la particion de disco.",
                "Monitoreo emite alarma critica de almacenamiento: cero megabytes libres en el volumen de sistema del servidor de produccion.",
            ],
        },
        # inf-07: Alerta termica y ventilacion en rack del datacenter
        {
            "family_id": "inf-07",
            "titles": [
                "Alerta de sobrecalentamiento y temperatura critica en rack de servidores",
                "Falla en ventiladores de chasis de servidores en centro de datos",
                "Temperatura de CPU supero umbral maximo en servidor de infraestructura",
                "Apagado termico preventivo inminente en hardware de centro de datos",
            ],
            "descriptions": [
                "Los sensores del servidor de infraestructura registran 85 grados en los procesadores por averia en el flujo de aire del rack.",
                "Varios ventiladores del servidor fisico dejaron de girar, activando la advertencia de sobrecalentamiento en el datacenter.",
                "El sistema de gestion de hardware notifica que el equipo entrara en apagado termico si la temperatura no disminuye.",
                "Se detecta fallo en la unidad de refrigeracion del gabinete de servidores, elevando peligrosamente la temperatura del hardware.",
            ],
        },
        # inf-08: Falla en snapshot o sincronizacion de almacenamiento
        {
            "family_id": "inf-08",
            "titles": [
                "Error al consolidar snapshot de almacenamiento en servidor virtual",
                "Falla en proceso de instantanea de volumen en cabina de almacenamiento",
                "Bloqueo de maquina virtual durante consolidacion de disco de snapshot",
                "Espacio de almacenamiento saturado por retencion de snapshots antiguos",
            ],
            "descriptions": [
                "La consolidacion de snapshots de una maquina virtual critica arrojo error y mantiene bloqueados los archivos de disco VMDK.",
                "El proceso de instantanea en la cabina de almacenamiento quedo atascado, consumiendo espacio del datastore compartido.",
                "Una maquina virtual dejo de responder durante la fase de eliminacion de snapshot por retencion excesiva de deltas.",
                "Los snapshots antiguos no se eliminaron automaticamente y llenaron la capacidad total del volumen de almacenamiento.",
            ],
        },
    ],
    "security_access": [
        # sec-01: Expiracion de certificado SSL/TLS
        {
            "family_id": "sec-01",
            "titles": [
                "Expiracion de certificado SSL/TLS en pasarela web institucional",
                "Alerta de certificado digital caducado generando advertencias de seguridad",
                "Certificado HTTPS vencido impide acceso seguro de usuarios a portales",
                "Error NET::ERR_CERT_DATE_INVALID en sitio web por certificado expirado",
            ],
            "descriptions": [
                "El certificado digital SSL del dominio institucional expiro a medianoche, mostrando advertencias de sitio no seguro a los visitantes.",
                "Los navegadores web bloquean el ingreso al portal debido a que el certificado de seguridad HTTPS se encuentra vencido.",
                "Se reporta imposibilidad de transaccionar de forma segura por caducidad del certificado SSL instalado en el balanceador.",
                "Monitoreo de seguridad alerta que el certificado TLS del portal de tramites expiro y requiere renovacion e instalacion inmediata.",
            ],
        },
        # sec-02: Bloqueo de cuentas de servicio en Directorio Activo/LDAP
        {
            "family_id": "sec-02",
            "titles": [
                "Bloqueo masivo de cuenta de servicio en Directorio Activo institucional",
                "Cuenta de integracion bloqueada por multiples intentos de clave fallida",
                "Servicio de autenticacion rechaza credenciales por cuenta deshabilitada en LDAP",
                "Politica de seguridad bloqueo el usuario de servicio de conexion entre sistemas",
            ],
            "descriptions": [
                "La cuenta de servicio utilizada para la sincronizacion de usuarios quedo bloqueada en el Directorio Activo tras varios intentos fallidos.",
                "Los sistemas de gestion no pueden autenticar usuarios porque la cuenta de enlace en el servidor LDAP esta suspendida.",
                "Una politica de seguridad automatica desactivo las credenciales de servicio institucional, paralizando las consultas de autenticacion.",
                "Se constata que la cuenta tecnica de consulta se encuentra bloqueada por exceso de reintentos con contrasena invalida.",
            ],
        },
        # sec-03: Regla de firewall bloqueando trafico legitimo
        {
            "family_id": "sec-03",
            "titles": [
                "Regla de firewall perimetral bloquea trafico de aplicacion institucional",
                "Denegacion de acceso por politica de seguridad en firewall perimetral",
                "Trafico HTTPS legitimo filtrado y descartado por regla de seguridad",
                "Falta de apertura de puerto en firewall impide comunicacion entre servidores",
            ],
            "descriptions": [
                "Una modificacion en las politicas del firewall perimetral cerro el puerto necesario para la comunicacion con el servicio de tramites.",
                "El firewall corporativo esta denegando las peticiones legitimas hacia la subred DMZ por una regla de seguridad mal configurada.",
                "Los servidores de aplicacion no logran comunicarse con el servicio externo debido a un bloqueo explicito en el cortafuegos.",
                "Las conexiones entre sedes quedan rechazadas con paquetes TCP RST emitidos por la politica de seguridad del firewall.",
            ],
        },
        # sec-04: Falla en proveedor de identidad Keycloak/SSO
        {
            "family_id": "sec-04",
            "titles": [
                "Falla en proveedor de identidad Keycloak impidiendo inicio de sesion unico",
                "Servidor de autenticacion SSO no responde a solicitudes de validacion de tokens",
                "Error en federacion de identidades para el acceso unico de usuarios",
                "Servicio de inicio de sesion centralizado Keycloak fuera de linea",
            ],
            "descriptions": [
                "El servidor de autenticacion Keycloak no responde, impidiendo que los usuarios inicien sesion en los diferentes aplicativos institucionales.",
                "La validacion de tokens de seguridad OAuth2 falla de manera continua por indisponibilidad del servicio de federacion de identidades.",
                "Ningun funcionario puede acceder a las plataformas internas al fallar la redireccion hacia la pantalla de autenticacion SSO.",
                "Monitoreo de seguridad reporta error de comunicacion con el proveedor de identidad corporativo centralizado.",
            ],
        },
        # sec-05: Ataque de fuerza bruta o alerta de IDS/EDR
        {
            "family_id": "sec-05",
            "titles": [
                "Alerta de seguridad por ataque de fuerza bruta SSH en servidor publico",
                "Sistema IDS detecta escaneo de puertos y patron de ataque perimetral",
                "Alerta de EDR por ejecucion de comandos sospechosos en servidor de gestion",
                "Bloqueo preventivo de direccion IP por multiples intentos de intrusion detectados",
            ],
            "descriptions": [
                "El sistema de deteccion de intrusiones alerta sobre miles de intentos simultaneos de acceso SSH por fuerza bruta desde IPs externas.",
                "La plataforma de seguridad EDR emitio una alerta critica por deteccion de actividad anomala y ejecucion no autorizada en un servidor.",
                "Se detecta un escaneo masivo de vulnerabilidades y puertos dirigido contra la direccion IP publica del portal de servicios.",
                "El firewall de seguridad procedio al aislamiento preventivo de un host tras registrar patrones coincidentes con un intento de intrusion.",
            ],
        },
        # sec-06: Llave SSH rechazada por permisos o caducidad
        {
            "family_id": "sec-06",
            "titles": [
                "Llave SSH de administracion rechazada por permisos en authorized_keys",
                "Fallo de autenticacion por clave publica SSH en servidores de infraestructura",
                "Acceso administrativo bloqueado por revocacion o desajuste de llaves SSH",
                "Permission denied publickey al intentar ingresar a servidor seguro",
            ],
            "descriptions": [
                "Los administradores no logran conectarse a los servidores mediante llave SSH debido a permisos incorrectos en el directorio del usuario.",
                "La sesion remota de administracion rechaza la llave publica autorizada tras una sincronizacion defectuosa del archivo de configuracion.",
                "El servicio OpenSSH rechaza las conexiones de gestion arrojando Permission denied publickey en los nodos de infraestructura.",
                "Se requiere correccion urgente de politicas de permisos en el archivo authorized_keys para recuperar acceso administrativo.",
            ],
        },
        # sec-07: Denegacion de permisos por directivas RBAC o PAM
        {
            "family_id": "sec-07",
            "titles": [
                "Acceso denegado a operadores por directivas de autorizacion RBAC",
                "Falla en modulo PAM de autenticacion en servidores de aplicacion",
                "Permisos insuficientes para administracion de servicios por cambio en politicas",
                "Bloqueo de elevacion de privilegios mediante sudo para tecnicos de guardia",
            ],
            "descriptions": [
                "Los tecnicos de guardia reportan que la directiva de seguridad RBAC rechaza la ejecucion de tareas autorizadas de mantenimiento.",
                "El modulo de autenticacion PAM rechaza la comprobacion de permisos en los servidores Linux de la infraestructura.",
                "Una actualizacion de la politica de control de acceso despojo de privilegios legitimos al grupo de soporte de operaciones.",
                "Los operadores autorizados no logran ejecutar comandos con privilegios debido a un fallo de autorizacion en la politica de seguridad.",
            ],
        },
        # sec-08: Certificado autofirmado o no confiable en API interna
        {
            "family_id": "sec-08",
            "titles": [
                "Error de certificado SSL autofirmado bloquea comunicacion entre servicios",
                "Alerta de seguridad: cadena de confianza de certificado SSL no verificable",
                "Servicios internos rechazan peticiones por certificado TLS autofirmado",
                "Fallo en handshake TLS debido a certificado de seguridad desconocido",
            ],
            "descriptions": [
                "La integracion entre microservicios se interrumpe debido a que un componente interno utiliza un certificado TLS autofirmado no reconocido.",
                "El cliente HTTP del sistema arroja SSLHandshakeException indicando que no confia en la entidad emisora del certificado.",
                "La comunicacion cifrada entre servidores falla al no poder validar la cadena de certificacion en el almacen de certificados del sistema.",
                "Se reportan errores criticos de conexion segura debido a la introduccion de un certificado de prueba no firmado por la CA corporativa.",
            ],
        },
    ],
}

PREFIXES = [
    "Alerta de monitoreo Zabbix:",
    "Reporte de turno de guardia:",
    "Incidente reportado por operador:",
    "Alerta urgente del sistema de infraestructura:",
    "Notificacion de guardia tecnica:",
    "Aviso de monitoreo en tiempo real:",
    "Ticket generado por personal de guardia:",
    "Registro inicial de mesa de ayuda tecnica:",
]

SUFFIXES = [
    "Se requiere revision prioritaria por parte del equipo especialista.",
    "El problema persiste tras verificacion inicial en la consola de administracion.",
    "Se solicita intervencion de la guardia tecnica para mitigar la degradacion.",
    "Se escalo el incidente a la Unidad de Operaciones e Infraestructura Tecnologica.",
    "El impacto afecta la continuidad operativa de los servicios de la entidad.",
    "Los logs iniciales adjuntos confirman la anomalia reportada.",
    "Se procede al registro para su correspondiente clasificacion y tratamiento.",
    "Agradecemos la asignacion oportuna al area tecnica pertinente.",
]
