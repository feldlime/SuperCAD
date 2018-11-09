from solve import *
import sympy


def assert_flat_dicts_equal(d1, d2):
    assert isinstance(d1, dict)
    assert isinstance(d2, dict)
    assert set(d1.keys()) == set(d2.keys())
    for k, v1 in d1.items():
        v2 = d2[k]
        assert v1 == v2


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

