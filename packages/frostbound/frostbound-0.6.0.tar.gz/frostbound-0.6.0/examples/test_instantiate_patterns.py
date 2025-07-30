"""
Test Patterns for frostbound.pydanticonf._instantiate

This file demonstrates how to test applications that use dynamic instantiation.
Testing configuration-driven applications requires special patterns.
"""

from typing import Any, Dict, List
from unittest.mock import Mock, patch

from rich.console import Console

from frostbound.pydanticonf import DynamicConfig, instantiate, register_dependency

console = Console()

# ============================================================================
# Example Classes for Testing
# ============================================================================


class EmailService:
    """Example service for testing."""

    def __init__(self, smtp_host: str, port: int = 587, username: str = ""):
        self.smtp_host = smtp_host
        self.port = port
        self.username = username
        self.sent_emails = []

    def send_email(self, to: str, subject: str, body: str) -> bool:
        email = {"to": to, "subject": subject, "body": body}
        self.sent_emails.append(email)
        return True


class DatabaseService:
    """Example database service for testing."""

    def __init__(self, connection_string: str, pool_size: int = 5):
        self.connection_string = connection_string
        self.pool_size = pool_size
        self.queries_executed = []

    def execute(self, query: str) -> List[Dict[str, Any]]:
        self.queries_executed.append(query)
        return [{"id": 1, "result": "mock_data"}]


class UserService:
    """Example service with dependencies for testing."""

    def __init__(self, database: DatabaseService, email: EmailService, cache_ttl: int = 3600):
        self.database = database
        self.email = email
        self.cache_ttl = cache_ttl

    def create_user(self, username: str, email_addr: str) -> Dict[str, Any]:
        # Create user in database
        query = f"INSERT INTO users (username, email) VALUES ('{username}', '{email_addr}')"
        result = self.database.execute(query)

        # Send welcome email
        self.email.send_email(to=email_addr, subject="Welcome!", body=f"Welcome {username}!")

        return {"id": result[0]["id"], "username": username, "email": email_addr}


# ============================================================================
# Configuration Models
# ============================================================================


class EmailConfig(DynamicConfig[EmailService]):
    smtp_host: str
    port: int = 587
    username: str = ""


class DatabaseConfig(DynamicConfig[DatabaseService]):
    connection_string: str
    pool_size: int = 5


class UserServiceConfig(DynamicConfig[UserService]):
    database: DatabaseConfig
    email: EmailConfig
    cache_ttl: int = 3600


# ============================================================================
# Test Patterns
# ============================================================================


def test_pattern_1_basic_instantiation():
    """Pattern 1: Test basic object instantiation."""
    console.print("🧪 Test Pattern 1: Basic Instantiation")

    # Test instantiation from DynamicConfig
    email_config = EmailConfig(
        _target_="__main__.EmailService", smtp_host="smtp.test.com", port=587, username="test_user"
    )

    email_service = instantiate(email_config)

    # Verify the object was created correctly
    assert isinstance(email_service, EmailService)
    assert email_service.smtp_host == "smtp.test.com"
    assert email_service.port == 587
    assert email_service.username == "test_user"

    # Test functionality
    result = email_service.send_email("user@test.com", "Test", "Test body")
    assert result is True
    assert len(email_service.sent_emails) == 1
    assert email_service.sent_emails[0]["to"] == "user@test.com"

    console.print("✅ Basic instantiation test passed")


def test_pattern_2_parameter_overrides():
    """Pattern 2: Test parameter overrides at instantiation time."""
    console.print("🧪 Test Pattern 2: Parameter Overrides")

    # Base configuration
    db_config = DatabaseConfig(
        _target_="__main__.DatabaseService", connection_string="postgresql://localhost:5432/test", pool_size=5
    )

    # Instantiate with overrides
    db_service = instantiate(db_config, pool_size=10, connection_string="postgresql://prod:5432/prod")

    # Verify overrides were applied
    assert db_service.connection_string == "postgresql://prod:5432/prod"
    assert db_service.pool_size == 10

    console.print("✅ Parameter override test passed")


def test_pattern_3_dependency_injection():
    """Pattern 3: Test dependency injection."""
    console.print("🧪 Test Pattern 3: Dependency Injection")

    # Create mock dependencies
    mock_database = Mock(spec=DatabaseService)
    mock_database.execute.return_value = [{"id": 123, "result": "mock"}]

    mock_email = Mock(spec=EmailService)
    mock_email.send_email.return_value = True

    # Register dependencies
    register_dependency("database", mock_database)
    register_dependency("email", mock_email)

    # Configuration without explicit dependencies
    user_config = {
        "_target_": "__main__.UserService",
        "cache_ttl": 7200,
        # database and email will be injected
    }

    user_service = instantiate(user_config)

    # Verify dependencies were injected
    assert user_service.database is mock_database
    assert user_service.email is mock_email
    assert user_service.cache_ttl == 7200

    # Test that the service works with injected dependencies
    user_service.create_user("testuser", "test@example.com")

    # Verify mocks were called
    mock_database.execute.assert_called_once()
    mock_email.send_email.assert_called_once_with(to="test@example.com", subject="Welcome!", body="Welcome testuser!")

    console.print("✅ Dependency injection test passed")


def test_pattern_4_recursive_instantiation():
    """Pattern 4: Test recursive instantiation of nested configs."""
    console.print("🧪 Test Pattern 4: Recursive Instantiation")

    # Nested configuration
    user_service_config = UserServiceConfig(
        _target_="__main__.UserService",
        database=DatabaseConfig(
            _target_="__main__.DatabaseService", connection_string="postgresql://localhost:5432/test", pool_size=3
        ),
        email=EmailConfig(_target_="__main__.EmailService", smtp_host="smtp.test.com", port=25),
        cache_ttl=1800,
    )

    user_service = instantiate(user_service_config)

    # Verify the main object
    assert isinstance(user_service, UserService)
    assert user_service.cache_ttl == 1800

    # Verify nested objects were instantiated
    assert isinstance(user_service.database, DatabaseService)
    assert user_service.database.connection_string == "postgresql://localhost:5432/test"
    assert user_service.database.pool_size == 3

    assert isinstance(user_service.email, EmailService)
    assert user_service.email.smtp_host == "smtp.test.com"
    assert user_service.email.port == 25

    # Test the complete workflow
    result = user_service.create_user("recursive_user", "recursive@test.com")

    assert result["username"] == "recursive_user"
    assert len(user_service.database.queries_executed) == 1
    assert len(user_service.email.sent_emails) == 1

    console.print("✅ Recursive instantiation test passed")


def test_pattern_5_mocking_instantiation():
    """Pattern 5: Test by mocking the instantiate function itself."""
    console.print("🧪 Test Pattern 5: Mocking Instantiation")

    # Mock the instantiate function to return controlled objects
    mock_email_service = Mock(spec=EmailService)
    mock_database_service = Mock(spec=DatabaseService)

    def mock_instantiate(config, **kwargs):
        if isinstance(config, dict) and config.get("_target_") == "__main__.EmailService":
            return mock_email_service
        elif isinstance(config, dict) and config.get("_target_") == "__main__.DatabaseService":
            return mock_database_service
        elif isinstance(config, EmailConfig):
            return mock_email_service
        elif isinstance(config, DatabaseConfig):
            return mock_database_service
        else:
            # For the main UserService, create it normally but with mocked dependencies
            return UserService(
                database=mock_database_service, email=mock_email_service, cache_ttl=kwargs.get("cache_ttl", 3600)
            )

    with patch("__main__.instantiate", side_effect=mock_instantiate):
        user_config = UserServiceConfig(
            _target_="__main__.UserService",
            database=DatabaseConfig(_target_="__main__.DatabaseService", connection_string="test://db"),
            email=EmailConfig(_target_="__main__.EmailService", smtp_host="test.smtp.com"),
        )

        user_service = instantiate(user_config)

        # Verify we got the mocked dependencies
        assert user_service.database is mock_database_service
        assert user_service.email is mock_email_service

    console.print("✅ Mocking instantiation test passed")


def test_pattern_6_configuration_validation():
    """Pattern 6: Test configuration validation before instantiation."""
    console.print("🧪 Test Pattern 6: Configuration Validation")

    # Test valid configuration
    valid_config = EmailConfig(_target_="__main__.EmailService", smtp_host="valid.smtp.com", port=587)

    # This should not raise any validation errors
    email_service = instantiate(valid_config)
    assert email_service.smtp_host == "valid.smtp.com"

    # Test invalid configuration (this would be caught by Pydantic)
    try:
        EmailConfig(
            _target_="__main__.EmailService",
            smtp_host="valid.smtp.com",
            port="not_a_number",  # This should fail validation
        )
        raise AssertionError("Should have raised validation error")
    except Exception as e:
        assert "validation error" in str(e).lower() or "invalid" in str(e).lower()

    console.print("✅ Configuration validation test passed")


def test_pattern_7_error_handling():
    """Pattern 7: Test error handling in instantiation."""
    console.print("🧪 Test Pattern 7: Error Handling")

    # Test missing _target_
    try:
        instantiate({"smtp_host": "test.com"})
        raise AssertionError("Should have raised InstantiationError")
    except Exception as e:
        assert "target" in str(e).lower()

    # Test invalid _target_
    try:
        instantiate({"_target_": "nonexistent.module.Class"})
        raise AssertionError("Should have raised InstantiationError")
    except Exception as e:
        assert "import" in str(e).lower() or "module" in str(e).lower()

    # Test missing required parameters
    try:
        instantiate({"_target_": "__main__.EmailService"})  # Missing required smtp_host
        raise AssertionError("Should have raised TypeError")
    except TypeError as e:
        assert "required" in str(e).lower() or "missing" in str(e).lower()

    console.print("✅ Error handling test passed")


def test_pattern_8_partial_instantiation():
    """Pattern 8: Test partial instantiation for factory patterns."""
    console.print("🧪 Test Pattern 8: Partial Instantiation")

    # Create a factory for email services
    email_factory = instantiate(
        {"_target_": "__main__.EmailService", "_partial_": True, "smtp_host": "factory.smtp.com", "port": 587}
    )

    # Use the factory to create instances
    email1 = email_factory(username="user1")
    email2 = email_factory(username="user2")

    # Verify both instances have the factory defaults
    assert email1.smtp_host == "factory.smtp.com"
    assert email1.port == 587
    assert email1.username == "user1"

    assert email2.smtp_host == "factory.smtp.com"
    assert email2.port == 587
    assert email2.username == "user2"

    # Verify they are different instances
    assert email1 is not email2

    console.print("✅ Partial instantiation test passed")


def run_all_tests():
    """Run all test patterns."""
    console.print("🧪 Running All Test Patterns for Instantiation\n")

    test_pattern_1_basic_instantiation()
    test_pattern_2_parameter_overrides()
    test_pattern_3_dependency_injection()
    test_pattern_4_recursive_instantiation()
    test_pattern_5_mocking_instantiation()
    test_pattern_6_configuration_validation()
    test_pattern_7_error_handling()
    test_pattern_8_partial_instantiation()

    console.print("\n🎉 All test patterns passed!")
    console.print("\n💡 Key testing insights:")
    console.print("   • Test instantiation separately from business logic")
    console.print("   • Use dependency injection for easier mocking")
    console.print("   • Validate configurations before instantiation")
    console.print("   • Mock the instantiate function for complex scenarios")
    console.print("   • Test error conditions and edge cases")
    console.print("   • Use partial instantiation for factory testing")


if __name__ == "__main__":
    run_all_tests()
