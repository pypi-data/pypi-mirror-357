import dolfin
from pyadjoint.overloaded_type import create_overloaded_object
from pyadjoint.tape import stop_annotating


def refine(*args, **kwargs):
    """ Refine is overloaded to ensure that the returned mesh is overloaded.
    """
    kwargs.pop("ad_block_tag", None)
    with stop_annotating():
        output = dolfin.refine(*args, **kwargs)
    overloaded = create_overloaded_object(output)
    return overloaded
