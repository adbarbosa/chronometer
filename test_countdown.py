"""Testes da contagem com avanço explícito do tempo, sem esperas reais."""

import pytest

from chronometer.countdown import Countdown


def test_elapsed_time_survives_late_updates():
    """Um atraso na interface não se transforma num atraso acumulado na contagem."""
    clock = [100.0]
    timer = Countdown(600, clock=lambda: clock[0])
    timer.start()
    clock[0] += 7.4
    assert timer.remaining_seconds == 593
    clock[0] += 593.6
    assert timer.remaining_seconds == -1


def test_pause_retains_fraction_and_excludes_stopped_time():
    """Retomar conserva a fração de segundo, mas ignora o intervalo em pausa."""
    clock = [0.0]
    timer = Countdown(60, clock=lambda: clock[0])
    timer.start()
    clock[0] = 2.75
    timer.pause()
    clock[0] = 100.0
    assert timer.remaining_seconds == 58
    timer.start()
    clock[0] = 100.25
    assert timer.remaining_seconds == 57


def test_start_reset_and_expired_restart():
    """Iniciar de novo mantém uma contagem positiva e reinicia uma duração esgotada."""
    clock = [0.0]
    timer = Countdown(1, clock=lambda: clock[0])
    timer.start()
    clock[0] = 0.5
    timer.start()
    clock[0] = 2.0
    assert timer.remaining_seconds == -1
    timer.pause()
    timer.start()
    assert timer.remaining_seconds == 1
    timer.reset()
    assert not timer.is_running
    assert timer.remaining_seconds == 1


def test_load_and_zero_duration():
    """Carregar para a contagem; zero permite medir tempo excedido desde o início."""
    clock = [0.0]
    timer = Countdown(60, clock=lambda: clock[0])
    timer.start()
    timer.load(0)
    assert not timer.is_running
    timer.start()
    clock[0] = 3.0
    assert timer.remaining_seconds == -3
    with pytest.raises(ValueError):
        timer.load(-1)
