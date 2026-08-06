import ast
from dataclasses import fields
from pathlib import Path

import cpu
from cpu import FlagsDefinedMask, FlagsSnapshot
from emulator import (
    ArchitecturalState,
    ArchitecturalStateSnapshot,
    DecodedInstruction,
    DiagnosticIdentifier,
    DiagnosticSeverity,
    ExecutionPolicy,
    Opcode,
    StepResult,
)

ROOT = Path(__file__).parents[1]
CPU_PATH = ROOT / "cpu"
EMULATOR_PATH = ROOT / "emulator"
ALLOWED_EMULATOR_IMPORTS = {
    "collections",
    "dataclasses",
    "enum",
    "typing",
    "cpu",
}
FORBIDDEN_EMULATOR_IMPORTS = {
    "assembler",
    "control_word",
    "hardware",
    "loader",
    "microcode",
    "simulator",
    "gpio",
}
FORBIDDEN_EMULATOR_IDENTIFIERS = {
    "DATA_BUS",
    "EEPROM",
    "MAR",
    "MEM_OWNER",
    "MICROSTEP",
    "PC_OP",
    "RAM_WE",
    "clock_tick",
    "control_word",
    "microcode",
    "microstep_counter",
    "rising_edge",
}
FORBIDDEN_CPU_FUNCTIONS = {
    "execute_instruction",
    "execute_next",
    "fetch_instruction",
    "run",
    "run_program",
    "step",
}


def _python_files(package_path: Path) -> tuple[Path, ...]:
    return tuple(sorted(package_path.glob("*.py")))


def _trees(package_path: Path) -> tuple[ast.Module, ...]:
    return tuple(ast.parse(path.read_text()) for path in _python_files(package_path))


def _import_roots(tree: ast.Module) -> set[str]:
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module is not None:
            roots.add(node.module.split(".", 1)[0])
    return roots


def _identifiers(tree: ast.Module) -> set[str]:
    identifiers: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            identifiers.add(node.id)
        elif isinstance(node, ast.Attribute):
            identifiers.add(node.attr)
    return identifiers


def test_emulator_imports_only_allowed_layers() -> None:
    imported = set().union(*(_import_roots(tree) for tree in _trees(EMULATOR_PATH)))

    assert imported <= ALLOWED_EMULATOR_IMPORTS
    assert imported.isdisjoint(FORBIDDEN_EMULATOR_IMPORTS)
    assert "cpu" in imported


def test_cpu_does_not_import_emulator_or_forbidden_execution_layers() -> None:
    imported = set().union(*(_import_roots(tree) for tree in _trees(CPU_PATH)))

    assert "emulator" not in imported
    assert imported.isdisjoint(FORBIDDEN_EMULATOR_IMPORTS)


def test_emulator_source_has_no_microarchitectural_execution_identifiers() -> None:
    used = set().union(*(_identifiers(tree) for tree in _trees(EMULATOR_PATH)))

    assert used.isdisjoint(FORBIDDEN_EMULATOR_IDENTIFIERS)


def test_cpu_exports_reusable_components_not_complete_isa_execution() -> None:
    assert not hasattr(cpu, "ArchitecturalState")
    assert not hasattr(cpu, "DecodedInstruction")
    assert not hasattr(cpu, "StepResult")
    assert not hasattr(cpu, "step")
    assert hasattr(cpu, "MicrostepCounter")
    assert hasattr(cpu, "MemoryAddressRegister")
    assert not (set(cpu.__all__) & {"ArchitecturalState", "DecodedInstruction", "StepResult"})

    function_names = {
        node.name
        for tree in _trees(CPU_PATH)
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert function_names.isdisjoint(FORBIDDEN_CPU_FUNCTIONS)


def test_emulator_owns_atomic_execution_path_and_public_result_types() -> None:
    assert hasattr(ArchitecturalState, "fetch_instruction")
    assert hasattr(ArchitecturalState, "execute_instruction")
    assert hasattr(ArchitecturalState, "step")
    assert not hasattr(cpu, "execute_instruction")
    assert not hasattr(cpu, "fetch_instruction")
    assert {field.name for field in fields(ArchitecturalStateSnapshot)} == {
        "a",
        "pc",
        "irh",
        "irl",
        "flags",
        "flags_defined_mask",
        "halt_state",
        "memory",
    }
    assert {field.name for field in fields(StepResult)} == {
        "instruction",
        "pre_state",
        "post_state",
        "diagnostic",
    }


def test_architectural_state_has_no_microarchitectural_or_external_policy_fields() -> None:
    state = ArchitecturalState()
    forbidden_fields = {
        "b",
        "clock_phase",
        "control_word",
        "data_bus",
        "diagnostic",
        "diagnostics",
        "eeprom_address",
        "execution_policy",
        "halt_reason",
        "mar",
        "microstep",
        "policy",
    }

    assert forbidden_fields.isdisjoint(dir(state))
    assert not hasattr(state.snapshot(), "diagnostic")
    assert not hasattr(state.snapshot(), "policy")


def test_step_result_does_not_add_policy_timing_or_trace_state() -> None:
    state = ArchitecturalState()
    state._memory.write(0x000, 0x00)
    state._memory.write(0x001, 0x00)
    result = state.step(policy=ExecutionPolicy.HARDWARE_LIKE)

    assert isinstance(result.instruction, DecodedInstruction)
    assert isinstance(result.pre_state, ArchitecturalStateSnapshot)
    assert isinstance(result.post_state, ArchitecturalStateSnapshot)
    assert result.diagnostic is None
    result_fields = {field.name for field in fields(result)}
    assert not {
        "bus_trace",
        "clock_count",
        "cycle_count",
        "microstep_trace",
        "policy",
        "trace",
    }.intersection(result_fields)


def test_opcode_mapping_matches_approved_isa() -> None:
    expected = {
        0x0: Opcode.NOP,
        0x1: Opcode.LDI,
        0x2: Opcode.LDA,
        0x3: Opcode.ADD,
        0x4: Opcode.SUB,
        0x5: Opcode.STA,
        0x6: Opcode.JMP,
        0x7: Opcode.JC,
        0x8: Opcode.JZ,
        0x9: Opcode.JN,
        0xA: Opcode.JV,
        0xB: Opcode.RESERVED_B,
        0xC: Opcode.RESERVED_C,
        0xD: Opcode.RESERVED_D,
        0xE: Opcode.RESERVED_E,
        0xF: Opcode.HLT,
    }

    assert {opcode.value: opcode for opcode in Opcode} == expected


def test_reset_fetch_and_result_boundaries_remain_architectural() -> None:
    state = ArchitecturalState()
    state._a.load(0xA5)
    state._pc.load(0xFFF)
    state._flags = FlagsSnapshot.reset()
    state._memory.write(0xFFF, 0x10)
    state._memory.write(0x000, 0x42)
    before_memory = state.memory_image

    result = state.step()

    assert result.instruction == DecodedInstruction(Opcode.LDI, 0x042)
    assert result.pre_state.pc == 0xFFF
    assert result.post_state.pc == 0x001
    assert result.post_state.a == 0x42
    assert result.post_state.flags_defined_mask == FlagsDefinedMask.zero_and_sign()
    assert state.memory_image == before_memory

    state.reset()
    assert state.pc == 0x000
    assert state.a == 0x00
    assert (state.irh, state.irl) == (0x00, 0x00)
    assert state.flags == FlagsSnapshot.reset()
    assert state.flags_defined_mask == FlagsDefinedMask.all()
    assert state.halt_state is False
    assert state.memory_image == before_memory


def test_diagnostic_and_halt_observations_stay_outside_architectural_snapshots() -> None:
    state = ArchitecturalState()
    state._memory.write(0x000, 0xB0)
    state._memory.write(0x001, 0x00)

    result = state.step()

    assert result.diagnostic is not None
    assert result.diagnostic.identifier is DiagnosticIdentifier.ILLEGAL_OPCODE
    assert result.diagnostic.severity is DiagnosticSeverity.ERROR
    assert result.post_state.halt_state is True
    assert not hasattr(result.pre_state, "diagnostic")
    assert not hasattr(result.post_state, "diagnostic")
    halted = state.step()
    assert halted.instruction is None
    assert halted.diagnostic is None
