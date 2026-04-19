import uuid
from datetime import datetime, timezone, timedelta
from app.db.session import SessionLocal
from app.models import (
    User, AdminUser, Resource, ResourceStatus, 
    Topic, Post, TopicStatus, Feedback, 
    FeedbackStatus, FileMeta, FileStatus, FileUsage, TargetType
)
from app.core.security import hash_password, generate_phone_blind_index

TEST_ACCOUNTS = [
    {"phone": "13800000001", "password": "Reli@Super2026!", "nickname": "ReliAdmin", "rank": "专家", "reputation_points": 9999, "gold_beans": 9999, "admin_role": "SUPER_ADMIN", "admin_username": "reliadmin"},
    {"phone": "13800000002", "password": "Reli@Mod2026!", "nickname": "ReliModerator", "rank": "老炮", "reputation_points": 1200, "gold_beans": 500, "admin_role": "OPERATOR", "admin_username": "relimod"},
    {"phone": "13800000011", "password": "Reli@Xin2026!", "nickname": "赵新兵", "rank": "新兵", "reputation_points": 50, "gold_beans": 20},
    {"phone": "13800000012", "password": "Reli@Xin2026b", "nickname": "钱小白", "rank": "新兵", "reputation_points": 80, "gold_beans": 30},
    {"phone": "13800000013", "password": "Reli@Cai2026!", "nickname": "孙菜鸟", "rank": "菜鸟", "reputation_points": 150, "gold_beans": 80},
    {"phone": "13800000014", "password": "Reli@Cai2026b", "nickname": "李初学", "rank": "菜鸟", "reputation_points": 250, "gold_beans": 120},
    {"phone": "13800000015", "password": "Reli@Ru2026!", "nickname": "周入门", "rank": "入门", "reputation_points": 400, "gold_beans": 200},
    {"phone": "13800000016", "password": "Reli@Ru2026b", "nickname": "吴进阶", "rank": "入门", "reputation_points": 550, "gold_beans": 300},
    {"phone": "13800000017", "password": "Reli@Shu2026!", "nickname": "郑熟手", "rank": "熟手", "reputation_points": 700, "gold_beans": 500},
    {"phone": "13800000018", "password": "Reli@Shu2026b", "nickname": "王资深", "rank": "熟手", "reputation_points": 900, "gold_beans": 600},
    {"phone": "13800000019", "password": "Reli@Lao2026!", "nickname": "冯老炮", "rank": "老炮", "reputation_points": 1200, "gold_beans": 800},
    {"phone": "13800000020", "password": "Reli@Da2026!", "nickname": "陈达人", "rank": "达人", "reputation_points": 2500, "gold_beans": 1200},
    {"phone": "13800000021", "password": "Reli@Zhuan2026!", "nickname": "魏专家", "rank": "专家", "reputation_points": 6000, "gold_beans": 3000},
]


def create_seed_data():
    db = SessionLocal()
    try:
        users = []

        for i, acct in enumerate(TEST_ACCOUNTS):
            u_id = uuid.uuid4().hex
            u = User(
                id=u_id,
                nickname=acct["nickname"],
                phone=acct["phone"],
                phone_blind_index=generate_phone_blind_index(acct["phone"]),
                password_hash=hash_password(acct["password"]),
                rank=acct["rank"],
                reputation_points=acct["reputation_points"],
                gold_beans=acct["gold_beans"],
                bonus_beans=0,
                status="ACTIVE",
                invite_code=uuid.uuid4().hex[:8].upper(),
                agreement_timestamp=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc) - timedelta(days=len(TEST_ACCOUNTS) - i),
            )
            db.add(u)
            users.append(u)

            if "admin_role" in acct:
                admin_rec = AdminUser(
                    id=u_id,
                    username=acct["admin_username"],
                    password_hash=hash_password(acct["password"]),
                    role=acct["admin_role"],
                    is_active=True,
                )
                db.add(admin_rec)

        db.commit()
        print(f"Created {len(users)} test users (2 admin + 10 regular).")

        file_id = uuid.uuid4().hex
        file_meta = FileMeta(
            file_uuid=file_id,
            file_hash="d41d8cd98f00b204e9800998ecf8427e",
            oss_path="resources/test_guide.pdf",
            file_name="可靠性设计指南.pdf",
            file_size=2048576,
            mime_type="application/pdf",
            status=FileStatus.NORMAL.value,
            uploader_uid=users[2].id
        )
        db.add(file_meta)
        db.commit()
        print("FileMeta created.")

        regular_users = users[2:]
        for i, u in enumerate(regular_users):
            res_id = uuid.uuid4().hex
            res = Resource(
                id=res_id,
                uploader_id=u.id,
                title=f"可靠性测试资源 {i+1}",
                description=f"这是关于可靠性测试的第 {i+1} 份详细资源。",
                category_id=1,
                tags=f"['可靠性', '测试', '资源{i+1}']",
                price=10 * (i + 1),
                file_uuid=file_id,
                status=ResourceStatus.APPROVED,
                view_count=100 * (i + 1),
                download_count=10 * (i + 1),
                like_count=5 * (i + 1),
                heat_score=50.5 + i
            )
            db.add(res)

            usage = FileUsage(
                id=uuid.uuid4().hex,
                file_uuid=file_id,
                target_id=res_id,
                target_type=TargetType.RESOURCE.value,
                user_id=u.id
            )
            db.add(usage)

        db.commit()
        print("Resources created.")

        for i, u in enumerate(regular_users):
            t_id = uuid.uuid4().hex
            topic = Topic(
                id=t_id,
                author_id=u.id,
                title=f"如何提高系统可靠性? {i+1}",
                content=f"在我的项目中，我遇到了关于系统可靠性的问题 {i+1}...",
                category_id=2,
                status=TopicStatus.NORMAL,
                view_count=50 * (i + 1),
                post_count=1,
                heat_score=20.0 + i,
                created_at=datetime.now(timezone.utc) - timedelta(days=i)
            )
            db.add(topic)

            other_idx = (i + 1) % len(regular_users)
            post = Post(
                id=uuid.uuid4().hex,
                topic_id=t_id,
                author_id=regular_users[other_idx].id,
                content=f"我觉得你可以尝试使用冗余设计方案 {i+1}。",
                like_count=i + 1
            )
            db.add(post)

        db.commit()
        print("Topics created.")

        for i in range(1, 4):
            fb = Feedback(
                id=uuid.uuid4().hex,
                user_id=regular_users[i % len(regular_users)].id,
                type="BUG" if i == 1 else "SUGGESTION",
                content=f"反馈内容 {i}: 这是一个测试反馈。",
                status=FeedbackStatus.PENDING,
                created_at=datetime.now(timezone.utc)
            )
            db.add(fb)

        db.commit()
        print("Feedbacks created.")

        print("\n=== Seed data creation successful! ===")
        print("\nTest accounts (also saved in prototype/test-accounts.csv):")
        print(f"{'Role':<12} {'Rank':<6} {'Nickname':<14} {'Phone':<13} {'Password':<18}")
        print("-" * 70)
        for acct in TEST_ACCOUNTS:
            role = acct.get("admin_role", "用户")
            print(f"{role:<12} {acct['rank']:<6} {acct['nickname']:<14} {acct['phone']:<13} {acct['password']:<18}")

    except Exception as e:
        db.rollback()
        print(f"Error creating seed data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_seed_data()
