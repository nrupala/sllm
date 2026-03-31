import json
import time
from pathlib import Path
from typing import Callable, Optional


class Benchmark:
    def __init__(self, name: str, task: str, expected_output: Optional[str] = None, 
                 validator: Optional[Callable] = None):
        self.name = name
        self.task = task
        self.expected_output = expected_output
        self.validator = validator
        self.results = []

    def validate(self, output: str) -> dict:
        if self.validator:
            return self.validator(output)
        
        if self.expected_output:
            correct = self.expected_output.lower() in output.lower()
            return {"passed": correct, "score": 1 if correct else 0}
        
        return {"passed": True, "score": 1}


class BenchmarkSuite:
    def __init__(self, suite_path: str = "D:/sl/projects/sllm/eval/benchmarks.json"):
        self.suite_path = Path(suite_path)
        self.benchmarks = []
        self.results_path = self.suite_path.parent / "results.jsonl"
        self._load_benchmarks()

    def _load_benchmarks(self):
        if self.suite_path.exists():
            data = json.loads(self.suite_path.read_text())
            for b in data.get("benchmarks", []):
                self.benchmarks.append(Benchmark(
                    name=b["name"],
                    task=b["task"],
                    expected_output=b.get("expected")
                ))

    def add_benchmark(self, benchmark: Benchmark):
        self.benchmarks.append(benchmark)

    def run_benchmark(self, benchmark: Benchmark, agent) -> dict:
        start_time = time.time()
        
        result = agent.execute_task(benchmark.task)
        elapsed = time.time() - start_time
        
        validation = benchmark.validate(result.get("output", ""))
        
        return {
            "benchmark": benchmark.name,
            "passed": validation["passed"],
            "score": validation["score"],
            "elapsed": elapsed,
            "output": result.get("output", "")[:500]
        }

    def run_all(self, agent) -> dict:
        results = []
        
        for benchmark in self.benchmarks:
            print(f"Running benchmark: {benchmark.name}")
            result = self.run_benchmark(benchmark, agent)
            results.append(result)
            print(f"  -> Passed: {result['passed']}, Score: {result['score']}")
        
        total_score = sum(r["score"] for r in results)
        avg_time = sum(r["elapsed"] for r in results) / len(results) if results else 0
        
        summary = {
            "total": len(results),
            "passed": sum(1 for r in results if r["passed"]),
            "avg_score": total_score / len(results) if results else 0,
            "avg_time": avg_time,
            "results": results
        }
        
        with open(self.results_path, "a") as f:
            f.write(json.dumps(summary) + "\n")
        
        return summary


class ImprovementTracker:
    def __init__(self, history_path: str = "D:/sl/projects/sllm/eval/improvement_history.jsonl"):
        self.history_path = Path(history_path)
        self.history_path.parent.mkdir(parents=True, exist_ok=True)

    def record_improvement(self, benchmark: str, before_score: float, after_score: float, 
                          modification: str):
        record = {
            "timestamp": time.time(),
            "benchmark": benchmark,
            "before": before_score,
            "after": after_score,
            "delta": after_score - before_score,
            "modification": modification
        }
        
        with open(self.history_path, "a") as f:
            f.write(json.dumps(record) + "\n")
        
        return record

    def get_trend(self, benchmark: str) -> list:
        if not self.history_path.exists():
            return []
        
        with open(self.history_path, "r") as f:
            records = [json.loads(line) for line in f if line.strip()]
        
        return [r for r in records if r["benchmark"] == benchmark]


class SelfEvolutionController:
    def __init__(self, agent, benchmark_suite: BenchmarkSuite, 
                 improvement_tracker: ImprovementTracker):
        self.agent = agent
        self.benchmark_suite = benchmark_suite
        self.improvement_tracker = improvement_tracker
        self.max_iterations = 5
        self.min_improvement = 0.1

    def run_evolution_cycle(self) -> dict:
        baseline = self.benchmark_suite.run_all(self.agent)
        print(f"\nBaseline: {baseline['passed']}/{baseline['total']} passed, avg score: {baseline['avg_score']:.2f}")
        
        for i in range(self.max_iterations):
            print(f"\n--- Evolution iteration {i+1} ---")
            
            improvements_found = 0
            
            for benchmark in self.benchmark_suite.benchmarks:
                result = self.benchmark_suite.run_benchmark(benchmark, self.agent)
                
                if not result["passed"]:
                    print(f"  Attempting to improve: {benchmark.name}")
                    
                    task = f"Improve this code to pass: {benchmark.task}"
                    improvement_result = self.agent.run_self_improvement_cycle(task)
                    
                    if improvement_result.get("improvement_result", {}).get("success"):
                        new_result = self.benchmark_suite.run_benchmark(benchmark, self.agent)
                        
                        if new_result["score"] > result["score"]:
                            self.improvement_tracker.record_improvement(
                                benchmark.name,
                                result["score"],
                                new_result["score"],
                                str(improvement_result)
                            )
                            improvements_found += 1
            
            if improvements_found == 0:
                print("No improvements found in this iteration")
                break
            
            current = self.benchmark_suite.run_all(self.agent)
            print(f"Current: {current['passed']}/{current['total']} passed, avg score: {current['avg_score']:.2f}")
            
            if current["avg_score"] >= 1.0:
                print("All benchmarks passed!")
                break
        
        return {"completed": True, "iterations": i + 1}


def create_default_benchmarks():
    benchmarks = {
        "benchmarks": [
            {
                "name": "fibonacci",
                "task": "Write a Python function to calculate the nth Fibonacci number",
                "expected": "fibonacci"
            },
            {
                "name": "string_reverse",
                "task": "Write a Python function to reverse a string",
                "expected": "reversed"
            },
            {
                "name": "prime_check",
                "task": "Write a Python function to check if a number is prime",
                "expected": "prime"
            },
            {
                "name": "list_sort",
                "task": "Write a Python function to sort a list",
                "expected": "sorted"
            }
        ]
    }
    
    path = Path("D:/sl/projects/sllm/eval/benchmarks.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(benchmarks, indent=2))
    print(f"Created default benchmarks at {path}")


if __name__ == "__main__":
    create_default_benchmarks()