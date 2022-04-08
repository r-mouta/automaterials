import numpy as np
from nyquistlib import get_data_exp, get_data_fit, get_data_mdl
from pymatgen.core.spectrum import Spectrum
from collections import OrderedDict
from plotting import pretty_plot


class NyquistPlotter:
    def __init__(self, xshift=0.0, yshift=0.0):
        self.xshift = xshift
        self.yshift = yshift
        self.colors = []
        self._impedance_exp = OrderedDict()
        self._impedance_fit = OrderedDict()

    def add_impedance(self, label, impedance_exp, impedance_fit):
        self._impedance_exp[label] = impedance_exp
        self._impedance_fit[label] = impedance_fit

    def add_impedances(self, impedance_exp, impedance_fit):
        keys_exp = impedance_exp.keys()
        keys_fit = impedance_fit.keys()

        if keys_exp == keys_fit:
            for label in keys_exp:
                self.add_impedance(label, impedance_exp[label], impedance_fit[label])

    def get_plot(self, xlim=None, ylim=None):

        plt = pretty_plot(8, 8)
        i = 0
        if len(self._impedance_exp.keys()) != 1:
            cmap = plt.cm.get_cmap('Set1')
            temperatures = self._impedance_exp.keys()
            print(temperatures)
            t_final = max(temperatures)
            t_initial = min(temperatures)
            t_range = t_final - t_initial
            cm_pos = [
                (temperature - t_initial) / t_range
                for temperature in temperatures
            ]
            self.colors = [cmap(pos) for pos in cm_pos]
        else:
            self.colors = 'red'

        for key, sp in self._impedance_exp.items():
            plt.plot(
                sp.x,
                sp.y,
                'o',
                color=self.colors[i],
                ms=10,
                alpha=0.90,
                mfc='white',
                label=str(key) + '-Exp',
                linewidth=1,
            )
            i += 1

        j = 0
        for key_fit, sp_fit in self._impedance_fit.items():
            plt.plot(
                sp_fit.x,
                sp_fit.y,
                color=self.colors[j],
                label=str(key_fit) + '-Fit',
                linewidth=2,
            )
            j += 1
        plt.xlabel("Z' ($\\Omega)$")
        plt.ylabel('$-$Z" ($\\Omega)$')

        if xlim:
            plt.xlim(xlim)
        if ylim:
            plt.ylim(ylim)

        plt.legend()
        leg = plt.gca().get_legend()
        ltext = leg.get_texts()
        plt.setp(ltext, fontsize=10)
        plt.tight_layout()

        return plt

    def improvised_plotter(self, pathexp, pathfit):
        dexp = get_data_exp(datapath=pathexp, pattern='*.txt', )
        dfit = get_data_fit(datapath=pathfit, pattern='*.z', )
        data_exp = {}
        for key_exp in sorted(dexp.keys()):
            x_exp = np.array(dexp[key_exp])[:, 0].astype(float)
            y_exp = np.array(dexp[key_exp])[:, 1].astype(float)
            spectrum = Spectrum(x_exp, -y_exp)
            data_exp.update({int(key_exp): spectrum})

        data_fit = {}
        for key_fit in sorted(dfit.keys()):
            x_fit = np.array(dfit[key_fit])[:, 0].astype(float)
            y_fit = np.array(dfit[key_fit])[:, 1].astype(float)
            spectrum = Spectrum(x_fit, -y_fit)
            data_fit.update({int(key_fit): spectrum})

        self.add_impedances(impedance_exp=data_exp, impedance_fit=data_fit)
        self.show()

    def save_plot(self):
        pass

    def show(self, **kwargs):
        plt = self.get_plot(**kwargs)
        plt.show()
