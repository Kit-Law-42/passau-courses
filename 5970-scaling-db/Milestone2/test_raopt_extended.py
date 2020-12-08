import radb
import radb.ast
import radb.parse
import raopt
import unittest

'''
Tests check several rewriting rules for the logical optimization
of relational algebra expressions.

Tests assume that all relational algebra queries have been
compiled from SQL queries by the canonical translation.
Therefore, they use projection, selection, the cross product
and the renaming operator only.
'''

'''
Tests that selections are broken up correctly.
'''


class TestRuleBreakUpSelections(unittest.TestCase):

    def _check(self, input, expected):
        computed_expr = raopt.rule_break_up_selections(radb.parse.one_statement_from_string(input))
        expected_expr = radb.parse.one_statement_from_string(expected)
        self.assertEqual(str(computed_expr), str(expected_expr))

    def test_extend_1(self):
        self._check("\select_{Person.gender = 'f' and Person.age = 16 and Person.name = 'Amy'} Person;",
                    "\select_{Person.gender = 'f'} \select_{Person.age = 16} \select_{Person.name = 'Amy'} Person;")


'''
Tests selection pushdown.
Assumes that conjunctions in selections have been broken up.
'''


class TestRulePushDownSelections(unittest.TestCase):

    def _check(self, input, expected):
        # The data dictionary records the relational schema.
        dd = {}
        dd["Person"] = {"name": "string", "age": "integer", "gender": "string"}
        dd["Eats"] = {"name": "string", "pizza": "string"}
        dd["Serves"] = {"pizzeria": "string", "pizza": "string", "price": "integer"}

        computed_expr = raopt.rule_push_down_selections(radb.parse.one_statement_from_string(input), dd)
        expected_expr = radb.parse.one_statement_from_string(expected)
        self.assertEqual(str(computed_expr), str(expected_expr))

    def test_extend_1(self):
        self._check("\project_{E.pizza} (\select_{E.pizza = 'mushroom'} ((\\rename_{E: *} Eats) \cross Frequents));",
                    "\project_{E.pizza} ((\select_{E.pizza = 'mushroom'} \\rename_{E: *}(Eats)) \cross Frequents);")

    def test_extend_2(self):
        self._check("\select_{E.pizza = 'mushroom'} ((\\rename_{E: *} Eats) \cross Frequents);",
                    "(\select_{E.pizza = 'mushroom'} \\rename_{E: *}(Eats)) \cross Frequents;")


'''
Tests that nested selections are properly merged.
'''


class TestMergeSelections(unittest.TestCase):

    def _check(self, input, expected):
        computed_expr = raopt.rule_merge_selections(radb.parse.one_statement_from_string(input))
        expected_expr = radb.parse.one_statement_from_string(expected)
        self.assertEqual(str(computed_expr), str(expected_expr))

    def test_extend_1(self):
        self._check(
            "\project_{Person.name} (\select_{Person.name = 'Amy'} \select_{gender = 'f'} \select_{age = 16} Person);",
            "\project_{Person.name} (\select_{Person.name = 'Amy' and gender = 'f' and age = 16} Person);")

    def test_extend_2(self):
        self._check("\select_{Person.name = 'Amy'} \select_{gender = 'f'} \select_{age = 16} Person;",
                    "\select_{Person.name = 'Amy' and gender = 'f' and age = 16} Person;")

    def test_extend_3(self):
        self._check("""((\select_{Person.name = 'Amy'} \select_{gender = 'f'} \select_{age = 16} Person) 
                            \cross (\select_{Eats.name = 'Amy'} \select_{pizza = 'mushroom'} Eats))
                            \cross (\select_{pizzeria = 'Pizza Hut'} Serves);""",
                    """((\select_{Person.name = 'Amy' and gender = 'f' and age = 16} Person) 
                            \cross (\select_{Eats.name = 'Amy' and pizza = 'mushroom'} Eats))
                            \cross (\select_{pizzeria = 'Pizza Hut'} Serves);""")


'''
Tests the introduction of joins.
Assumes that all selections have been pushed down as far as possible.
'''


class TestIntroduceJoins(unittest.TestCase):

    def _check(self, input, expected):
        computed_expr = raopt.rule_introduce_joins(radb.parse.one_statement_from_string(input))
        expected_expr = radb.parse.one_statement_from_string(expected)
        self.assertEqual(str(computed_expr), str(expected_expr))

    def test_extend_1(self):
        self._check("""\select_{Eats.pizza = Serves.pizza}((\select_{Person.name = Eats.name}
                       (\select_{Person.name = 'Amy'} Person \cross \select_{Person.name = 'Amy'} Eats)) \cross \select_{Serves.pizzeria = 'Pizza Hut'} Serves);""",
                    """(\select_{Person.name = 'Amy'} Person \join_{Person.name = Eats.name} \select_{Person.name = 'Amy'} Eats) \join_{Eats.pizza =
                       Serves.pizza} \select_{Serves.pizzeria = 'Pizza Hut'} Serves;""")

    def test_extend_2(self):
        self._check(
            "\select_{Person.name = Eats.name and Person.name = Eats.pizza} (Person \cross \select_{Eats.name = 'Amy'} Eats);",
            "Person \join_{Person.name = Eats.name and Person.name = Eats.pizza} \select_{Eats.name = 'Amy'} Eats;")


'''
Tests all rules in combination.
'''


class TestAllSteps(unittest.TestCase):

    def _check(self, input, expected):
        dd = {}
        dd["Person"] = {"name": "string", "age": "integer", "gender": "string"}
        dd["Eats"] = {"name": "string", "pizza": "string"}
        dd["Serves"] = {"pizzeria": "string", "pizza": "string", "price": "integer"}

        ra0 = radb.parse.one_statement_from_string(input)
        ra1 = raopt.rule_break_up_selections(ra0)
        ra2 = raopt.rule_push_down_selections(ra1, dd)
        ra3 = raopt.rule_merge_selections(ra2)
        ra4 = raopt.rule_introduce_joins(ra3)

        computed_expr = ra4
        expected_expr = radb.parse.one_statement_from_string(expected)
        self.assertEqual(str(computed_expr), str(expected_expr))

    def test_extend_1(self):
        self._check(
            "\project_{P1.name, P2.name} \select_{P1.age = 16 and P2.age = 16 and P1.name = P2.name} ((\\rename_{P1: *} Person) \cross (\\rename_{P2: *} Person));",
            "\project_{P1.name, P2.name} ((\select_{P1.age = 16} \\rename_{P1: *} Person) \join_{P1.name = P2.name} (\select_{P2.age = 16} \\rename_{P2: *} Person));")

    def test_extend_2(self):
        self._check(
            "\project_{P.name} (\select_{P.name = E.name} (\select_{P.age = 16} (\select_{E.pizza = 'mushroom'} ((\\rename_{P: *} Person) \cross (\\rename_{E: *} Eats)))));",
            "\project_{P.name} ((\select_{P.age = 16} \\rename_{P: *} Person) \join_{P.name = E.name} (\select_{E.pizza = 'mushroom'} \\rename_{E: *} Eats));")

    def test_extend_3(self):
        self._check("\\rename_{P: *} Person \cross Eats;", "\\rename_{P: *} Person \cross Eats;")

    def test_extend_4(self):
        self._check("\select_{Person.gender='f' and Person.age=16}(Person \cross Eats);",
                    "(\select_{Person.gender='f' and Person.age=16} Person) \cross Eats;")

    def test_extend_5(self):
        self._check("Person;", "Person;")

    def test_extend_6(self):
        self._check("(Person \cross Eats) \cross Serves;", "(Person \cross Eats) \cross Serves;")

    def test_extend_7(self):
        self._check("""\project_{Person.name, pizzeria}(\select_{Person.name = Eats.name
                       and Eats.pizza = Serves.pizza}((Person \cross Eats) \cross Serves));""",
                    """\project_{Person.name, pizzeria}((Person \join_{Person.name = Eats.name} Eats)
                       \join_{Eats.pizza = Serves.pizza} Serves);""")


if __name__ == '__main__':
    unittest.main()
