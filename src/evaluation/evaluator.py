"""
Evaluation module: Tests the RAG system with 20 domain-specific questions.
Records answers, retrieval results, and calculates accuracy scores.
"""

import os
import sys
import json
import time
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@dataclass
class EvalResult:
    """Result for a single evaluation question."""
    question_id: int
    question: str
    expected_answer: str
    system_answer: str
    correctness: float  # 1.0, 0.5, or 0.0
    top_3_sources: List[dict]
    source_relevance: List[bool]
    latency_seconds: float


class Evaluator:
    """
    Runs the evaluation pipeline:
    1. Load 20 test questions
    2. Run each through the RAG system
    3. Record answers and sources
    4. Calculate accuracy
    """

    def __init__(self, questions_path: str = "evaluation/questions.json"):
        self.questions_path = questions_path

    def load_questions(self) -> List[dict]:
        """Load test questions from JSON file."""
        with open(self.questions_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def run_evaluation(self, engine, output_path: str = "evaluation/results/eval_results.json") -> Dict:
        """
        Run full evaluation.

        Args:
            engine: RAGEngine instance
            output_path: Path to save results

        Returns:
            Summary dict with accuracy and details
        """
        questions = self.load_questions()
        results = []

        print(f"\nRunning evaluation: {len(questions)} questions")
        print("=" * 60)

        for i, q in enumerate(questions):
            qid = q.get("id", i + 1)
            question = q["question"]
            expected = q.get("expected_answer", "")

            print(f"\n[{qid}/{len(questions)}] {question[:80]}...")

            start = time.time()
            response = engine.ask(question)
            latency = time.time() - start

            # Get top 3 sources
            top_3 = response.sources[:3]

            result = EvalResult(
                question_id=qid,
                question=question,
                expected_answer=expected,
                system_answer=response.answer,
                correctness=-1,  # to be manually assessed
                top_3_sources=top_3,
                source_relevance=[False] * len(top_3),
                latency_seconds=round(latency, 2),
            )
            results.append(result)

            print(f"  Answer: {response.answer[:100]}...")
            print(f"  Sources: {len(response.sources)}, Latency: {latency:.1f}s")

        # Save results
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump([asdict(r) for r in results], f, ensure_ascii=False, indent=2)

        print(f"\n{'='*60}")
        print(f"Evaluation complete. Results saved to: {output_path}")
        print(f"Total questions: {len(results)}")
        print(f"Avg latency: {sum(r.latency_seconds for r in results) / len(results):.1f}s")
        print(f"\nPlease manually assess correctness (1/0.5/0) in the results file.")

        return {
            "total_questions": len(results),
            "results_path": output_path,
            "avg_latency": sum(r.latency_seconds for r in results) / len(results),
        }

    @staticmethod
    def calculate_accuracy(results_path: str) -> Dict:
        """Calculate accuracy after manual assessment."""
        with open(results_path, 'r', encoding='utf-8') as f:
            results = json.load(f)

        assessed = [r for r in results if r["correctness"] >= 0]
        if not assessed:
            return {"error": "No manually assessed results found."}

        total = sum(r["correctness"] for r in assessed)
        accuracy = total / len(assessed)

        return {
            "total_assessed": len(assessed),
            "correct": sum(1 for r in assessed if r["correctness"] == 1),
            "partial": sum(1 for r in assessed if r["correctness"] == 0.5),
            "incorrect": sum(1 for r in assessed if r["correctness"] == 0),
            "accuracy": round(accuracy, 4),
        }
