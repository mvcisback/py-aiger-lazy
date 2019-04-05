from enum import Enum
from typing import Mapping, Tuple, FrozenSet, Union
from functools import partial

import aiger
import attr


@attr.s(frozen=True, slots=True, auto_attribs=True)
class SeqComp:
    left: "AIG"
    right: "AIG"


@attr.s(frozen=True, slots=True, auto_attribs=True)
class ParComp:
    left: "AIG"
    right: "AIG"


@attr.s(frozen=True, slots=True, auto_attribs=True)
class Wire:
    input: str
    output: str
    latch: Union[str, None] = None
    initial: bool = False
    keep_output: bool = True


@attr.s(frozen=True, slots=True, auto_attribs=True)
class Feedback:
    data: "AIG"
    wires: Tuple[Wire]


@attr.s(frozen=True, auto_attribs=True, repr=False)
class LazyAIG:
    data: Union[ParComp, SeqComp, Feedback, aiger.AIG]
    inputs: FrozenSet[str] = frozenset()
    outputs: FrozenSet[str] = frozenset()
    latches: FrozenSet[str]  = frozenset()

    def __repr__(self):
        return repr(self.flatten())

    def __call__(self, inputs, latches=None):
        raise NotImplementedError

    def __getattr__(self, attr):
        return partial(getattr(aiger.AIG, attr), self=self)

    def __rshift__(self, other):
        # TODO: implement unit propogation.
        interface = self.outputs & other.inputs
        assert not (self.outputs - interface) & other.outputs
        assert not self.latches & other.latches
        return LazyAIG(
            data=SeqComp(left=self, right=other),
            inputs=self.inputs | (other.inputs - interface),
            outputs=(self.outputs - interface) | other.outputs,
            latches=self.latches | other.latches
        )

    def __or__(self, other):
        assert not aig1.outputs & aig2.outputs
        assert not aig1.latches & aig2.latches
        return LazyAIG(
            data=ParComp(left=self, right=other),
            inputs=self.inputs | other.inputs,
            outputs=self.outputs | other.outputs,
            latches=self.latches | other.latches
        )

    @property
    def aig(self):
        return self

    def flatten(self):
        # TODO: implement non-naive flattening
        data = self.data
        if isinstance(data, ParComp):
            return data.left.flatten() | data.right.flatten()

        elif isinstance(data, Feedback):
            # TODO: update after aiger feedback api update.

            return data.flatten().feedback(
                inputs=[x.input for x in data.wires],
                outputs=[x.output for x in data.wires],
                initials=[x.initial for x in data.wires],
                latches=[x.latch for x in data.wires],
                keep_output=data.wires[0].keep_output
            )

        elif isinstance(data, SeqComp):
            return data.left.flatten() >> data.right.flatten()

        else:
            return self.data


def lazify(circ):
    return LazyAIG(
        data=circ, 
        inputs=circ.inputs,
        outputs=circ.outputs,
        latches=circ.latches
    )
