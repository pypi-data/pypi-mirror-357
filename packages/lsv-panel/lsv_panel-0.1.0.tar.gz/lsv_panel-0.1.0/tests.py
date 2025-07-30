import os

import numpy as np
import pytest

import lsv_panel


@pytest.fixture
def data_dir() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def test_n0012(data_dir):
    file_name = os.path.join(data_dir, "n0012-il.txt")
    coords = np.loadtxt(file_name, skiprows=1)
    co, cp, cl = lsv_panel.solve(coords, -3.0)
    assert np.array(co).shape[0] == len(coords) - 1
    assert np.array(co).shape[1] == 2
    assert np.array(cp).shape[0] == len(coords) - 1
    assert pytest.approx(cl, 0.01) == -0.36


def test_n63412(data_dir):
    file_name = os.path.join(data_dir, "n63412-il.txt")
    coords = np.loadtxt(file_name, skiprows=1)
    co, cp, cl = lsv_panel.solve(coords, 5.0)
    assert np.array(co).shape[0] == len(coords) - 1
    assert np.array(co).shape[1] == 2
    assert np.array(cp).shape[0] == len(coords) - 1
    assert pytest.approx(cl, 0.01) == 0.95


def test_nlf0414(data_dir):
    file_name = os.path.join(data_dir, "nlf414f-il.txt")
    coords = np.loadtxt(file_name, skiprows=1)
    co, cp, cl = lsv_panel.solve(coords, 0.0)
    assert np.array(co).shape[0] == len(coords) - 1
    assert np.array(co).shape[1] == 2
    assert np.array(cp).shape[0] == len(coords) - 1
    assert pytest.approx(cl, 0.01) == 0.33


def test_n0012_sweep(data_dir):
    file_name = os.path.join(data_dir, "n0012-il.txt")
    coords = np.loadtxt(file_name, skiprows=1)
    alpha_deg = np.linspace(-10.0, 10.0, 21).tolist()
    co_list, cp_list, cl_list = lsv_panel.sweep_alpha(coords, alpha_deg)
    assert np.array(co_list).shape[0] == len(alpha_deg)
    assert np.array(co_list).shape[1] == len(coords) - 1
    assert np.array(co_list).shape[2] == 2
    assert np.array(cp_list).shape[0] == len(alpha_deg)
    assert np.array(cp_list).shape[1] == len(coords) - 1
    assert np.array(cl_list).shape[0] == len(alpha_deg)
