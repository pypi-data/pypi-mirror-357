
'''
This file contains functions for handling input data, i.e. reading from files and converting to 
datastructures usable by this implementation.

Classes
----------
None

Functions
----------
multi_interp_treatment_generator()
    Creates interpolating treatment functions from exposure data.
create_datasets()
    Converts input-data to a form structured around the individual treatments.
read_exposure_survival()
    Reads a xlsx file with the exposure and survival data and converts it into useable datastructures.
get_xc()
    Extracts every exposure-function for a given treatment.
split_control_treatment_dataset():
    Splits a dataset into control and treatment datasets.
plot()
    Visualizes the Exposure- and Survival-data as imported by the input_data.read_exposure_survival()-function.
'''
import os
import pandas as pd
from scipy import interpolate
import matplotlib.pyplot as plt
import numpy as np

def multi_interp_treatment_generator(treatments):
    '''
    Creates interpolating treatment functions from exposure data.
    
    Parameters
    ----------
    treatments: pandas.DataFrame
        DataFrame containing the exposure concentrations with the treatments as columns and the timepoints as rows.

    Returns
    ----------
    treatment_funcs: dict
        Dictionary with the treatment-names as keys and the corresponding functions as values. 
    '''
    treatment_funcs = {}
    for treat in treatments:
        t = treatments[treat].index
        conc = treatments[treat].values
        conc1 = conc[~np.isnan(conc)]
        t = t[~np.isnan(conc)]
        s = interpolate.InterpolatedUnivariateSpline(t, conc1, k=1)
        s.__name__ = f'treatment_{treat.lower()}'
        treatment_funcs[treat] = s
    return treatment_funcs


def create_datasets(exposure_funcs, survival_data, treatment_list=None):
    '''
    Converts input-data to a form structured around the individual treatments.

    Parameters
    ----------
    exposure_funcs: dictionary
        Dict of exposures and treatments containing functions representing the external concentrations.
    survival_data: pandas.Dataframe
        Pandas.DataFrame containing the survival for the treatments and timepoints.
    treatment_list: list, optional
        List of strings to name the treatments. If None, the headers of the survival_data-dataframe are used.

    Returns
    ----------
    datasets: list
        List of datasets containing tuples with all exposures and the corresponding survival per treatment.
        In the following Form:
        [
            (exposure_1_treatment_1, exposure_2_treatment_1, ... , exposure_n_treatment_1, survival_treatment_1),
            (exposure_1_treatment_2, exposure_2_treatment_2, ... , exposure_n_treatment_2, survival_treatment_2),
            ...
            (exposure_1_treatment_m, exposure_2_treatment_m, ... , exposure_n_treatment_m, survival_treatment_m)
        ]
    '''
    datasets = []
    if treatment_list == None:
        survival_columns = list(survival_data.keys())
    else:
        survival_columns = treatment_list
    for treatment in survival_columns:
        current_exposure = []
        for sub in exposure_funcs:
            current_exposure.append(exposure_funcs[sub][treatment])
        datasets.append((*current_exposure, survival_data[treatment].dropna()))
    return datasets
    

def read_exposure_survival(
    path, 
    file_name, 
    exposure_name="Exposure", 
    survival_name="Survival", 
    info_name="Info", 
    with_info_dict=False, 
    with_raw_exposure_data=False, 
    visualize=False
):
    
    """
    Reads a xlsx file with the exposure and survival data and converts it into useable datastructures.
    
    Parameters
    --------
    path : str
        Path to the file
    file_name : str
        File name of the xlsx file with the survival and exposure data
    exposure_name : str, default='Exposure'
        Name of the datasheet(s) containing the exposure data
    survival_name : str, default='Survival'
        Name of the datasheet containing the survival data
    info_name : str, default='Info'
        Name of the datasheet containing additional informations
    with_info_dict : bool, default=False
        If True the information datasheet is extracted and converted into a dictionary
    with_raw_exposure_data : bool, default=False
        If the raw exposure data should be returned
    visualize : bool, default=False
        If True the imported data is visualized in two plots
    
    Returns
    --------
    exposure_funcs : dict 
        Dictionairy containing the exposure functions
    survival_data : DataFrame
        Pandas DataFrame containing the treatments as columns and times as index
    num_expos : int
        Number of different expositions that the organisms are subject to. This will be one in the standard guts models but e.g. the number of substances
        used in the exposure when considering a guts-mixtures model.
    info_dict : dict, optional
        Contents of the info datasheet, only returned if 'with_info_dict'=True
    """
    file = pd.ExcelFile(os.path.join(path, file_name))
    exposure_sheets = [exp for exp in file.sheet_names if exposure_name in exp]
    num_expos = len(exposure_sheets)
    if num_expos < 1:
        raise ValueError(f'No sheet named {exposure_name} in the Excel file')
    else:
        exposure_funcs = {}
        raw_exposure_data = {}
        for exposure_sheet in exposure_sheets:
            exposure_data = file.parse(sheet_name=exposure_sheet,index_col=0)
            exposure_funcs[exposure_sheet] = multi_interp_treatment_generator(exposure_data)
            raw_exposure_data.update({exposure_sheet: exposure_data})
    survival_data = file.parse(sheet_name=survival_name,index_col=0)

    if visualize:
        plot(exposure_funcs, survival_data)
    
    return_data = [exposure_funcs, survival_data, num_expos]

    if with_info_dict:
        df_info = file.parse( header=None, sheet_name=info_name)
        info_array = df_info.to_numpy()
        info_dict = {info[0]:info[1:] for info in info_array}
        return_data += [info_dict]

    if with_raw_exposure_data:
        return_data += [raw_exposure_data]

    return tuple(return_data)
    

def get_xc(treatment, exposure_funcs):
    '''
    Extracts every exposure-function for a given treatment.

    Parameters
    ----------
    treatment: String
        Name of the treatment to be handled.
    exposure_funcs: dict
        Dictionary of the exposures and treamtents containing the exposure-functions.
    
    Returns
    ----------
    xc: Tuple
        Tuple containing all exposure-functions for the given treatment.
    '''
    xc_list = []
    for exposure in exposure_funcs:
        xc_list.append(exposure_funcs[exposure][treatment])
    xc = tuple(xc_list)
    return xc


def split_control_treatment_dataset(datasets):
    """
    Splits a dataset into control and treatment datasets

    Parameters
    ----------
    datasets: dict
        A dictionary of all datasets that should be categorized.

    Returns
    ----------
    control_datasets: dict
        A dictionary containing the control datasets
    treat_datasets: dict
        A dictionary containing all other datasets
    """
    control_datasets = []
    treat_datasets = []
    for dataset in datasets:
        if "control" in dataset[-1].name.lower().strip():
            control_datasets.append(dataset)
        else:
            treat_datasets.append(dataset)

    return control_datasets, treat_datasets 


def plot(exposure_funcs, survival_data):
    """
    Visualizes the Exposure- and Survival-data as imported by the input_data.read_exposure_survival()-function.

    Parameters
    ----------
    exposure_funcs: dict
        Dictionary of functions representing the time dependant external exposure to be visualized
    survival_data: pandas.DataFrame
        Table of survival-data to be visualized
    """
    fig, ax = plt.subplots()
    times = survival_data.index
    for col in survival_data.columns:
        ax.plot(times, survival_data[col], label = col)
    ax.legend()
    ax.set(xlabel='Time', ylabel='Survival', title='Observed survival per treatment over Time')
    plt.show()

    fig, ax = plt.subplots()
    for substance in exposure_funcs.keys():
        for treatment in exposure_funcs[substance].keys():
            times = np.linspace(exposure_funcs[substance][treatment].get_knots()[0],exposure_funcs[substance][treatment].get_knots()[-1], 1000)
            ax.plot(times, exposure_funcs[substance][treatment](times), label = treatment)
    ax.legend()
    ax.set(xlabel='Time', ylabel='Concentration', title='Exposure-Concentrations/Treatments over Time')
    plt.show()
