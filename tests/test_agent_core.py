import pytest
from agent_core.planner import Planner
from agent_core.executor import Executor

def test_agent_core_basic():
    planner = Planner()
    executor = Executor()
    assert planner is not None
    assert executor is not None
    assert True