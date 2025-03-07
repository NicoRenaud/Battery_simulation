from math import ceil
from typing import Iterator, Tuple
import numpy as np
from scipy.sparse.linalg import splu
from skfem import *
from skfem.models.poisson import laplace, mass
from skfem import MeshTri, Basis, ElementTriP2
from skimage.data import binary_blobs
from nanomesh import Image
from skfem import MeshTri
from skfem.helpers import dot, grad

class Mesh:

    '''
    Getting mesh of blobs into nanomesh, then skfem
    '''

    def __init__(self,plane,length):
        """
        """
        self.plane= plane
        self.length=length

    def nano_mesher(self):
        """
        """
        sk_mesh = self.plane.generate_mesh(opts='q30a10')
        sk_mesh.points = (sk_mesh.points) / self.length / 2 - 1
        return sk_mesh

    def skfem_mesher(self):
        """
        """
        triangles=self.nano_mesher().get('triangle')
        p = triangles.points.T
        t = triangles.cells.T
        lithium_list = []
        lyte_list = []
        f = -1
        for ele in triangles.cell_data["physical"]:
            f = f + 1
            if ele == 2:
                lithium_list.append(f)
            else:
                lyte_list.append(f)
        lithium_list = np.array(lithium_list)
        lyte_list = np.array(lyte_list)
        m = MeshTri(p, t, _subdomains={"lithium": lithium_list, "electrolyte": lyte_list})
        m = m.with_boundaries({"l": lambda x: x[1] == -1, "r": lambda x: x[0] == 1})
        return m

    def basis(self):
        """
        """
        e=ElementTriP1()
        basis=Basis(self.skfem_mesher(),e)
        return basis
