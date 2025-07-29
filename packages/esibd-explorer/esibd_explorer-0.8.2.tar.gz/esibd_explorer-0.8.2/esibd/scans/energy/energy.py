from typing import TYPE_CHECKING, cast

import h5py
import numpy as np
from matplotlib.text import Annotation
from scipy import optimize

from esibd.core import INOUT, PARAMETERTYPE, PRINT, ControlCursor, CursorAxes, MetaChannel, Parameter, colors, parameterDict, plotting
from esibd.plugins import Scan

if TYPE_CHECKING:
    from esibd.plugins import Plugin


def providePlugins() -> 'list[type[Plugin]]':
    """Return list of provided plugins. Indicates that this module provides plugins."""
    return [Energy]


class Energy(Scan):
    """Scan that records the current on one electrode, typically a detector plate, as a function of one potential, typically a retarding grid.

    The display shows the measured transmission data, a discrete derivative,
    and a Gaussian fit that reveals beam-energy center and width. The
    potential on the selected channel can be changed by clicking and
    dragging on the image while holding down the Ctrl key.
    """

    name = 'Energy'
    version = '1.0'
    iconFile = 'energy.png'
    useInvalidWhileWaiting = True

    display: 'Energy.Display'

    class Display(Scan.Display):
        """Display for Energy scan."""

        scan: 'Energy'
        axes: list[CursorAxes]

        def initGUI(self) -> None:
            """Initialize GUI."""
            super().initGUI()
            self.mouseActive = True

        def initFig(self) -> None:
            super().initFig()
            if self.fig and self.canvas:
                self.axes.append(cast('CursorAxes', self.fig.add_subplot(111)))
                self.axes.append(cast('CursorAxes', self.axes[0].twinx()))  # creating twin axis
                self.canvas.mpl_connect('motion_notify_event', self.mouseEvent)
                self.canvas.mpl_connect('button_press_event', self.mouseEvent)
                self.canvas.mpl_connect('button_release_event', self.mouseEvent)
                self.axes[0].yaxis.label.set_color(self.scan.MYBLUE)
                self.axes[0].tick_params(axis='y', colors=self.scan.MYBLUE)
                self.axes[1].set_ylabel('-dI/dV (%)')
                self.axes[1].set_ylim((0, 115))  # keep top 15 % for label
                self.axes[1].yaxis.label.set_color(self.scan.MYRED)
                self.axes[1].tick_params(axis='y', colors=self.scan.MYRED)
                self.seRaw = self.axes[0].plot([], [], marker='.', linestyle='None', color=self.scan.MYBLUE, label='.')[0]  # dummy plot
                self.seGrad = self.axes[1].plot([], [], marker='.', linestyle='None', color=self.scan.MYRED)[0]  # dummy plot
                self.seFit = self.axes[1].plot([], [], color=self.scan.MYRED)[0]  # dummy plot
                self.axes[-1].cursor = None  # type: ignore  # noqa: PGH003
                self.scan.labelAxis = self.axes[0]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.useDisplayChannel = True
        self.previewFileTypes.append('.swp.dat')
        self.previewFileTypes.append('.swp.h5')

    def loadDataInternal(self) -> bool:
        """Load data in internal standard format for plotting."""
        if self.file.name.endswith('.swp.dat'):  # legacy ESIBD Control file
            headers = []
            with self.file.open('r', encoding=self.UTF8) as dataFile:
                dataFile.readline()
                headers = dataFile.readline().split(',')[1:][::2]  # read names from second line
            try:
                data = np.loadtxt(self.file, skiprows=4, delimiter=',', unpack=True)
            except ValueError as e:
                self.print(f'Loading from {self.file.name} failed: {e}', flag=PRINT.ERROR)
                return False
            if data.shape[0] == 0:
                self.print(f'No data found in file {self.file.name}.', flag=PRINT.ERROR)
                return False
            self.inputChannels.append(MetaChannel(parentPlugin=self, name='Voltage', recordingData=data[0], unit='V'))
            for name, dat in zip(headers, data[1:][::2], strict=True):
                self.addOutputChannel(name=name.strip(), unit='pA', recordingData=dat)
            return True
        if self.file.name.endswith('.swp.h5'):
            with h5py.File(self.file, 'r') as h5file:
                is03 = h5file[self.VERSION].attrs['VALUE'] == '0.3'  # legacy version 0.3, 0.4 if False
                self.inputChannels.append(MetaChannel(parentPlugin=self, name=cast('str', cast('h5py.Group', h5file['SESETTINGS'])['Channel'].attrs['VALUE']),
                                                       recordingData=cast('h5py.Dataset', h5file['Voltage'])[:] if is03 else cast('h5py.Dataset', h5file['INPUT'])[:],
                                               unit='V', inout=INOUT.IN))
                output_group = cast('h5py.Group', h5file['Current'] if is03 else h5file['OUTPUTS'])
                for name, item in output_group.items():
                    self.addOutputChannel(name=name, unit='pA', recordingData=item[:])
            return True
        return super().loadDataInternal()

    channelName: str

    def getDefaultSettings(self) -> dict[str, dict]:
        defaultSettings = super().getDefaultSettings()
        defaultSettings[self.WAIT][Parameter.VALUE] = 2000
        defaultSettings[self.CHANNEL] = parameterDict(value='RT_Grid', toolTip='Electrode that is swept through.', items='RT_Grid, RT_Sample-Center, RT_Sample-End',
                                                                      parameterType=PARAMETERTYPE.COMBO, attr='channelName', event=self.dummyInitialization)
        defaultSettings[self.START] = parameterDict(value=-10, parameterType=PARAMETERTYPE.FLOAT, attr='start', event=self.estimateScanTime)
        defaultSettings[self.STOP] = parameterDict(value=-5, parameterType=PARAMETERTYPE.FLOAT, attr='stop', event=self.estimateScanTime)
        defaultSettings[self.STEP] = parameterDict(value=.2, parameterType=PARAMETERTYPE.FLOAT, attr='step', minimum=.1, maximum=10, event=self.estimateScanTime)
        return defaultSettings

    def addInputChannels(self) -> None:
        super().addInputChannels()
        self.addInputChannel(self.channelName, self.start, self.stop, self.step)

    def map_percent(self, x) -> np.ndarray:
        """Map any range on range 0 to 100.

        :param x: Input values.
        :type x: np.ndarray
        :return: Mapped input values.
        :rtype: np.ndarray
        """
        # can't map if largest deviation from minimum is 0, i.e. all zero
        # has to return a sequence as matplotlib now expects sequences for set_x(y)data
        return (x - np.min(x)) / np.max(x - np.min(x)) * 100 if np.max(x - np.min(x)) > 0 else x

    @plotting
    def plot(self, update=False, done=True, **kwargs) -> None:  # pylint:disable=unused-argument  # noqa: ARG002
        # use first that matches display setting, use first available if not found
        # timing test with 20 data points: update True: 30 ms, update False: 48 ms
        if len(self.outputChannels) > 0:  # noqa: PLR1702
            inputRecordingData0 = self.inputChannels[0].getRecordingData()
            outputRecordingData = self.outputChannels[self.getOutputIndex()].getRecordingData()
            if inputRecordingData0 is not None and outputRecordingData is not None:
                y = np.diff(outputRecordingData) / np.diff(inputRecordingData0)
                x = inputRecordingData0[:y.shape[0]] + np.diff(inputRecordingData0)[0] / 2  # use as many data points as needed
                if update:  # only update data
                    self.display.seRaw.set_data(inputRecordingData0, outputRecordingData)
                    self.display.seGrad.set_data(x, self.map_percent(-y))
                else:
                    self.removeAnnotations(self.display.axes[1])
                    if len(self.outputChannels) > 0:
                        self.display.axes[0].set_xlim(inputRecordingData0[0], inputRecordingData0[-1])
                        self.display.axes[0].set_ylabel(f'{self.outputChannels[self.getOutputIndex()].name} {self.outputChannels[self.getOutputIndex()].unit}')
                        self.display.axes[0].set_xlabel(f'{self.inputChannels[0].name} ({self.inputChannels[0].unit})')
                        self.display.seRaw.set_data(inputRecordingData0, outputRecordingData)
                        self.display.seFit.set_data([], [])  # init
                        self.display.seGrad.set_data(x, self.map_percent(-y))
                        for ann in [child for child in self.display.axes[1].get_children() if isinstance(child, Annotation)]:
                            ann.remove()
                        if done:
                            try:
                                x_fit, y_fit, expected_value, fwhm = self.gauss_fit(x, y, np.mean(x))  # use center as starting guess
                                if inputRecordingData0[0] <= expected_value <= inputRecordingData0[-1]:
                                    self.display.seFit.set_data(x_fit, self.map_percent(y_fit))
                                    self.display.axes[1].annotate(text='', xy=(expected_value - fwhm / 2.3, 50), xycoords='data',
                                                                   xytext=(expected_value + fwhm / 2.3, 50), textcoords='data',
                                        arrowprops={'arrowstyle': '<->', 'color': self.MYRED}, va='center')
                                    self.display.axes[1].annotate(text=f'center: {expected_value:2.1f} V\nFWHM: {fwhm:2.1f} V',
                                                                   xy=(expected_value - fwhm / 1.6, 50), xycoords='data', fontsize=10.0,
                                        textcoords='data', ha='right', va='center', color=self.MYRED)
                                else:
                                    self.print('Fitted mean outside data range. Ignore fit.', flag=PRINT.WARNING)
                            except (RuntimeError, ValueError) as e:
                                self.print(f'Fit failed with error: {e}')
                        # ControlCursor has to be initialized last, otherwise axis limits may be affected.
                        self.display.axes[-1].cursor = ControlCursor(self.display.axes[-1], colors.highlight, horizOn=False)
                    else:  # no data
                        self.display.seRaw.set_data([], [])
                        self.display.seFit.set_data([], [])
                        self.display.seGrad.set_data([], [])
                self.display.axes[0].relim()  # only affects y axis
                self.setLabelMargin(self.display.axes[0], 0.15)
                # workaround as .relim() is not working on x ais due to twinx bug
                self.display.axes[0].set_xlim(inputRecordingData0[0], inputRecordingData0[-1])  # has to be called after setLabelMargin
        if len(self.outputChannels) > 0 and self.inputChannels[0].sourceChannel and not np.isnan(self.inputChannels[0].value):
            self.display.axes[-1].cursor.setPosition(self.inputChannels[0].value, 0)
        self.updateToolBar(update=update)
        self.defaultLabelPlot()

    def pythonPlotCode(self) -> str:
        return f"""# add your custom plot code here

MYBLUE='#1f77b4'
MYRED='#d62728'

from scipy import optimize

def map_percent(x):
    '''Maps any range on range 0 to 100.

    :param x: Input values.
    :type x: np.ndarray
    :return: Mapped input values.
    :rtype: np.ndarray
    '''
    return (x-np.min(x))/np.max(x-np.min(x))*100 if np.max(x-np.min(x) > 0) else 0

def gaussian(x, amp1, cen1, sigma1):
    '''Simple gaussian function.

    :param x: X values.
    :type x: np.ndarray
    :param amp1: amplitude
    :type amp1: float
    :param cen1: center
    :type cen1: float
    :param sigma1: width
    :type sigma1: float
    :return: Calculated Y values.
    :rtype: np.ndarray
    '''
    return amp1*(1/(sigma1*(np.sqrt(2*np.pi))))*(np.exp(-((x-cen1)**2)/(2*(sigma1)**2)))

def gauss_fit(x, y, c):
    '''Simple gaussian fit.

    :param x: X values.
    :type x: np.ndarray
    :param y: Y values.
    :type y: np.ndarray
    :param c: Guess of central value.
    :type c: float
    :return: X values with fine step size, corresponding fitted Y values, full with have maximum
    :rtype: np.ndarray, np.ndarray, float
    '''
    amp1 = 100
    sigma1 = 2
    gauss, *_ = optimize.curve_fit(gaussian, x, y, p0=[amp1, c, sigma1])
    fwhm = round(2.355 * gauss[2], 1)  # Calculate FWHM
    x_fine=np.arange(np.min(x), np.max(x), 0.05)
    return x_fine,-gaussian(x_fine, gauss[0], gauss[1], gauss[2]), gauss[1], fwhm

fig = plt.figure(num='{self.name} plot', constrained_layout=True)
ax0 = fig.add_subplot(111)
ax1 = ax0.twinx()
ax0.yaxis.label.set_color(MYBLUE)
ax0.tick_params(axis='y', colors=MYBLUE)
ax1.set_ylabel('-dI/dV (%)')
ax1.yaxis.label.set_color(MYRED)
ax1.tick_params(axis='y', colors=MYRED)

y = np.diff(outputChannels[output_index].recordingData)/np.diff(inputChannels[0].recordingData)
x = inputChannels[0].recordingData[:y.shape[0]]+np.diff(inputChannels[0].recordingData)[0]/2

ax0.set_xlim(inputChannels[0].recordingData[0], inputChannels[0].recordingData[-1])
ax0.set_ylabel(f'{{outputChannels[output_index].name}} ({{outputChannels[output_index].unit}})')
ax0.set_xlabel(f'{{inputChannels[0].name}} ({{inputChannels[0].unit}})')

ax0.plot(inputChannels[0].recordingData, outputChannels[output_index].recordingData, marker='.', linestyle='None', color=MYBLUE, label='.')[0]
ax1.plot(x, map_percent(-y), marker='.', linestyle='None', color=MYRED)[0]

try:
    x_fit, y_fit, expected_value, fwhm = gauss_fit(x, y, np.mean(x))
    if inputChannels[0].recordingData[0] <= expected_value <= inputChannels[0].recordingData[-1]:
        ax1.plot(x_fit, map_percent(y_fit), color=MYRED)[0]
        ax1.annotate(text='', xy=(expected_value-fwhm/2.3, 50), xycoords='data', xytext=(expected_value+fwhm/2.3, 50), textcoords='data',
            arrowprops=dict(arrowstyle="<->", color=MYRED), va='center')
        ax1.annotate(text=f'center: {{expected_value:2.1f}} V\\nFWHM: {{fwhm:2.1f}} V', xy=(expected_value-fwhm/1.6, 50), xycoords='data', fontsize=10.0,
            textcoords='data', ha='right', va='center', color=MYRED)
    else:
        print('Fitted mean outside data range. Ignore fit.')
except RuntimeError as e:
    print(f'Fit failed with error: {{e}}')

fig.show()
        """

    def gaussian(self, x, amp1, cen1, sigma1) -> np.ndarray:
        """Return simple gaussian.

        :param x: X values.
        :type x: np.ndarray
        :param amp1: amplitude
        :type amp1: float
        :param cen1: center
        :type cen1: float
        :param sigma1: width
        :type sigma1: float
        :return: Calculated Y values.
        :rtype: np.ndarray
        """
        return amp1 * (1 / (sigma1 * (np.sqrt(2 * np.pi)))) * (np.exp(-((x - cen1)**2) / (2 * (sigma1)**2)))

    def gauss_fit(self, x, y, c) -> tuple[np.ndarray, np.ndarray, float, float]:
        """Perform simple gaussian fit.

        :param x: X values.
        :type x: np.ndarray
        :param y: Y values.
        :type y: np.ndarray
        :param c: Guess of central value.
        :type c: float
        :return: X values with fine step size, corresponding fitted Y values, center, full with have maximum
        :rtype: np.ndarray, np.ndarray, float, float
        """
        # Define a gaussian to start with
        amp1 = 100
        sigma1 = 2
        gauss, *_ = optimize.curve_fit(self.gaussian, x, y, p0=[amp1, c, sigma1])
        fwhm = round(2.355 * gauss[2], 1)  # Calculate FWHM
        x_fine = np.arange(np.min(x), np.max(x), 0.05)
        return x_fine, -self.gaussian(x_fine, gauss[0], gauss[1], gauss[2]), gauss[1], fwhm
