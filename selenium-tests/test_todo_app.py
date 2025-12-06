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
    "email": "testuser@example.com",
    "password": "testpassword123"
}

@pytest.fixture(scope="session", autouse=True)
def setup_test_user():
    """Setup test user once before all tests"""
    print("\n" + "=" * 60)
    print("SETTING UP TEST USER...")
    print("=" * 60)
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
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
    """Setup headless Chrome driver for each test"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    
    yield driver
    driver.quit()

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

class TestTodoOperations:
    """Test todo CRUD operations"""
    
    def test_06_add_todo_success(self, driver):
        print("TEST 6: Add todo successfully")
        print("\n" + "="*60)
        print("TEST 6: Add Todo Successfully")
        
        print("="*60)
    
    # Login first
        login_user(driver, TEST_USER["email"], TEST_USER["password"])
        time.sleep(2)
        
        # Direct navigation to add todo page
        driver.get(f"{BASE_URL}/todos/add")
        time.sleep(3)
        
        # Wait for the form to be fully loaded
        try:
            title_field = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.NAME, "title"))
            )
            details_field = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.NAME, "details"))
            )
            print("✓ Form fields loaded successfully")
        except TimeoutException:
            print(f"⚠️  TIMEOUT: Form not loaded. Current URL: {driver.current_url}")
            print(f"⚠️  Page title: {driver.title}")
            raise
        
        # Generate unique todo data
        todo_title = f"Selenium Test Todo {int(time.time())}"
        todo_details = "Test details for automated todo"
        
        print(f"Adding todo: {todo_title}")
        
        # Clear and fill the fields - IMPORTANT: Use JavaScript to bypass client-side validation issues
        driver.execute_script("arguments[0].value = '';", title_field)
        driver.execute_script("arguments[0].value = arguments[1];", title_field, todo_title)
        
        driver.execute_script("arguments[0].value = '';", details_field)
        driver.execute_script("arguments[0].value = arguments[1];", details_field, todo_details)
        
        # Verify fields were filled
        print(f"✓ Title field value: {title_field.get_attribute('value')[:50]}")
        print(f"✓ Details field value: {details_field.get_attribute('value')[:50]}")
        
        # Find the form element
        form = driver.find_element(By.CSS_SELECTOR, "form[action='/todos']")
        print(f"✓ Form found with action: {form.get_attribute('action')}")
        print(f"✓ Form method: {form.get_attribute('method')}")
        
        # Find submit button
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        
        print("✓ About to submit form...")
        
        # Method 1: Try regular click
        try:
            submit_button.click()
            print("✓ Form submitted via button click")
        except Exception as e:
            print(f"⚠️  Button click failed: {e}")
            # Method 2: Try JavaScript submit
            print("✓ Trying JavaScript form submit...")
            driver.execute_script("arguments[0].submit();", form)
            print("✓ Form submitted via JavaScript")
        
        # Wait for redirect with explicit wait
        print("⏳ Waiting for redirect...")
        try:
            WebDriverWait(driver, 10).until(
                lambda d: "/todos/add" not in d.current_url.lower()
            )
            print("✓ Redirected away from /todos/add")
        except TimeoutException:
            print("⚠️  No redirect detected after 10 seconds")
        
        time.sleep(2)
        
        # Check if successfully redirected and todo was added
        current_url = driver.current_url.lower()
        page_source = driver.page_source
        
        print(f"\nCurrent URL after submit: {driver.current_url}")
        
        # DEBUG: Check for error messages on the page
        try:
            error_elements = driver.find_elements(By.CSS_SELECTOR, ".alert-danger, .alert-error, .error, .alert")
            if error_elements:
                print("\n⚠️  MESSAGES FOUND ON PAGE:")
                for error in error_elements:
                    error_text = error.text
                    if error_text.strip():
                        print(f"   - {error_text}")
        except Exception as e:
            print(f"Could not check for errors: {e}")
        
        # Multiple success criteria
        redirected_to_todos = "todos" in current_url and "add" not in current_url
        has_success_message = "success" in page_source.lower()
        todo_in_page = todo_title.lower() in page_source.lower()
        
        print(f"\n✓ Redirected to /todos: {redirected_to_todos}")
        print(f"✓ Success message present: {has_success_message}")
        print(f"✓ Todo appears in page: {todo_in_page}")
        
        success = redirected_to_todos or has_success_message or todo_in_page
        
        if not success:
            print(f"\n❌ FAILED - Current URL: {driver.current_url}")
            print(f"❌ Page does not contain success indicators")
            # Save full page source for debugging
            with open("failed_page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("❌ Full page source saved to: failed_page_source.html")
            print("\n📄 First 1000 chars of page source:")
            print(page_source[:1000])
            
        assert success, f"Todo was not added successfully. URL: {driver.current_url}"
        print("✅ TEST PASSED: Todo added successfully")
        

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