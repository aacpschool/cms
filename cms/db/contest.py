#!/usr/bin/env python3

# Contest Management System - http://cms-dev.github.io/
# Copyright © 2010-2012 Giovanni Mascellani <mascellani@poisson.phc.unipi.it>
# Copyright © 2010-2018 Stefano Maggiolo <s.maggiolo@gmail.com>
# Copyright © 2010-2012 Matteo Boscariol <boscarim@hotmail.com>
# Copyright © 2012-2018 Luca Wehrstedt <luca.wehrstedt@gmail.com>
# Copyright © 2013 Bernard Blackham <bernard@largestprime.net>
# Copyright © 2016 Myungwoo Chun <mc.tamaki@gmail.com>
# Copyright © 2016 Amir Keivan Mohtashami <akmohtashami97@gmail.com>
# Copyright © 2018 William Di Luigi <williamdiluigi@gmail.com>
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

"""Contest-related database interface for SQLAlchemy.

"""
# 與比賽相關的 SQLAlchemy 數據庫介面。

from datetime import datetime, timedelta

from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, CheckConstraint
from sqlalchemy.types import Integer, Unicode, DateTime, Interval, Enum, \
    Boolean, String

from cms import TOKEN_MODE_DISABLED, TOKEN_MODE_FINITE, TOKEN_MODE_INFINITE
from . import Codename, Base, Admin


class Contest(Base):
    """Class to store a contest (which is a single day of a
    programming competition).

    """
    # 用於存儲比賽的類（即一天的程式設計競賽）。
    __tablename__ = 'contests'
    __table_args__ = (
        CheckConstraint("start <= stop"),
        CheckConstraint("stop <= analysis_start"),
        CheckConstraint("analysis_start <= analysis_stop"),
        CheckConstraint("token_gen_initial <= token_gen_max"),
    )

    # 主鍵自動遞增。
    # Auto increment primary key.
    id = Column(
        Integer,
        primary_key=True)

    # 比賽的簡短名稱。
    # Short name of the contest.
    name = Column(
        Codename,
        nullable=False,
        unique=True)
    # 比賽的描述（人類可讀）。
    # Description of the contest (human readable).
    description = Column(
        Unicode,
        nullable=False)

    # 允許參賽者使用的本地化語言代碼列表（空表示全部）。
    # The list of language codes of the localizations that contestants
    # are allowed to use (empty means all).
    allowed_localizations = Column(
        ARRAY(String),
        nullable=False,
        default=[])

    # 比賽中允許使用的語言名稱列表。
    # The list of names of languages allowed in the contest.
    languages = Column(
        ARRAY(String),
        nullable=False,
        default=["C++17 / g++"])

    # 是否允許參賽者下載他們的提交。
    # Whether contestants allowed to download their submissions.
    submissions_download_allowed = Column(
        Boolean,
        nullable=False,
        default=True)

    # 是否啟用用戶問題功能。
    # Whether the user question is enabled.
    allow_questions = Column(
        Boolean,
        nullable=False,
        default=True)

    # 是否啟用用戶測試介面。
    # Whether the user test interface is enabled.
    allow_user_tests = Column(
        Boolean,
        nullable=False,
        default=True)

    # 是否阻止隱藏的參賽者登入。
    # Whether to prevent hidden participations to log in.
    block_hidden_participations = Column(
        Boolean,
        nullable=False,
        default=False)

    # 是否允許使用者名稱/密碼認證。
    # Whether to allow username/password authentication
    allow_password_authentication = Column(
        Boolean,
        nullable=False,
        default=True)

    # 是否啟用新用戶註冊。
    # Whether the registration of new users is enabled.
    allow_registration = Column(
        Boolean,
        nullable=False,
        default=False)

    # 是否強制請求的 IP 地址必須與參賽者指定的 IP 地址或子網相符（如果有）。
    # Whether to enforce that the IP address of the request matches
    # the IP address or subnet specified for the participation (if
    # present).
    ip_restriction = Column(
        Boolean,
        nullable=False,
        default=True)

    # 是否自動登入來自參賽者 IP 的使用者。
    # Whether to automatically log in users connecting from an IP
    # address specified in the ip field of a participation to this
    # contest.
    ip_autologin = Column(
        Boolean,
        nullable=False,
        default=False)

    # 控制比賽令牌的參數。注意，這些參數在比賽期間的效果取決於與每個任務上定義的任務令牌參數的互動。

    # 比賽期間令牌規則的“類型”。
    # - disabled: 使用者永遠無法使用任何令牌。
    # - finite: 使用者有有限數量的令牌，可以選擇何時使用，但受某些限制。令牌可能不會全部在開始時可用，而是在比賽期間定期發放。
    # - infinite: 使用者將始終能夠使用令牌。
    # The "kind" of token rules that will be active during the contest.
    # - disabled: The user will never be able to use any token.
    # - finite: The user has a finite amount of tokens and can choose
    #   when to use them, subject to some limitations. Tokens may not
    #   be all available at start, but given periodically during the
    #   contest instead.
    # - infinite: The user will always be able to use a token.
    token_mode = Column(
        Enum(TOKEN_MODE_DISABLED, TOKEN_MODE_FINITE, TOKEN_MODE_INFINITE,
             name="token_mode"),
        nullable=False,
        default=TOKEN_MODE_INFINITE)

    # 參賽者在整個比賽期間允許使用的最大令牌數量（所有任務總和）。
    # The maximum number of tokens a contestant is allowed to use
    # during the whole contest (on all tasks).
    token_max_number = Column(
        Integer,
        CheckConstraint("token_max_number > 0"),
        nullable=True)

    # 同一使用者兩次使用令牌之間的最小間隔（任務不限）。
    # The minimum interval between two successive uses of tokens for
    # the same user (on any task).
    token_min_interval = Column(
        Interval,
        CheckConstraint("token_min_interval >= '0 seconds'"),
        nullable=False,
        default=timedelta())

    # 控制生成的參數（如果模式是“有限”）：使用者開始時有“initial”個令牌，每隔“interval”會收到“number”個令牌，但總數被限制為“max”。
    # The parameters that control generation (if mode is "finite"):
    # the user starts with "initial" tokens and receives "number" more
    # every "interval", but their total number is capped to "max".
    token_gen_initial = Column(
        Integer,
        CheckConstraint("token_gen_initial >= 0"),
        nullable=False,
        default=2)
    token_gen_number = Column(
        Integer,
        CheckConstraint("token_gen_number >= 0"),
        nullable=False,
        default=2)
    token_gen_interval = Column(
        Interval,
        CheckConstraint("token_gen_interval > '0 seconds'"),
        nullable=False,
        default=timedelta(minutes=30))
    token_gen_max = Column(
        Integer,
        CheckConstraint("token_gen_max > 0"),
        nullable=True)

    # 比賽的開始和結束時間。
    # Beginning and ending of the contest.
    start = Column(
        DateTime,
        nullable=False,
        default=datetime(2025, 1, 1))
    stop = Column(
        DateTime,
        nullable=False,
        default=datetime(2025, 1, 1))

    # 比賽分析模式的開始和結束時間。
    # Beginning and ending of the contest anaylsis mode.
    analysis_enabled = Column(
        Boolean,
        nullable=False,
        default=False)
    analysis_start = Column(
        DateTime,
        nullable=False,
        default=datetime(2030, 1, 1))
    analysis_stop = Column(
        DateTime,
        nullable=False,
        default=datetime(2030, 1, 1))

    # 比賽的時區。所有 CWS 中的時間戳將使用登入使用者關聯的時區顯示，或者（如果為 None 或無效字串）使用比賽關聯的時區，或者（如果為 None 或無效字串）使用伺服器本地時區。此值必須是類似 "Europe/Rome"、"Australia/Sydney"、"America/New_York" 等的字串。
    # Timezone for the contest. All timestamps in CWS will be shown
    # using the timezone associated to the logged-in user or (if it's
    # None or an invalid string) the timezone associated to the
    # contest or (if it's None or an invalid string) the local
    # timezone of the server. This value has to be a string like
    # "Europe/Rome", "Australia/Sydney", "America/New_York", etc.
    timezone = Column(
        Unicode,
        nullable=True)

    # 每個使用者的最大比賽時間（秒）。
    # Max contest time for each user in seconds.
    per_user_time = Column(
        Interval,
        CheckConstraint("per_user_time >= '0 seconds'"),
        nullable=True)

    # 每個使用者在整個比賽期間允許的最大提交數或用戶測試數，或 None 表示不限制。
    # Maximum number of submissions or user_tests allowed for each user
    # during the whole contest or None to not enforce this limitation.
    max_submission_number = Column(
        Integer,
        CheckConstraint("max_submission_number > 0"),
        nullable=True)
    max_user_test_number = Column(
        Integer,
        CheckConstraint("max_user_test_number > 0"),
        nullable=True)

    # 兩次提交或用戶測試之間的最小間隔，或 None 表示不限制。
    # Minimum interval between two submissions or user_tests, or None to
    # not enforce this limitation.
    min_submission_interval = Column(
        Interval,
        CheckConstraint("min_submission_interval > '60 seconds'"),
        nullable=True)
    min_user_test_interval = Column(
        Interval,
        CheckConstraint("min_user_test_interval > '0 seconds'"),
        nullable=True)

    # 此比賽的分數將四捨五入到此小數位數。
    # The scores for this contest will be rounded to this number of
    # decimal places.
    score_precision = Column(
        Integer,
        CheckConstraint("score_precision >= 0"),
        nullable=False,
        default=0)

    # 這些一對多關係是“子”類中使用外鍵定義的反向方向。

    # These one-to-many relationships are the reversed directions of
    # the ones defined in the "child" classes using foreign keys.

    tasks = relationship(
        "Task",
        collection_class=ordering_list("num"),
        order_by="[Task.num]",
        cascade="all",
        passive_deletes=True,
        back_populates="contest")

    announcements = relationship(
        "Announcement",
        order_by="[Announcement.timestamp]",
        cascade="all, delete-orphan",
        passive_deletes=True,
        back_populates="contest")

    participations = relationship(
        "Participation",
        cascade="all, delete-orphan",
        passive_deletes=True,
        back_populates="contest")

    def phase(self, timestamp):
        """Return: -1 if contest isn't started yet at time timestamp,
                    0 if the contest is active at time timestamp,
                    1 if the contest has ended but analysis mode
                      hasn't started yet
                    2 if the contest has ended and analysis mode is active
                    3 if the contest has ended and analysis mode is disabled or
                      has ended

        timestamp (datetime): the time we are iterested in.
        return (int): contest phase as above.

        """
        # 返回：如果比賽在 timestamp 時間尚未開始，返回 -1；
        # 如果比賽在 timestamp 時間正在進行，返回 0；
        # 如果比賽已結束但分析模式尚未開始，返回 1；
        # 如果比賽已結束且分析模式正在進行，返回 2；
        # 如果比賽已結束且分析模式被禁用或已結束，返回 3。
        if timestamp < self.start:
            return -1
        if timestamp <= self.stop:
            return 0
        if self.analysis_enabled:
            if timestamp < self.analysis_start:
                return 1
            elif timestamp <= self.analysis_stop:
                return 2
        return 3


class Announcement(Base):
    """Class to store a messages sent by the contest managers to all
    the users.

    """
    # 用於存儲比賽管理員發送給所有用戶的消息的類。
    __tablename__ = 'announcements'

    # 主鍵自動遞增。
    # Auto increment primary key.
    id = Column(
        Integer,
        primary_key=True)

    # 公告的時間、主題和內容。
    # Time, subject and text of the announcement.
    timestamp = Column(
        DateTime,
        nullable=False)
    subject = Column(
        Unicode,
        nullable=False)
    text = Column(
        Unicode,
        nullable=False)

    # 擁有該公告的比賽（ID 和對象）。
    # Contest (id and object) owning the announcement.
    contest_id = Column(
        Integer,
        ForeignKey(Contest.id,
                   onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True)
    contest = relationship(
        Contest,
        back_populates="announcements")

    # 創建公告的管理員（如果管理員已被刪除則為空）。管理員僅鬆散地“擁有”公告，因此我們不在 Admin 中反向關聯任何欄位，也不會在管理員被刪除時刪除公告。
    # Admin that created the announcement (or null if the admin has been
    # later deleted). Admins only loosely "own" an announcement, so we do not
    # back populate any field in Admin, nor delete the announcement if the
    # admin gets deleted.
    admin_id = Column(
        Integer,
        ForeignKey(Admin.id,
                   onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
        index=True)
    admin = relationship(Admin)