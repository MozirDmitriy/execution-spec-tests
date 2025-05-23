"""
abstract: Tests [EIP-1153: Transient Storage Opcodes](https://eips.ethereum.org/EIPS/eip-1153)
    Test [EIP-1153: Transient Storage Opcodes](https://eips.ethereum.org/EIPS/eip-1153). Ports
    and extends some tests from
    [ethereum/tests/src/EIPTestsFiller/StateTests/stEIP1153-transientStorage/](https://github.com/ethereum/tests/blob/9b00b68593f5869eb51a6659e1cc983e875e616b/src/EIPTestsFiller/StateTests/stEIP1153-transientStorage).
"""  # noqa: E501

from enum import unique

import pytest

from ethereum_test_tools import (
    Account,
    Alloc,
    Bytecode,
    CodeGasMeasure,
    Environment,
    StateTestFiller,
    Transaction,
)
from ethereum_test_tools import Opcodes as Op

from . import PytestParameterEnum
from .spec import Spec, ref_spec_1153

REFERENCE_SPEC_GIT_PATH = ref_spec_1153.git_path
REFERENCE_SPEC_VERSION = ref_spec_1153.version

pytestmark = [pytest.mark.valid_from("Cancun")]

code_address = 0x100


def test_transient_storage_unset_values(state_test: StateTestFiller, pre: Alloc):
    """
    Test that tload returns zero for unset values. Loading an arbitrary value is
    0 at beginning of transaction: TLOAD(x) is 0.

    Based on [ethereum/tests/.../01_tloadBeginningTxnFiller.yml](https://github.com/ethereum/tests/blob/9b00b68593f5869eb51a6659e1cc983e875e616b/src/EIPTestsFiller/StateTests/stEIP1153-transientStorage/01_tloadBeginningTxnFiller.yml)",
    """  # noqa: E501
    env = Environment()

    slots_under_test = [0, 1, 2, 2**128, 2**256 - 1]
    code = sum(Op.SSTORE(slot, Op.TLOAD(slot)) for slot in slots_under_test)

    code_address = pre.deploy_contract(
        code=code,  # type: ignore
        storage={slot: 1 for slot in slots_under_test},
    )

    tx = Transaction(
        sender=pre.fund_eoa(),
        to=code_address,
        gas_limit=1_000_000,
    )

    post = {code_address: Account(storage={slot: 0 for slot in slots_under_test})}

    state_test(
        env=env,
        pre=pre,
        post=post,
        tx=tx,
    )


def test_tload_after_tstore(state_test: StateTestFiller, pre: Alloc):
    """
    Loading after storing returns the stored value: TSTORE(x, y), TLOAD(x)
    returns y.

    Based on [ethereum/tests/.../02_tloadAfterTstoreFiller.yml](https://github.com/ethereum/tests/blob/9b00b68593f5869eb51a6659e1cc983e875e616b/src/EIPTestsFiller/StateTests/stEIP1153-transientStorage/02_tloadAfterTstoreFiller.yml)",
    """  # noqa: E501
    env = Environment()

    slots_under_test = [0, 1, 2, 2**128, 2**256 - 1]
    code = sum(
        Op.TSTORE(slot, slot) + Op.SSTORE(slot, Op.TLOAD(slot)) for slot in slots_under_test
    )
    code_address = pre.deploy_contract(
        code=code,  # type: ignore
        storage={slot: 0xFF for slot in slots_under_test},
    )

    tx = Transaction(
        sender=pre.fund_eoa(),
        to=code_address,
        gas_limit=1_000_000,
    )

    post = {code_address: Account(storage={slot: slot for slot in slots_under_test})}

    state_test(
        env=env,
        pre=pre,
        post=post,
        tx=tx,
    )


def test_tload_after_sstore(state_test: StateTestFiller, pre: Alloc):
    """
    Loading after storing returns the stored value: TSTORE(x, y), TLOAD(x)
    returns y.

    Based on [ethereum/tests/.../18_tloadAfterStoreFiller.yml](https://github.com/ethereum/tests/blob/9b00b68593f5869eb51a6659e1cc983e875e616b/src/EIPTestsFiller/StateTests/stEIP1153-transientStorage/18_tloadAfterStoreFiller.yml)",
    """  # noqa: E501
    env = Environment()

    slots_under_test = [1, 3, 2**128, 2**256 - 1]
    code = sum(
        Op.SSTORE(slot - 1, 0xFF) + Op.SSTORE(slot, Op.TLOAD(slot - 1))
        for slot in slots_under_test
    )
    code_address = pre.deploy_contract(
        code=code,  # type: ignore
        storage={slot: 1 for slot in slots_under_test},
    )

    tx = Transaction(
        sender=pre.fund_eoa(),
        to=code_address,
        gas_limit=1_000_000,
    )

    post = {
        code_address: Account(
            code=code,
            storage={slot - 1: 0xFF for slot in slots_under_test}
            | {slot: 0 for slot in slots_under_test},
        )
    }

    state_test(
        env=env,
        pre=pre,
        post=post,
        tx=tx,
    )


def test_tload_after_tstore_is_zero(state_test: StateTestFiller, pre: Alloc):
    """
    Test that tload returns zero after tstore is called with zero.

    Based on [ethereum/tests/.../03_tloadAfterStoreIs0Filler.yml](https://github.com/ethereum/tests/blob/9b00b68593f5869eb51a6659e1cc983e875e616b/src/EIPTestsFiller/StateTests/stEIP1153-transientStorage/03_tloadAfterStoreIs0Filler.yml)",
    """  # noqa: E501
    env = Environment()

    slots_to_write = [1, 4, 2**128, 2**256 - 2]
    slots_to_read = [slot - 1 for slot in slots_to_write] + [slot + 1 for slot in slots_to_write]
    assert set.intersection(set(slots_to_write), set(slots_to_read)) == set()

    code = sum(Op.TSTORE(slot, 1234) for slot in slots_to_write) + sum(
        Op.SSTORE(slot, Op.TLOAD(slot)) for slot in slots_to_read
    )

    code_address = pre.deploy_contract(
        code=code,  # type: ignore
        storage={slot: 0xFFFF for slot in slots_to_write + slots_to_read},
    )

    tx = Transaction(
        sender=pre.fund_eoa(),
        to=code_address,
        gas_limit=1_000_000,
    )

    post = {
        code_address: Account(
            storage={slot: 0 for slot in slots_to_read} | {slot: 0xFFFF for slot in slots_to_write}
        )
    }

    state_test(
        env=env,
        pre=pre,
        post=post,
        tx=tx,
    )


@unique
class GasMeasureTestCases(PytestParameterEnum):
    """Test cases for gas measurement."""

    TLOAD = {
        "description": "Test that tload() of an empty slot consumes the expected gas.",
        "bytecode": Op.TLOAD(10),
        "overhead_cost": 3,  # 1 x PUSH1
        "extra_stack_items": 1,
        "expected_gas": Spec.TLOAD_GAS_COST,
    }
    TSTORE_TLOAD = {
        "description": "Test that tload() of a used slot consumes the expected gas.",
        "bytecode": Op.TSTORE(10, 10) + Op.TLOAD(10),
        "overhead_cost": 3 * 3,  # 3 x PUSH1
        "extra_stack_items": 1,
        "expected_gas": Spec.TSTORE_GAS_COST + Spec.TLOAD_GAS_COST,
    }
    TSTORE_COLD = {
        "description": "Test that tstore() of a previously unused slot consumes the expected gas.",
        "bytecode": Op.TSTORE(10, 10),
        "overhead_cost": 2 * 3,  # 2 x PUSH1
        "extra_stack_items": 0,
        "expected_gas": Spec.TSTORE_GAS_COST,
    }
    TSTORE_WARM = {
        "description": "Test that tstore() of a previously used slot consumes the expected gas.",
        "bytecode": Op.TSTORE(10, 10) + Op.TSTORE(10, 11),
        "overhead_cost": 4 * 3,  # 4 x PUSH1
        "extra_stack_items": 0,
        "expected_gas": 2 * Spec.TSTORE_GAS_COST,
    }


@GasMeasureTestCases.parametrize()
def test_gas_usage(
    state_test: StateTestFiller,
    pre: Alloc,
    bytecode: Bytecode,
    expected_gas: int,
    overhead_cost: int,
    extra_stack_items: int,
):
    """Test that tstore and tload consume the expected gas."""
    gas_measure_bytecode = CodeGasMeasure(
        code=bytecode, overhead_cost=overhead_cost, extra_stack_items=extra_stack_items
    )

    env = Environment()
    code_address = pre.deploy_contract(code=gas_measure_bytecode)
    tx = Transaction(
        sender=pre.fund_eoa(),
        to=code_address,
        gas_limit=1_000_000,
    )
    post = {
        code_address: Account(code=gas_measure_bytecode, storage={0: expected_gas}),
    }
    state_test(env=env, pre=pre, tx=tx, post=post)


@unique
class LoopRunUntilOutOfGasCases(PytestParameterEnum):
    """Test cases to run until out of gas."""

    TSTORE = {
        "description": "Run tstore in loop until out of gas",
        "repeat_bytecode": Op.TSTORE(Op.GAS, Op.GAS),
        "bytecode_repeat_times": 1000,
    }
    TSTORE_WIDE_ADDRESS_SPACE = {
        "description": "Run tstore in loop until out of gas, using a wide address space",
        "repeat_bytecode": Op.TSTORE(Op.ADD(Op.SHL(Op.PC, 1), Op.GAS), Op.GAS),
        "bytecode_repeat_times": 32,
    }
    TSTORE_TLOAD = {
        "description": "Run tstore and tload in loop until out of gas",
        "repeat_bytecode": Op.GAS + Op.DUP1 + Op.DUP1 + Op.TSTORE + Op.TLOAD + Op.POP,
        "bytecode_repeat_times": 1000,
    }


@LoopRunUntilOutOfGasCases.parametrize()
@pytest.mark.slow()
def test_run_until_out_of_gas(
    state_test: StateTestFiller,
    pre: Alloc,
    repeat_bytecode: Bytecode,
    bytecode_repeat_times: int,
):
    """Use TSTORE over and over to different keys until we run out of gas."""
    env = Environment()

    bytecode = Op.JUMPDEST + repeat_bytecode * bytecode_repeat_times + Op.JUMP(Op.PUSH0)
    code_address = pre.deploy_contract(code=bytecode)
    tx = Transaction(
        sender=pre.fund_eoa(),
        to=code_address,
        gas_limit=env.gas_limit,
    )
    post = {
        code_address: Account(code=bytecode, storage={}),
    }
    state_test(env=env, pre=pre, tx=tx, post=post)
