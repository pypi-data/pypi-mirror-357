import dolfin
from pyadjoint.tape import get_working_tape, stop_annotating, annotate_tape, no_annotations
from .blocks import LinearVariationalSolveBlock, NonlinearVariationalSolveBlock


class NonlinearVariationalProblem(dolfin.NonlinearVariationalProblem):
    """This object is overloaded so that solves using this class are automatically annotated,
    so that pyadjoint can automatically derive the adjoint and tangent linear models."""

    @no_annotations
    def __init__(self, F, u, bcs=None, J=None, *args, **kwargs):
        super(NonlinearVariationalProblem, self).__init__(F, u, bcs, J,
                                                          *args, **kwargs)
        self._ad_F = F
        self._ad_u = u
        self._ad_bcs = bcs
        self._ad_J = J
        self._ad_args = args
        self._ad_kwargs = kwargs


class NonlinearVariationalSolver(dolfin.NonlinearVariationalSolver):
    """This object is overloaded so that solves using this class are automatically annotated,
    so that pyadjoint can automatically derive the adjoint and tangent linear models."""

    @no_annotations
    def __init__(self, problem, *args, **kwargs):
        super(NonlinearVariationalSolver, self).__init__(problem, *args, **kwargs)
        self.ad_block_tag = kwargs.pop("ad_block_tag", None)
        self._ad_problem = problem
        self._ad_args = args
        self._ad_kwargs = kwargs

    def solve(self, *args, **kwargs):
        """To disable the annotation, just pass :py:data:`annotate=False` to this routine, and it acts exactly like the
        Dolfin solve call. This is useful in cases where the solve is known to be irrelevant or diagnostic
        for the purposes of the adjoint computation (such as projecting fields to other function spaces
        for the purposes of visualisation)."""

        annotate = annotate_tape(kwargs)
        if annotate:
            tape = get_working_tape()
            problem = self._ad_problem
            sb_kwargs = NonlinearVariationalSolveBlock.pop_kwargs(kwargs)
            sb_kwargs.update(kwargs)
            block = NonlinearVariationalSolveBlock(problem._ad_F == 0,
                                                   problem._ad_u,
                                                   problem._ad_bcs,
                                                   problem_J=problem._ad_J,
                                                   problem_args=problem._ad_args,
                                                   problem_kwargs=problem._ad_kwargs,
                                                   solver_params=self.parameters,
                                                   solver_args=self._ad_args,
                                                   solver_kwargs=self._ad_kwargs,
                                                   solve_args=args,
                                                   solve_kwargs=kwargs,
                                                   ad_block_tag=self.ad_block_tag,
                                                   **sb_kwargs)
            tape.add_block(block)

        with stop_annotating():
            out = super(NonlinearVariationalSolver, self).solve(*args, **kwargs)

        if annotate:
            block.add_output(self._ad_problem._ad_u.create_block_variable())

        return out


class LinearVariationalProblem(dolfin.LinearVariationalProblem):
    """This object is overloaded so that solves using this class are automatically annotated,
    so that pyadjoint can automatically derive the adjoint and tangent linear models."""

    @no_annotations
    def __init__(self, a, L, u, bcs=None, *args, **kwargs):
        super(LinearVariationalProblem, self).__init__(a, L, u, bcs,
                                                       *args, **kwargs)
        self._ad_a = a
        self._ad_L = L
        self._ad_u = u
        self._ad_bcs = bcs
        self._ad_args = args
        self._ad_kwargs = kwargs


class LinearVariationalSolver(dolfin.LinearVariationalSolver):
    """This object is overloaded so that solves using this class are automatically annotated,
    so that pyadjoint can automatically derive the adjoint and tangent linear models."""

    @no_annotations
    def __init__(self, problem, *args, **kwargs):
        super(LinearVariationalSolver, self).__init__(problem, *args, **kwargs)
        self.ad_block_tag = kwargs.pop("ad_block_tag", None)
        self._ad_problem = problem
        self._ad_args = args
        self._ad_kwargs = kwargs

    def solve(self, *args, **kwargs):
        """To disable the annotation, just pass :py:data:`annotate=False` to this routine, and it acts exactly like the
        Dolfin solve call. This is useful in cases where the solve is known to be irrelevant or diagnostic
        for the purposes of the adjoint computation (such as projecting fields to other function spaces
        for the purposes of visualisation)."""

        annotate = annotate_tape(kwargs)
        if annotate:
            tape = get_working_tape()
            problem = self._ad_problem
            sb_kwargs = LinearVariationalSolveBlock.pop_kwargs(kwargs)
            sb_kwargs.update(kwargs)
            block = LinearVariationalSolveBlock(problem._ad_a == problem._ad_L,
                                                problem._ad_u,
                                                problem._ad_bcs,
                                                problem_args=problem._ad_args,
                                                problem_kwargs=problem._ad_kwargs,
                                                solver_params=self.parameters,
                                                solver_args=self._ad_args,
                                                solver_kwargs=self._ad_kwargs,
                                                solve_args=args,
                                                solve_kwargs=kwargs,
                                                ad_block_tag=self.ad_block_tag,
                                                **sb_kwargs)
            tape.add_block(block)

        with stop_annotating():
            out = super(LinearVariationalSolver, self).solve(*args, **kwargs)

        if annotate:
            block.add_output(self._ad_problem._ad_u.create_block_variable())

        return out
