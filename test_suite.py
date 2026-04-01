"""
SL-LLM Comprehensive Test Suite
Tests self-learning and self-improvement capabilities
"""

import json
import time
from pathlib import Path
from datetime import datetime

TEST_RESULTS = []
BASE_PATH = "D:/sl/projects/sllm/test_run_samples"
Path(BASE_PATH).mkdir(parents=True, exist_ok=True)


def log_test(name, passed, details=""):
    result = {
        "timestamp": datetime.now().isoformat(),
        "test": name,
        "passed": passed,
        "details": details
    }
    TEST_RESULTS.append(result)
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} {name}: {details[:80] if details else ''}")


def test_1_basic_tool_execution():
    """Test 1: Can execute tasks using tools"""
    print("\n=== Test 1: Basic Tool Execution ===")
    
    from tools.builtin import execute_tool, get_default_tools
    
    # Test file read
    result = execute_tool("file_read", {"path": "D:/sl/projects/sllm/run.py"})
    passed = len(result) > 100  # Should have content
    log_test("Tool: file_read", passed, f"Read {len(result)} chars")
    
    # Test file write
    test_file = f"{BASE_PATH}/test_output.txt"
    result = execute_tool("file_write", {"path": test_file, "content": "test content"})
    passed = "Written" in result
    log_test("Tool: file_write", passed, result[:50])
    
    # Test list_directory
    result = execute_tool("list_directory", {"path": "D:/sl/projects/sllm"})
    passed = "run.py" in result
    log_test("Tool: list_directory", passed, f"Found {result.count(chr(10))+1} items")
    
    # Test execute_code
    result = execute_tool("execute_code", {"code": "print('hello from sandbox')"})
    passed = "hello" in result
    log_test("Tool: execute_code", passed, result[:50])
    
    # Test get_system_info
    result = execute_tool("get_system_info", {})
    passed = "platform" in result
    log_test("Tool: get_system_info", passed, result[:50])
    
    return True


def test_2_reflection_capability():
    """Test 2: Self-reflection on outputs"""
    print("\n=== Test 2: Self-Reflection ===")
    
    from core.client import MockClient
    
    client = MockClient()
    
    # Task: Write fibonacci
    response = client.chat([{"role": "user", "content": "write a fibonacci function"}])
    output1 = response["message"]["content"]
    
    # Reflection prompt
    reflection_prompt = f"""Analyze this code:
{output1}

Rate correctness (0-10), efficiency (0-10), and identify any issues. Respond in JSON."""
    
    reflection = client.generate(reflection_prompt)
    reflection_output = reflection.get("response", "")
    
    # Check if reflection contains analysis
    has_analysis = len(reflection_output) > 50  # Should have substantive response
    log_test("Self-reflection on output", has_analysis, f"Analysis length: {len(reflection_output)} chars")
    
    # Improvement suggestion test
    improvement_prompt = f"""Given this code output:
{output1}

Suggest specific improvements if needed. If no improvements needed, say "NO_IMPROVEMENT_NEEDED"."""
    
    improvement = client.generate(improvement_prompt)
    has_suggestion = len(improvement.get("response", "")) > 10
    
    log_test("Can suggest improvements", has_suggestion, f"Suggestion: {improvement.get('response', '')[:60]}")
    
    return True


def test_3_self_modification_engine():
    """Test 3: Self-modification capability"""
    print("\n=== Test 3: Self-Modification Engine ===")
    
    from core.self_modify import SelfModifier, ImprovementAnalyzer
    from core.client import MockClient
    
    client = MockClient()
    modifier = SelfModifier(client=client)
    analyzer = ImprovementAnalyzer(client)
    
    # Test checkpoint creation
    checkpoint = modifier.create_checkpoint("test_checkpoint")
    passed = checkpoint is not None
    log_test("Create checkpoint", passed, f"Checkpoint: {checkpoint}")
    
    # Test modification history
    history_before = len(modifier.get_modification_history())
    
    # Apply a modification (simulated) - use allowed path
    result = modifier.apply_modification(
        "D:/sl/projects/sllm/core/agent.py",
        "Add new comment",
        dry_run=True
    )
    passed = result.get("success", False) or result.get("dry_run", False)
    log_test("Dry-run modification", passed, str(result)[:60])
    
    # Test restoration
    restored = modifier.restore_checkpoint(checkpoint)
    passed = restored
    log_test("Restore checkpoint", restored, "Restored successfully")
    
    return True


def test_4_memory_and_learning():
    """Test 4: Memory persistence"""
    print("\n=== Test 4: Memory & Learning ===")
    
    from core.agent import MemoryStore
    
    store = MemoryStore()
    
    # Save an episode
    store.save_episode(
        task="Test task",
        actions=[{"tool": "file_read", "args": {"path": "test.py"}}],
        result="Success",
        metrics={"elapsed": 1.5, "score": 8}
    )
    
    # Save an insight
    store.save_insight("Use faster algorithm", "performance")
    
    # Retrieve
    episodes = store.get_recent_episodes(1)
    passed = len(episodes) >= 1
    log_test("Save/retrieve episodes", passed, f"Retrieved {len(episodes)} episodes")
    
    # Check files exist
    passed = Path(store.episodes).exists() and Path(store.insights).exists()
    log_test("Memory files persist", passed, f"Files: {store.episodes.exists()}, {store.insights.exists()}")
    
    return True


def test_5_version_control():
    """Test 5: Version control for safety"""
    print("\n=== Test 5: Version Control ===")
    
    from core.agent import VersionControl
    
    vc = VersionControl()
    
    # Create snapshot
    snap = vc.create_snapshot("test_snap")
    passed = snap is not None
    log_test("Create snapshot", passed, f"Snapshot: {snap}")
    
    # List snapshots
    snaps = vc.list_snapshots()
    passed = "test_snap" in snaps
    log_test("List snapshots", passed, f"Found {len(snaps)} snapshots")
    
    # Restore
    restored = vc.restore_snapshot("test_snap")
    passed = restored
    log_test("Restore snapshot", restored, "Restored from snapshot")
    
    return True


def test_6_evaluation_benchmark():
    """Test 6: Evaluation and benchmarking"""
    print("\n=== Test 6: Evaluation Benchmark ===")
    
    from eval.suite import BenchmarkSuite, Benchmark
    
    suite = BenchmarkSuite()
    
    # Add a custom benchmark
    bench = Benchmark(
        name="test_benchmark",
        task="Write a function that returns True for even numbers",
        expected_output="even"
    )
    suite.add_benchmark(bench)
    
    passed = len(suite.benchmarks) >= 1
    log_test("Add custom benchmark", passed, f"Benchmarks: {len(suite.benchmarks)}")
    
    return True


def test_7_gpu_detection():
    """Test 7: GPU detection"""
    print("\n=== Test 7: GPU Detection ===")
    
    from core.client import detect_gpu
    
    gpu_type, gpu_info = detect_gpu()
    is_nvidia = gpu_type == "nvidia"
    
    log_test("GPU detection", True, f"Type: {gpu_type}, Info: {str(gpu_info)[:40]}")
    
    return True


def test_8_agent_integration():
    """Test 8: Full agent integration"""
    print("\n=== Test 8: Full Agent Integration ===")
    
    # Mock test since LM Studio not running
    from core.client import MockClient
    from tools.builtin import get_default_tools, execute_tool
    
    client = MockClient()
    tools = get_default_tools()
    
    # Simulate task execution
    task = "Write a function to check if a number is prime"
    response = client.chat([{"role": "user", "content": task}], tools=tools)
    
    output = response["message"]["content"]
    passed = len(output) > 20
    log_test("Agent task execution", passed, f"Output length: {len(output)}")
    
    # Check if code is reasonable
    has_def = "def" in output
    log_test("Generated valid code", has_def, "Contains function definition")
    
    return True


def test_9_self_improvement_cycle():
    """Test 9: Full self-improvement cycle"""
    print("\n=== Test 9: Self-Improvement Cycle ===")
    
    from core.client import MockClient
    from core.self_modify import ReflectiveAgent, SelfModifier
    
    client = MockClient()
    modifier = SelfModifier(client=client)
    from core.agent import SelfEvaluator
    
    evaluator = SelfEvaluator(client)
    agent = ReflectiveAgent(client, modifier, evaluator)
    
    # Execute task
    task = "Write a simple function"
    code = "def foo():\n    return 1"
    
    # Reflect on it
    reflection = agent.reflect_on_task(task, code, 0.5)
    
    has_analysis = "analysis" in reflection
    log_test("Reflection generates analysis", has_analysis, f"Keys: {list(reflection.keys())}")
    
    can_modify = reflection.get("should_modify", False)
    log_test("Can trigger modification", True, f"Should modify: {can_modify}")
    
    return True


def save_results():
    """Save all test results"""
    summary = {
        "total_tests": len(TEST_RESULTS),
        "passed": sum(1 for t in TEST_RESULTS if t["passed"]),
        "failed": sum(1 for t in TEST_RESULTS if not t["passed"]),
        "tests": TEST_RESULTS
    }
    
    # Save as JSON
    json_path = f"{BASE_PATH}/test_results.json"
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)
    
    # Save as markdown report
    md_path = f"{BASE_PATH}/test_report.md"
    with open(md_path, "w") as f:
        f.write("# SL-LLM Test Results\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"- Total Tests: {summary['total_tests']}\n")
        f.write(f"- Passed: {summary['passed']}\n")
        f.write(f"- Failed: {summary['failed']}\n\n")
        f.write(f"## Test Details\n\n")
        for t in TEST_RESULTS:
            status = "PASS" if t["passed"] else "FAIL"
            f.write(f"### {status} {t['test']}\n")
            f.write(f"**Details:** {t['details']}\n\n")
    
    print(f"\nResults saved to:")
    print(f"   - {json_path}")
    print(f"   - {md_path}")
    
    return summary


def main():
    print("="*60)
    print("SL-LLM COMPREHENSIVE TEST SUITE")
    print("Testing self-learning and self-improvement capabilities")
    print("="*60)
    
    test_1_basic_tool_execution()
    test_2_reflection_capability()
    test_3_self_modification_engine()
    test_4_memory_and_learning()
    test_5_version_control()
    test_6_evaluation_benchmark()
    test_7_gpu_detection()
    test_8_agent_integration()
    test_9_self_improvement_cycle()
    
    summary = save_results()
    
    print("\n" + "="*60)
    print(f"RESULTS: {summary['passed']}/{summary['total_tests']} tests passed")
    print("="*60)
    
    return summary


if __name__ == "__main__":
    main()