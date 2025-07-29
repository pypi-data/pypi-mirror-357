import dolfin
from pyadjoint.tape import get_working_tape, annotate_tape, stop_annotating
from pyadjoint.overloaded_type import OverloadedType, create_overloaded_object
from pyadjoint.enlisting import Enlist
from fenics_adjoint.blocks import FunctionAssignerBlock


__all__ = ["FunctionAssigner"]


class FunctionAssigner(dolfin.FunctionAssigner):

    def __init__(self, *args, **kwargs):
        super(FunctionAssigner, self).__init__(*args, **kwargs)
        self.input_spaces = Enlist(args[1])
        self.output_spaces = Enlist(args[0])
        self.adj_assigner = dolfin.FunctionAssigner(args[1],
                                                    args[0],
                                                    **kwargs)

    def assign(self, *args, **kwargs):
        annotate = annotate_tape(kwargs)
        outputs = Enlist(args[0])
        inputs = Enlist(args[1])

        if annotate:
            for i, o in enumerate(outputs):
                if not isinstance(o, OverloadedType):
                    outputs[i] = create_overloaded_object(o)

            for j, i in enumerate(outputs):
                if not isinstance(i, OverloadedType):
                    inputs[j] = create_overloaded_object(i)

            block = FunctionAssignerBlock(self, inputs)
            tape = get_working_tape()
            tape.add_block(block)

        with stop_annotating():
            ret = dolfin.FunctionAssigner.assign(self, outputs.delist(), inputs.delist(), **kwargs)

        if annotate:
            for output in outputs:
                block.add_output(output.block_variable)
        return ret
