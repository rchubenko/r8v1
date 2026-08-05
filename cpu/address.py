"""Stateless 12-bit address source selection for R8 v1."""

from enum import Enum

from .values import validate_address


class AddressSource(Enum):
    """Sources supported by the public address path selector API."""

    PC = "pc"
    IR_OPERAND = "ir_operand"


def select_address(
    source: AddressSource,
    *,
    pc: object,
    ir_operand: object,
) -> int:
    """Select one validated 12-bit address without storing or latching state."""

    if not isinstance(source, AddressSource):
        raise TypeError(f"source must be an AddressSource; got {source!r}")

    pc_value = validate_address(pc)
    ir_operand_value = validate_address(ir_operand)
    return pc_value if source is AddressSource.PC else ir_operand_value
