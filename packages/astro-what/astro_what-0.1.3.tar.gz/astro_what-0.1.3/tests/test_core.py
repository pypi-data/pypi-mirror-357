from astro_what.core import get_moon_info
from astro_what.core import get_next_lunar_phases

def test_output_types():
    result = get_moon_info("2025-06-23")
    assert isinstance(result["phase"], str)
    assert 0 <= result["illumination"] <= 100
    assert -90 <= result["altitude"] <= 90
    assert 0 <= result["azimuth"] <= 360



def test_lunar_phase_results():
    results = get_next_lunar_phases("2025-06-23", days_ahead=7)
    assert isinstance(results, list)
    assert len(results) > 0
    for phase in results:
        assert "phase" in phase
        assert "timestamp" in phase
