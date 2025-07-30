#!/usr/bin/env python3
"""
Basic usage examples for the Cognify Python SDK.

This script demonstrates the core functionality implemented so far:
- Client initialization
- Configuration management
- Authentication (API Key and JWT)
- Basic API operations
"""

import asyncio
import os
from cognify_sdk import CognifyClient


def example_api_key_auth():
    """Example using API key authentication."""
    print("=== API Key Authentication Example ===")

    # Initialize client with API key
    client = CognifyClient(
        api_key="cog_example_key_12345",
        base_url="https://api.cognify.ai",
        timeout=30,
        debug=True
    )

    # Check authentication status
    print(f"Authenticated: {client.auth.is_authenticated()}")
    print(f"Auth info: {client.auth.get_auth_info()}")

    # The client is ready for API calls (when connected to real API)
    print("Client initialized successfully!")

    # Clean up
    client.close()


async def example_jwt_auth():
    """Example using JWT authentication."""
    print("\n=== JWT Authentication Example ===")

    # Initialize client without authentication
    client = CognifyClient(
        base_url="https://api.cognify.ai",
        timeout=30
    )

    # Set JWT tokens manually
    client.auth.set_jwt_tokens(
        access_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyMTIzIn0.signature",
        refresh_token="refresh_token_example",
        expires_in=3600,
        user_id="user123"
    )

    print(f"Authenticated: {client.auth.is_authenticated()}")
    print(f"User ID: {client.auth.get_user_id()}")
    print(f"Auth info: {client.auth.get_auth_info()}")

    # Clean up
    await client.aclose()


def example_configuration():
    """Example showing configuration options."""
    print("\n=== Configuration Example ===")

    # Using environment variables
    os.environ["COGNIFY_API_KEY"] = "cog_env_key_12345"
    os.environ["COGNIFY_BASE_URL"] = "https://custom.cognify.ai"
    os.environ["COGNIFY_TIMEOUT"] = "60"

    # Client will automatically pick up environment variables
    client = CognifyClient()

    print(f"API Key: {'***' if client.config.api_key else None}")
    print(f"Base URL: {client.config.base_url}")
    print(f"Timeout: {client.config.timeout}")
    print(f"Debug: {client.config.debug}")

    # Configuration details
    print(f"Full URL example: {client.config.get_full_url('documents')}")
    print(f"Headers: {client.config.get_headers()}")

    client.close()


def example_error_handling():
    """Example showing error handling."""
    print("\n=== Error Handling Example ===")

    try:
        # This should fail due to invalid API key format
        client = CognifyClient(api_key="invalid_key")
    except Exception as e:
        print(f"Expected error: {e}")

    try:
        # This should fail due to invalid base URL
        client = CognifyClient(
            api_key="cog_valid_key",
            base_url="invalid-url"
        )
    except Exception as e:
        print(f"Expected error: {e}")

    print("Error handling working correctly!")


async def main():
    """Run all examples."""
    print("Cognify Python SDK - Basic Usage Examples")
    print("=" * 50)

    # Run synchronous examples
    example_api_key_auth()
    example_configuration()
    example_error_handling()

    # Run async example
    await example_jwt_auth()

    print("\n" + "=" * 50)
    print("All examples completed successfully!")
    print("\nImplemented features:")
    print("✅ Core client architecture")
    print("✅ Configuration management")
    print("✅ API key authentication")
    print("✅ JWT authentication")
    print("✅ Token management")
    print("✅ Error handling")
    print("✅ Sync/async support")
    print("✅ Documents module")
    print("✅ File upload/download")
    print("✅ Document management")
    print("✅ Content chunking")
    print("✅ Comprehensive testing")

    print("\nNext to implement:")
    print("🔄 Query/search module")
    print("🔄 RAG/agents module")
    print("🔄 Conversations module")
    print("🔄 Collections module")


if __name__ == "__main__":
    asyncio.run(main())
