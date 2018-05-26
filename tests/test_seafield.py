import unittest
from itertools import chain

from seawar_skeleton.seaplayground import SeaPlayground, Cell, IncorrectShipPosition, NoSpaceLeft, SeaField, \
    IncorrectCoordinate, ComputerPlayer


class SeaPlaygroundTest(unittest.TestCase):

    def test_create(self):
        base = SeaField()
        assert len(base._cells) == 100

    def test_set_ship(self):
        base = SeaField(5, 5)
        SeaPlayground._set_ship(base, 1, 1, 3)
        ship = [(1, 1), (2, 1), (3, 1)]
        for cell in base._cells:
            if (cell.x, cell.y) in ship:
                assert cell.value == Cell.SHIP
            else:
                assert cell.value == Cell.EMPTY

    def test_set_border(self):
        base = SeaField(5, 5)
        SeaPlayground._set_border(base, 1, 1, 3)
        border = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0),
                  (0, 1), (4, 1),
                  (0, 2), (1, 2), (2, 2), (3, 2), (4, 2)]
        for cell in base._cells:
            if (cell.x, cell.y) in border:
                assert cell.value == Cell.BORDER
            else:
                assert cell.value == Cell.EMPTY

    def test_set_border_edge(self):
        base = SeaField(4, 4)
        SeaPlayground._set_border(base, 0, 0, 2, True)
        SeaPlayground._set_border(base, 2, 3, 2)
        border = [(1, 0), (1, 1), (0, 2), (1, 2),
                  (2, 2), (3, 2), (1, 3)]
        for cell in base._cells:
            if (cell.x, cell.y) in border:
                assert cell.value == Cell.BORDER
            else:
                assert cell.value == Cell.EMPTY

    def test_put_ship(self):
        base = SeaField(5, 5)
        SeaPlayground.put_ship(base, 2, 1, 3, True)
        ship = [(2, 1), (2, 2), (2, 3)]
        border = [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4),
                  (2, 0), (2, 4),
                  (3, 0), (3, 1), (3, 2), (3, 3), (3, 4)]

        for cell in base._cells:
            if (cell.x, cell.y) in ship:
                assert cell.value == Cell.SHIP
            elif (cell.x, cell.y) in border:
                assert cell.value == Cell.BORDER
            else:
                assert cell.value == Cell.EMPTY

    def test_suitable_cell(self):
        base = SeaField(5, 5)
        assert SeaPlayground.is_cell_suitable(base, 1, 1, 1)
        assert SeaPlayground.is_cell_suitable(base, 1, 1, 3)
        assert SeaPlayground.is_cell_suitable(base, 1, 1, 3, True)

        assert not SeaPlayground.is_cell_suitable(base, -1, 1, 1)
        assert not SeaPlayground.is_cell_suitable(base, 5, 1, 1)
        assert not SeaPlayground.is_cell_suitable(base, 1, 1, 11)

        SeaPlayground.put_ship(base, 1, 1, 3)

        assert not SeaPlayground.is_cell_suitable(base, 0, 0, 1)
        assert not SeaPlayground.is_cell_suitable(base, 0, 2, 2, True)

    def test_incorrect_placement(self):
        base = SeaField(5, 5)
        SeaPlayground.put_ship(base, 1, 1, 3)
        with self.assertRaises(IncorrectCoordinate):
            SeaPlayground.put_ship(base, -1, 2, 2, True)
        with self.assertRaises(IncorrectShipPosition):
            SeaPlayground.put_ship(base, 0, 2, 2, True)

    def test_get_suitable_cells(self):
        base = SeaField(3, 3)
        SeaPlayground.put_ship(base, 0, 0, 1)
        assert SeaPlayground.get_suitable_cells(base, 3) == [(2, 0, True), (0, 2, False)]
        assert SeaPlayground.get_suitable_cells(base, 2) == [(2, 0, True), (2, 1, True), (0, 2, False), (1, 2, False)]

        assert SeaPlayground.get_suitable_cells(base, 1) == [(2, 0, True), (2, 0, False), (2, 1, True), (2, 1, False),
                                                             (0, 2, True), (0, 2, False), (1, 2, True), (1, 2, False),
                                                             (2, 2, True), (2, 2, False)]

    def test_put_random_ship(self):
        base = SeaField(4, 4)
        SeaPlayground._put_ship_random(base, 3)
        with self.assertRaises(NoSpaceLeft):
            SeaPlayground._put_ship_random(base, 3)
            SeaPlayground._put_ship_random(base, 3)

    def test_put_random_many(self):
        base = SeaField()
        SeaPlayground.put_ships_random(base)
        assert len([cell for cell in base._cells if cell.value == Cell.SHIP]) == 20

    def test_income_shoot(self):
        base = SeaField()
        SeaPlayground.put_ship(base, 2, 2, 3)
        assert SeaPlayground.income_shoot(base, 3, 0) is Cell.MISSED
        assert SeaPlayground.income_shoot(base, 3, 1) is Cell.MISSED
        assert SeaPlayground.income_shoot(base, 3, 2) is Cell.HIT
        assert SeaPlayground.income_shoot(base, 3, 3) is Cell.MISSED
        assert SeaPlayground.income_shoot(base, 3, 4) is Cell.MISSED

    def test_incorrect_income_shoot(self):
        base = SeaField()
        with self.assertRaises(IncorrectCoordinate):
            SeaPlayground.income_shoot(base, -3, 0)
        with self.assertRaises(IncorrectCoordinate):
            SeaPlayground.income_shoot(base, 11, 0)

    def test_target_anwer_mark_cell(self):
        base = SeaField(5, 5)
        SeaPlayground._target_answer_mark_cell(base, 1, 1, Cell.MISSED)
        SeaPlayground._target_answer_mark_cell(base, 2, 2, Cell.HIT)
        SeaPlayground._target_answer_mark_cell(base, 3, 3, Cell.MISSED)
        for cell in base._cells:
            if (cell.x, cell.y) in ((1, 1), (3, 3)):
                assert cell.value == Cell.MISSED
            elif cell.x == 2 and cell.y == 2:
                assert cell.value == Cell.HIT
            else:
                assert cell.value == Cell.EMPTY

    def test_find_ship(self):
        base = SeaField(5, 5)
        SeaPlayground.put_ship(base, 1, 1, 3)
        ship = SeaPlayground._find_ship_cells(base, 2, 1)
        assert set(ship) == set([(1, 1), (2, 1), (3, 1)])

    def test_find_ship_vertical(self):
        base = SeaField(5, 5)
        SeaPlayground.put_ship(base, 1, 1, 3, True)
        ship = SeaPlayground._find_ship_cells(base, 1, 2)
        assert set(ship) == set([(1, 1), (1, 2), (1, 3)])

    def test_find_abcent(self):
        base = SeaField(5, 5)
        ship = SeaPlayground._find_ship_cells(base, 1, 2)
        assert ship == []

    def test_is_killed_ship_alive(self):
        base = SeaField(5, 5)
        base.set(1, 2, Cell.SHIP)
        base.set(1, 3, Cell.SHIP)
        base.set(1, 4, Cell.SHIP)
        assert SeaPlayground._is_ship_killed(base, 1, 3) is False

    def test_is_killed_ship_injured(self):
        base = SeaField(5, 5)
        base.set(1, 2, Cell.HIT)
        base.set(1, 3, Cell.HIT)
        base.set(1, 4, Cell.SHIP)
        assert SeaPlayground._is_ship_killed(base, 1, 3) is False

        base.set(1, 2, Cell.HIT)
        base.set(1, 3, Cell.SHIP)
        base.set(1, 4, Cell.HIT)
        assert SeaPlayground._is_ship_killed(base, 1, 3) is False

    def test_is_killed_ship_killed(self):
        base = SeaField(5, 5)
        base.set(1, 2, Cell.HIT)
        base.set(1, 3, Cell.HIT)
        base.set(1, 4, Cell.HIT)
        assert SeaPlayground._is_ship_killed(base, 1, 3) is True

    def test_find_ship_vector(self):
        assert SeaPlayground._find_ship_vector([(1, 1), (2, 1), (3, 1)]) == (1, 1, 3, False)
        assert SeaPlayground._find_ship_vector([(1, 0), (1, 1), (1, 2), (1, 3)]) == (1, 0, 4, True)

    def test_answer_target_mark_border(self):
        base = SeaField(5, 5)
        base.set(2, 2, Cell.MISSED)
        SeaPlayground._target_answer_mark_border(base, [(0, 0)], Cell.KILLED)
        SeaPlayground._target_answer_mark_border(base, [(3, 3)], Cell.HIT)
        SeaPlayground._target_answer_mark_border(base, [(0, 4)], Cell.MISSED)
        SeaPlayground._target_answer_mark_border(base, [(4, 0)], Cell.MISSED)
        for cell in base._cells:
            if (cell.x, cell.y) in ((0, 1), (1, 0), (1, 1),
                                    (2, 4), (4, 2), (4, 4)):
                assert cell.value == Cell.BORDER
            elif cell.x == 2 and cell.y == 2:
                assert cell.value == Cell.MISSED
            else:
                assert cell.value == Cell.EMPTY

    def test_answet_target(self):
        base = SeaField(4, 4)
        SeaPlayground.target_answer(base, 0, 1, Cell.HIT)
        SeaPlayground.target_answer(base, 1, 1, Cell.MISSED)
        SeaPlayground.target_answer(base, 2, 1, Cell.MISSED)
        SeaPlayground.target_answer(base, 3, 1, Cell.KILLED)
        for cell in base._cells:
            if cell.x in (1, 2, 3) and cell.y in (0, 2):
                assert cell.value == Cell.BORDER
            elif (cell.x, cell.y) in ((1, 1), (2, 1)):
                assert cell.value == Cell.MISSED
            elif (cell.x, cell.y) == (0, 1):
                assert cell.value == Cell.HIT
            elif (cell.x, cell.y) == (3, 1):
                assert cell.value == Cell.KILLED
            else:
                assert cell.value == Cell.EMPTY


class ComputerPlayerTest:

    def test_find_target(self):
        base = SeaField(2, 2)
        list(map(base.set, (0, 0, 1), (0, 1, 0), (1, 1, 1)))
        assert ComputerPlayer.find_target(base) == (1, 1)
