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
            # Realizamos el proceso automatizado en una misma ventana del navegador
            driver = iniciar_driver()
            automatizar_proceso_consejo_judicial(driver, cedula)
            automatizar_proceso_gestion_fiscalias(driver, cedula)
            automatizar_proceso_supa(driver, cedula)
        except Exception as e:
            error_message = f"Error al consultar: {traceback.format_exc()}"
        finally:
            # No cerramos el navegador para que las pestañas permanezcan abiertas
            pass

    return render_template("index.html", cedula=cedula, error_message=error_message)


def iniciar_driver():
    """
    Inicializa el navegador Chrome y devuelve la instancia del driver.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Descomentar esta línea si deseas que el navegador no sea visible:
    # options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


def automatizar_proceso_consejo_judicial(driver, cedula):
    """
    Automatiza el proceso de consulta en la página del Consejo Judicial.
    """
    try:
        print("Cargando la página del Consejo Judicial...")
        url = "https://consultas.funcionjudicial.gob.ec/informacionjudicialindividual/pages/index.jsf"
        driver.get(url)

        print("Esperando que la página cargue completamente...")
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

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
        nueva_pestana = [tab for tab in driver.window_handles if tab != driver.current_window_handle][0]
        driver.switch_to.window(nueva_pestana)
        print("Nueva pestaña abierta con el documento.")

    except Exception as e:
        print(f"Error durante el proceso en Consejo Judicial: {e}")
        traceback.print_exc()


def automatizar_proceso_gestion_fiscalias(driver, cedula):
    """
    Automatiza el proceso de consulta en la página de Gestión de Fiscalías.
    """
    try:
        print("Abriendo una nueva pestaña para la Gestión de Fiscalías...")
        driver.execute_script("window.open('');")
        nueva_pestana = driver.window_handles[-1]
        driver.switch_to.window(nueva_pestana)

        url = "https://www.gestiondefiscalias.gob.ec/siaf/informacion/web/noticiasdelito/index.php"
        driver.get(url)

        print("Esperando que la página cargue completamente...")
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Llenar campo de cédula
        print("Llenando el campo de cédula en Gestión de Fiscalías...")
        campo_cedula = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "pwd"))
        )
        campo_cedula.clear()
        campo_cedula.send_keys(cedula)

        # Hacer clic en el botón "Buscar Denuncia"
        print("Haciendo clic en el botón 'Buscar Denuncia'...")
        boton_buscar = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.ID, "btn_buscar_denuncia"))
        )
        boton_buscar.click()

        print("Consulta en Gestión de Fiscalías completada. Ventana abierta.")

    except Exception as e:
        print(f"Error durante el proceso en Gestión de Fiscalías: {e}")
        traceback.print_exc()


def automatizar_proceso_supa(driver, cedula):
    """
    Automatiza el proceso de consulta en la página de SUPA.
    """
    try:
        print("Abriendo una nueva pestaña para la página de SUPA...")
        driver.execute_script("window.open('');")
        nueva_pestana = driver.window_handles[-1]
        driver.switch_to.window(nueva_pestana)

        url = "https://supa.funcionjudicial.gob.ec/pensiones/publico/consulta.jsf"
        driver.get(url)

        print("Esperando que la página cargue completamente...")
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Llenar campo de cédula
        print("Llenando el campo de cédula en SUPA...")
        campo_cedula = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "form:t_texto_cedula"))
        )
        campo_cedula.clear()
        campo_cedula.send_keys(cedula)

        # Hacer clic en el botón "Buscar"
        print("Haciendo clic en el botón 'Buscar' en SUPA...")
        boton_buscar = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.ID, "form:b_buscar_cedula"))
        )
        boton_buscar.click()

        print("Consulta en SUPA completada. Ventana abierta.")

    except Exception as e:
        print(f"Error durante el proceso en SUPA: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    app.run(debug=True, port=5001)
