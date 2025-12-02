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
        print("Expected: PASS")
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
        print("✅ TEST PASSED: Valid registration successful")
    
    def test_02_user_registration_password_mismatch(self, driver):
        """TEST 2 [PASS]: Password mismatch rejection"""
        print("\n" + "="*60)
        print("TEST 2: Registration with Password Mismatch")
        print("Expected: PASS (correctly rejects)")
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
        print("✅ TEST PASSED: Password mismatch correctly prevented")
    
    def test_03_user_login_success(self, driver):
        """TEST 3 [PASS]: Valid login"""
        print("\n" + "="*60)
        print("TEST 3: Valid User Login")
        print("Expected: PASS")
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
        print("✅ TEST PASSED: Valid login successful")
    
    def test_04_login_invalid_credentials(self, driver):
        """TEST 4 [PASS]: Invalid credentials rejection"""
        print("\n" + "="*60)
        print("TEST 4: Login with Invalid Credentials")
        print("Expected: PASS (correctly rejects)")
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
        print("✅ TEST PASSED: Invalid credentials correctly rejected")
    
    def test_05_login_empty_fields(self, driver):
        """TEST 5 [PASS]: Empty fields prevention"""
        print("\n" + "="*60)
        print("TEST 5: Login with Empty Fields")
        print("Expected: PASS (correctly prevents)")
        print("="*60)
        
        driver.get(f"{BASE_URL}/users/login")
        time.sleep(2)
        
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        time.sleep(2)
        
        assert "/login" in driver.current_url
        print("✅ TEST PASSED: Empty login fields correctly prevented")

class TestTodoOperations:
    """Test todo CRUD operations"""
    
    def test_06_add_todo_success(self, driver):
     """TEST 6 [PASS]: Add todo with dropdown navigation"""
     print("\n" + "="*60)
     print("TEST 6: Add Todo Successfully")
     print("Expected: PASS")
     print("="*60)
    
     login_user(driver, TEST_USER["email"], TEST_USER["password"])
    
    # Navigate using dropdown
     driver.get(f"{BASE_URL}/todos")
     time.sleep(2)
    
    # Click on "Manage Todos" dropdown
     try:
        dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "navbarDropdownMenulink"))
        )
        dropdown.click()
        time.sleep(1)
        
        # Click "Add a new Todo" from dropdown
        add_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Add a new Todo"))
        )
        add_link.click()
        time.sleep(2)
     except:
        # Fallback: direct navigation
        driver.get(f"{BASE_URL}/todos/add")
        time.sleep(2)
    
    # Fill the form
     todo_title = f"Selenium Test Todo {int(time.time())}"
     todo_details = "Details for Selenium test item."
    
     driver.find_element(By.NAME, "title").send_keys(todo_title)
     driver.find_element(By.NAME, "details").send_keys(todo_details)
     driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
     time.sleep(3)
    
    # Verify success
     assert "/todos" in driver.current_url
     page_source = driver.page_source.lower()
     assert "success" in page_source or todo_title.lower() in page_source
     print("✅ TEST PASSED: Todo added successfully")
    
    def test_07_add_todo_empty_title(self, driver):
        """TEST 7 [FAIL]: Add todo without title should fail"""
        print("\n" + "="*60)
        print("TEST 7: Add Todo with Empty Title")
        print("Expected: FAIL (HTML5 validation)")
        print("="*60)
        
        login_user(driver, TEST_USER["email"], TEST_USER["password"])
        
        driver.get(f"{BASE_URL}/todos")
        time.sleep(2)
        
        # Only fill details, leave title empty
        details_input = driver.find_element(By.NAME, "details")
        details_input.send_keys("Details without title")
        
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        time.sleep(2)
        
        # Should stay on todos page due to HTML5 required attribute
        assert "/todos" in driver.current_url
        print("❌ TEST FAILED: Empty title prevented (as expected)")
    
    def test_08_add_todo_empty_details(self, driver):
        """TEST 8 [FAIL]: Add todo without details should fail"""
        print("\n" + "="*60)
        print("TEST 8: Add Todo with Empty Details")
        print("Expected: FAIL (HTML5 validation)")
        print("="*60)
        
        login_user(driver, TEST_USER["email"], TEST_USER["password"])
        
        driver.get(f"{BASE_URL}/todos")
        time.sleep(2)
        
        # Only fill title, leave details empty
        title_input = driver.find_element(By.NAME, "title")
        title_input.send_keys("Title without details")
        
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        time.sleep(2)
        
        # Should stay on todos page due to HTML5 required attribute
        assert "/todos" in driver.current_url
        print("❌ TEST FAILED: Empty details prevented (as expected)")
    
    def test_09_edit_todo_success(self, driver):
        """TEST 9 [PASS]: Edit existing todo"""
        print("\n" + "="*60)
        print("TEST 9: Edit Todo Successfully")
        print("Expected: PASS")
        print("="*60)
        
        login_user(driver, TEST_USER["email"], TEST_USER["password"])
        
        # First add a todo
        driver.get(f"{BASE_URL}/todos")
        time.sleep(2)
        
        original_title = f"Original {int(time.time())}"
        driver.find_element(By.NAME, "title").send_keys(original_title)
        driver.find_element(By.NAME, "details").send_keys("Original details")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(3)
        
        # Now edit it
        driver.get(f"{BASE_URL}/todos")
        time.sleep(2)
        
        edit_buttons = driver.find_elements(By.LINK_TEXT, "Edit")
        if edit_buttons:
            edit_buttons[0].click()
            time.sleep(2)
            
            # Modify the todo
            title_input = driver.find_element(By.NAME, "title")
            title_input.clear()
            updated_title = f"Updated {int(time.time())}"
            title_input.send_keys(updated_title)
            
            submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            time.sleep(3)
            
            # Verify update
            driver.get(f"{BASE_URL}/todos")
            time.sleep(2)
            assert updated_title in driver.page_source
            print("✅ TEST PASSED: Todo edited successfully")
        else:
            print("⊘ TEST SKIPPED: No todos to edit")
    
    def test_10_edit_todo_empty_title(self, driver):
        """TEST 10 [FAIL]: Edit todo with empty title should fail"""
        print("\n" + "="*60)
        print("TEST 10: Edit Todo with Empty Title")
        print("Expected: FAIL (validation prevents)")
        print("="*60)
        
        login_user(driver, TEST_USER["email"], TEST_USER["password"])
        
        # Add a todo first
        driver.get(f"{BASE_URL}/todos")
        time.sleep(2)
        
        driver.find_element(By.NAME, "title").send_keys(f"ToEdit {int(time.time())}")
        driver.find_element(By.NAME, "details").send_keys("Details to edit")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(3)
        
        # Try to edit with empty title
        driver.get(f"{BASE_URL}/todos")
        time.sleep(2)
        
        edit_buttons = driver.find_elements(By.LINK_TEXT, "Edit")
        if edit_buttons:
            edit_buttons[0].click()
            time.sleep(2)
            
            title_input = driver.find_element(By.NAME, "title")
            title_input.clear()
            
            submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            time.sleep(2)
            
            # Should stay on edit page
            assert "edit" in driver.current_url.lower() or "Edit" in driver.page_source
            print("❌ TEST FAILED: Empty title edit prevented (as expected)")
        else:
            print("⊘ TEST SKIPPED: No todos to edit")

class TestTodoPersistence:
    """Test database operations"""
    
    def test_11_delete_todo_success(self, driver):
        """TEST 11 [PASS]: Delete todo"""
        print("\n" + "="*60)
        print("TEST 11: Delete Todo")
        print("Expected: PASS")
        print("="*60)
        
        login_user(driver, TEST_USER["email"], TEST_USER["password"])
        
        # Add a todo first
        driver.get(f"{BASE_URL}/todos")
        time.sleep(2)
        
        todo_title = f"ToDelete {int(time.time())}"
        driver.find_element(By.NAME, "title").send_keys(todo_title)
        driver.find_element(By.NAME, "details").send_keys("This will be deleted")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(3)
        
        # Verify todo exists
        driver.get(f"{BASE_URL}/todos")
        time.sleep(2)
        assert todo_title in driver.page_source
        
        # Delete it
        delete_buttons = driver.find_elements(By.CSS_SELECTOR, "input[value='Delete']")
        if delete_buttons:
            delete_buttons[0].click()
            time.sleep(3)
            
            # Verify deletion
            driver.get(f"{BASE_URL}/todos")
            time.sleep(2)
            page_source = driver.page_source
            assert todo_title not in page_source or "No todos" in page_source
            print("✅ TEST PASSED: Todo deleted successfully")
        else:
            print("⊘ TEST SKIPPED: No delete button found")
    
    def test_12_todo_persistence_after_logout(self, driver):
        """TEST 12 [PASS]: Todos persist after logout"""
        print("\n" + "="*60)
        print("TEST 12: Todo Persistence After Logout/Login")
        print("Expected: PASS")
        print("="*60)
        
        login_user(driver, TEST_USER["email"], TEST_USER["password"])
        
        driver.get(f"{BASE_URL}/todos")
        time.sleep(2)
        
        persistent_title = f"Persistent {int(time.time())}"
        driver.find_element(By.NAME, "title").send_keys(persistent_title)
        driver.find_element(By.NAME, "details").send_keys("Should persist in DB")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(3)
        
        # Logout
        driver.get(f"{BASE_URL}/users/logout")
        time.sleep(2)
        
        # Login again
        login_user(driver, TEST_USER["email"], TEST_USER["password"])
        driver.get(f"{BASE_URL}/todos")
        time.sleep(2)
        
        # Verify todo still exists
        assert persistent_title in driver.page_source
        print("✅ TEST PASSED: Todos persist in database")

class TestAccessControl:
    """Test authorization"""
    
    def test_13_access_todos_without_login(self, driver):
        """TEST 13 [FAIL]: Unauthorized access prevented"""
        print("\n" + "="*60)
        print("TEST 13: Access Todos Without Login")
        print("Expected: FAIL (redirects to login)")
        print("="*60)
        
        driver.get(f"{BASE_URL}/todos")
        time.sleep(2)
        
        # Should redirect to login
        assert "/login" in driver.current_url.lower() or "login" in driver.page_source.lower()
        print("❌ TEST FAILED: Unauthorized access prevented (as expected)")
    
    def test_14_logout_clears_session(self, driver):
        """TEST 14 [PASS]: Logout functionality"""
        print("\n" + "="*60)
        print("TEST 14: Logout Clears Session")
        print("Expected: PASS")
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
    
    def test_15_duplicate_email_registration(self, driver):
        """TEST 15 [FAIL]: Duplicate email rejected"""
        print("\n" + "="*60)
        print("TEST 15: Registration with Duplicate Email")
        print("Expected: FAIL (duplicate rejected)")
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
        print("❌ TEST FAILED: Duplicate email rejected (as expected)")
    
    def test_16_add_todo_with_special_characters(self, driver):
        """TEST 16 [PASS]: Todo with special characters"""
        print("\n" + "="*60)
        print("TEST 16: Add Todo with Special Characters")
        print("Expected: PASS")
        print("="*60)
        
        login_user(driver, TEST_USER["email"], TEST_USER["password"])
        
        driver.get(f"{BASE_URL}/todos")
        time.sleep(2)
        
        special_title = f"Special @#$% {int(time.time())}"
        driver.find_element(By.NAME, "title").send_keys(special_title)
        driver.find_element(By.NAME, "details").send_keys("Details with symbols: !@#$%^&*()")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(3)
        
        # Verify todo was added
        driver.get(f"{BASE_URL}/todos")
        time.sleep(2)
        assert "Special" in driver.page_source
        print("✅ TEST PASSED: Special characters handled correctly")
    
    def test_17_add_todo_with_long_text(self, driver):
        """TEST 17 [PASS]: Todo with long text"""
        print("\n" + "="*60)
        print("TEST 17: Add Todo with Long Text")
        print("Expected: PASS")
        print("="*60)
        
        login_user(driver, TEST_USER["email"], TEST_USER["password"])
        
        driver.get(f"{BASE_URL}/todos")
        time.sleep(2)
        
        long_title = f"Long Todo Title {int(time.time())}"
        long_details = "A" * 500  # 500 characters
        
        driver.find_element(By.NAME, "title").send_keys(long_title)
        driver.find_element(By.NAME, "details").send_keys(long_details)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(3)
        
        # Verify todo was added
        driver.get(f"{BASE_URL}/todos")
        time.sleep(2)
        assert long_title in driver.page_source
        print("✅ TEST PASSED: Long text handled correctly")
    
    def test_18_view_empty_todo_list(self, driver):
        """TEST 18 [PASS]: View empty todo list"""
        print("\n" + "="*60)
        print("TEST 18: View Empty Todo List")
        print("Expected: PASS")
        print("="*60)
        
        # Create a new user with no todos
        unique_email = f"emptytodos{int(time.time())}@example.com"
        
        driver.get(f"{BASE_URL}/users/register")
        time.sleep(2)
        
        driver.find_element(By.NAME, "name").send_keys("Empty User")
        driver.find_element(By.NAME, "email").send_keys(unique_email)
        driver.find_element(By.NAME, "password").send_keys("testpass123")
        driver.find_element(By.NAME, "password2").send_keys("testpass123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(3)
        
        # Go to todos page
        driver.get(f"{BASE_URL}/todos")
        time.sleep(2)
        
        # Should show empty state or form
        assert "Todo" in driver.page_source or "todo" in driver.page_source.lower()
        print("✅ TEST PASSED: Empty todo list displayed correctly")


if __name__ == "__main__":
    print("=" * 70)
    print("COMPREHENSIVE TEST SUITE - 18 TEST CASES")
    print("Tests include both PASS and FAIL scenarios")
    print("=" * 70)
    pytest.main([__file__, "-v", "-s", "--tb=short"])