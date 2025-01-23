from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import traceback

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    cedula = request.form.get("cedula", "")
    error_message = None

    if cedula:
        try:
            # Realizamos el proceso automatizado
            automatizar_proceso(cedula)
        except Exception as e:
            error_message = f"Error al consultar: {traceback.format_exc()}"

    return render_template("index.html", cedula=cedula, error_message=error_message)


def automatizar_proceso(cedula):
    """
    Automatiza el proceso completo en el navegador.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Descomentar esta línea si deseas que el navegador no sea visible:
    # options.add_argument("--headless")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        print("Cargando la página del Consejo Judicial...")
        url = "https://consultas.funcionjudicial.gob.ec/informacionjudicialindividual/pages/index.jsf"
        driver.get(url)

        print("Esperando que la página cargue completamente...")
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Guardar el manejador de la pestaña principal
        original_tab = driver.current_window_handle

        # Seleccionar checkbox de cédula
        print("Seleccionando la opción 'Cédula'...")
        opcion_cedula = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//md-radio-button[@value='cedula']"))
        )
        driver.execute_script("arguments[0].click();", opcion_cedula)

        # Llenar campo de cédula
        print("Llenando el campo de cédula...")
        campo_cedula = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.ID, "input_3"))
        )
        campo_cedula.clear()
        campo_cedula.send_keys(cedula)

        # Hacer clic en buscar
        print("Haciendo clic en el botón de búsqueda...")
        boton_buscar = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@ng-click='vmAntecedente.buscarAntecedentePenal()']"))
        )
        boton_buscar.click()

        # Esperar que el botón "Visualizar" esté disponible
        print("Esperando que el botón 'Visualizar' esté disponible...")
        boton_visualizar = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@ng-click='vmAntecedente.imprimirReporte()']"))
        )
        print("Haciendo clic en el botón 'Visualizar'...")
        boton_visualizar.click()

        # Esperar que se abra una nueva pestaña
        print("Esperando que se abra una nueva pestaña...")
        WebDriverWait(driver, 30).until(EC.number_of_windows_to_be(2))

        # Cambiar a la nueva pestaña
        nueva_pestana = [tab for tab in driver.window_handles if tab != original_tab][0]
        driver.switch_to.window(nueva_pestana)
        print("Nueva pestaña abierta con el documento.")

        # Cerrar la pestaña del Consejo Judicial
        print("Cerrando la pestaña del Consejo Judicial...")
        driver.switch_to.window(original_tab)
        driver.close()

        # Volver a la pestaña con el documento
        driver.switch_to.window(nueva_pestana)
        print("Proceso completado. Documento visible en la nueva pestaña.")

    except Exception as e:
        print(f"Error durante el proceso: {e}")
        traceback.print_exc()
    finally:
        print("Finalizando el proceso automatizado. El navegador sigue abierto para interactuar.")


if __name__ == "__main__":
    app.run(debug=True, port=5001)
