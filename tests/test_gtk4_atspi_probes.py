from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_activity_probes_pin_and_restore_the_modern_atspi_bus():
    for name in ('scripts/sugar-gtk4-calculate-roundtrip.py',
                 'scripts/sugar-gtk4-help-visible.py'):
        text = (ROOT / name).read_text()
        assert 'MODERN_ATSPI_BUS' in text
        assert 'xprop' in text
        assert 'AT_SPI_BUS' in text
        assert 'atexit.register(restore)' in text

