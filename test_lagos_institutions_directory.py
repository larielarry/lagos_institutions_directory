from lagos_institutions_directory import InstitutionDirectory

def load_dir():
    return InstitutionDirectory.from_csv("institutions_sample.csv")

def test_filter_by_category():
    d = load_dir()
    unis = d.filter(category="university")
    assert len(unis) >= 1
    assert all(i.category == "university" for i in unis)

def test_filter_by_course_keyword():
    d = load_dir()
    cs = d.filter(course_keyword="computer")
    assert len(cs) >= 1
    assert all(any("computer" in c.lower() for c in i.courses) for i in cs)

def test_sort_by_accreditation_desc():
    d = load_dir()
    data = d.sort(d.filter(), by="accreditation", descending=True)
    assert data == sorted(data, key=lambda x: x.accreditation_score, reverse=True)

def test_rank_score_monotonicity():
    d = load_dir()
    ranked = d.sort(d.filter(), by="rank", descending=True)
    # Ensure decreasing rank score
    scores = [i.rank_score() for i in ranked]
    assert all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
