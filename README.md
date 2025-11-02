# 🎓 Lagos Tertiary Institution Directory (CSC 825)
**Name:** Adeniyi Omolara Mariam  
**Matric No:** 24310591766  
**Course Code:** CSC 825  
**Course Title:** Advanced Computer Algorithm and Programming Languages

## 🧠 Problem Statement
Students and parents often struggle to find reliable, organized information about tertiary institutions in Lagos State. This project provides a **searchable, filterable, and rankable directory** of **universities, polytechnics, and colleges of education**, using **OOP** to model institutions and **algorithms** for search/sort/ranking.

## 🧩 OOP Integration
- **Abstraction:** `BaseInstitution` abstract class defines the core interface.
- **Inheritance:** `University`, `Polytechnic`, `CollegeOfEducation` specialize ranking emphasis.
- **Encapsulation:** Validated, read-only properties protect internal state.
- **Polymorphism:** `rank_score()` differs per subclass via weight overrides but used uniformly.

## ⚙️ Features
- Filter by **category**, **ownership**, **LGA**, **course**, **min accreditation**, **max tuition**  
- Sort by **rank**, **accreditation**, **tuition**, **name**, or **population**  
- Composite **rank score** combining accreditation, affordability, and size

## ▶️ How to Run
```bash
python lagos_institutions_directory.py --csv institutions_sample.csv \
  --category university --course Computer --max-tuition 500000 \
  --sort-by accreditation --top 5
