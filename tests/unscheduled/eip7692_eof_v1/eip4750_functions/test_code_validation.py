"""Code validation of CALLF, RETF opcodes tests."""

from typing import List

import pytest

from ethereum_test_tools import EOFException, EOFTestFiller
from ethereum_test_tools.vm.opcode import Opcodes as Op
from ethereum_test_types.eof.constants import MAX_RUNTIME_STACK_HEIGHT
from ethereum_test_types.eof.v1 import Container, Section
from ethereum_test_types.eof.v1.constants import (
    MAX_CODE_OUTPUTS,
    MAX_CODE_SECTIONS,
    MAX_STACK_INCREASE_LIMIT,
)

from .. import EOF_FORK_NAME

REFERENCE_SPEC_GIT_PATH = "EIPS/eip-4750.md"
REFERENCE_SPEC_VERSION = "14400434e1199c57d912082127b1d22643788d11"

pytestmark = pytest.mark.valid_from(EOF_FORK_NAME)

VALID: List[Container] = [
    Container(
        name="retf_stack_validation_0",
        sections=[
            Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
            Section.Code(
                code=Op.PUSH0 * 2 + Op.RETF,
                code_outputs=2,
                max_stack_height=2,
            ),
        ],
    ),
    Container(
        name="retf_stack_validation_3",
        sections=[
            Section.Code(
                code=Op.PUSH0 + Op.CALLF[1] + Op.STOP,
                max_stack_height=2,
            ),
            Section.Code(
                code=Op.RJUMPI[7] + Op.PUSH1[1] * 2 + Op.RJUMP[2] + Op.PUSH0 * 2 + Op.RETF,
                code_inputs=1,
                code_outputs=2,
                max_stack_height=2,
            ),
        ],
    ),
    Container(
        name="retf_code_input_output",
        sections=[
            Section.Code(code=Op.PUSH0 + Op.CALLF[1] + Op.POP + Op.POP + Op.STOP),
            Section.Code(
                code=Op.PUSH0 + Op.RETF,
                code_outputs=1,
            ),
        ],
    ),
    Container(
        name="stack_height_equal_code_outputs_retf_zero_stop",
        sections=[
            Section.Code(
                code=Op.CALLF[1] + Op.POP + Op.STOP,
                code_inputs=0,
                max_stack_height=1,
            ),
            Section.Code(
                code=(
                    Op.RJUMPI[len(Op.PUSH0) + len(Op.RETF)](Op.ORIGIN)
                    + Op.PUSH0
                    + Op.RETF
                    + Op.STOP
                ),
                code_inputs=0,
                code_outputs=1,
                max_stack_height=1,
            ),
        ],
    ),
    Container(
        name="callf_max_code_sections_1",
        sections=[
            Section.Code(code=(sum(Op.CALLF[i] for i in range(1, MAX_CODE_SECTIONS)) + Op.STOP))
        ]
        + (
            [
                Section.Code(
                    code=Op.RETF,
                    code_outputs=0,
                )
            ]
            * (MAX_CODE_SECTIONS - 1)
        ),
    ),
    Container(
        name="callf_max_code_sections_2",
        sections=[Section.Code(code=(Op.CALLF[1] + Op.STOP))]
        + [
            Section.Code(
                code=(Op.CALLF[i + 2] + Op.RETF),
                code_outputs=0,
            )
            for i in range(MAX_CODE_SECTIONS - 2)
        ]
        + [
            Section.Code(
                code=Op.RETF,
                code_outputs=0,
            )
        ],
    ),
]

INVALID: List[Container] = [
    Container(
        name="retf_stack_validation_1",
        sections=[
            Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
            Section.Code(
                code=Op.PUSH0 + Op.RETF,
                code_outputs=2,
                max_stack_height=1,
            ),
        ],
        validity_error=EOFException.STACK_UNDERFLOW,
    ),
    Container(
        name="retf_variable_stack_0",
        sections=[
            Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=5),
            Section.Code(
                code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.RETF,
                code_outputs=5,
                max_stack_height=3,
            ),
        ],
        validity_error=EOFException.STACK_UNDERFLOW,
    ),
    Container(
        name="retf_variable_stack_1",
        sections=[
            Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=3),
            Section.Code(
                code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.RETF,
                code_outputs=3,
                max_stack_height=3,
            ),
        ],
        validity_error=EOFException.STACK_UNDERFLOW,
    ),
    Container(
        name="retf_variable_stack_4",
        sections=[
            Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=3),
            Section.Code(
                code=Op.PUSH0 * 3 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.POP * 2 + Op.RETF,
                code_outputs=3,
                max_stack_height=4,
            ),
        ],
        validity_error=EOFException.STACK_UNDERFLOW,
    ),
    Container(
        name="callf_inputs_underflow_0",
        sections=[
            Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=1),
            Section.Code(
                code=Op.PUSH0 + Op.CALLF[2] + Op.RETF,
                code_outputs=1,
                max_stack_height=1,
            ),
            Section.Code(
                code=Op.POP + Op.RETF,
                code_inputs=2,
                code_outputs=1,
                max_stack_height=2,
            ),
        ],
        validity_error=EOFException.STACK_UNDERFLOW,
    ),
    Container(
        # CALLF to function with incorrectly specified number of inputs
        name="code_inputs_underflow_1",  # EOF1I4750_0020
        sections=[
            Section.Code(code=(Op.PUSH0 + Op.PUSH0 + Op.CALLF[1] + Op.STOP)),
            Section.Code(
                code=(Op.ADD + Op.RETF),
                code_inputs=0,
                code_outputs=0,
            ),
        ],
        validity_error=EOFException.STACK_UNDERFLOW,
    ),
    Container(
        name="code_inputs_underflow_2",
        sections=[
            Section.Code(code=(Op.PUSH0 + Op.CALLF[1] + Op.STOP)),
            Section.Code(
                code=(Op.POP + Op.POP + Op.RETF),
                code_inputs=1,
                code_outputs=0,
            ),
        ],
        validity_error=EOFException.STACK_UNDERFLOW,
    ),
    Container(
        # CALLF without enough inputs
        name="callf_inputs_underflow",  # EOF1I4750_0019
        sections=[
            Section.Code(code=(Op.CALLF[1] + Op.STOP)),
            Section.Code(
                code=(Op.ADD + Op.RETF),
                code_inputs=2,
                code_outputs=1,
            ),
        ],
        validity_error=EOFException.STACK_UNDERFLOW,
    ),
    Container(
        name="retf_stack_validation_2",
        sections=[
            Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=2),
            Section.Code(
                code=Op.PUSH0 * 3 + Op.RETF,
                code_outputs=2,
                max_stack_height=3,
            ),
        ],
        validity_error=EOFException.STACK_HIGHER_THAN_OUTPUTS,
    ),
    Container(
        name="retf_variable_stack_2",
        sections=[
            Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=1),
            Section.Code(
                code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.RETF,
                code_outputs=1,
                max_stack_height=3,
            ),
        ],
        validity_error=EOFException.STACK_HIGHER_THAN_OUTPUTS,
    ),
    Container(
        name="retf_variable_stack_5",
        sections=[
            Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=1),
            Section.Code(
                code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[1] + Op.PUSH0 + Op.RETF,
                code_outputs=1,
                max_stack_height=3,
            ),
        ],
        validity_error=EOFException.STACK_HIGHER_THAN_OUTPUTS,
    ),
    Container(
        name="retf_variable_stack_6",
        sections=[
            Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=1),
            Section.Code(
                code=Op.PUSH0 * 2 + Op.PUSH1[0] + Op.RJUMPI[1] + Op.POP + Op.RETF,
                code_outputs=1,
                max_stack_height=3,
            ),
        ],
        validity_error=EOFException.STACK_HIGHER_THAN_OUTPUTS,
    ),
    Container(
        name="retf_variable_stack_3",
        sections=[
            Section.Code(code=Op.CALLF[1] + Op.STOP),
            Section.Code(
                code=Op.PUSH0 + Op.PUSH1[0] + Op.RJUMPI[2] + Op.PUSH0 * 2 + Op.RETF,
                code_outputs=0,
                max_stack_height=3,
            ),
        ],
        validity_error=EOFException.STACK_HIGHER_THAN_OUTPUTS,
    ),
    Container(
        name="stack_higher_than_code_outputs",
        sections=[
            Section.Code(
                code=(Op.CALLF[1] + Op.STOP),
            ),
            Section.Code(
                code=(Op.PUSH0 + Op.RETF),
                code_outputs=0,
            ),
        ],
        validity_error=EOFException.STACK_HIGHER_THAN_OUTPUTS,
    ),
    Container(
        name="stack_shorter_than_code_outputs",
        sections=[
            Section.Code(
                code=(Op.CALLF[1] + Op.STOP),
            ),
            Section.Code(
                code=(Op.PUSH0 + Op.RETF),
                code_outputs=2,
                max_stack_height=1,
            ),
        ],
        validity_error=EOFException.INVALID_MAX_STACK_INCREASE,
    ),
    Container(
        name="stack_shorter_than_code_outputs_1",
        sections=[
            Section.Code(
                code=(Op.CALLF[1] + Op.STOP),
                # max_stack_heights of sections aligned with actual stack
                max_stack_height=1,
            ),
            Section.Code(
                code=(Op.PUSH0 + Op.RETF),
                code_outputs=2,
                max_stack_height=1,
            ),
        ],
        validity_error=EOFException.INVALID_MAX_STACK_INCREASE,
    ),
    Container(
        name="stack_shorter_than_code_outputs_2",
        sections=[
            Section.Code(
                code=(Op.CALLF[1] + Op.STOP),
                # max_stack_heights of sections aligned with declared outputs
                max_stack_height=2,
            ),
            Section.Code(
                code=(Op.PUSH0 + Op.RETF),
                code_outputs=2,
                max_stack_height=2,
            ),
        ],
        validity_error=EOFException.STACK_UNDERFLOW,
    ),
    Container(
        name="overflow_code_sections_1",
        sections=[
            Section.Code(
                code=(Op.CALLF[1] + Op.STOP),
            )
        ]
        + [
            Section.Code(
                code=(Op.CALLF[i + 2] + Op.RETF),
                code_outputs=0,
            )
            for i in range(MAX_CODE_SECTIONS)
        ]
        + [
            Section.Code(
                code=Op.RETF,
                code_outputs=0,
            )
        ],
        validity_error=EOFException.TOO_MANY_CODE_SECTIONS,
    ),
]


def container_name(c: Container):
    """Return the name of the container for use in pytest ids."""
    if hasattr(c, "name"):
        return c.name
    else:
        return c.__class__.__name__


@pytest.mark.parametrize(
    "container",
    [*VALID, *INVALID],
    ids=container_name,
)
def test_eof_validity(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test EOF container validation for features around EIP-4750 / Functions / Code Sections."""
    eof_test(container=container)


@pytest.mark.parametrize(
    "container",
    [
        Container(
            name="imm0",
            sections=[
                Section.Code(
                    code=Op.CALLF,
                )
            ],
        ),
        Container(
            name="imm1",
            sections=[
                Section.Code(
                    code=Op.CALLF + b"\x00",
                )
            ],
        ),
        Container(
            name="imm_from_next_section",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.PUSH0 + Op.CALLF[1] + Op.STOP,
                ),
                Section.Code(
                    code=Op.CALLF + b"\x00",  # would be valid with "02" + Op.RETF.
                    code_inputs=2,
                    code_outputs=1,
                    max_stack_height=2,
                ),
                Section.Code(
                    code=Op.SUB + Op.RETF,  # SUB (0x02) can be confused with CALLF[2].
                    code_inputs=2,
                    code_outputs=1,
                    max_stack_height=2,
                ),
            ],
        ),
    ],
    ids=container_name,
)
def test_callf_truncated_immediate(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test cases for CALLF instructions with truncated immediate bytes."""
    eof_test(container=container, expect_exception=EOFException.TRUNCATED_INSTRUCTION)


@pytest.mark.parametrize(
    "container",
    [
        Container(
            name="callf1",  # EOF1I4750_0010
            sections=[
                Section.Code(
                    Op.CALLF[1] + Op.STOP,
                )
            ],
        ),
        Container(
            name="callf2",  # EOF1I0011
            sections=[
                Section.Code(
                    Op.CALLF[2] + Op.STOP,
                ),
                Section.Code(
                    Op.RETF,
                    code_outputs=0,
                ),
            ],
        ),
        Container(
            name="callf1_callf2",
            sections=[
                Section.Code(
                    Op.CALLF[1] + Op.STOP,
                ),
                Section.Code(
                    Op.CALLF[2] + Op.RETF,
                    code_outputs=0,
                ),
            ],
        ),
    ],
    ids=container_name,
)
def test_invalid_code_section_index(
    eof_test: EOFTestFiller,
    container: Container,
):
    """Test cases for CALLF instructions with invalid target code section index."""
    eof_test(container=container, expect_exception=EOFException.INVALID_CODE_SECTION_INDEX)


@pytest.mark.parametrize(
    "container",
    [
        Container(
            name="unreachable1",
            sections=[
                Section.Code(Op.INVALID),
                Section.Code(Op.INVALID),  # unreachable
            ],
        ),
        Container(
            name="unreachable1_selfjumpf",
            sections=[
                Section.Code(Op.INVALID),
                Section.Code(Op.JUMPF[1]),  # unreachable
            ],
        ),
        Container(
            name="unreachable1_selfcallf",
            sections=[
                Section.Code(Op.INVALID),
                Section.Code(Op.CALLF[1] + Op.STOP),  # unreachable
            ],
        ),
        Container(
            name="unreachable1_jumpf0",
            sections=[
                Section.Code(Op.INVALID),
                Section.Code(Op.JUMPF[0]),  # unreachable
            ],
        ),
        Container(
            name="unreachable1_callf0",
            sections=[
                Section.Code(Op.INVALID),
                Section.Code(Op.CALLF[0] + Op.STOP),  # unreachable
            ],
        ),
        Container(
            name="unreachable1_selfcall_jumpf0",
            sections=[
                Section.Code(Op.INVALID),
                Section.Code(Op.CALLF[1] + Op.JUMPF[0]),  # unreachable
            ],
        ),
        Container(
            name="unreachable12_of3_2jumpf1",
            sections=[
                Section.Code(Op.INVALID),
                Section.Code(Op.STOP),  # unreachable
                Section.Code(Op.JUMPF[1]),  # unreachable
            ],
        ),
        Container(
            name="unreachable12_of3_2callf1",
            sections=[
                Section.Code(Op.INVALID),
                Section.Code(Op.STOP),  # unreachable
                Section.Code(Op.CALLF[1] + Op.STOP),  # unreachable
            ],
        ),
        Container(
            name="unreachable12_of3_jumpf_loop",
            sections=[
                Section.Code(Op.INVALID),
                Section.Code(Op.JUMPF[2]),  # unreachable
                Section.Code(Op.JUMPF[1]),  # unreachable
            ],
        ),
        Container(
            name="unreachable12_of3_callf_loop_stop",
            sections=[
                Section.Code(Op.INVALID),
                Section.Code(Op.CALLF[2] + Op.STOP),  # unreachable
                Section.Code(Op.CALLF[1] + Op.STOP),  # unreachable
            ],
        ),
        Container(
            name="unreachable12_of3_callf_loop_retf",
            sections=[
                Section.Code(Op.INVALID),
                Section.Code(Op.CALLF[2] + Op.RETF, code_outputs=0),  # unreachable
                Section.Code(Op.CALLF[1] + Op.RETF, code_outputs=0),  # unreachable
            ],
        ),
        Container(
            name="unreachable12_of3_callf_loop_mixed",
            sections=[
                Section.Code(Op.INVALID),
                Section.Code(Op.CALLF[2] + Op.STOP),  # unreachable
                Section.Code(Op.CALLF[1] + Op.RETF, code_outputs=0),  # unreachable
            ],
        ),
        Container(
            name="selfjumpf0_unreachable1",
            sections=[
                Section.Code(Op.JUMPF[0]),  # self-reference
                Section.Code(Op.JUMPF[1]),  # unreachable
            ],
        ),
        Container(
            name="unreachable2_of3",
            sections=[
                Section.Code(Op.CALLF[1] + Op.STOP),
                Section.Code(Op.RETF, code_outputs=0),
                Section.Code(Op.INVALID),  # unreachable
            ],
        ),
        Container(
            name="unreachable1_of3",
            sections=[
                Section.Code(Op.CALLF[2] + Op.STOP),
                Section.Code(Op.INVALID),  # unreachable
                Section.Code(Op.RETF, code_outputs=0),
            ],
        ),
        Container(
            name="unreachable1_of4",
            sections=[
                Section.Code(Op.CALLF[3] + Op.STOP),
                Section.Code(Op.INVALID),  # unreachable
                Section.Code(Op.RETF, code_outputs=0),
                Section.Code(Op.CALLF[2] + Op.RETF, code_outputs=0),
            ],
        ),
        Container(
            name="unreachable2_of3_retf",
            sections=[
                Section.Code(Op.JUMPF[1]),
                Section.Code(Op.STOP),
                Section.Code(Op.RETF, code_outputs=0),
            ],
        ),
        Container(
            name="unreachable2-255",
            sections=[
                Section.Code(Op.JUMPF[1]),
                Section.Code(Op.JUMPF[1]),  # self-reference
            ]
            + [Section.Code(Op.JUMPF[i]) for i in range(3, 255)]  # unreachable
            + [Section.Code(Op.STOP)],  # unreachable
        ),
        Container(
            name="unreachable255",
            sections=[Section.Code(Op.JUMPF[i]) for i in range(1, 255)]
            + [
                Section.Code(Op.JUMPF[254]),  # self-reference
                Section.Code(Op.STOP),  # unreachable
            ],
        ),
    ],
    ids=container_name,
)
def test_unreachable_code_sections(
    eof_test: EOFTestFiller,
    container: Container,
):
    """
    Test cases for EOF unreachable code sections
    (i.e. code sections not reachable from the code section 0).
    """
    eof_test(container=container, expect_exception=EOFException.UNREACHABLE_CODE_SECTIONS)


@pytest.mark.parametrize("callee_outputs", [1, 2, MAX_CODE_OUTPUTS])
def test_callf_stack_height_limit_exceeded(eof_test, callee_outputs):
    """
    Test for invalid EOF code containing CALLF instruction exceeding the stack height limit.
    The code reaches the maximum runtime stack height (1024)
    which is above the EOF limit for the stack height in the type section (1023).
    """
    callf_stack_height = MAX_RUNTIME_STACK_HEIGHT - callee_outputs
    container = Container(
        sections=[
            Section.Code(
                Op.PUSH0 * callf_stack_height + Op.CALLF[1] + Op.STOP,
                max_stack_height=MAX_RUNTIME_STACK_HEIGHT,
            ),
            Section.Code(
                Op.PUSH0 * callee_outputs + Op.RETF,
                code_outputs=callee_outputs,
                max_stack_height=callee_outputs,
            ),
        ],
    )
    eof_test(container=container, expect_exception=EOFException.MAX_STACK_INCREASE_ABOVE_LIMIT)


@pytest.mark.parametrize("stack_height", [512, 513, 1023])
def test_callf_stack_overflow(eof_test: EOFTestFiller, stack_height: int):
    """Test CALLF instruction recursively calling itself causing stack overflow."""
    container = Container(
        sections=[
            Section.Code(code=Op.CALLF[1] + Op.STOP),
            Section.Code(
                code=Op.PUSH1[1] * stack_height + Op.CALLF[1] + Op.POP * stack_height + Op.RETF,
                code_outputs=0,
                max_stack_height=stack_height,
            ),
        ],
    )
    stack_overflow = stack_height > MAX_RUNTIME_STACK_HEIGHT // 2
    eof_test(
        container=container,
        expect_exception=EOFException.STACK_OVERFLOW if stack_overflow else None,
    )


@pytest.mark.parametrize("stack_height", [1, 2])
def test_callf_stack_overflow_after_callf(eof_test: EOFTestFiller, stack_height: int):
    """Test CALLF instruction calling next function causing stack overflow at validation time."""
    container = Container(
        sections=[
            Section.Code(code=Op.CALLF[1] + Op.STOP),
            Section.Code(
                code=Op.PUSH1[1] * 1023 + Op.CALLF[2] + Op.POP * 1023 + Op.RETF,
                code_outputs=0,
                max_stack_height=1023,
            ),
            Section.Code(
                code=Op.PUSH0 * stack_height + Op.POP * stack_height + Op.RETF,
                code_outputs=0,
                max_stack_height=stack_height,
            ),
        ],
    )
    stack_overflow = 1023 + stack_height > MAX_RUNTIME_STACK_HEIGHT
    eof_test(
        container=container,
        expect_exception=EOFException.STACK_OVERFLOW if stack_overflow else None,
    )


@pytest.mark.parametrize("stack_height", [512, 514, 515])
def test_callf_stack_overflow_variable_stack(eof_test: EOFTestFiller, stack_height: int):
    """Test CALLF instruction causing stack overflow."""
    container = Container(
        sections=[
            Section.Code(
                code=Op.RJUMPI[2](0)
                + Op.PUSH0 * (MAX_RUNTIME_STACK_HEIGHT // 2)
                + Op.CALLF[1]
                + Op.STOP,
                max_stack_height=512,
            ),
            Section.Code(
                code=Op.PUSH1[1] * stack_height + Op.POP * stack_height + Op.RETF,
                code_outputs=0,
                max_stack_height=stack_height,
            ),
        ],
    )
    stack_overflow = stack_height > MAX_RUNTIME_STACK_HEIGHT // 2
    eof_test(
        container=container,
        expect_exception=EOFException.STACK_OVERFLOW if stack_overflow else None,
    )


@pytest.mark.parametrize("stack_height", [509, 510, 512])
def test_callf_stack_overflow_variable_stack_2(eof_test: EOFTestFiller, stack_height: int):
    """Test CALLF instruction causing stack overflow."""
    container = Container(
        sections=[
            Section.Code(
                code=Op.PUSH0 * 2
                + Op.RJUMPI[2](0)
                + Op.POP * 2
                + Op.PUSH0 * (MAX_RUNTIME_STACK_HEIGHT // 2)
                + Op.CALLF[1]
                + Op.STOP,
                max_stack_height=514,
            ),
            Section.Code(
                code=Op.PUSH1[1] * stack_height + Op.POP * stack_height + Op.RETF,
                code_outputs=0,
                max_stack_height=stack_height,
            ),
        ],
    )
    stack_overflow = stack_height > (MAX_RUNTIME_STACK_HEIGHT // 2) - 2
    eof_test(
        container=container,
        expect_exception=EOFException.STACK_OVERFLOW if stack_overflow else None,
    )


@pytest.mark.parametrize("stack_height", [1, 2, 5])
def test_callf_stack_overflow_variable_stack_3(eof_test: EOFTestFiller, stack_height: int):
    """Test CALLF instruction causing stack overflow."""
    container = Container(
        sections=[
            Section.Code(
                code=Op.RJUMPI[2](0)
                + Op.PUSH0 * (MAX_RUNTIME_STACK_HEIGHT - 1)
                + Op.CALLF[1]
                + Op.STOP,
                max_stack_height=1023,
            ),
            Section.Code(
                code=Op.PUSH0 * stack_height + Op.POP * stack_height + Op.RETF,
                code_outputs=0,
                max_stack_height=stack_height,
            ),
        ],
    )
    assert container.sections[0].max_stack_height is not None
    stack_overflow = (
        container.sections[0].max_stack_height + stack_height > MAX_RUNTIME_STACK_HEIGHT
    )
    eof_test(
        container=container,
        expect_exception=EOFException.STACK_OVERFLOW if stack_overflow else None,
    )


def test_callf_stack_overflow_variable_stack_4(eof_test: EOFTestFiller):
    """Test reaching stack overflow before CALLF instruction."""
    container = Container(
        sections=[
            Section.Code(
                code=Op.PUSH0 * 2
                + Op.RJUMPI[2](0)
                + Op.POP * 2
                + Op.PUSH0 * (MAX_RUNTIME_STACK_HEIGHT - 1)
                + Op.CALLF[1]
                + Op.STOP,
                max_stack_height=1023,
            ),
            Section.Code(
                code=Op.RETF,
                code_outputs=0,
                max_stack_height=0,
            ),
        ],
    )
    eof_test(
        container=container,
        expect_exception=EOFException.STACK_OVERFLOW,
    )


@pytest.mark.parametrize("stack_height", [2, 3])
def test_callf_validate_outputs(eof_test: EOFTestFiller, stack_height: int):
    """Test CALLF instruction when calling a function returning more outputs than expected."""
    container = Container(
        sections=[
            Section.Code(code=Op.CALLF[1] + Op.STOP, max_stack_height=1),
            Section.Code(
                code=Op.PUSH0 * stack_height + Op.CALLF[2] + Op.RETF,
                code_outputs=1,
                max_stack_height=stack_height,
            ),
            Section.Code(
                code=Op.POP + Op.RETF,
                code_inputs=2,
                code_outputs=1,
                max_stack_height=2,
            ),
        ],
    )
    # Only 1 item consumed by function 2, if stack height > 2
    # there will be more than 1 item as outputs in function 1
    outputs_error = stack_height > 2
    eof_test(
        container=container,
        expect_exception=EOFException.STACK_HIGHER_THAN_OUTPUTS if outputs_error else None,
    )


@pytest.mark.parametrize("push_stack", [1023, 1024])
@pytest.mark.parametrize("pop_stack", [1019, 1020, 1021])
@pytest.mark.parametrize(
    "code_section",
    [
        pytest.param(
            Section.Code(
                code=Op.POP * 2 + Op.RETF,
                code_inputs=2,
                code_outputs=0,
                max_stack_height=2,
            ),
            id="pop2",
        ),
        pytest.param(
            Section.Code(
                code=Op.PUSH1[1] + Op.POP + Op.RETF,
                code_inputs=3,
                code_outputs=3,
                max_stack_height=4,
            ),
            id="push_pop",
        ),
        pytest.param(
            Section.Code(
                code=Op.PUSH0 * 2 + Op.RETF,
                code_inputs=3,
                code_outputs=5,
                max_stack_height=5,
            ),
            id="push2",
        ),
        pytest.param(
            Section.Code(
                code=Op.PUSH0 * 2 + Op.POP * 2 + Op.RETF,
                code_inputs=3,
                code_outputs=3,
                max_stack_height=5,
            ),
            id="push2_pop2",
        ),
        pytest.param(
            Section.Code(
                code=Op.PUSH0 + Op.POP * 3 + Op.RETF,
                code_inputs=2,
                code_outputs=0,
                max_stack_height=3,
            ),
            id="push_pop3",
        ),
        pytest.param(
            Section.Code(
                code=Op.PUSH0 * 2 + Op.POP * 4 + Op.RETF,
                code_inputs=2,
                code_outputs=0,
                max_stack_height=4,
            ),
            id="push2_pop4",
        ),
    ],
)
def test_callf_with_inputs_stack_overflow(
    eof_test: EOFTestFiller, code_section: Section, push_stack: int, pop_stack: int
):
    """Test CALLF to code section with inputs."""
    container = Container(
        name="callf_with_inputs_stack_overflow_0",
        sections=[
            Section.Code(
                code=Op.PUSH1[1] * push_stack + Op.CALLF[1] + Op.POP * pop_stack + Op.RETURN,
                max_stack_height=1023,
            ),
            code_section,
        ],
    )
    assert code_section.max_stack_height is not None
    exception = None
    if (
        push_stack + code_section.max_stack_height - code_section.code_inputs
        > MAX_RUNTIME_STACK_HEIGHT
    ):
        exception = EOFException.STACK_OVERFLOW
    elif push_stack - code_section.code_inputs + code_section.code_outputs - pop_stack < 2:
        exception = EOFException.STACK_UNDERFLOW
    elif push_stack != container.sections[0].max_stack_height:
        exception = EOFException.INVALID_MAX_STACK_INCREASE

    eof_test(container=container, expect_exception=exception)


@pytest.mark.parametrize(
    "code_section",
    [
        pytest.param(
            Section.Code(
                code=Op.POP * 2 + Op.RETF,
                code_inputs=2,
                code_outputs=0,
                max_stack_height=2,
            ),
            id="pop2",
        ),
        pytest.param(
            Section.Code(
                code=Op.PUSH1[1] + Op.POP + Op.RETF,
                code_inputs=3,
                code_outputs=3,
                max_stack_height=4,
            ),
            id="push_pop",
        ),
        pytest.param(
            Section.Code(
                code=Op.PUSH0 * 4 + Op.RETF,
                code_inputs=3,
                code_outputs=7,
                max_stack_height=7,
            ),
            id="push4",
        ),
        pytest.param(
            Section.Code(
                code=Op.PUSH0 * 2 + Op.RETF,
                code_inputs=3,
                code_outputs=5,
                max_stack_height=5,
            ),
            id="push2",
        ),
        pytest.param(
            Section.Code(
                code=Op.PUSH0 * 4 + Op.POP * 2 + Op.RETF,
                code_inputs=3,
                code_outputs=3,
                max_stack_height=7,
            ),
            id="push4_pop2",
        ),
        pytest.param(
            Section.Code(
                code=Op.PUSH0 * 2 + Op.POP * 2 + Op.RETF,
                code_inputs=3,
                code_outputs=3,
                max_stack_height=5,
            ),
            id="push2_pop2",
        ),
        pytest.param(
            Section.Code(
                code=Op.PUSH0 * 3 + Op.POP * 5 + Op.RETF,
                code_inputs=2,
                code_outputs=0,
                max_stack_height=5,
            ),
            id="push3_pop5",
        ),
        pytest.param(
            Section.Code(
                code=Op.PUSH0 + Op.POP * 3 + Op.RETF,
                code_inputs=2,
                code_outputs=0,
                max_stack_height=3,
            ),
            id="push_pop3",
        ),
        pytest.param(
            Section.Code(
                code=Op.PUSH0 * 4 + Op.POP * 6 + Op.RETF,
                code_inputs=2,
                code_outputs=0,
                max_stack_height=6,
            ),
            id="push4_pop6",
        ),
        pytest.param(
            Section.Code(
                code=Op.PUSH0 * 2 + Op.POP * 4 + Op.RETF,
                code_inputs=2,
                code_outputs=0,
                max_stack_height=4,
            ),
            id="push2_pop4",
        ),
    ],
)
@pytest.mark.parametrize("push_stack", [1020, 1021])
def test_callf_with_inputs_stack_overflow_variable_stack(
    eof_test: EOFTestFiller, code_section: Section, push_stack: int
):
    """Test CALLF to code section with inputs (variable stack)."""
    container = Container(
        sections=[
            Section.Code(
                code=Op.PUSH0
                + Op.PUSH1[0]
                + Op.RJUMPI[2]
                + Op.PUSH0 * 2
                + Op.PUSH1[1] * push_stack
                + Op.CALLF[1]
                + Op.STOP,
                max_stack_height=1023,
            ),
            code_section,
        ],
    )
    initial_stack = 3  # Initial items in the scak
    assert code_section.max_stack_height is not None
    exception = None
    if (
        push_stack + initial_stack + code_section.max_stack_height - code_section.code_inputs
        > MAX_RUNTIME_STACK_HEIGHT
    ):
        exception = EOFException.STACK_OVERFLOW
    elif push_stack + initial_stack > 1023:
        exception = EOFException.INVALID_MAX_STACK_INCREASE

    eof_test(container=container, expect_exception=exception)


@pytest.mark.parametrize("callee_outputs", [1, 2, MAX_CODE_OUTPUTS - 1, MAX_CODE_OUTPUTS])
@pytest.mark.parametrize(
    "max_stack_height", [0, 1, MAX_STACK_INCREASE_LIMIT - 1, MAX_STACK_INCREASE_LIMIT]
)
def test_callf_stack_overflow_by_outputs(eof_test, callee_outputs, max_stack_height):
    """
    Test for invalid EOF code containing CALLF instruction exceeding the runtime stack height limit
    by calling a function with at least one output. The computed stack height of the code section 0
    is always above the maximum allowed in the EOF type section. Therefore, the test declares
    an invalid max_stack_height.
    """
    callf_stack_height = (MAX_RUNTIME_STACK_HEIGHT + 1) - callee_outputs
    container = Container(
        sections=[
            Section.Code(
                Op.PUSH0 * callf_stack_height + Op.CALLF[1] + Op.STOP,
                max_stack_height=max_stack_height,
            ),
            Section.Code(
                Op.PUSH0 + Op.DUP1 + Op.RETF,
                code_outputs=callee_outputs,
                max_stack_height=callee_outputs,
            ),
        ],
    )
    eof_test(container=container, expect_exception=EOFException.STACK_OVERFLOW)


@pytest.mark.parametrize(
    "callee_stack_height",
    [2, 3, MAX_STACK_INCREASE_LIMIT - 1, MAX_STACK_INCREASE_LIMIT],
)
def test_callf_stack_overflow_by_height(eof_test, callee_stack_height):
    """
    Test for invalid EOF code containing CALLF instruction exceeding the runtime stack height limit
    by calling a function with 2+ maximum stack height.
    The callee with the maximum stack height of 1 is valid because runtime limit (1024)
    is 1 bigger than the EOF limit (1023).
    """
    container = Container(
        sections=[
            Section.Code(
                Op.PUSH0 * MAX_STACK_INCREASE_LIMIT + Op.CALLF[1] + Op.STOP,
                max_stack_height=MAX_STACK_INCREASE_LIMIT,
            ),
            Section.Code(
                Op.PUSH0 * callee_stack_height + Op.POP * callee_stack_height + Op.RETF,
                code_outputs=0,
                max_stack_height=callee_stack_height,
            ),
        ],
    )
    eof_test(container=container, expect_exception=EOFException.STACK_OVERFLOW)


@pytest.mark.parametrize(
    "container",
    [
        Container(
            name="underflow_1",
            sections=[
                Section.Code(
                    code=Op.CALLF[1] + Op.STOP,
                    max_stack_height=1,
                ),
                Section.Code(
                    code=Op.PUSH0 + Op.RETF,
                    code_inputs=1,
                    code_outputs=2,
                    max_stack_height=2,
                ),
            ],
        ),
        Container(
            name="underflow_2",
            sections=[
                Section.Code(
                    code=Op.CALLF[1] + Op.STOP,
                    max_stack_height=2,
                ),
                Section.Code(
                    code=Op.PUSH0 + Op.RETF,
                    code_inputs=1,
                    code_outputs=2,
                    max_stack_height=2,
                ),
            ],
        ),
        Container(
            name="underflow_variable_stack_2",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.RJUMPI[2](0) + Op.PUSH0 + Op.PUSH0 + Op.CALLF[1] + Op.STOP,
                    max_stack_height=4,
                ),
                Section.Code(
                    code=Op.PUSH0 + Op.RETF,
                    code_inputs=4,
                    code_outputs=5,
                    max_stack_height=5,
                ),
            ],
        ),
        Container(
            name="underflow_variable_stack_2a",
            sections=[
                Section.Code(
                    code=Op.PUSH0
                    + Op.PUSH0
                    + Op.RJUMPI[2](0)
                    + Op.PUSH0
                    + Op.PUSH0
                    + Op.CALLF[1]
                    + Op.STOP,
                    max_stack_height=5,
                ),
                Section.Code(
                    code=Op.PUSH0 + Op.RETF,
                    code_inputs=4,
                    code_outputs=5,
                    max_stack_height=5,
                ),
            ],
        ),
        Container(
            name="underflow_variable_stack_3",
            sections=[
                Section.Code(
                    code=Op.PUSH0 + Op.RJUMPI[2](0) + Op.PUSH0 + Op.PUSH0 + Op.CALLF[1] + Op.STOP,
                    max_stack_height=4,
                ),
                Section.Code(
                    code=Op.PUSH0 + Op.RETF,
                    code_inputs=3,
                    code_outputs=4,
                    max_stack_height=4,
                ),
            ],
        ),
        Container(
            name="underflow_variable_stack_4",
            sections=[
                Section.Code(
                    code=Op.PUSH0 * 3 + Op.RJUMPI[1](0) + Op.POP + Op.CALLF[1] + Op.STOP,
                    max_stack_height=4,
                ),
                Section.Code(
                    code=Op.PUSH0 + Op.RETF,
                    code_inputs=3,
                    code_outputs=4,
                    max_stack_height=4,
                ),
            ],
        ),
    ],
    ids=lambda x: x.name,
)
def test_callf_stack_underflow_examples(eof_test, container):
    """Test CALLF instruction causing validation time stack underflow."""
    eof_test(container=container, expect_exception=EOFException.STACK_UNDERFLOW)


def test_returning_section_aborts(
    eof_test: EOFTestFiller,
):
    """
    Test EOF container validation where in the same code section we have returning
    and nonreturning terminating instructions.
    """
    container = Container(
        name="returning_section_aborts",
        sections=[
            Section.Code(code=Op.PUSH0 + Op.CALLF[1] + Op.POP + Op.POP + Op.STOP),
            Section.Code(
                code=Op.PUSH0 * 2 + Op.RJUMPI[1] + Op.RETF + Op.INVALID,
                code_outputs=1,
            ),
        ],
    )
    eof_test(container=container)
