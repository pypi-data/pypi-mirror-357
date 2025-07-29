
import numpy as np
from mensajes.hola.saludo import generar_array


def test_generar_array():
    np.testing.assert_array_equal(
            np.array([0,1,2,3,4,5]),
            generar_array(6))
    
