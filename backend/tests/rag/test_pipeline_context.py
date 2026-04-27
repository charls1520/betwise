from src.rag.pipeline import build_match_context

def test_build_match_context_with_derby_and_absences():
    match_info = {"team1": "Real Madrid", "team2": "Barcelona"}
    derby_info = "El Clásico"
    absences = [{"player": "Messi", "reason": "Injured"}]
    
    context = build_match_context(match_info, derby_info, absences)
    
    assert "El Clásico" in context
    assert "Messi" in context