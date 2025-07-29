# OrKa: Orchestrator Kit Agents
# Copyright © 2025 Marco Somma
#
# This file is part of OrKa – https://github.com/marcosomma/orka-resoning
#
# Licensed under the Apache License, Version 2.0 (Apache 2.0).
# You may not use this file for commercial purposes without explicit permission.
#
# Full license: https://www.apache.org/licenses/LICENSE-2.0
# For commercial use, contact: marcosomma.work@gmail.com
#
# Required attribution: OrKa by Marco Somma – https://github.com/marcosomma/orka-resoning

from dotenv import load_dotenv
from fake_redis import FakeRedisClient

from orka.memory_logger import RedisMemoryLogger

# Load env
load_dotenv()


def test_logger_write_and_read(monkeypatch):
    # Inject fake Redis client
    logger = RedisMemoryLogger()
    logger.client = FakeRedisClient()

    logger.log("test_agent", "output", {"foo": "bar"})

    # Validate written item
    items = logger.client.xrevrange("orka:memory", count=1)
    assert len(items) == 1
    assert "agent_id" in items[0]  # or items[0].get("agent_id")
