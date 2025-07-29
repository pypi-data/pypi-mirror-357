import numpy as np

from pymodaq_plugins_datamixer.extensions.utils.model import DataMixerModel, np  # np will be used in method eval of the formula

from pymodaq_utils.math_utils import gauss1D, my_moment

from pymodaq_data.data import DataToExport, DataWithAxes
from pymodaq_gui.parameter import Parameter

from pymodaq_plugins_datamixer.extensions.utils.parser import (
    extract_data_names, split_formulae, replace_names_in_formula)


def gaussian_fit(x, amp, x0, dx, offset):
    return amp * gauss1D(x, x0, dx) + offset


class DataMixerModelFit(DataMixerModel):
    params = [

    ]

    def ini_model(self):
        pass

    def update_settings(self, param: Parameter):
        pass

    def process_dte(self, dte: DataToExport):
        dte_processed = DataToExport('computed')
        dwa = dte.get_data_from_full_name('Spectrum - ROI_00/Hlineout_ROI_00').deepcopy()

        dte_processed.append(dwa)
        dte_processed.append(dwa.fit(gaussian_fit, self.get_guess(dwa)))

        return dte_processed

    @staticmethod
    def get_guess(dwa):
        offset = np.min(dwa).value()
        moments = my_moment(dwa.axes[0].get_data(), dwa.data[0])
        amp = (np.max(dwa) - np.min(dwa)).value()
        x0 = float(moments[0])
        dx = float(moments[1])

        return amp, x0, dx, offset


