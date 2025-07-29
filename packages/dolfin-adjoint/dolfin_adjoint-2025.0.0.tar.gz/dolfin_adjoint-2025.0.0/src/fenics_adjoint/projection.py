import dolfin
from pyadjoint.tape import get_working_tape, annotate_tape, stop_annotating
from pyadjoint.overloaded_type import create_overloaded_object
from .blocks import ProjectBlock


def project(*args, **kwargs):
    """The project call performs an equation solve, and so it too must be annotated so that the
    adjoint and tangent linear models may be constructed automatically by pyadjoint.

    To disable the annotation of this function, just pass :py:data:`annotate=False`. This is useful in
    cases where the solve is known to be irrelevant or diagnostic for the purposes of the adjoint
    computation (such as projecting fields to other function spaces for the purposes of
    visualisation)."""

    ad_block_tag = kwargs.pop("ad_block_tag", None)
    annotate = annotate_tape(kwargs)
    with stop_annotating():
        output = dolfin.project(*args, **kwargs)
    output = create_overloaded_object(output)

    if annotate:
        bcs = kwargs.pop("bcs", [])
        sb_kwargs = ProjectBlock.pop_kwargs(kwargs)
        sb_kwargs.update(kwargs)
        block = ProjectBlock(args[0], args[1], output, bcs,
                             ad_block_tag=ad_block_tag, **sb_kwargs)

        tape = get_working_tape()
        tape.add_block(block)

        block.add_output(output.block_variable)

    return output
