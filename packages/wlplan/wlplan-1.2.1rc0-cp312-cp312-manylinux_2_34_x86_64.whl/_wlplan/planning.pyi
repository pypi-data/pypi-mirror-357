from __future__ import annotations
import typing
__all__ = ['Atom', 'ComparatorType', 'ConstantExpression', 'Domain', 'Fluent', 'FluentExpression', 'FormulaExpression', 'Function', 'NumericCondition', 'NumericExpression', 'Object', 'OperatorType', 'Predicate', 'Problem', 'State']
class Atom:
    """
    Parameters
    ----------
        predicate : Predicate
            Predicate object.
    
        objects : list[Object]
            List of object names.
    """
    __hash__: typing.ClassVar[None] = None
    def __eq__(self, arg0: Atom) -> bool:
        ...
    def __init__(self, predicate: Predicate, objects: list[str]) -> None:
        ...
    def __repr__(self) -> str:
        ...
class ComparatorType:
    """
    Members:
    
      GreaterThan
    
      GreaterThanOrEqual
    
      Equal
    """
    Equal: typing.ClassVar[ComparatorType]  # value = <ComparatorType.Equal: 2>
    GreaterThan: typing.ClassVar[ComparatorType]  # value = <ComparatorType.GreaterThan: 0>
    GreaterThanOrEqual: typing.ClassVar[ComparatorType]  # value = <ComparatorType.GreaterThanOrEqual: 1>
    __members__: typing.ClassVar[dict[str, ComparatorType]]  # value = {'GreaterThan': <ComparatorType.GreaterThan: 0>, 'GreaterThanOrEqual': <ComparatorType.GreaterThanOrEqual: 1>, 'Equal': <ComparatorType.Equal: 2>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class ConstantExpression(NumericExpression):
    """
    Parameters
    ----------
        value : float
            Numeric value.
    """
    def __init__(self, value: float) -> None:
        ...
class Domain:
    """
    Parameters
    ----------
        name : str
            Domain name.
    
        predicates : list[Predicate]
            List of predicates.
    
        functions : list[Function], optional
            List of functions.
    
        constant_objects : list[Object], optional
            List of constant objects.
    """
    __hash__: typing.ClassVar[None] = None
    def __eq__(self, arg0: Domain) -> bool:
        ...
    @typing.overload
    def __init__(self, name: str, predicates: list[Predicate], functions: list[Function], constant_objects: list[str]) -> None:
        ...
    @typing.overload
    def __init__(self, name: str, predicates: list[Predicate], constant_objects: list[str]) -> None:
        ...
    @typing.overload
    def __init__(self, name: str, predicates: list[Predicate]) -> None:
        ...
    @typing.overload
    def __init__(self, name: str, predicates: list[Predicate], functions: list[Function]) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def constant_objects(self) -> list[str]:
        ...
    @property
    def functions(self) -> list[Function]:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def predicates(self) -> list[Predicate]:
        ...
class Fluent:
    """
    Parameters
    ----------
        function : Function
            Function object.
    
        objects : list[Object]
            List of object names.
    """
    __hash__: typing.ClassVar[None] = None
    def __eq__(self, arg0: Fluent) -> bool:
        ...
    def __init__(self, function: Function, objects: list[str]) -> None:
        ...
    def __repr__(self) -> str:
        ...
class FluentExpression(NumericExpression):
    """
    Parameters
    ----------
        id : int
            Fluent ID.
    
        fluent_name : str
            Fluent name.
    """
    def __init__(self, id: int, fluent_name: str) -> None:
        ...
class FormulaExpression(NumericExpression):
    """
    Parameters
    ----------
        op_type : OperatorType
            Operator enum class.
    
        expr_a : NumericExpression
            Numeric expression.
    
        expr_b : NumericExpression
            Numeric expression.
    """
    def __init__(self, op_type: OperatorType, expr_a: NumericExpression, expr_b: NumericExpression) -> None:
        ...
class Function:
    """
    Parameters
    ----------
        name : str
            Predicate name.
    
        arity : int
            Predicate arity.
    """
    __hash__: typing.ClassVar[None] = None
    def __eq__(self, arg0: Function) -> bool:
        ...
    def __init__(self, name: str, arity: int) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def arity(self) -> int:
        ...
    @property
    def name(self) -> str:
        ...
class NumericCondition:
    """
    Parameters
    ----------
        comparator_type : ComparatorType
            Comparator enum class.
    
        expression : NumericExpression
            Numeric expression constituting the LHS of the condition :math:`\\xi \\unrhd 0`.
    """
    def __init__(self, comparator_type: ComparatorType, expression: NumericExpression) -> None:
        ...
    def evaluate_error(self, values: list[float]) -> float:
        ...
    def evaluate_formula(self, values: list[float]) -> bool:
        ...
    def evaluate_formula_and_error(self, values: list[float]) -> tuple[bool, float]:
        ...
class NumericExpression:
    """
    NumericExpression is an abstract class for numeric expressions.
    """
    def __repr__(self) -> str:
        ...
    def evaluate(self, values: list[float]) -> float:
        ...
    def get_fluent_ids(self) -> list[int]:
        ...
class Object:
    """
    Object is a type alias for a str. WLPlan does not exploit object types.
    """
class OperatorType:
    """
    Members:
    
      Plus
    
      Minus
    
      Multiply
    
      Divide
    """
    Divide: typing.ClassVar[OperatorType]  # value = <OperatorType.Divide: 3>
    Minus: typing.ClassVar[OperatorType]  # value = <OperatorType.Minus: 1>
    Multiply: typing.ClassVar[OperatorType]  # value = <OperatorType.Multiply: 2>
    Plus: typing.ClassVar[OperatorType]  # value = <OperatorType.Plus: 0>
    __members__: typing.ClassVar[dict[str, OperatorType]]  # value = {'Plus': <OperatorType.Plus: 0>, 'Minus': <OperatorType.Minus: 1>, 'Multiply': <OperatorType.Multiply: 2>, 'Divide': <OperatorType.Divide: 3>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class Predicate:
    """
    Parameters
    ----------
        name : str
            Predicate name.
    
        arity : int
            Predicate arity.
    """
    __hash__: typing.ClassVar[None] = None
    def __eq__(self, arg0: Predicate) -> bool:
        ...
    def __init__(self, name: str, arity: int) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def arity(self) -> int:
        ...
    @property
    def name(self) -> str:
        ...
class Problem:
    """
    Parameters
    ----------
        domain : Domain
            Domain object.
    
        objects : list[Object]
            List of object names.
    
        statics: list[Atom], optional
            List of static atoms.
    
        fluents: list[Fluent], optional
            List of fluents.
    
        fluent_values: list[float], optional
            List of fluent values of the initial state of the problem.
    
        positive_goals : list[Atom]
            List of positive goal atoms.
    
        negative_goals : list[Atom]
            List of negative goal atoms.
        
        numeric_goals : list[NumericCondition], optional
            List of numeric goals.
    """
    @typing.overload
    def __init__(self, domain: Domain, objects: list[str], statics: list[Atom], fluents: list[Fluent], fluent_values: list[float], positive_goals: list[Atom], negative_goals: list[Atom], numeric_goals: list[NumericCondition]) -> None:
        ...
    @typing.overload
    def __init__(self, domain: Domain, objects: list[str], fluents: list[Fluent], fluent_values: list[float], positive_goals: list[Atom], negative_goals: list[Atom], numeric_goals: list[NumericCondition]) -> None:
        ...
    @typing.overload
    def __init__(self, domain: Domain, objects: list[str], positive_goals: list[Atom], negative_goals: list[Atom]) -> None:
        ...
    def dump(self) -> None:
        ...
    @property
    def constant_objects(self) -> list[str]:
        ...
    @property
    def domain(self) -> Domain:
        ...
    @property
    def fluent_name_to_id(self) -> dict[str, int]:
        ...
    @property
    def fluents(self) -> list[Fluent]:
        ...
    @property
    def init_fluent_values(self) -> list[float]:
        ...
    @property
    def negative_goals(self) -> list[Atom]:
        ...
    @property
    def numeric_goals(self) -> list[NumericCondition]:
        ...
    @property
    def objects(self) -> list[str]:
        ...
    @property
    def positive_goals(self) -> list[Atom]:
        ...
    @property
    def statics(self) -> list[Atom]:
        ...
class State:
    """
    Parameters
    ----------
        atoms : list[Atom]
            List of atoms.
    
        values : list[float], optional
            List of values for fluents defined in the problem.
    """
    def __eq__(self, arg0: State) -> bool:
        ...
    def __hash__(self) -> int:
        ...
    @typing.overload
    def __init__(self, atoms: list[Atom]) -> None:
        ...
    @typing.overload
    def __init__(self, atoms: list[Atom], values: list[float]) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def atoms(self) -> list[Atom]:
        ...
    @property
    def values(self) -> list[float]:
        ...
