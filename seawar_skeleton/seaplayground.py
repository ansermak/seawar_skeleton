from itertools import chain, product, takewhile, starmap
from random import choice


STANDARD_SHIP_FLEET = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
DEFAULT_MAX_X = 10
DEFAULT_MAX_Y = 10


class SIGNALS:
    WIN = 5
    KILLED = 4
    HITTING = 3
    MISS = 2


def filter_correct_coordinates(f):
    def decor(field, *args, **kwargs):
        return [cell for cell in f(field, *args, **kwargs) if field.is_coord_correct(*cell)]
    return decor


def check_coordinates(f):
    def decor(field, coord_x, coord_y, *args, **kwargs):
        if field.is_coord_correct(coord_x, coord_y):
            return f(field, coord_x, coord_y, *args, **kwargs)
        raise IncorrectCoordinate(f'({coord_x}: {coord_y}) for Field({field.max_x}:{field.max_y})')
    return decor


class IncorrectCoordinate(Exception):
    pass


class IncorrectShipPosition(IncorrectCoordinate):
    pass


class NoSpaceLeft(Exception):
    pass


class Cell:
    EMPTY = 0
    BORDER = 1
    SHIP = 10
    HIT = -10
    MISSED = -1
    PROBABLY_SHIP = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.value = Cell.EMPTY

    def __repr__(self):
        return f'<Cell: ({self.x}; {self.y} = {self.value})>'


class Matrix:

    def __init__(self, max_x=DEFAULT_MAX_X, max_y=DEFAULT_MAX_Y):
        self.max_x = max_x
        self.max_y = max_y
        self._field = [[Cell(i, j) for i in range(max_x)] for j in range(max_y)]
        self._cells = list(chain(*self._field))
        self.cells = [(cell.x, cell.y) for cell in self._cells]

    def __repr__(self):
        return '<Matrix (max_x={}; max_y={})>'.format(self.max_x, self.max_y)

    def __str__(self):
        out = repr(self)
        for row in self._field:
            out += '\n\t' + ''.join([f'{cell.value:4}' for cell in row])
        return out + '\n'

    def set(self, coord_x, coord_y, value):
        self._field[coord_y][coord_x].value = value

    def get(self, coord_x, coord_y):
        return self._field[coord_y][coord_x].value

    def is_coord_correct(self, coord_x, coord_y):
        return (0 <= coord_x < self.max_x) and (0 <= coord_y < self.max_y)

    @staticmethod
    def next_cell(coord_x, coord_y, is_vertical=False, length=None, step=1):
        cond = (lambda l: (lambda: True) if l is None else (lambda i=iter(range(l, -1, -1)): next(i)))(length)
        while cond():
            yield (coord_x, coord_y)
            coord_x, coord_y = coord_x + step * (not is_vertical), coord_y + step * is_vertical


class SeaField(Matrix):

    def is_cell_ship(self, coord_x, coord_y):
        return self.get(coord_x, coord_y) in (Cell.SHIP, Cell.HIT)

    def is_cell_empty(self, coord_x, coord_y):
        return self.get(coord_x, coord_y) in (Cell.EMPTY, Cell.PROBABLY_SHIP)

    def set_ship(self, coord_x, coord_y, length, is_vertical=False):
        [self.set(value=Cell.SHIP, *cell) for cell in self.next_cell(coord_x, coord_y, is_vertical, length)]

    def set_border(self, coord_x, coord_y, length=None, is_vertical=False):
        if length:
            cells = self._find_border_cells(coord_x, coord_y, length, is_vertical)
        else:
            cells = self._find_cell_corners(coord_x, coord_y)
        [self.set(value=Cell.BORDER, *cell) for cell in cells if self.is_cell_empty(*cell)]

    def is_cell_suitable(self, coord_x, coord_y, length, is_vertical=False):
        check = lambda x, y: self.is_coord_correct(x, y) and self.is_cell_empty(x, y)
        return all(starmap(check, self.next_cell(coord_x, coord_y, is_vertical, length)))

    def find_ship_by_cells(self, coord_x, coord_y):
        out = []
        for step, is_vertical in product([-1, 1], [True, False]):
            out.extend(takewhile(
                lambda cell: (self.is_coord_correct(*cell) and self.is_cell_ship(*cell)),
                self.next_cell(coord_x, coord_y, is_vertical, None, step)))
        return set(out)

    def has_any_alive_ship(self):
        return any([cell for cell in self._cells if cell.value is Cell.SHIP])

    @staticmethod
    def find_ship_vector(ship_cells):
        (x1, y1), (x2, y2) = map(min, zip(*ship_cells)), map(max, zip(*ship_cells))
        length = max(x2 - x1, y2 - y1)
        is_vertical = y1 + length == y2
        return x1, y1, length + 1, is_vertical

    @filter_correct_coordinates
    def _find_border_cells(self, coord_x, coord_y, length, is_vertical=False):
        v_length, h_length = (length, 1) if is_vertical else (1, length)
        return (list(Matrix.next_cell(coord_x - 1, coord_y - 1, True, v_length + 2)) +
                list(Matrix.next_cell(coord_x + h_length, coord_y - 1, True, v_length + 2)) +
                list(Matrix.next_cell(coord_x, coord_y - 1, False, h_length)) +
                list(Matrix.next_cell(coord_x, coord_y + v_length, False, h_length)))

    @filter_correct_coordinates
    def _find_cell_corners(self, coord_x, coord_y):
        return map(lambda c, d: (c[0] + d[0], c[1] + d[1]), [(coord_x, coord_y)] * 4, product((-1, 1), (-1, 1)))

    @filter_correct_coordinates
    def _find_cell_ribs(self, coord_x, coord_y):
        return map(lambda c, d: (c[0] + d[0], c[1] + d[1]), [(coord_x, coord_y)] * 4,
                   ((-1, 0), (1, 0), (0, -1), (0, 1)))


class _SeaPlaygroundShips:

    @staticmethod
    @check_coordinates
    def put_ship(field, coord_x, coord_y, length, is_vertical=False):
        if field.is_cell_suitable(coord_x, coord_y, length, is_vertical):
            field.set_ship(coord_x, coord_y, length, is_vertical)
            field.set_border(coord_x, coord_y, length, is_vertical)
        else:
            raise IncorrectShipPosition()

    @staticmethod
    def get_suitable_cells(field, length):
        return [(x, y, is_vertical)
                for (x, y), is_vertical in product(field.cells, (True, False))
                if field.is_cell_suitable(x, y, length, is_vertical)]

    @staticmethod
    def _put_ship_random(field, length):
        cells = _SeaPlaygroundShips.get_suitable_cells(field, length)
        if not cells:
            raise NoSpaceLeft()
        coord_x, coord_y, is_vertical = choice(cells)
        field.set_ship(coord_x, coord_y, length, is_vertical)
        field.set_border(coord_x, coord_y, length, is_vertical)

    @staticmethod
    def put_ships_random(field, fleet:list=None):
        fleet = fleet if fleet else STANDARD_SHIP_FLEET
        for length in fleet:
            _SeaPlaygroundShips._put_ship_random(field, length)


class _SeaPlaygroundShoots:

    @staticmethod
    @check_coordinates
    def income_shoot_to(field, *coord):
        signal, cell_mark = (SIGNALS.HITTING, Cell.HIT) if field.is_cell_ship(*coord) else (SIGNALS.MISS, Cell.MISSED)
        field.set(*coord, cell_mark)
        killed_cells = (signal is SIGNALS.HITTING) and list(_SeaPlaygroundShoots._get_killed_ship(field, *coord)) or []
        signal = (SIGNALS.WIN if not field.has_any_alive_ship() else SIGNALS.KILLED) if killed_cells else signal
        return dict(signal=signal, cells=(killed_cells or [coord]))

    @staticmethod
    def handle_shoot_answer(field, signal, cells):
        if not all(starmap(field.is_coord_correct, cells)):
            raise IncorrectCoordinate(f'{cells} for Field({field.max_x}:{field.max_y})')
        _SeaPlaygroundShoots._shoot_answer_mark_cell(field, signal, cells)
        _SeaPlaygroundShoots._shoot_answer_mark_border(field, signal, cells)

    @staticmethod
    def _shoot_answer_mark_cell(field, signal, cells):
        answer = Cell.HIT if signal in (SIGNALS.HITTING, SIGNALS.KILLED, SIGNALS.WIN) else Cell.MISSED
        [field.set(value=answer, *cell) for cell in cells]

    @staticmethod
    def _shoot_answer_mark_border(field, signal, cells):
        if signal == SIGNALS.KILLED:
            field.set_border(*field.find_ship_vector(cells))
        elif signal == SIGNALS.HITTING:
            field.set_border(*cells[0])

    @staticmethod
    def _get_killed_ship(field, coord_x, coord_y):
        ship_cells = field.find_ship_by_cells(coord_x, coord_y)
        return ship_cells if all([field.get(*cell) == Cell.HIT for cell in ship_cells]) else []

    @staticmethod
    def make_shoot_by_computer(comp, enemy_field):
        x, y = comp.select_target()
        answer = SeaPlayground.income_shoot_to(enemy_field, x, y)
        comp.handle_shoot_answer(**answer)
        return answer


class SeaPlayground(_SeaPlaygroundShips, _SeaPlaygroundShoots):
    pass


class ComputerPlayer:

    def __init__(self, max_x=DEFAULT_MAX_X, max_y=DEFAULT_MAX_Y):
        self.target_field = SeaField(max_x, max_y)

    def handle_shoot_answer(self, signal, cells):
        SeaPlayground.handle_shoot_answer(self.target_field,  signal, cells)
        if signal is SIGNALS.HITTING:
            for answer_cell in cells:
                [self.target_field.set(value=Cell.PROBABLY_SHIP, *cl)
                 for cl in self.target_field._find_cell_ribs(*answer_cell)
                 if self.target_field.is_cell_empty(*cl)]

    def select_target(self):
        cells = [cell for cell in self.target_field.cells if self.target_field.get(*cell) == Cell.PROBABLY_SHIP]
        if not cells:
            cells = [cell for cell in self.target_field.cells if self.target_field.is_cell_empty(*cell)]
        return choice(cells)
