from solve import *
from utils import IncorrectParamValue

import sympy
import pytest


def assert_flat_dicts_equal(d1, d2):
    assert isinstance(d1, dict)
    assert isinstance(d2, dict)
    assert set(d1.keys()) == set(d2.keys())
    for k, v1 in d1.items():
        v2 = d2[k]
        assert v1 == v2


def assert_sequences_equal(s1, s2):
    assert type(s1) == type(s2)
    assert len(s1) == len(s2)
    for e1, e2 in zip(sorted(s1), sorted(s2)):
        assert e1 == e2


# noinspection PyTypeChecker
class TestBaseFunctions:
    def test_compose_and_split_full_name(self):
        base_, object_ = 'figure_1', 'x'
        full_ = compose_full_name(base_, object_)
        base_new, object_new = split_full_name(full_)
        assert base_ == base_new and object_ == object_new

    def test_roll_up_and_unroll(self):
        flatten = {
            f'figure1{DELIMITER}x': 1.,
            f'figure1{DELIMITER}y': 2.,
            f'figure2{DELIMITER}x1': 3.,
            f'figure2{DELIMITER}y1': 4.,
            f'figure2{DELIMITER}x2': 5.,
            f'figure2{DELIMITER}y2': 6.,
            f'figure3{DELIMITER}z': 7.,
        }
        hierarchical = {
            'figure1': {
                'x': 1.,
                'y': 2.,
            },
            'figure2': {
                'x1': 3.,
                'y1': 4.,
                'x2': 5.,
                'y2': 6.,
            },
            'figure3': {
                'z': 7.,
            }
        }

        hierarchical_ = roll_up_values_dict(flatten)
        assert set(hierarchical_.keys()) == set(hierarchical.keys())
        for base_name, base in hierarchical.items():
            base_ = hierarchical_[base_name]
            assert_flat_dicts_equal(base_, base)

        flatten_ = unroll_values_dict(hierarchical)
        assert_flat_dicts_equal(flatten_, flatten)

    def test_getting_equation_symbols(self):
        symbols_names = ['a', 'b', 'c', 'd']
        a, b, c, d = sympy.symbols(' '.join(symbols_names))
        eq = sympy.Eq(a**2 + b * b, c - a)
        eq_symbols_names_ = get_equation_symbols_names(eq, symbols_names)
        assert eq_symbols_names_ == {'a', 'b', 'c'}


class TestSubstitutor:
    def test_pass(self):
        symbols_names = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
        a, b, c, d, e, f, g = sympy.symbols(' '.join(symbols_names))
        system = [
            sympy.Eq(a ** 2 + b * 2, c - a),
            sympy.Eq(a, 6),
            sympy.Eq(d, 10),
            sympy.Eq(e, b),
            sympy.Eq(f * 2, a + c),
            sympy.Eq(f, c)
        ]

        substitutor = Substitutor().fit(system, symbols_names)

        simplified = [
            sympy.Eq(6.0 ** 2 + b * 2, c - 6.0),
            sympy.Eq(c * 2, 6.0 + c)
        ]
        simplified_ = substitutor.sub(system)
        assert isinstance(simplified_, list)
        assert len(simplified_) == len(simplified)
        for eq, eq_ in zip(simplified, simplified_):
            assert eq.simplify() == eq_.simplify()

        simplified_answer = {
            'b': -12.0,
            'c': 6.0
        }
        answer = {
            'a': 6.0,
            'b': -12.0,
            'c': 6.0,
            'd': 10.0,
            'e': -12.0,
            'f': 6.0,
        }
        result = substitutor.restore(simplified_answer)
        assert_flat_dicts_equal(answer, result)


class TestEquationsSystem:
    def test_addition_and_removing_symbols(self):
        system = EquationsSystem()
        system.add_figure_symbols('figure1', ['x', 'y'])
        system.add_figure_symbols('figure2', ['x1', 'y1', 'x2', 'y2'])
        system.add_figure_symbols('figure3', ['z'])

        with pytest.raises(IncorrectParamValue):
            system.add_figure_symbols('figure1', ['z', 'w'])

        symbols_ = system.get_symbols('figure1')
        assert isinstance(symbols_, dict)
        assert_sequences_equal(list(symbols_), ['x', 'y'])

        symbols_ = system.get_symbols('figure2', 'x2')
        assert isinstance(symbols_, sympy.Symbol)

        with pytest.raises(IncorrectParamValue):
            system.get_symbols('figure2', 'x3')

        symbols_ = system.get_symbols('figure3')
        assert isinstance(symbols_, dict)
        assert_sequences_equal(list(symbols_.keys()), ['z'])

        system.remove_figure_symbols('figure1')
        with pytest.raises(IncorrectParamValue):
            system.get_symbols('figure1')

        with pytest.raises(IncorrectParamValue):
            system.remove_figure_symbols('figure1')

    def test_addition_and_removing_equations(self):
        system = EquationsSystem()
        system.add_figure_symbols('figure1', ['x', 'y'])
        system.add_figure_symbols('figure2', ['x1', 'y1', 'x2', 'y2'])
        system.add_figure_symbols('figure3', ['z'])

        f1_ = system.get_symbols('figure1')
        f1_x, f1_y = f1_['x'], f1_['y']

        f2_ = system.get_symbols('figure2')
        f2_x1, f2_y1, f2_x2, f2_y2 = f2_['x1'], f2_['y1'], f2_['x2'], f2_['y2']

        fixed_f1 = [
            sympy.Eq(f1_x, 1),
            sympy.Eq(f1_y, 2)
         ]
        joint_f1_f21 = [
            sympy.Eq(f2_x1, f1_x),
            sympy.Eq(f2_y1, f1_y)
        ]
        fixed_length_f2 = [
            sympy.Eq((f2_x2 - f2_x1) ** 2 + (f2_y2 - f2_y1) ** 2, 5 ** 2)
        ]

        system.add_restriction_equations('fixed_f1', fixed_f1)
        system.add_restriction_equations('joint_f1_f21', joint_f1_f21)
        system.add_restriction_equations('fixed_length_f2', fixed_length_f2)

        with pytest.raises(IncorrectParamValue):
            system.add_restriction_equations('fixed_f1', fixed_f1)

        system.remove_restriction_equations('fixed_f1')
        system.remove_restriction_equations('joint_f1_f21')
        system.remove_restriction_equations('fixed_length_f2')

        with pytest.raises(IncorrectParamValue):
            system.remove_restriction_equations('fixed_f1')
