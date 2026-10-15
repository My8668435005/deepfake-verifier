"""ScoreFusion: combine module scores into one suspicious score, label, confidence."""
import math
from collections import Counter
from typing import Optional

from app import config
from app.models.result import AnalysisResult, Label, ModuleResult


class ScoreFusion:
    def __init__(self, weights: Optional[dict] = None,
                 authentic_max: Optional[float] = None, fake_min: Optional[float] = None):
        self.weights = dict(weights or config.FUSION_WEIGHTS)
        self.authentic_max = config.AUTHENTIC_MAX if authentic_max is None else authentic_max
        self.fake_min = config.FAKE_MIN if fake_min is None else fake_min

    def _group(self, r: ModuleResult) -> Optional[str]:
        return config.MODULE_WEIGHT_GROUP.get(r.module_name)

    def _usable(self, results: list) -> list:
        usable = []
        for r in results:
            g = self._group(r)
            if r.is_applicable() and g in self.weights and self.weights[g] > 0:
                if not 0.0 <= r.score <= 1.0:
                    raise ValueError(f"{r.module_name}: score {r.score} not in 0..1")
                usable.append(r)
        return usable

    def normalize_weights(self, results: list) -> dict:
        """module_name -> weight, re-normalised over the modules that actually ran."""
        usable = self._usable(results)
        counts = Counter(self._group(r) for r in usable)
        raw = {r.module_name: self.weights[self._group(r)] / counts[self._group(r)] for r in usable}
        total = sum(raw.values())
        return {name: w / total for name, w in raw.items()} if total else {}

    def to_label(self, score: float) -> Label:
        if score < self.authentic_max:
            return Label.LIKELY_AUTHENTIC
        if score >= self.fake_min:
            return Label.LIKELY_FAKE
        return Label.SUSPICIOUS

    def compute_confidence(self, results: list) -> float:
        """Agreement between modules (weighted std-dev), lower when only one module ran."""
        w = self.normalize_weights(results)
        usable = [r for r in self._usable(results)]
        if not usable:
            return 0.0
        mean = sum(w[r.module_name] * r.score for r in usable)
        std = math.sqrt(sum(w[r.module_name] * (r.score - mean) ** 2 for r in usable))
        agreement = 1.0 - min(1.0, 2.0 * std)
        coverage = 0.7 if len(usable) == 1 else 1.0
        return round(agreement * coverage, 2)

    def fuse(self, results: list, submission_id: Optional[int] = None) -> AnalysisResult:
        weights = self.normalize_weights(results)
        if not weights:
            raise ValueError("no applicable module results to fuse")
        for r in results:
            r.weight = weights.get(r.module_name, 0.0)
        score = round(sum(weights[r.module_name] * r.score for r in results if r.module_name in weights), 4)
        label = self.to_label(score)
        top = max((r for r in results if r.module_name in weights), key=lambda r: r.score)
        summary = (f"{label.value.replace('_', ' ').title()}: suspicious score {score:.2f} from "
                   f"{len(weights)} module(s); strongest signal: {top.module_name} ({top.score:.2f}).")
        res = AnalysisResult(submission_id=submission_id, suspicious_score=score, label=label,
                             confidence=self.compute_confidence(results), summary=summary)
        res.module_results = list(results)
        return res
