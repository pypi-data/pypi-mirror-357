"""
# File       : models.py
# Time       ：2024/8/20 下午5:20
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Table, UniqueConstraint, PrimaryKeyConstraint
from passlib.context import CryptContext
from svc_user_auth_zxw.apis.schemas import Payload

Base = declarative_base()  # 创建一个基类,

user_role_table = Table(
    'user_role',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    # 账号 - 必填
    username = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=False, nullable=True)
    phone = Column(String, unique=True, index=True, nullable=True)
    openid = Column(String, unique=True, index=True, nullable=True)
    # 密码，可以为空，因为有的用户可能是第三方登录
    hashed_password = Column(String, nullable=True)
    #
    nickname = Column(String, nullable=True)
    notes = Column(String, nullable=True)

    referer_id = Column(Integer, ForeignKey('users.id'), nullable=True, comment="邀请人id")
    referer = relationship("User", remote_side=[id], backref="invitees")

    # secondary作用是指定中间表，back_populates作用是指定反向关系
    # 中间表用于存储多对多关系，反向关系用于在查询时，通过一个表查询另一个表
    # lazy='selectin'表示在查询时，会将关联的表一次性查询出来，而不是按需查询. 可以在fastapi中避免由于session关闭导致的查询异常。
    roles = relationship(
        "Role",
        secondary=user_role_table,
        back_populates="users",
        join_depth=2  # 保留这个设置以确保预加载到 App 层级
    )

    def verify_password(self, password: str) -> bool:
        # 密码为空代表是第三方登录
        if password == "":
            return False
        return pwd_context.verify(password, self.hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    async def to_payload(self) -> Payload:
        # 修改为异步方法
        roles_data = []
        for role in self.roles:
            # 使用 awaitable 方式访问关联数据
            app = role.app
            print("[User.to_payload] app = ", app)
            roles_data.append({
                "role_name": role.name,
                "app_id": role.app_id,
                "app_name": app.name if app else None
            })

        return Payload(
            sub=self.username,
            username=self.username,
            nickname=self.nickname,
            roles=roles_data
        )


class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    app_id = Column(Integer, ForeignKey('apps.id'))

    # 移除联合主键约束，改为唯一约束
    __table_args__ = (
        UniqueConstraint('name', 'app_id', name='uq_role_name_app_id'),
    )

    app = relationship(
        "App",
        back_populates="roles",
        lazy='selectin'
    )
    users = relationship(
        "User",
        secondary=user_role_table,
        back_populates="roles"
    )


class App(Base):
    __tablename__ = 'apps'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    roles = relationship("Role", back_populates="app")
    UniqueConstraint('name', name='uq_app_name')
