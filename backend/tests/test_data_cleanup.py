"""
测试数据清理检查工具
用于验证测试执行后是否清理了所有测试数据
"""
import pytest
from sqlalchemy import func, text
from tests.conftest import TEST_DATABASE_URL
from sqlalchemy import create_engine, inspect


def check_test_data_cleanup():
    """
    Check if test data has been properly cleaned up.
    
    This function inspects the database for common test data patterns:
    - Users with phone numbers starting with test patterns (13800138000)
    - Resources/topics with test prefixes
    - AI sessions created during tests
    
    Returns:
        dict: Cleanup status report
    """
    engine = create_engine(TEST_DATABASE_URL)
    connection = engine.connect()
    
    cleanup_report = {
        "clean": True,
        "issues": [],
        "tables_checked": 0,
        "test_data_found": 0,
        "error": None
    }
    
    try:
        # Check if tables exist first
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if not existing_tables:
            cleanup_report["error"] = "Database is empty (no tables found)"
            return cleanup_report
        
        # Check users table for test data
        if "users" in existing_tables:
            result = connection.execute(
                text("SELECT COUNT(*) FROM users WHERE phone LIKE '13800138%' OR nickname LIKE 'test%'")
            )
            test_users_count = result.scalar()
            if test_users_count > 0:
                cleanup_report["clean"] = False
                cleanup_report["issues"].append(f"Found {test_users_count} test users")
                cleanup_report["test_data_found"] += test_users_count
            
            cleanup_report["tables_checked"] += 1
        
        # Check resources table for test data
        if "resources" in existing_tables:
            result = connection.execute(
                text("SELECT COUNT(*) FROM resources WHERE title LIKE 'Test%' OR description LIKE 'Test%'")
            )
            test_resources_count = result.scalar()
            if test_resources_count > 0:
                cleanup_report["clean"] = False
                cleanup_report["issues"].append(f"Found {test_resources_count} test resources")
                cleanup_report["test_data_found"] += test_resources_count
            
            cleanup_report["tables_checked"] += 1
        
        # Check topics table for test data
        if "topics" in existing_tables:
            result = connection.execute(
                text("SELECT COUNT(*) FROM topics WHERE title LIKE 'Test%' OR content LIKE 'Test%'")
            )
            test_topics_count = result.scalar()
            if test_topics_count > 0:
                cleanup_report["clean"] = False
                cleanup_report["issues"].append(f"Found {test_topics_count} test topics")
                cleanup_report["test_data_found"] += test_topics_count
            
            cleanup_report["tables_checked"] += 1
        
        # Check AI sessions for test data
        if "ai_sessions" in existing_tables:
            result = connection.execute(
                text("SELECT COUNT(*) FROM ai_sessions WHERE title LIKE 'Test%'")
            )
            test_sessions_count = result.scalar()
            if test_sessions_count > 0:
                cleanup_report["clean"] = False
                cleanup_report["issues"].append(f"Found {test_sessions_count} test AI sessions")
                cleanup_report["test_data_found"] += test_sessions_count
            
            cleanup_report["tables_checked"] += 1
        
    except Exception as e:
        cleanup_report["error"] = str(e)
        cleanup_report["clean"] = False
    finally:
        connection.close()
        engine.dispose()
    
    return cleanup_report


def test_data_cleanup_verification():
    """
    Pytest test to verify test data cleanup.
    
    This test should be run periodically to ensure:
    1. Tests are properly cleaning up after themselves
    2. No test data is leaking between test runs
    3. Database remains in a clean state
    
    Run with: pytest tests/test_data_cleanup.py::test_data_cleanup_verification -v
    """
    report = check_test_data_cleanup()
    
    # Assert that cleanup is complete
    assert report["clean"], (
        f"Test data cleanup verification failed!\n"
        f"Tables checked: {report['tables_checked']}\n"
        f"Test data found: {report['test_data_found']}\n"
        f"Issues:\n" + "\n".join(f"  - {issue}" for issue in report["issues"])
    )
    
    print(f"✅ Test data cleanup verification passed")
    print(f"   Tables checked: {report['tables_checked']}")
    print(f"   Test data found: {report['test_data_found']}")


if __name__ == "__main__":
    # Run cleanup check manually
    report = check_test_data_cleanup()
    
    print("\n" + "="*60)
    print("测试数据清理检查报告")
    print("="*60)
    print(f"检查状态：{'✅ 通过' if report['clean'] else '❌ 失败'}")
    print(f"检查表数：{report['tables_checked']}")
    print(f"发现测试数据：{report['test_data_found']} 条")
    
    if report["issues"]:
        print("\n发现的问题:")
        for issue in report["issues"]:
            print(f"  - {issue}")
    else:
        print("\n✅ 未发现测试数据残留")
    
    print("="*60 + "\n")
