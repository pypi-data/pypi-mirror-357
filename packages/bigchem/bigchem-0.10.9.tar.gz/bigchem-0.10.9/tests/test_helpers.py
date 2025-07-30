from qcio import CalcType, ProgramInput

from bigchem.utils import _gradient_inputs


def test_gradient_inputs(water):
    dh = 1

    gradients = _gradient_inputs(
        ProgramInput(
            structure=water, model={"method": "fake"}, calctype=CalcType.hessian
        ),
        dh,
    )

    assert len(gradients) == (3 * 2 * len(water.symbols))

    geoms = []
    for i in range(len(water.geometry.flatten())):
        for sign in [1, -1]:
            modified_geom = water.geometry.flatten()
            modified_geom[i] += dh * sign
            geoms.append(modified_geom)

    for i, geom in enumerate(geoms):
        assert gradients[i].calctype == CalcType.gradient
        assert (gradients[i].structure.geometry.flatten() == geom).all()
