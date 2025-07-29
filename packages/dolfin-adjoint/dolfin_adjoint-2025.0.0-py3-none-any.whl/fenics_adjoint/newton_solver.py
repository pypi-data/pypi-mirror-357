import dolfin
from pyadjoint.tape import annotate_tape, get_working_tape
from .blocks import SolveVarFormBlock


class NewtonSolver(dolfin.NewtonSolver):
    def solve(self, *args, **kwargs):
        ad_block_tag = kwargs.pop("ad_block_tag", None)
        annotate = annotate_tape(kwargs)

        if annotate:
            tape = get_working_tape()
            factory = args[0]
            vec = args[1]
            b = dolfin.as_backend_type(vec).__class__()

            factory.F(b=b, x=vec)

            F = b.form
            bcs = b.bcs

            u = vec.function

            sb_kwargs = SolveVarFormBlock.pop_kwargs(kwargs)
            block = SolveVarFormBlock(F == 0, u, bcs,
                                      solver_parameters={"newton_solver": self.parameters.copy()},
                                      ad_block_tag=ad_block_tag,
                                      **sb_kwargs)
            tape.add_block(block)

        newargs = [self] + list(args)
        out = dolfin.NewtonSolver.solve(*newargs, **kwargs)

        if annotate:
            block.add_output(u.create_block_variable())

        return out
