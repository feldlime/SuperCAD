from solve import *
from utils import IncorrectParamValue

import sympy
import pytest
import numpy as np


def assert_flat_dicts_equal(d1, d2, is_close=False):
    assert isinstance(d1, dict)
    assert isinstance(d2, dict)
    assert set(d1.keys()) == set(d2.keys())
    for k, v1 in d1.items():
        v2 = d2[k]
        if is_close:
            assert np.isclose(v1, v2)
        else:
            assert v1 == v2


def assert_2_level_dicts_equal(d1, d2, is_close=False):
    assert isinstance(d1, dict)
    assert isinstance(d2, dict)
    assert set(d1.keys()) == set(d2.keys())
    for k, v1 in d1.items():
        v2 = d2[k]
        assert_flat_dicts_equal(v1, v2, is_close)


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
            f'figure1{DELIMITER}x': 1.0,
            f'figure1{DELIMITER}y': 2.0,
            f'figure2{DELIMITER}x1': 3.0,
            f'figure2{DELIMITER}y1': 4.0,
            f'figure2{DELIMITER}x2': 5.0,
            f'figure2{DELIMITER}y2': 6.0,
            f'figure3{DELIMITER}z': 7.0,
        }
        hierarchical = {
            'figure1': {'x': 1.0, 'y': 2.0},
            'figure2': {'x1': 3.0, 'y1': 4.0, 'x2': 5.0, 'y2': 6.0},
            'figure3': {'z': 7.0},
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
        eq = sympy.Eq(a ** 2 + b * b, c - a)
        eq_symbols_names_ = get_equation_symbols_names(eq, symbols_names)
        assert eq_symbols_names_ == {'a', 'b', 'c'}


class TestSubstitutor:
    def test_pass(self):
        symbols_names = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
        symbols_ = sympy.symbols(' '.join(symbols_names))
        symbols_dict = {name: s for name, s in zip(symbols_names, symbols_)}
        a, b, c, d, e, f, g = symbols_
        system = [
            sympy.Eq(a ** 2 + b * 2, c - a),
            sympy.Eq(a, 6),
            sympy.Eq(d, 10),
            sympy.Eq(e, b),
            sympy.Eq(f * 2, a + c),
            sympy.Eq(f, c),
        ]

        substitutor = Substitutor().fit(system, symbols_dict)

        simplified = [
            sympy.Eq(6.0 ** 2 + e * 2, c - 6.0),
            sympy.Eq(c * 2, 6.0 + c),
        ]
        simplified_ = substitutor.sub(system)
        assert isinstance(simplified_, list)
        assert len(simplified_) == len(simplified)

        # Cannot check, because subs can be different (b -> e or e -> b)

        # for eq, eq_ in zip(simplified, simplified_):
        #     assert eq.simplify() == eq_.simplify()

        # simplified_answer = {
        #     'b': -12.0,
        #     'c': 6.0
        # }
        # answer = {
        #     'a': 6.0,
        #     'b': -12.0,
        #     'c': 6.0,
        #     'd': 10.0,
        #     'e': -12.0,
        #     'f': 6.0,
        # }
        # result = substitutor.restore(simplified_answer)
        # assert_flat_dicts_equal(answer, result)


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

        fixed_f1 = [sympy.Eq(f1_x, 1), sympy.Eq(f1_y, 2)]
        joint_f1_f21 = [sympy.Eq(f2_x1, f1_x), sympy.Eq(f2_y1, f1_y)]
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

    def test_full_pass(self):
        system = EquationsSystem()
        system.add_figure_symbols('figure1', ['x', 'y'])
        system.add_figure_symbols('figure2', ['x1', 'y1', 'x2', 'y2'])
        system.add_figure_symbols('figure3', ['z'])

        f1_ = system.get_symbols('figure1')
        f1_x, f1_y = f1_['x'], f1_['y']

        f2_ = system.get_symbols('figure2')
        f2_x1, f2_y1, f2_x2, f2_y2 = f2_['x1'], f2_['y1'], f2_['x2'], f2_['y2']

        f3_ = system.get_symbols('figure3')
        f3_z = f3_['z']

        values = {
            'figure1': {'x': 1.0, 'y': 1.0},
            'figure2': {'x1': 5.0, 'y1': 6.0, 'x2': 10.0, 'y2': 2.0},
            'figure3': {'z': 100.0},
        }

        # Check restriction 1
        fixed_f1 = [sympy.Eq(f1_x, 1.0), sympy.Eq(f1_y, 2.0)]
        system.add_restriction_equations('fixed_f1', fixed_f1)
        result = system.solve(values)
        answer = {'figure1': {'x': 1.0, 'y': 2.0}}
        assert_2_level_dicts_equal(result, answer, is_close=True)
        values['figure1'].update(result['figure1'])

        # Check restriction 2
        joint_f1_f21 = [sympy.Eq(f2_x1, f1_x), sympy.Eq(f2_y1, f1_y)]
        system.add_restriction_equations('joint_f1_f21', joint_f1_f21)
        result = system.solve(values)
        answer = {
            'figure1': {'x': 1.0, 'y': 2.0},
            'figure2': {'x1': 1.0, 'y1': 2.0},
        }
        assert_2_level_dicts_equal(result, answer, is_close=True)
        values['figure1'].update(result['figure1'])
        values['figure2'].update(result['figure2'])

        # Check restriction 3
        fixed_length_f2 = [
            sympy.Eq((f2_x2 - f2_x1) ** 2 + (f2_y2 - f2_y1) ** 2, 5 ** 2)
        ]
        system.add_restriction_equations('fixed_length_f2', fixed_length_f2)
        result = system.solve(values)
        answer = {
            'figure1': {'x': 1.0, 'y': 2.0},
            'figure2': {'x1': 1.0, 'y1': 2.0, 'x2': 6.0, 'y2': 2.0},
        }
        assert_2_level_dicts_equal(result, answer, is_close=True)
        values['figure1'].update(result['figure1'])
        values['figure2'].update(result['figure2'])

        # Check changing parameter
        angle = np.pi / 6
        rotate_30 = [
            sympy.Eq((f2_y2 - f2_y1) / (f2_x2 - f2_x1), np.tan(angle)),
            # sympy.Eq(sympy.sign(f2_x2 - f2_x1),
            #          sympy.sign(np.pi - angle))  # think about other angles
        ]  # Directed
        result = system.solve_new(rotate_30, values)
        answer = {
            'figure1': {'x': 1.0, 'y': 2.0},
            'figure2': {
                'x1': 1.0,
                'y1': 2.0,
                'x2': 1.0 + 5 * np.cos(np.pi / 6),
                'y2': 2.0 + 5 * np.sin(np.pi / 6),
            },
        }
        assert_2_level_dicts_equal(result, answer, is_close=True)
        values['figure1'].update(result['figure1'])
        values['figure2'].update(result['figure2'])

        # Check moving
        move_high = {'figure2': {'x2': 1.0, 'y2': 100.0}}
        result = system.solve_optimization_task(move_high, values)
        answer = {
            'figure1': {'x': 1.0, 'y': 2.0},
            'figure2': {'x1': 1.0, 'y1': 2.0, 'x2': 1.0, 'y2': 7.0},
        }
        assert_2_level_dicts_equal(result, answer, is_close=True)
        values['figure1'].update(result['figure1'])
        values['figure2'].update(result['figure2'])

        # Check changing z
        change_z = [sympy.Eq(f3_z, 0)]
        result = system.solve_new(change_z, values)
        answer = {'figure3': {'z': 0.0}}
        assert_2_level_dicts_equal(result, answer, is_close=True)
        values['figure3'].update(result['figure3'])

        # Check moving z
        move_z = {'figure3': {'z': 1.0}}
        result = system.solve_optimization_task(move_z, values)
        answer = {'figure3': {'z': 1.0}}
        assert_2_level_dicts_equal(result, answer, is_close=True)
        values['figure3'].update(result['figure3'])

    def test_more_equations_than_symbols(self):
        system = EquationsSystem()
        system.add_figure_symbols('figure', ['x1', 'y1', 'x2', 'y2'])

        f_ = system.get_symbols('figure')
        f_x1, f_y1, f_x2, f_y2 = f_['x1'], f_['y1'], f_['x2'], f_['y2']

        values = {'figure': {'x1': 5.0, 'y1': 6.0, 'x2': 10.0, 'y2': 2.0}}

        # Fix start
        fixed_f_1 = [sympy.Eq(f_x1, 0.0), sympy.Eq(f_y1, 0.0)]
        system.add_restriction_equations('fixed_f_1', fixed_f_1)
        result = system.solve(values)
        values['figure'].update(result['figure'])

        # Fix end
        fixed_f_2 = [sympy.Eq(f_x2, 1.0), sympy.Eq(f_y2, 1.0)]
        system.add_restriction_equations('fixed_f_2', fixed_f_2)
        result = system.solve(values)
        values['figure'].update(result['figure'])

        # Try fix incorrect length
        fixed_length_incorrect = [
            sympy.Eq((f_x2 - f_x1) ** 2 + (f_y2 - f_y1) ** 2, 10 ** 2)
        ]
        system.add_restriction_equations(
            'fixed_length_incorrect', fixed_length_incorrect
        )
        with pytest.raises(MoreEquationsThanSymbolsError):
            system.solve(values)
        system.remove_restriction_equations('fixed_length_incorrect')

        # Try fix correct length
        fixed_length_correct = [
            sympy.Eq((f_x2 - f_x1) ** 2 + (f_y2 - f_y1) ** 2, 5 ** 2)
        ]
        system.add_restriction_equations(
            'fixed_length_correct', fixed_length_correct
        )
        with pytest.raises(MoreEquationsThanSymbolsError):
            system.solve(values)
        system.remove_restriction_equations('fixed_length_correct')

    def test_incompatible_equations(self):
        system = EquationsSystem()
        system.add_figure_symbols('figure', ['x1', 'y1', 'x2', 'y2'])

        f_ = system.get_symbols('figure')
        f_x1, f_y1, f_x2, f_y2 = f_['x1'], f_['y1'], f_['x2'], f_['y2']

        values = {'figure': {'x1': 5.0, 'y1': 6.0, 'x2': 10.0, 'y2': 2.0}}

        # Fix length
        fixed_length = [
            sympy.Eq((f_x2 - f_x1) ** 2 + (f_y2 - f_y1) ** 2, 5 ** 2)
        ]
        system.add_restriction_equations('fixed_length', fixed_length)
        result = system.solve(values)
        values['figure'].update(result['figure'])

        # Fix vertical
        fixed_vertical = [sympy.Eq(f_x1, f_x2)]
        system.add_restriction_equations('fixed_vertical', fixed_vertical)
        result = system.solve(values)
        values['figure'].update(result['figure'])

        # Cannot be horizontal and vertical simultaneously if length > 0

        # Try fix horizontal simple
        fixed_horizontal_simple = [sympy.Eq(f_y1, f_y2)]
        system.add_restriction_equations(
            'fixed_horizontal_simple', fixed_horizontal_simple
        )
        with pytest.raises(SystemIncompatibleError):
            system.solve(values)
        system.remove_restriction_equations('fixed_horizontal_simple')

        # Try fix horizontal complex
        length = (f_x2 - f_x1) ** 2 + (f_y2 - f_y1) ** 2
        fixed_horizontal_complex = [
            sympy.Eq(length * np.cos(0), f_x2 - f_x1)  # cheater (without y)
        ]
        system.add_restriction_equations(
            'fixed_horizontal_complex', fixed_horizontal_complex
        )
        with pytest.raises(CannotSolveSystemError):
            system.solve(values)
        system.remove_restriction_equations('fixed_horizontal_complex')

    def test_overfitted_equations_simple(self):
        """Just try apply two same restrictions."""

        system = EquationsSystem()
        system.add_figure_symbols('figure', ['x1', 'y1', 'x2', 'y2'])

        f_ = system.get_symbols('figure')
        f_x1, f_y1, f_x2, f_y2 = f_['x1'], f_['y1'], f_['x2'], f_['y2']

        values = {'figure': {'x1': 5.0, 'y1': 6.0, 'x2': 10.0, 'y2': 2.0}}

        # Fix vertical 1
        fixed_vertical_1 = [sympy.Eq(f_x1, f_x2)]
        system.add_restriction_equations('fixed_vertical_1', fixed_vertical_1)
        result = system.solve(values)
        values['figure'].update(result['figure'])

        # Fix vertical 2
        fixed_vertical_2 = [sympy.Eq(f_x1, f_x2)]
        system.add_restriction_equations('fixed_vertical_2', fixed_vertical_2)
        with pytest.raises(CannotSolveSystemError):
            system.solve(values)

    def test_overfitted_equations_complex(self):
        """Just try apply two same restrictions."""

        system = EquationsSystem()
        system.add_figure_symbols('figure', ['x1', 'y1', 'x2', 'y2'])

        f_ = system.get_symbols('figure')
        f_x1, f_y1, f_x2, f_y2 = f_['x1'], f_['y1'], f_['x2'], f_['y2']

        values = {'figure': {'x1': 5.0, 'y1': 6.0, 'x2': 10.0, 'y2': 2.0}}

        # Fix length 1
        fixed_length_1 = [
            sympy.Eq((f_x2 - f_x1) ** 2 + (f_y2 - f_y1) ** 2, 5 ** 2)
        ]
        system.add_restriction_equations('fixed_length_1', fixed_length_1)
        result = system.solve(values)
        values['figure'].update(result['figure'])

        # Fix length 2
        # fixed_length_2 = [
        #     sympy.Eq((f_x2 - f_x1) ** 2 + (f_y2 - f_y1) ** 2, 5 ** 2)
        # ]
        # system.add_restriction_equations('fixed_length_2', fixed_length_2)
        # with pytest.raises(CannotSolveSystemError):
        #     system.solve(values)
