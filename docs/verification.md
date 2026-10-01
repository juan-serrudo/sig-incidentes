# Comprobaciones de la entrega

## Entrenamiento ejecutado

- 1.104 mensajes de cinco categorías, organizados en 60 familias.
- 736 / 184 / 184 mensajes para entrenamiento, validación y prueba.
- TF-IDF y regresión logística entrenados con C = 1 y C = 4; selección de C = 4 por validación.
- Macro-F1 de prueba: modelo 0,7014; reglas 0,8778. Se informa que la regla obtuvo mejor resultado.
- Revisión en prueba: 67 mensajes marcados; 117 superan el criterio, con exactitud de 88,9%. No se alcanza el 90% buscado en validación.
- Informe, matriz y predicciones individuales guardados.

## Pruebas automáticas

Comando: `python -m pytest -q`.

**Resultado: 28 pruebas correctas.** Incluyen:

- Reproducibilidad y validación del conjunto sintético.
- Familias y textos normalizados separados entre particiones.
- Rechazo de duplicados y etiquetas contradictorias.
- Reglas por palabras completas y respaldo explícito.
- Cálculo de métricas sobre todos los casos.
- Selección del umbral y alternativa que marca todos los casos para revisión.
- Aviso cuando no se reconoce vocabulario.
- Coincidencia entre informe, pipeline y API.
- Vocabulario fijo durante inferencia y contribuciones correctas de términos.
- Rechazo de mensajes y campos inválidos.
- Archivos estáticos, documentación de API y respuesta cuando falta el modelo.

`pip check` no detectó incompatibilidades. Starlette emite un aviso de deprecación de un alias de AnyIO en el cliente de pruebas; no impide la ejecución y no se oculta.

## Frontend y escenarios

Se revisa la sintaxis de `frontend/app.js` con `node --check`. Node se utilizó solo en la comprobación y no es necesario para instalar o ejecutar la aplicación.

Se comprueban identificadores HTML, etiquetas del formulario, recursos y enlaces relativos. Los seis escenarios se ejecutan mediante el cliente de pruebas de la API y se guardan en `artifacts/example_predictions.json`. Sus resultados son observaciones de la demostración, no una nueva estimación independiente del desempeño.

En los seis escenarios la API respondió correctamente. El mensaje del teclado se marcó para revisión, pero el ambiguo y el de la cafetería no: el segundo recibió la categoría de accesos con un puntaje de 0,802. Este error concreto muestra que el umbral no detecta temas ajenos y que un puntaje alto no garantiza una clasificación correcta. La aplicación requiere revisión humana y no debe enrutar solicitudes reales automáticamente.

**Limitación:** no se completó la revisión visual ni la interacción del frontend en navegador. La herramienta bloqueó el acceso porque no pudo verificar su política administrativa. No se eludió el control. La verificación de la API y de los archivos no sustituye una prueba visual.

## Revisión manual pendiente

1. Iniciar con `python run.py` y abrir la dirección indicada.
2. Ejecutar los seis escenarios y leer alternativas y avisos.
3. Modificar el texto y comprobar que desaparece la respuesta anterior.
4. Enviar un texto inválido y revisar el mensaje de error.
5. Abrir Resultados y Datos y método; contrastar las cifras con el informe.
6. Navegar con teclado y probar una ventana estrecha.

Estas comprobaciones manuales se declaran pendientes, no como aprobadas.
