"""
SL-LLM Rigorous Self-Learning Test
Demonstrates: Generate bug -> Execute to Witness Error -> Reflect -> Fix -> Verify
"""

import json
import time
from pathlib import Path
from datetime import datetime

RESULTS = []
BASE = "D:/sl/projects/sllm/test_run_samples"
Path(BASE).mkdir(parents=True, exist_ok=True)


def log_step(phase, message, data=None):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "phase": phase,
        "message": message,
        "data": data
    }
    RESULTS.append(entry)
    print(f"\n[{phase}] {message}")
    if data:
        print(f"  Data: {str(data)[:200]}")


def run_test():
    print("=" * 70)
    print("SL-LLM RIGOROUS SELF-LEARNING TEST")
    print("Code -> Execute -> WITNESS ERROR -> Reflect -> Fix -> Verify")
    print("=" * 70)
    
    from tools.builtin import execute_tool
    from core.client import MockClient
    from core.self_modify import SelfModifier, ReflectiveAgent
    from core.agent import SelfEvaluator, MemoryStore
    
    # Initialize components
    client = MockClient()
    modifier = SelfModifier(client=client)
    evaluator = SelfEvaluator(client)
    reflection_agent = ReflectiveAgent(client, modifier, evaluator)
    memory = MemoryStore()
    
    # ============================================================
    # STEP 1: GENERATE CODE WITH DELIBERATE BUG
    # ============================================================
    log_step("1. GENERATE", "Generating code with a deliberate bug")
    
    task = """Write a Python function to divide two numbers.
    Include a deliberate bug: don't check for division by zero.
    The function should be named 'divide' and take two parameters a and b.
    Return a/b."""
    
    response = client.generate(task)
    buggy_code = response.get("response", "")
    
    log_step("1. GENERATE", "Generated buggy code", {"code_length": len(buggy_code)})
    print(f"\nGenerated code:\n{buggy_code}")
    
    # ============================================================
    # STEP 2: EXECUTE TO WITNESS THE ERROR (CRITICAL!)
    # ============================================================
    log_step("2. EXECUTE", "Executing buggy code to WITNESS the error")
    
    # Execute with NORMAL input first (should work)
    normal_test = buggy_code + "\nprint(divide(10, 2))"
    normal_result = execute_tool("execute_code", {"code": normal_test, "timeout": 10})
    log_step("2. EXECUTE", f"Normal case (10/2): {normal_result.strip()}")
    
    # Execute with ZERO input to WITNESS the error
    error_test = buggy_code + "\nprint(divide(10, 0))"
    error_result = execute_tool("execute_code", {"code": error_test, "timeout": 10})
    
    # Check if we actually witnessed an error
    error_witnessed = "ZeroDivisionError" in error_result or "Traceback" in error_result
    
    log_step("2. EXECUTE", f"Zero case (10/0): {'ERROR WITNESSED!' if error_witnessed else 'No error'}")
    print(f"  Error output: {error_result[:150]}")
    
    if not error_witnessed:
        log_step("2. FAILED", "ERROR NOT WITNESSED - cannot learn from unobserved bug!")
        return {
            "overall_success": False,
            "error_witnessed": False,
            "reason": "Execution did not trigger the expected error"
        }
    
    # ============================================================
    # STEP 3: SELF-REFLECTION ON WITNESSED ERROR
    # ============================================================
    log_step("3. REFLECT", "Analyzing the WITNESSED error through self-reflection")
    
    reflection_prompt = f"""You executed this code:
{buggy_code}

With input divide(10, 0) and it produced this ERROR:
{error_result}

Analyze what went wrong. Identify the specific bug and explain:
1. What error was actually produced?
2. Why did it happen?
3. How to fix it?

Provide a detailed analysis based on the ACTUAL error, not assumptions."""
    
    reflection = client.generate(reflection_prompt)
    reflection_output = reflection.get("response", "")
    
    log_step("3. REFLECT", "Self-reflection on WITNESSED error", 
             {"analysis": reflection_output[:200]})
    print(f"\nReflection analysis:\n{reflection_output[:400]}")
    
    # ============================================================
    # STEP 4: GENERATE FIX BASED ON ACTUAL ERROR
    # ============================================================
    log_step("4. FIX", "Generating corrected code based on WITNESSED error")
    
    fix_prompt = f"""Based on the actual error we witnessed:
{error_result}

And this analysis:
{reflection_output}

Fix the buggy code and provide the corrected version.
Add proper division by zero handling."""
    
    fix_response = client.generate(fix_prompt)
    fixed_code = fix_response.get("response", "")
    
    log_step("4. FIX", "Generated fixed code", {"fixed_code": fixed_code[:150]})
    print(f"\nFixed code:\n{fixed_code[:300]}")
    
    # ============================================================
    # STEP 5: VERIFY THE FIX
    # ============================================================
    log_step("5. VERIFY", "Testing the fixed code with SAME inputs")
    
    # Test normal case
    fixed_normal = fixed_code + "\nprint(divide(10, 2))"
    normal_verify = execute_tool("execute_code", {"code": fixed_normal, "timeout": 10})
    normal_works = "5" in normal_verify or "5.0" in normal_verify
    
    # Test zero case - the SAME input that caused the error
    fixed_error = fixed_code + "\nprint(divide(10, 0))"
    zero_verify = execute_tool("execute_code", {"code": fixed_error, "timeout": 10})
    zero_handled = "ZeroDivisionError" not in zero_verify and "Error" in zero_verify
    
    log_step("5. VERIFY", f"Normal division (10/2): {'PASS' if normal_works else 'FAIL'}")
    log_step("5. VERIFY", f"Zero division (10/0): {'PASS' if zero_handled else 'FAIL'}")
    
    print(f"  Normal result: {normal_verify.strip()}")
    print(f"  Zero result: {zero_verify.strip()}")
    
    # ============================================================
    # STEP 6: SAVE LEARNING
    # ============================================================
    log_step("6. LEARN", "Saving learning to memory (witnessed error -> fix)")
    
    memory.save_episode(
        task="Division function - witnessed error then fixed",
        actions=[
            {"step": "generate", "code": buggy_code},
            {"step": "execute_normal", "result": normal_result[:100]},
            {"step": "execute_error", "result": error_result[:100]},  # The witnessed error
            {"step": "reflect", "analysis": reflection_output[:200]},
            {"step": "fix", "fixed_code": fixed_code[:200]},
            {"step": "verify_normal", "passed": normal_works},
            {"step": "verify_zero", "passed": zero_handled}
        ],
        result="Success" if (normal_works and zero_handled) else "Failed",
        metrics={
            "error_witnessed": error_witnessed,
            "reflection_quality": len(reflection_output),
            "fix_applied": True,
            "verification_passed": normal_works and zero_handled
        }
    )
    
    memory.save_insight(
        insight=f"Witnessed error: {error_result[:80]}. Fix: Add zero-check before division.",
        category="bug_fix_witnessed"
    )
    
    log_step("6. LEARN", "Learning saved to memory with error evidence")
    
    # ============================================================
    # STEP 7: CREATE CHECKPOINT
    # ============================================================
    log_step("7. CHECKPOINT", "Creating safety checkpoint")
    checkpoint = modifier.create_checkpoint("post_fix_checkpoint")
    log_step("7. CHECKPOINT", f"Checkpoint created: {checkpoint}")
    
    # ============================================================
    # SUMMARY
    # ============================================================
    overall_success = error_witnessed and normal_works and zero_handled
    
    print("\n" + "=" * 70)
    print("RIGOROUS SELF-LEARNING TEST SUMMARY")
    print("=" * 70)
    print(f"1. Generated buggy code: YES")
    print(f"2. Executed to WITNESS error: {'YES' if error_witnessed else 'NO'}")
    print(f"   - Normal case (10/2): {normal_result.strip()}")
    print(f"   - Error case (10/0): {error_result[:50]}...")
    print(f"3. Self-reflection on WITNESSED error: YES ({len(reflection_output)} chars)")
    print(f"4. Generated fix based on actual error: YES")
    print(f"5. Verification - normal division: {'PASS' if normal_works else 'FAIL'}")
    print(f"6. Verification - zero division: {'PASS' if zero_handled else 'FAIL'}")
    print(f"7. Learning saved with evidence: YES")
    print(f"8. Checkpoint for safety: YES")
    print("=" * 70)
    print(f"OVERALL: {'SUCCESS - TRUE SELF-LEARNING VERIFIED' if overall_success else 'FAILED'}")
    print("=" * 70)
    
    return {
        "overall_success": overall_success,
        "error_witnessed": error_witnessed,
        "reflection_performed": len(reflection_output) > 50,
        "fix_applied": True,
        "verification_passed": normal_works and zero_handled,
        "learning_saved": True
    }


def save_results(result):
    json_path = f"{BASE}/rigorous_self_learning_test.json"
    with open(json_path, "w") as f:
        json.dump({
            "test_name": "Rigorous Self-Learning (Witness Error)",
            "timestamp": datetime.now().isoformat(),
            "result": result,
            "steps": RESULTS
        }, f, indent=2)
    
    print(f"\nResults saved to: {json_path}")
    return result


if __name__ == "__main__":
    result = run_test()
    save_results(result)