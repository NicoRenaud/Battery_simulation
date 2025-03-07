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

class FEM():

    def __init__(self,dt,t_max,initial_temp,mesh,basis,Diffusivity_coefficient):
        """
        """
        self.Diffusivity_coefficient = Diffusivity_coefficient
        self.m=mesh
        self.basis=basis
        self.dt=dt
        self.t_max=t_max
        self.initial_temp=initial_temp

    def diffusivity(self):
        """
        """
        diffusivity = self.basis.zero_w()
        for subdomain, elements in self.m.subdomains.items():
            diffusivity[elements] = self.Diffusivity_coefficient[subdomain]
        return diffusivity

    def assembly(self, type):
        self.type=type

        @BilinearForm
        def laplace1(u, v, w):
            return dot(w["diffusivity"] * grad(u), grad(v))

        L0 = asm(laplace1, self.basis, diffusivity=self.diffusivity())
        M0 = asm(mass, self.basis)
        theta = 0.5
        A = M0 + theta * L0 * self.dt
        B = M0 - (1 - theta) * L0 * self.dt
        if type==0:
            return A
        if type == 1:
            return B

    def initial_condition(self):
        u_init = np.zeros(len(self.basis.doflocs.prod(0)))
        for ele in self.basis.get_dofs("l").nodal['u']:
            u_init[ele] = 200
        return u_init

    def frame(self,t: float,
           u: np.ndarray) -> Iterator[Tuple[float, np.ndarray]]:
        self.t=t
        self.u=u
        backsolve = splu(self.assembly(0).T).solve
        while self.t < self.t_max:
            for ele in self.basis.get_dofs("l").nodal['u']:
                u[ele] = self.initial_temp

            t, u = t + self.dt, backsolve(self.assembly(1) @ u)
            for ele in self.basis.get_dofs("l").nodal['u']:
                u[ele] = self.initial_temp
            yield t, u

    def simulate(self):

        # Having Argparse inside a class method feels kinda wrong ... 
        
        # from argparse import ArgumentParser
        # from pathlib import Path

        # from matplotlib.animation import FuncAnimation
        # import matplotlib.pyplot as plt

        # from skfem.visuals.matplotlib import plot

        # parser = ArgumentParser(description='heat equation in a rectangle')
        # parser.add_argument('-g', '--gif', action='store_true',
        #                     help='write animated GIF', )
        # args = parser.parse_args()
        '''
            CHECK THIS
        '''
        ax = plot(self.m, self.initial_condition(), shading='gouraud')
        title = ax.set_title('t = 0.00')
        field = ax.get_children()[0]  # vertex-based temperature-colour
        fig = ax.get_figure()
        fig.colorbar(field)

        def update(event):
            t, u = event
            title.set_text(f'$t$ = {t:.2f}')
            field.set_array(u)

        animation = FuncAnimation(
            fig,
            update,
            self.frame(0.,self.initial_condition()),
            repeat=False,
            interval=50,
        )
        if args.gif:
            animation.save(Path(__file__).with_suffix('.gif'), 'imagemagick')
        else:
            plt.show()









