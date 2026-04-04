#!/usr/bin/env python3
"""
Sprint B 全面审查验收脚本

执行所有审查检查点，生成详细审查报告。
"""
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# 添加 backend 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))


class CheckStatus(Enum):
    PASS = "✅ 通过"
    FAIL = "❌ 失败"
    WARNING = "⚠️ 警告"
    SKIP = "⚪ 跳过"


@dataclass
class CheckResult:
    name: str
    status: CheckStatus
    message: str
    details: str = ""


class SprintBReviewer:
    """Sprint B 审查器"""
    
    def __init__(self):
        self.results: Dict[str, List[CheckResult]] = {}
        # 使用绝对路径
        self.root_path = Path(__file__).parent.parent.parent
        self.backend_path = self.root_path / 'backend'
        self.docs_path = self.root_path / 'docs'
        
    def run_all_checks(self) -> bool:
        """执行所有审查检查"""
        print("=" * 80)
        print("Sprint B 全面审查验收")
        print("=" * 80)
        print()
        
        # 阶段 1: 数据库与 ORM 模型
        self.check_stage1_models()
        
        # 阶段 2: Pydantic Schemas
        self.check_stage2_schemas()
        
        # 阶段 3: Service 服务层
        self.check_stage3_services()
        
        # 阶段 4: API 路由层
        self.check_stage4_routers()
        
        # 阶段 5: 测试与文档
        self.check_stage5_tests_docs()
        
        # 生成报告
        self.generate_report()
        
        # 返回是否全部通过
        return all(
            all(r.status == CheckStatus.PASS for r in results)
            for results in self.results.values()
        )
    
    def check_stage1_models(self):
        """阶段 1: 数据库与 ORM 模型审查"""
        print("\n📊 阶段 1: 数据库与 ORM 模型审查")
        print("-" * 80)
        
        results = []
        
        # 1.1 检查模型文件完整性
        model_files = [
            'ai_session.py',
            'ai_message.py',
            'file_meta.py',
            'resources.py',
            'topic.py',
            'ledger.py',
            'notification.py',
        ]
        
        models_path = self.backend_path / 'app' / 'models'
        
        for file_name in model_files:
            file_path = models_path / file_name
            if file_path.exists():
                results.append(CheckResult(
                    name=f"模型文件：{file_name}",
                    status=CheckStatus.PASS,
                    message=f"文件存在"
                ))
            else:
                results.append(CheckResult(
                    name=f"模型文件：{file_name}",
                    status=CheckStatus.FAIL,
                    message=f"文件不存在"
                ))
        
        # 检查 __init__.py
        init_path = models_path / '__init__.py'
        if init_path.exists():
            content = init_path.read_text()
            required_imports = [
                'AISession', 'AIMessage', 'FileMeta', 'Resource',
                'Topic', 'Post', 'PointLedger', 'Notification'
            ]
            
            missing = [imp for imp in required_imports if imp not in content]
            if not missing:
                results.append(CheckResult(
                    name="模型导出：__init__.py",
                    status=CheckStatus.PASS,
                    message="所有模型正确导出"
                ))
            else:
                results.append(CheckResult(
                    name="模型导出：__init__.py",
                    status=CheckStatus.FAIL,
                    message=f"缺少导出：{missing}"
                ))
        else:
            results.append(CheckResult(
                name="模型导出：__init__.py",
                status=CheckStatus.FAIL,
                message="文件不存在"
            ))
        
        # 1.2 检查 Migration 脚本
        versions_path = self.backend_path / 'alembic' / 'versions'
        migration_files = list(versions_path.glob('*_add_ai_resource*.py'))
        
        if migration_files:
            migration_file = migration_files[0]
            content = migration_file.read_text()
            
            # 检查 upgrade 和 downgrade 函数
            has_upgrade = 'def upgrade()' in content
            has_downgrade = 'def downgrade()' in content
            
            # 检查表创建
            required_tables = [
                'ai_sessions', 'ai_messages', 'file_meta', 'file_usage',
                'resources', 'resource_previews', 'topics', 'posts',
                'point_ledger', 'notifications'
            ]
            
            missing_tables = [
                table for table in required_tables 
                if f"create_table('{table}'" not in content
            ]
            
            if has_upgrade and has_downgrade and not missing_tables:
                results.append(CheckResult(
                    name="Migration 脚本",
                    status=CheckStatus.PASS,
                    message=f"包含 upgrade/downgrade，创建 {len(required_tables)} 个表"
                ))
            else:
                issues = []
                if not has_upgrade:
                    issues.append("缺少 upgrade 函数")
                if not has_downgrade:
                    issues.append("缺少 downgrade 函数")
                if missing_tables:
                    issues.append(f"缺少表：{missing_tables}")
                
                results.append(CheckResult(
                    name="Migration 脚本",
                    status=CheckStatus.FAIL,
                    message=", ".join(issues)
                ))
        else:
            results.append(CheckResult(
                name="Migration 脚本",
                status=CheckStatus.FAIL,
                message="Migration 文件不存在"
            ))
        
        # 1.3 检查 Enum 定义
        enum_checks = []
        
        # 检查 file_meta.py 中的 Enum
        file_meta_path = models_path / 'file_meta.py'
        if file_meta_path.exists():
            content = file_meta_path.read_text()
            has_file_status = 'class FileStatus' in content
            has_lifecycle_status = 'class LifecycleStatus' in content
            
            if has_file_status and has_lifecycle_status:
                enum_checks.append("FileStatus, LifecycleStatus ✅")
            else:
                enum_checks.append("缺少 Enum 定义")
        
        # 检查 resources.py 中的 Enum
        resource_path = models_path / 'resources.py'
        if resource_path.exists():
            content = resource_path.read_text()
            has_resource_status = 'class ResourceStatus' in content
            
            if has_resource_status:
                enum_checks.append("ResourceStatus ✅")
            else:
                enum_checks.append("缺少 ResourceStatus")
        
        # 检查 topic.py 中的 Enum
        topic_path = models_path / 'topic.py'
        if topic_path.exists():
            content = topic_path.read_text()
            has_bounty_status = 'class BountyStatus' in content
            has_topic_status = 'class TopicStatus' in content
            
            if has_bounty_status and has_topic_status:
                enum_checks.append("BountyStatus, TopicStatus ✅")
            else:
                enum_checks.append("缺少 Enum 定义")
        
        # 检查 ledger.py 中的 Enum
        ledger_path = models_path / 'ledger.py'
        if ledger_path.exists():
            content = ledger_path.read_text()
            has_point_type = 'class PointType' in content
            has_order_type = 'class OrderType' in content
            
            if has_point_type and has_order_type:
                enum_checks.append("PointType, OrderType ✅")
            else:
                enum_checks.append("缺少 Enum 定义")
        
        # 检查 notification.py 中的 Enum
        notification_path = models_path / 'notification.py'
        if notification_path.exists():
            content = notification_path.read_text()
            has_notification_type = 'class NotificationType' in content
            has_notification_priority = 'class NotificationPriority' in content
            
            if has_notification_type and has_notification_priority:
                enum_checks.append("NotificationType, NotificationPriority ✅")
            else:
                enum_checks.append("缺少 Enum 定义")
        
        results.append(CheckResult(
            name="Enum 定义完整性",
            status=CheckStatus.PASS if all('✅' in c for c in enum_checks) else CheckStatus.FAIL,
            message=", ".join(enum_checks)
        ))
        
        self.results['阶段 1_数据库与 ORM 模型'] = results
    
    def check_stage2_schemas(self):
        """阶段 2: Pydantic Schemas 审查"""
        print("\n📋 阶段 2: Pydantic Schemas 审查")
        print("-" * 80)
        
        results = []
        schemas_path = self.backend_path / 'app' / 'schemas'
        
        # 2.1 检查 Schema 文件完整性
        schema_files = [
            'ai.py',
            'resource.py',
            'community.py',
            'ledger.py',
            'notification.py',
            'file.py',
        ]
        
        for file_name in schema_files:
            file_path = schemas_path / file_name
            if file_path.exists():
                content = file_path.read_text()
                
                # 检查是否包含 Request 和 Response Schema
                has_request = 'Request' in content
                has_response = 'Response' in content
                
                if has_request and has_response:
                    results.append(CheckResult(
                        name=f"Schema 文件：{file_name}",
                        status=CheckStatus.PASS,
                        message="包含 Request 和 Response Schema"
                    ))
                else:
                    results.append(CheckResult(
                        name=f"Schema 文件：{file_name}",
                        status=CheckStatus.WARNING,
                        message=f"缺少：{'Request' if not has_request else ''} {'Response' if not has_response else ''}"
                    ))
            else:
                results.append(CheckResult(
                    name=f"Schema 文件：{file_name}",
                    status=CheckStatus.FAIL,
                    message="文件不存在"
                ))
        
        # 2.2 检查 __init__.py 导出
        init_path = schemas_path / '__init__.py'
        if init_path.exists():
            content = init_path.read_text()
            
            # 检查是否从所有模块导入
            required_modules = ['ai', 'resource', 'community', 'ledger', 'notification', 'file']
            missing_modules = [mod for mod in required_modules if f'from .{mod}' not in content]
            
            if not missing_modules:
                results.append(CheckResult(
                    name="Schema 导出：__init__.py",
                    status=CheckStatus.PASS,
                    message="所有模块正确导出"
                ))
            else:
                results.append(CheckResult(
                    name="Schema 导出：__init__.py",
                    status=CheckStatus.FAIL,
                    message=f"缺少模块：{missing_modules}"
                ))
        else:
            results.append(CheckResult(
                name="Schema 导出：__init__.py",
                status=CheckStatus.FAIL,
                message="文件不存在"
            ))
        
        # 2.3 检查 Pydantic v2 兼容性
        ai_schema_path = schemas_path / 'ai.py'
        if ai_schema_path.exists():
            content = ai_schema_path.read_text()
            
            # 检查是否使用 Pydantic v2 语法
            uses_v2 = 'from pydantic import' in content
            has_field = 'Field(' in content
            
            if uses_v2 and has_field:
                results.append(CheckResult(
                    name="Pydantic v2 兼容性",
                    status=CheckStatus.PASS,
                    message="使用 Pydantic v2 语法"
                ))
            else:
                results.append(CheckResult(
                    name="Pydantic v2 兼容性",
                    status=CheckStatus.WARNING,
                    message="可能使用旧版 Pydantic"
                ))
        
        self.results['阶段 2_Pydantic_Schemas'] = results
    
    def check_stage3_services(self):
        """阶段 3: Service 服务层审查"""
        print("\n⚙️  阶段 3: Service 服务层审查")
        print("-" * 80)
        
        results = []
        services_path = self.backend_path / 'app' / 'services'
        
        # 3.1 检查 Service 文件完整性
        service_files = [
            'ai_service.py',
            'resource_service.py',
            'community_service.py',
            'ledger_service.py',
            'notification_service.py',
            'file_service.py',
        ]
        
        for file_name in service_files:
            file_path = services_path / file_name
            if file_path.exists():
                content = file_path.read_text()
                
                # 检查是否包含 Service 类
                has_service_class = 'Service' in file_name.replace('_', ' ').title()
                has_class = 'class' in content and 'Service' in content
                
                # 检查是否使用异步
                has_async = 'async def' in content
                
                if has_class and has_async:
                    results.append(CheckResult(
                        name=f"Service 文件：{file_name}",
                        status=CheckStatus.PASS,
                        message="包含异步 Service 类"
                    ))
                else:
                    results.append(CheckResult(
                        name=f"Service 文件：{file_name}",
                        status=CheckStatus.WARNING,
                        message=f"缺少：{'Service 类' if not has_class else ''} {'异步方法' if not has_async else ''}"
                    ))
            else:
                results.append(CheckResult(
                    name=f"Service 文件：{file_name}",
                    status=CheckStatus.FAIL,
                    message="文件不存在"
                ))
        
        # 3.2 检查服务层依赖注入
        ai_service_path = services_path / 'ai_service.py'
        if ai_service_path.exists():
            content = ai_service_path.read_text()
            
            # 检查是否接受 db 会话
            has_db_param = 'db: AsyncSession' in content or 'db: Session' in content
            
            if has_db_param:
                results.append(CheckResult(
                    name="依赖注入模式",
                    status=CheckStatus.PASS,
                    message="使用数据库会话依赖注入"
                ))
            else:
                results.append(CheckResult(
                    name="依赖注入模式",
                    status=CheckStatus.WARNING,
                    message="未使用标准的依赖注入模式"
                ))
        
        self.results['阶段 3_Service 服务层'] = results
    
    def check_stage4_routers(self):
        """阶段 4: API 路由层审查"""
        print("\n🌐 阶段 4: API 路由层审查")
        print("-" * 80)
        
        results = []
        api_path = self.backend_path / 'app' / 'api' / 'v1'
        
        # 4.1 检查路由模块完整性
        router_modules = [
            'ai',
            'community',
            'ledger',
            'notification',
            'files',
        ]
        
        for module in router_modules:
            router_path = api_path / module / 'router.py'
            init_path = api_path / module / '__init__.py'
            
            if router_path.exists():
                content = router_path.read_text()
                
                # 检查是否包含路由装饰器
                has_router = '@router.' in content
                has_endpoint = 'async def' in content
                
                if has_router and has_endpoint:
                    results.append(CheckResult(
                        name=f"路由模块：{module}",
                        status=CheckStatus.PASS,
                        message="包含路由定义"
                    ))
                else:
                    results.append(CheckResult(
                        name=f"路由模块：{module}",
                        status=CheckStatus.FAIL,
                        message="缺少路由定义"
                    ))
            else:
                results.append(CheckResult(
                    name=f"路由模块：{module}",
                    status=CheckStatus.FAIL,
                    message="文件不存在"
                ))
        
        # 4.2 检查路由注册
        v1_init_path = api_path / '__init__.py'
        if v1_init_path.exists():
            content = v1_init_path.read_text()
            
            # 检查是否注册所有路由
            required_routers = ['ai_router', 'community_router', 'ledger_router', 
                              'notification_router', 'files_router']
            missing_routers = [r for r in required_routers if r not in content]
            
            if not missing_routers:
                results.append(CheckResult(
                    name="路由注册",
                    status=CheckStatus.PASS,
                    message="所有路由正确注册"
                ))
            else:
                results.append(CheckResult(
                    name="路由注册",
                    status=CheckStatus.FAIL,
                    message=f"缺少注册：{missing_routers}"
                ))
        else:
            results.append(CheckResult(
                name="路由注册",
                status=CheckStatus.FAIL,
                message="__init__.py 不存在"
            ))
        
        self.results['阶段 4_API 路由层'] = results
    
    def check_stage5_tests_docs(self):
        """阶段 5: 测试与文档审查"""
        print("\n📝 阶段 5: 测试与文档审查")
        print("-" * 80)
        
        results = []
        
        # 5.1 检查测试文件
        tests_path = self.backend_path / 'tests'
        test_files = ['test_sprint_b.py']
        
        for test_file in test_files:
            test_path = tests_path / test_file
            if test_path.exists():
                content = test_path.read_text()
                
                # 检查是否包含测试用例
                has_tests = 'async def test_' in content
                has_pytest = 'pytest' in content or 'assert' in content
                
                if has_tests and has_pytest:
                    results.append(CheckResult(
                        name=f"测试文件：{test_file}",
                        status=CheckStatus.PASS,
                        message="包含测试用例"
                    ))
                else:
                    results.append(CheckResult(
                        name=f"测试文件：{test_file}",
                        status=CheckStatus.WARNING,
                        message="测试用例不完整"
                    ))
            else:
                results.append(CheckResult(
                    name=f"测试文件：{test_file}",
                    status=CheckStatus.FAIL,
                    message="文件不存在"
                ))
        
        # 5.2 检查文档文件
        review_docs_path = self.docs_path / '05_审查报告'
        required_docs = [
            'Sprint_B_阶段 1_自我审查报告.md',
            'Sprint_B_最终审查报告.md',
        ]
        
        for doc_file in required_docs:
            doc_path = review_docs_path / doc_file
            if doc_path.exists():
                results.append(CheckResult(
                    name=f"审查文档：{doc_file}",
                    status=CheckStatus.PASS,
                    message="文档存在"
                ))
            else:
                results.append(CheckResult(
                    name=f"审查文档：{doc_file}",
                    status=CheckStatus.FAIL,
                    message="文档不存在"
                ))
        
        # 检查 API 文档
        api_docs_path = self.docs_path / '03_API 文档'
        api_doc_file = api_docs_path / 'Sprint_B_API 文档.md'
        
        if api_doc_file.exists():
            results.append(CheckResult(
                name="API 文档",
                status=CheckStatus.PASS,
                message="API 文档存在"
            ))
        else:
            results.append(CheckResult(
                name="API 文档",
                status=CheckStatus.FAIL,
                message="API 文档不存在"
            ))
        
        self.results['阶段 5_测试与文档'] = results
    
    def generate_report(self):
        """生成审查报告"""
        print("\n" + "=" * 80)
        print("📊 审查报告汇总")
        print("=" * 80)
        
        total_checks = 0
        total_pass = 0
        total_fail = 0
        total_warning = 0
        
        for stage, checks in self.results.items():
            print(f"\n{stage}")
            print("-" * 80)
            
            stage_pass = 0
            stage_fail = 0
            stage_warning = 0
            
            for check in checks:
                total_checks += 1
                
                if check.status == CheckStatus.PASS:
                    stage_pass += 1
                    total_pass += 1
                    symbol = "✅"
                elif check.status == CheckStatus.FAIL:
                    stage_fail += 1
                    total_fail += 1
                    symbol = "❌"
                elif check.status == CheckStatus.WARNING:
                    stage_warning += 1
                    total_warning += 1
                    symbol = "⚠️"
                else:
                    symbol = "⚪"
                
                print(f"  {symbol} {check.name}: {check.message}")
            
            # 阶段通过率
            stage_total = stage_pass + stage_fail
            stage_rate = (stage_pass / stage_total * 100) if stage_total > 0 else 0
            
            print(f"\n  阶段通过率：{stage_pass}/{stage_total} ({stage_rate:.1f}%)")
        
        # 总体统计
        print("\n" + "=" * 80)
        print("📈 总体统计")
        print("=" * 80)
        print(f"总检查项：{total_checks}")
        print(f"✅ 通过：{total_pass}")
        print(f"❌ 失败：{total_fail}")
        print(f"⚠️  警告：{total_warning}")
        
        overall_rate = (total_pass / total_checks * 100) if total_checks > 0 else 0
        print(f"\n总体通过率：{overall_rate:.1f}%")
        
        # 审查结论
        print("\n" + "=" * 80)
        print("📋 审查结论")
        print("=" * 80)
        
        if total_fail == 0 and total_warning == 0:
            print("✅ 审查通过 - 所有检查项均符合标准")
        elif total_fail == 0:
            print("⚠️  审查通过 - 存在警告项，建议改进")
        else:
            print(f"❌ 审查未通过 - 有 {total_fail} 项未通过检查")
        
        print("=" * 80)


if __name__ == '__main__':
    reviewer = SprintBReviewer()
    success = reviewer.run_all_checks()
    
    # 退出码
    sys.exit(0 if success else 1)
