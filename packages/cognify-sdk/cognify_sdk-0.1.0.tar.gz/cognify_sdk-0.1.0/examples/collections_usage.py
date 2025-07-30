"""
Collections Usage Examples for Cognify SDK

This example demonstrates how to use the Collections module for managing
collections, collaborators, and analytics in the Cognify platform.
"""

import asyncio
import os
from typing import List

from cognify_sdk import (
    CognifyClient,
    Collection,
    CollectionVisibility,
    CollaboratorRole,
    Collaborator,
    CollectionStats,
)


async def main():
    """Main example function demonstrating collections usage."""
    # Initialize client
    client = CognifyClient(
        api_key=os.getenv("COGNIFY_API_KEY", "your_api_key_here"),
        base_url=os.getenv("COGNIFY_BASE_URL", "https://api.cognify.ai"),
    )

    try:
        print("🚀 Cognify Collections Module Examples")
        print("=" * 50)

        # Example 1: Create a new collection
        print("\n📁 Creating a new collection...")
        collection = await client.collections.create(
            name="My Project Codebase",
            description="Main codebase for my project with documentation",
            visibility=CollectionVisibility.ORGANIZATION,
            tags=["python", "backend", "api"],
            metadata={
                "project_type": "web_application",
                "language": "python",
                "framework": "fastapi",
            },
        )
        print(f"✅ Created collection: {collection.name} (ID: {collection.id})")
        print(f"   Visibility: {collection.visibility}")
        print(f"   Tags: {collection.tags}")

        # Example 2: List collections
        print("\n📋 Listing collections...")
        collections_response = await client.collections.list(
            visibility=CollectionVisibility.ORGANIZATION,
            limit=10,
        )
        print(f"✅ Found {len(collections_response.collections)} collections:")
        for col in collections_response.collections:
            print(f"   - {col.name} ({col.document_count} documents)")

        # Example 3: Search collections
        print("\n🔍 Searching collections...")
        search_response = await client.collections.search(
            query="python",
            visibility=CollectionVisibility.ORGANIZATION,
            limit=5,
        )
        print(f"✅ Found {len(search_response.collections)} collections matching 'python':")
        for col in search_response.collections:
            print(f"   - {col.name}: {col.description}")

        # Example 4: Add collaborators
        print("\n👥 Adding collaborators...")
        try:
            collaborator = await client.collections.add_collaborator(
                collection.id,
                email="developer@company.com",
                role=CollaboratorRole.CONTRIBUTOR,
                permissions=["read", "write", "comment"],
            )
            print(f"✅ Added collaborator: {collaborator.name} ({collaborator.email})")
            print(f"   Role: {collaborator.role}")
            print(f"   Permissions: {collaborator.permissions}")

            # Add another collaborator with different role
            manager = await client.collections.add_collaborator(
                collection.id,
                email="manager@company.com",
                role=CollaboratorRole.VIEWER,
            )
            print(f"✅ Added manager: {manager.name} ({manager.role})")

        except Exception as e:
            print(f"⚠️  Could not add collaborators: {e}")

        # Example 5: List collaborators
        print("\n👥 Listing collaborators...")
        try:
            collaborators = await client.collections.get_collaborators(collection.id)
            print(f"✅ Collection has {len(collaborators)} collaborators:")
            for collab in collaborators:
                print(f"   - {collab.name} ({collab.email}) - {collab.role}")
                print(f"     Added: {collab.added_at}")
                print(f"     Last accessed: {collab.last_accessed_at}")

        except Exception as e:
            print(f"⚠️  Could not list collaborators: {e}")

        # Example 6: Check user permissions
        print("\n🔐 Checking user permissions...")
        try:
            permissions = await client.collections.get_user_permissions(collection.id)
            print(f"✅ Current user permissions: {permissions}")

            # Check specific permission
            can_admin = await client.collections.check_user_access(
                collection.id, "admin"
            )
            print(f"   Can admin collection: {can_admin}")

        except Exception as e:
            print(f"⚠️  Could not check permissions: {e}")

        # Example 7: Get collection statistics
        print("\n📊 Getting collection analytics...")
        try:
            stats = await client.collections.get_collection_stats(collection.id)
            print(f"✅ Collection Statistics:")
            print(f"   Documents: {stats.document_count}")
            print(f"   Total size: {stats.total_size_bytes} bytes")
            print(f"   Queries (30d): {stats.query_count_30d}")
            print(f"   Views (30d): {stats.view_count_30d}")
            print(f"   Last activity: {stats.last_activity}")

            if stats.top_contributors:
                print(f"   Top contributors: {len(stats.top_contributors)}")
                for contributor in stats.top_contributors[:3]:
                    print(f"     - {contributor}")

        except Exception as e:
            print(f"⚠️  Could not get statistics: {e}")

        # Example 8: Get collection status
        print("\n⚡ Getting collection status...")
        try:
            status = await client.collections.get_status(collection.id)
            print(f"✅ Collection Status:")
            print(f"   Processing: {status.processing_status}")
            print(f"   Embedding: {status.embedding_status}")
            print(f"   Documents: {status.document_count}")
            print(f"   Processed: {status.processed_documents}")
            print(f"   Failed: {status.failed_documents}")

        except Exception as e:
            print(f"⚠️  Could not get status: {e}")

        # Example 9: Get collection documents
        print("\n📄 Getting collection documents...")
        try:
            documents = await client.collections.get_collection_documents(
                collection.id,
                limit=5,
                doc_status="completed",
            )
            print(f"✅ Found {len(documents)} completed documents:")
            for doc in documents[:3]:
                print(f"   - {doc.get('name', 'Unknown')} ({doc.get('id', 'No ID')})")
                print(f"     Status: {doc.get('status', 'Unknown')}")
                print(f"     Size: {doc.get('size', 0)} bytes")

        except Exception as e:
            print(f"⚠️  Could not get documents: {e}")

        # Example 10: Update collection
        print("\n✏️  Updating collection...")
        try:
            updated_collection = await client.collections.update(
                collection.id,
                description="Updated description with more details",
                tags=["python", "backend", "api", "updated"],
                metadata={
                    **collection.metadata,
                    "last_updated": "2025-06-24",
                    "version": "2.0",
                },
            )
            print(f"✅ Updated collection: {updated_collection.name}")
            print(f"   New description: {updated_collection.description}")
            print(f"   Updated tags: {updated_collection.tags}")

        except Exception as e:
            print(f"⚠️  Could not update collection: {e}")

        # Example 11: Update collaborator role
        print("\n👥 Updating collaborator role...")
        try:
            if collaborators:
                collaborator_to_update = collaborators[0]
                updated_collaborator = await client.collections.update_collaborator(
                    collection.id,
                    collaborator_to_update.user_id,
                    role=CollaboratorRole.EDITOR,
                    permissions=["read", "write", "edit", "comment"],
                )
                print(f"✅ Updated collaborator: {updated_collaborator.name}")
                print(f"   New role: {updated_collaborator.role}")
                print(f"   New permissions: {updated_collaborator.permissions}")

        except Exception as e:
            print(f"⚠️  Could not update collaborator: {e}")

        # Example 12: Export analytics
        print("\n📤 Exporting analytics...")
        try:
            export_data = await client.collections.export_analytics(
                collection.id,
                format="json",
                include_details=True,
            )
            print(f"✅ Exported analytics data:")
            print(f"   Format: json")
            print(f"   Size: {len(str(export_data))} characters")

        except Exception as e:
            print(f"⚠️  Could not export analytics: {e}")

        # Example 13: Get usage analytics
        print("\n📈 Getting usage analytics...")
        try:
            usage_analytics = await client.collections.get_usage_analytics(
                collection.id,
                days_back=30,
            )
            print(f"✅ Usage Analytics (30 days):")
            print(f"   Data keys: {list(usage_analytics.keys())}")

        except Exception as e:
            print(f"⚠️  Could not get usage analytics: {e}")

        print("\n🎉 Collections examples completed successfully!")

        # Note: In a real scenario, you might want to clean up test data
        # print("\n🧹 Cleaning up test collection...")
        # await client.collections.delete(collection.id)
        # print("✅ Test collection deleted")

    except Exception as e:
        print(f"❌ Error in collections examples: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Clean up client resources
        await client.aclose()


def sync_examples():
    """Example using synchronous methods."""
    print("\n🔄 Synchronous Collections Examples")
    print("=" * 40)

    # Initialize client
    client = CognifyClient(
        api_key=os.getenv("COGNIFY_API_KEY", "your_api_key_here"),
    )

    try:
        # Create collection synchronously
        collection = client.collections.create_sync(
            name="Sync Test Collection",
            description="Created using sync methods",
            visibility=CollectionVisibility.PRIVATE,
        )
        print(f"✅ Created collection synchronously: {collection.name}")

        # List collections synchronously
        collections_response = client.collections.list_sync(limit=5)
        print(f"✅ Listed {len(collections_response.collections)} collections synchronously")

        # Get collection synchronously
        retrieved_collection = client.collections.get_sync(collection.id)
        print(f"✅ Retrieved collection: {retrieved_collection.name}")

    except Exception as e:
        print(f"❌ Error in sync examples: {e}")

    finally:
        # Clean up client resources
        client.close()


if __name__ == "__main__":
    print("🚀 Starting Cognify Collections Examples")
    
    # Run async examples
    asyncio.run(main())
    
    # Run sync examples
    sync_examples()
    
    print("\n✨ All examples completed!")
