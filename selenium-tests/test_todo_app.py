import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time


# Base URL of your application
BASE_URL = "http://localhost:5000"

# Test credentials
TEST_USER = {
    "name": "Test User",
    "email": "ayeshaengineer@example.com",
    "password": "passrocky_123"
}

@pytest.fixture(scope="session", autouse=True)
def setup_test_user():
    """Setup test user once before all tests"""
    print("\n" + "=" * 60)
    print("SETTING UP TEST USER...")
    print("=" * 60)
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.get(f"{BASE_URL}/users/register")
        time.sleep(2)
        
        name_input = driver.find_element(By.NAME, "name")
        email_input = driver.find_element(By.NAME, "email")
        password_input = driver.find_element(By.NAME, "password")
        password2_input = driver.find_element(By.NAME, "password2")
        
        name_input.send_keys(TEST_USER["name"])
        email_input.send_keys(TEST_USER["email"])
        password_input.send_keys(TEST_USER["password"])
        password2_input.send_keys(TEST_USER["password"])
        
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        time.sleep(3)
        
        print(f"✓ Test user setup complete: {TEST_USER['email']}")
    except Exception as e:
        print(f"⚠ Test user might already exist (this is OK)")
    finally:
        driver.quit()
    
    print("=" * 60 + "\n")

@pytest.fixture(scope="function")
def driver():
    
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        # Use a new temporary user profile
        chrome_options.add_argument("--user-data-dir=C:/tmp/selenium_profile")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")

        # Disable Chrome password manager
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.notifications": 2  # block notifications
        }
        chrome_options.add_experimental_option("prefs", prefs)

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


        driver.implicitly_wait(10)
            
        yield driver
        driver.quit()
def open_todo_dropdown(driver):
    """Click the Manage Todos dropdown and wait for menu items"""
    dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "navbarDropdownMenulink"))
    )
    dropdown.click()
    # Wait for the dropdown links to appear
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.LINK_TEXT, "Add a new Todo"))
    )
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.LINK_TEXT, "List Todos"))
    )
    time.sleep(0.5)
def login_user(driver, email, password):
    """Helper function to login a user"""
    try:
        driver.get(f"{BASE_URL}/users/login")
        time.sleep(2)
        
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        password_input = driver.find_element(By.NAME, "password")
        
        email_input.clear()
        email_input.send_keys(email)
        password_input.clear()
        password_input.send_keys(password)
        
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        time.sleep(3)
    except Exception as e:
        print(f"Login failed: {str(e)}")
        raise

class TestUserAuthentication:
    """Test user authentication - both valid and invalid cases"""
    
    def test_01_user_registration_success(self, driver):
        """TEST 1 [PASS]: Valid user registration"""
        print("\n" + "="*60)
        print("TEST 1: Valid User Registration")
        
        print("="*60)
        
        driver.get(f"{BASE_URL}/users/register")
        time.sleep(2)
        
        name_input = driver.find_element(By.NAME, "name")
        email_input = driver.find_element(By.NAME, "email")
        password_input = driver.find_element(By.NAME, "password")
        password2_input = driver.find_element(By.NAME, "password2")
        
        unique_email = f"testuser{int(time.time())}@example.com"
        name_input.send_keys("New Test User")
        email_input.send_keys(unique_email)
        password_input.send_keys("testpass123")
        password2_input.send_keys("testpass123")
        
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        time.sleep(3)
        
        current_url = driver.current_url
        assert "/register" not in current_url or "success" in driver.page_source.lower()
        print("TEST PASSED: Valid registration successful")
    
    def test_02_user_registration_password_mismatch(self, driver):
        """TEST 2 [PASS]: Password mismatch rejection"""
        print("\n" + "="*60)
        print("TEST 2: Registration with Password Mismatch")
        
        print("="*60)
        
        driver.get(f"{BASE_URL}/users/register")
        time.sleep(2)
        
        name_input = driver.find_element(By.NAME, "name")
        email_input = driver.find_element(By.NAME, "email")
        password_input = driver.find_element(By.NAME, "password")
        password2_input = driver.find_element(By.NAME, "password2")
        
        unique_email = f"mismatch{int(time.time())}@example.com"
        name_input.send_keys("Mismatch User")
        email_input.send_keys(unique_email)
        password_input.send_keys("password123")
        password2_input.send_keys("differentpassword")
        
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        time.sleep(3)
        
        assert "/register" in driver.current_url or "password" in driver.page_source.lower()
        print("TEST PASSED: Password mismatch correctly prevented")
    
    def test_03_user_login_success(self, driver):
        """TEST 3 [PASS]: Valid login"""
        print("\n" + "="*60)
        print("TEST 3: Valid User Login")
        
        print("="*60)
        
        driver.get(f"{BASE_URL}/users/login")
        time.sleep(2)
        
        email_input = driver.find_element(By.NAME, "email")
        password_input = driver.find_element(By.NAME, "password")
        
        email_input.send_keys(TEST_USER["email"])
        password_input.send_keys(TEST_USER["password"])
        
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        time.sleep(3)
        
        current_url = driver.current_url
        assert "/login" not in current_url
        print("TEST PASSED: Valid login successful")
    
    def test_04_login_invalid_credentials(self, driver):
        """TEST 4 [PASS]: Invalid credentials rejection"""
        print("\n" + "="*60)
        print("TEST 4: Login with Invalid Credentials")
        
        print("="*60)
        
        driver.get(f"{BASE_URL}/users/login")
        time.sleep(2)
        
        email_input = driver.find_element(By.NAME, "email")
        password_input = driver.find_element(By.NAME, "password")
        
        email_input.send_keys("wrong@example.com")
        password_input.send_keys("wrongpassword")
        
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        time.sleep(3)
        
        page_source = driver.page_source.lower()
        assert "login" in driver.current_url.lower() or "error" in page_source or "invalid" in page_source
        print("Should give error--> Invalid credentials correctly rejected")
    
    def test_05_login_empty_fields(self, driver):
        """TEST 5 [PASS]: Empty fields prevention"""
        print("\n" + "="*60)
        print("TEST 5: Login with Empty Fields")
        
        print("="*60)
        
        driver.get(f"{BASE_URL}/users/login")
        time.sleep(2)
        
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        time.sleep(2)
        
        assert "/login" in driver.current_url
        print("Should give error --> Empty login fields correctly prevented")

class TestTodoManagement:
    def test_06_add_todo_success(self, driver):
        print("\n" + "="*60)
        print("TEST 6: Add Todo Successfully")
        print("="*60)

        login_user(driver, TEST_USER["email"], TEST_USER["password"])
        open_todo_dropdown(driver)

        driver.find_element(By.LINK_TEXT, "Add a new Todo").click()
        time.sleep(1)

        title_input = driver.find_element(By.NAME, "title")
        due_date_input = driver.find_element(By.NAME, "duedate")
        details_input = driver.find_element(By.NAME, "details")

        todo_title = f"Todo {int(time.time())}"
        title_input.send_keys(todo_title)
        due_date_input.send_keys("2025-12-31")
        details_input.send_keys("Adding via Selenium test")

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)

        assert "/todos" in driver.current_url.lower()
        assert todo_title in driver.page_source
        print("TEST PASSED: Todo added successfully")

    def test_07_todos_list_shows_items(self, driver):
        print("\n" + "="*60)
        print("TEST 7: Todos List Display")
        print("="*60)

        login_user(driver, TEST_USER["email"], TEST_USER["password"])
        open_todo_dropdown(driver)

        driver.find_element(By.LINK_TEXT, "List Todos").click()
        time.sleep(1)

        assert "todo" in driver.page_source.lower()
        print("TEST PASSED: Todos list visible to user")



class TestAccessControl:
    """Test authorization"""
    
    def test_7_access_todos_without_login(self, driver):
        """TEST 7  Unauthorized access prevented"""
        print("\n" + "="*60)
        print("TEST 7: Access Todos Without Login")
        print("="*60)
        
        driver.get(f"{BASE_URL}/todos")
        time.sleep(2)
        
        # Should redirect to login
        assert "/login" in driver.current_url.lower() or "login" in driver.page_source.lower()
        print(" Should give error--> Unauthorized access prevented (as expected)")
    
    def test_8_logout_clears_session(self, driver):
        """TEST 8 [PASS]: Logout functionality"""
        print("\n" + "="*60)
        print("TEST 8: Logout Clears Session")
        
        print("="*60)
        
        login_user(driver, TEST_USER["email"], TEST_USER["password"])
        time.sleep(2)
        
        # Logout
        driver.get(f"{BASE_URL}/users/logout")
        time.sleep(2)
        
        # Try to access protected page
        driver.get(f"{BASE_URL}/todos")
        time.sleep(2)
        
        # Should redirect to login
        assert "/login" in driver.current_url.lower()
        print("✅ TEST PASSED: Logout cleared session")

class TestEdgeCases:
    """Test edge cases and validation"""
    
    def test_9_duplicate_email_registration(self, driver):
        """TEST 9 [FAIL]: Duplicate email rejected"""
        print("\n" + "="*60)
        print("TEST 9: Registration with Duplicate Email")
        
        print("="*60)
        
        driver.get(f"{BASE_URL}/users/register")
        time.sleep(2)
        
        # Try to register with existing email
        driver.find_element(By.NAME, "name").send_keys("Duplicate User")
        driver.find_element(By.NAME, "email").send_keys(TEST_USER["email"])
        driver.find_element(By.NAME, "password").send_keys("newpass123")
        driver.find_element(By.NAME, "password2").send_keys("newpass123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(3)
        
        # Should show error or stay on register page
        page_source = driver.page_source.lower()
        assert "/register" in driver.current_url or "exist" in page_source or "error" in page_source
        print(" Should give error --> Duplicate email rejected (as expected)")
    
    

if __name__ == "__main__":
    print("=" * 70)
    print("COMPREHENSIVE TEST SUITE - 10 TEST CASES")
    print("Tests include both PASS and FAIL scenarios")
    print("=" * 70)
    pytest.main([__file__, "-v", "-s", "--tb=short"])
