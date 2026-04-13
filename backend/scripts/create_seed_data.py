import uuid
from datetime import datetime, timezone, timedelta
from app.db.session import SessionLocal
from app.models import (
    User, AdminUser, Resource, ResourceStatus, 
    Topic, Post, TopicStatus, Feedback, 
    FeedbackStatus, FileMeta, FileStatus, FileUsage, TargetType
)
from app.core.security import hash_password, generate_phone_blind_index

def create_seed_data():
    db = SessionLocal()
    try:
        # 1. Create Users
        users = []
        # Admin
        admin_id = uuid.uuid4().hex
        admin_user = User(
            id=admin_id,
            nickname="系统管理员",
            phone="13800000000",
            phone_blind_index=generate_phone_blind_index("13800000000"),
            password_hash=hash_password("admin123"),
            rank="高级工程师",
            reputation_points=1000,
            gold_beans=10000,
            status="ACTIVE"
        )
        db.add(admin_user)
        
        # Admin Record
        admin_rec = AdminUser(
            id=admin_id,
            username="admin",
            role="SUPER_ADMIN",
            is_active=True
        )
        db.add(admin_rec)
        
        # Test Users
        for i in range(1, 6):
            u_id = uuid.uuid4().hex
            u_phone = f"1390000000{i}"
            u = User(
                id=u_id,
                nickname=f"测试用户{i}",
                phone=u_phone,
                phone_blind_index=generate_phone_blind_index(u_phone),
                password_hash=hash_password("user123"),
                rank="新兵" if i > 2 else "老兵",
                reputation_points=50 if i > 2 else 150,
                gold_beans=100,
                status="ACTIVE",
                created_at=datetime.now(timezone.utc) - timedelta(days=i*2)
            )
            db.add(u)
            users.append(u)
        
        db.commit()
        print("Users created.")

        # 2. Create File Meta
        file_id = uuid.uuid4().hex
        file_meta = FileMeta(
            file_uuid=file_id,
            file_hash="d41d8cd98f00b204e9800998ecf8427e",
            oss_path="resources/test_guide.pdf",
            file_name="可靠性设计指南.pdf",
            file_size=2048576,
            mime_type="application/pdf",
            status=FileStatus.NORMAL.value,
            uploader_uid=users[0].id
        )
        db.add(file_meta)
        db.commit()
        print("FileMeta created.")

        # 3. Create Resources
        for i in range(1, 6):
            res_id = uuid.uuid4().hex
            res = Resource(
                id=res_id,
                uploader_id=users[i-1].id,
                title=f"可靠性测试资源 {i}",
                description=f"这是关于可靠性测试的第 {i} 份详细资源。",
                category_id=1,
                tags=f"['可靠性', '测试', '资源{i}']",
                price=10 * i,
                file_uuid=file_id,
                status=ResourceStatus.APPROVED,
                view_count=100 * i,
                download_count=10 * i,
                like_count=5 * i,
                heat_score=50.5 + i
            )
            db.add(res)
            
            # File Usage
            usage = FileUsage(
                id=uuid.uuid4().hex,
                file_uuid=file_id,
                target_id=res_id,
                target_type=TargetType.RESOURCE.value,
                user_id=users[i-1].id
            )
            db.add(usage)
            
        db.commit()
        print("Resources created.")

        # 4. Create Topics & Posts
        for i in range(1, 6):
            t_id = uuid.uuid4().hex
            topic = Topic(
                id=t_id,
                author_id=users[i-1].id,
                title=f"如何提高系统可靠性? {i}",
                content=f"在我的项目中，我遇到了关于系统可靠性的问题 {i}...",
                category_id=2,
                status=TopicStatus.NORMAL,
                view_count=50 * i,
                post_count=1,
                heat_score=20.0 + i,
                created_at=datetime.now(timezone.utc) - timedelta(days=i)
            )
            db.add(topic)
            
            # Post
            post = Post(
                id=uuid.uuid4().hex,
                topic_id=t_id,
                author_id=users[5-i].id,
                content=f"我觉得你可以尝试使用冗余设计方案 {i}。",
                like_count=i
            )
            db.add(post)
            
        db.commit()
        print("Topics created.")

        # 5. Create Feedbacks
        for i in range(1, 4):
            fb = Feedback(
                id=uuid.uuid4().hex,
                type="BUG" if i == 1 else "SUGGESTION",
                content=f"反馈内容 {i}: 这是一个测试反馈。",
                status=FeedbackStatus.PENDING,
                created_at=datetime.now(timezone.utc)
            )
            db.add(fb)
            
        db.commit()
        print("Feedbacks created.")

        print("Seed data creation successful!")

    except Exception as e:
        db.rollback()
        print(f"Error creating seed data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_seed_data()
