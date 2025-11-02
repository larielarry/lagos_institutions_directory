from __future__ import annotations
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List, Dict, Iterable, Optional, Tuple
import csv
import argparse


# ===============================
# Lagos Tertiary Institution Directory
# Demonstrates: Encapsulation, Abstraction, Inheritance, Polymorphism
# Algorithms: filtering, keyword search, multi-key sorting, composite ranking
# ===============================

# ---------- ABSTRACTION ----------
@dataclass
class BaseInstitution(ABC):
    _name: str
    _ownership: str            # "federal" | "state" | "private"
    _lga: str                  # Lagos LGA (e.g., "Ojo", "Ikeja", "Yaba")
    _courses: List[str]        # e.g., ["Computer Science","Mass Communication"]
    _tuition_avg: float        # average annual tuition (₦)
    _accreditation_score: float  # simple 0–100 scale for demo
    _student_population: int

    # ---------- ENCAPSULATION (validated properties) ----------
    @property
    def name(self) -> str: return self._name

    @property
    def ownership(self) -> str: return self._ownership.lower()

    @property
    def lga(self) -> str: return self._lga

    @property
    def courses(self) -> List[str]: return list(self._courses)

    @property
    def tuition_avg(self) -> float: return float(self._tuition_avg)

    @property
    def accreditation_score(self) -> float: return float(self._accreditation_score)

    @property
    def student_population(self) -> int: return int(self._student_population)

    def offers_course(self, course_keyword: str) -> bool:
        kw = course_keyword.strip().lower()
        return any(kw in c.lower() for c in self._courses)

    # Each subclass defines category label and ranking emphasis
    @property
    @abstractmethod
    def category(self) -> str: ...

    @abstractmethod
    def base_rank_weights(self) -> Tuple[float, float, float]:
        """
        Return weights for (accreditation, affordability, size_attractiveness)
        Affordability is inverse of tuition.
        """

    # ---------- POLYMORPHISM (per-type ranking) ----------
    def rank_score(self) -> float:
        w_acc, w_aff, w_size = self.base_rank_weights()

        # Normalize features to 0–1
        acc = max(0.0, min(1.0, self.accreditation_score / 100.0))
        # For affordability, lower tuition should mean higher score.
        # Use a soft cap to avoid division explosions.
        aff = 1.0 / (1.0 + (self.tuition_avg / 1_000_000.0))  # ₦1m scale
        # Size attractiveness (preference for moderate to large population)
        size = min(1.0, self.student_population / 30_000.0)

        return (w_acc * acc) + (w_aff * aff) + (w_size * size)

    # Friendly one-line summary
    def line(self) -> str:
        return (f"{self.name} [{self.category.title()} | {self.ownership.title()} | {self.lga}] "
                f"Accr {self.accreditation_score:.0f}/100 • Tuition ₦{self.tuition_avg:,.0f} • "
                f"Students {self.student_population:,}")


# ---------- INHERITANCE ----------
class University(BaseInstitution):
    @property
    def category(self) -> str: return "university"

    def base_rank_weights(self) -> Tuple[float, float, float]:
        # Universities value accreditation strongly, size moderately
        return (0.60, 0.20, 0.20)


class Polytechnic(BaseInstitution):
    @property
    def category(self) -> str: return "polytechnic"

    def base_rank_weights(self) -> Tuple[float, float, float]:
        # Polytechnics value affordability a bit more (skills orientation)
        return (0.45, 0.35, 0.20)


class CollegeOfEducation(BaseInstitution):
    @property
    def category(self) -> str: return "college"

    def base_rank_weights(self) -> Tuple[float, float, float]:
        # Colleges focus on accreditation and affordability
        return (0.50, 0.40, 0.10)


# ---------- Directory + Algorithms ----------
class InstitutionDirectory:
    def __init__(self, institutions: List[BaseInstitution]):
        self._inst = institutions

    @classmethod
    def from_csv(cls, path: str) -> "InstitutionDirectory":
        acc: List[BaseInstitution] = []
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                category = (row["category"] or "").strip().lower()
                name = row["name"].strip()
                ownership = row["ownership"].strip().lower()
                lga = row["lga"].strip()
                courses = [c.strip() for c in (row["courses"] or "").split("|") if c.strip()]
                tuition = float(row["tuition_avg"] or 0.0)
                accr = float(row["accreditation_score"] or 0.0)
                pop = int(row["student_population"] or 0)

                if category == "university":
                    obj = University(name, ownership, lga, courses, tuition, accr, pop)
                elif category == "polytechnic":
                    obj = Polytechnic(name, ownership, lga, courses, tuition, accr, pop)
                elif category in ("college", "college_of_education", "college of education"):
                    obj = CollegeOfEducation(name, ownership, lga, courses, tuition, accr, pop)
                else:
                    # Default to university if unspecified
                    obj = University(name, ownership, lga, courses, tuition, accr, pop)
                acc.append(obj)
        return cls(acc)

    # ------- Filtering & search (algorithmic) -------
    def filter(
        self,
        category: Optional[str] = None,
        ownership: Optional[str] = None,
        lga: Optional[str] = None,
        course_keyword: Optional[str] = None,
        min_accreditation: Optional[float] = None,
        max_tuition: Optional[float] = None,
    ) -> List[BaseInstitution]:
        res: Iterable[BaseInstitution] = self._inst
        if category:
            c = category.lower()
            res = (i for i in res if i.category == c)
        if ownership:
            ow = ownership.lower()
            res = (i for i in res if i.ownership == ow)
        if lga:
            lg = lga.lower()
            res = (i for i in res if i.lga.lower() == lg)
        if course_keyword:
            res = (i for i in res if i.offers_course(course_keyword))
        if min_accreditation is not None:
            res = (i for i in res if i.accreditation_score >= float(min_accreditation))
        if max_tuition is not None:
            res = (i for i in res if i.tuition_avg <= float(max_tuition))
        return list(res)

    def sort(
        self,
        institutions: List[BaseInstitution],
        by: str = "rank",
        descending: bool = True
    ) -> List[BaseInstitution]:
        keyf = {
            "rank": lambda x: x.rank_score(),
            "tuition": lambda x: x.tuition_avg,
            "accreditation": lambda x: x.accreditation_score,
            "name": lambda x: x.name.lower(),
            "population": lambda x: x.student_population
        }.get(by, lambda x: x.rank_score())
        return sorted(institutions, key=keyf, reverse=descending)

    def top_n(self, institutions: List[BaseInstitution], n: int = 5) -> List[BaseInstitution]:
        return institutions[:max(0, n)]

    def summarize(self, institutions: List[BaseInstitution]) -> str:
        if not institutions:
            return "No institutions matched your criteria."
        lines = []
        for i, inst in enumerate(institutions, 1):
            lines.append(f"{i:>2}. {inst.line()} • RankScore {inst.rank_score():.3f}")
        return "\n".join(lines)


# ---------- CLI ----------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Lagos Tertiary Institution Directory (Search & Rank)")
    p.add_argument("--csv", type=str, default="institutions_sample.csv", help="Path to CSV dataset")

    # Filters
    p.add_argument("--category", type=str, choices=["university", "polytechnic", "college"], help="Filter by category")
    p.add_argument("--ownership", type=str, choices=["federal", "state", "private"], help="Filter by ownership")
    p.add_argument("--lga", type=str, help="Filter by LGA (e.g., Ojo, Yaba, Ikeja)")
    p.add_argument("--course", type=str, help="Keyword in course name (e.g., 'Computer')")
    p.add_argument("--min-accr", type=float, help="Minimum accreditation score (0–100)")
    p.add_argument("--max-tuition", type=float, help="Maximum average tuition (₦)")

    # Sorting & output
    p.add_argument("--sort-by", type=str, default="rank",
                   choices=["rank", "tuition", "accreditation", "name", "population"],
                   help="Sort key")
    p.add_argument("--asc", action="store_true", help="Sort ascending (default: descending)")
    p.add_argument("--top", type=int, default=5, help="Show top N results")
    return p


def main():
    args = build_parser().parse_args()
    directory = InstitutionDirectory.from_csv(args.csv)

    filtered = directory.filter(
        category=args.category,
        ownership=args.ownership,
        lga=args.lga,
        course_keyword=args.course,
        min_accreditation=args.min_accr,
        max_tuition=args.max_tuition
    )
    sorted_list = directory.sort(filtered, by=args.sort_by, descending=not args.asc)
    top = directory.top_n(sorted_list, n=args.top)

    print("\n=== Lagos Tertiary Institution Directory — Results ===\n")
    print(directory.summarize(top))
    print("\nTip: adjust filters, e.g., --category university --course Computer --max-tuition 400000 --sort-by accreditation --top 10\n")


if __name__ == "__main__":
    main()
