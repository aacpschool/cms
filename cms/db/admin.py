#!/usr/bin/env python3

# Contest Management System - http://cms-dev.github.io/
# Copyright © 2015 Stefano Maggiolo <s.maggiolo@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Admin-related database interfaces for SQLAlchemy.

zh: 管理員相關的資料庫介面定義。
en: Database interfaces for contest administrators.
"""

from sqlalchemy.schema import Column
from sqlalchemy.types import Boolean, Integer, Unicode

from . import Codename, Base


class Admin(Base):
    """Admin table.

    zh: 儲存可存取管理後台的管理員帳號資訊。
    en: Stores information for users who can access the AdminWebServer.
    """

    __tablename__ = 'admins'

    # zh: 自增主鍵
    # en: Auto increment primary key.
    # Auto increment primary key.
    id = Column(
        Integer,
        primary_key=True)

    # zh: 使用者真實姓名
    # en: Real name of the administrator.
    # Real name (human readable) of the user.
    name = Column(
        Unicode,
        nullable=False)

    # zh: 登入 AWS 時使用的帳號名稱
    # en: Username used to log in to the AdminWebServer.
    # Username used to log in in AWS.
    username = Column(
        Codename,
        nullable=False,
        unique=True)

    # zh: 驗證字串，格式 <類型>:<字串>
    # en: Authentication string in the format <type>:<string>.
    # String used to authenticate the user, in the format
    # <authentication type>:<authentication_string>
    authentication = Column(
        Unicode,
        nullable=False)

    # zh: 帳號是否啟用；停用帳號將被視為不存在
    # en: Whether the account is enabled; disabled accounts are inactive.
    # Whether the account is enabled. Disabled accounts have their
    # info kept in the database, but for all other purposes it is like
    # they did not exist.
    enabled = Column(
        Boolean,
        nullable=False,
        default=True)

    # zh: 全域存取權限；擁有此權限可執行所有操作
    # en: All-access bit; grants permission to perform any operation.
    # All-access bit. If this is set, the admin can do any operation
    # in AWS, regardless of the value of the other access bits.
    permission_all = Column(
        Boolean,
        nullable=False,
        default=False)

    # zh: 訊息存取權限；可發布公告與私訊參賽者
    # en: Messaging-access bit; allows sending announcements and private messages.
    # Messaging-access bit. If this is set, the admin can communicate
    # with the contestants via announcement, private messages and
    # questions.
    permission_messaging = Column(
        Boolean,
        nullable=False,
        default=False)
