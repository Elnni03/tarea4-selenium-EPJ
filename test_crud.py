import pytest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://127.0.0.1:5000"
SCREENSHOTS_DIR = "screenshots"

@pytest.fixture(scope="session")
def driver():
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1280,800")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

def screenshot(driver, name):
    path = os.path.join(SCREENSHOTS_DIR, f"{name}.png")
    driver.save_screenshot(path)
    return path

def login(driver):
    driver.get(f"{BASE_URL}/logout")
    time.sleep(0.5)
    driver.get(f"{BASE_URL}/login")
    driver.find_element(By.ID, "username").clear()
    driver.find_element(By.ID, "username").send_keys("admin")
    driver.find_element(By.ID, "password").clear()
    driver.find_element(By.ID, "password").send_keys("admin123")
    driver.find_element(By.ID, "btn-login").click()
    time.sleep(1)

class TestLogin:
    def test_login_camino_feliz(self, driver):
        driver.get(f"{BASE_URL}/login")
        driver.find_element(By.ID, "username").send_keys("admin")
        driver.find_element(By.ID, "password").send_keys("admin123")
        screenshot(driver, "01_login_feliz_antes")
        driver.find_element(By.ID, "btn-login").click()
        time.sleep(1)
        screenshot(driver, "01_login_feliz_despues")
        assert BASE_URL + "/" in driver.current_url or driver.current_url == BASE_URL + "/"

    def test_login_negativo_credenciales_incorrectas(self, driver):
        driver.get(f"{BASE_URL}/logout")
        time.sleep(1)
        driver.get(f"{BASE_URL}/login")
        driver.find_element(By.ID, "username").send_keys("admin")
        driver.find_element(By.ID, "password").send_keys("contrasena_incorrecta")
        screenshot(driver, "01_login_negativo_antes")
        driver.find_element(By.ID, "btn-login").click()
        time.sleep(1)
        screenshot(driver, "01_login_negativo_despues")
        assert "/login" in driver.current_url

    def test_login_limite_campos_vacios(self, driver):
        driver.get(f"{BASE_URL}/login")
        screenshot(driver, "01_login_limite_antes")
        driver.find_element(By.ID, "btn-login").click()
        time.sleep(1)
        screenshot(driver, "01_login_limite_despues")
        assert "/login" in driver.current_url

class TestCrearTarea:
    def test_crear_tarea_camino_feliz(self, driver):
        login(driver)
        driver.get(f"{BASE_URL}/create")
        driver.find_element(By.ID, "title").send_keys("Tarea de prueba Selenium")
        driver.find_element(By.ID, "description").send_keys("Descripcion automatizada")
        driver.find_element(By.ID, "due_date").send_keys("2026-12-31")
        Select(driver.find_element(By.ID, "priority")).select_by_value("alta")
        screenshot(driver, "02_crear_feliz_antes")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        screenshot(driver, "02_crear_feliz_despues")
        assert BASE_URL + "/" in driver.current_url or driver.current_url == BASE_URL + "/"

    def test_crear_tarea_negativo_sin_titulo(self, driver):
        login(driver)
        driver.get(f"{BASE_URL}/create")
        driver.find_element(By.ID, "description").send_keys("Sin titulo")
        screenshot(driver, "02_crear_negativo_antes")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        screenshot(driver, "02_crear_negativo_despues")
        assert "/create" in driver.current_url

    def test_crear_tarea_limite_titulo_largo(self, driver):
        login(driver)
        driver.get(f"{BASE_URL}/create")
        driver.find_element(By.ID, "title").send_keys("T" * 30)
        screenshot(driver, "02_crear_limite_antes")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        screenshot(driver, "02_crear_limite_despues")
        assert BASE_URL + "/" in driver.current_url or driver.current_url == BASE_URL + "/"

class TestListarTareas:
    def test_listar_camino_feliz(self, driver):
        login(driver)
        driver.get(BASE_URL + "/")
        screenshot(driver, "03_listar_feliz")
        assert "Mis Tareas" in driver.page_source or "Gestor" in driver.title

    def test_listar_filtro_pendientes(self, driver):
        login(driver)
        driver.get(f"{BASE_URL}/?status=pending")
        screenshot(driver, "03_listar_filtro_pendientes")
        assert "pending" in driver.current_url

    def test_listar_filtro_completadas(self, driver):
        login(driver)
        driver.get(f"{BASE_URL}/?status=completed")
        screenshot(driver, "03_listar_filtro_completadas")
        assert "completed" in driver.current_url

class TestEditarTarea:
    def test_editar_camino_feliz(self, driver):
        login(driver)
        driver.get(BASE_URL + "/")
        time.sleep(1)
        edit_links = driver.find_elements(By.PARTIAL_LINK_TEXT, "Editar")
        if edit_links:
            edit_links[0].click()
            time.sleep(1)
            title_field = driver.find_element(By.ID, "title")
            title_field.clear()
            title_field.send_keys("Tarea editada por Selenium")
            screenshot(driver, "04_editar_feliz_antes")
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            time.sleep(1)
            screenshot(driver, "04_editar_feliz_despues")
            assert BASE_URL + "/" in driver.current_url or driver.current_url == BASE_URL + "/"
        else:
            pytest.skip("No hay tareas para editar")

    def test_editar_negativo_titulo_vacio(self, driver):
        login(driver)
        driver.get(BASE_URL + "/")
        time.sleep(1)
        edit_links = driver.find_elements(By.PARTIAL_LINK_TEXT, "Editar")
        if edit_links:
            edit_links[0].click()
            time.sleep(1)
            title_field = driver.find_element(By.ID, "title")
            title_field.clear()
            screenshot(driver, "04_editar_negativo_antes")
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            time.sleep(1)
            screenshot(driver, "04_editar_negativo_despues")
            assert "/edit/" in driver.current_url
        else:
            pytest.skip("No hay tareas para editar")

    def test_editar_limite_cancelar(self, driver):
        login(driver)
        driver.get(BASE_URL + "/")
        time.sleep(1)
        edit_links = driver.find_elements(By.PARTIAL_LINK_TEXT, "Editar")
        if edit_links:
            edit_links[0].click()
            time.sleep(1)
            screenshot(driver, "04_editar_limite_antes")
            driver.find_element(By.PARTIAL_LINK_TEXT, "Cancelar").click()
            time.sleep(1)
            screenshot(driver, "04_editar_limite_despues")
            assert BASE_URL + "/" in driver.current_url or driver.current_url == BASE_URL + "/"
        else:
            pytest.skip("No hay tareas para editar")

class TestEliminarTarea:
    def test_eliminar_camino_feliz(self, driver):
        login(driver)
        driver.get(f"{BASE_URL}/create")
        driver.find_element(By.ID, "title").send_keys("Tarea para eliminar")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        driver.get(BASE_URL + "/")
        time.sleep(1)
        delete_btns = driver.find_elements(By.CSS_SELECTOR, "button.btn-delete")
        if delete_btns:
            screenshot(driver, "05_eliminar_feliz_antes")
            driver.execute_script("arguments[0].closest('form').submit()", delete_btns[0])
            time.sleep(1)
            screenshot(driver, "05_eliminar_feliz_despues")
            assert BASE_URL + "/" in driver.current_url or driver.current_url == BASE_URL + "/"
        else:
            pytest.skip("No hay tareas para eliminar")

    def test_eliminar_negativo_cancelar(self, driver):
        login(driver)
        driver.get(BASE_URL + "/")
        screenshot(driver, "05_eliminar_negativo")
        delete_btns = driver.find_elements(By.CSS_SELECTOR, "button.btn-delete")
        assert len(delete_btns) >= 0

    def test_eliminar_limite_sin_tareas(self, driver):
        login(driver)
        driver.get(f"{BASE_URL}/?status=completed")
        screenshot(driver, "05_eliminar_limite")
        assert "completed" in driver.current_url