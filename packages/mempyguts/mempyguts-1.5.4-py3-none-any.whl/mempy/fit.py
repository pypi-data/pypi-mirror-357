'''
This file contains the datastructure mempy.fit, which can be used to fit models to input-data
and which must be passed as an attribute to functions performing simulation or validation.

Classes
----------
Fit
    __init__()
        Initialises a mempy.fit-object.
    _check_overwrite()
        Warns the user before they overwrite the information of an existing fit by performing a new fit.
    pretty_print()
        Prints all available information on the fit performed with this instance in a comprehensive way to the console.
    serialize()
        Serializes this Fit instance using the pickle library to ensure future availability of the achieved results.
    visualize()
        Plots the model solutions with the fitted parameter values and the input-survival-data
    non_lmfitize()
        Converts a lmfit.Parameters-object in to a dictionary of parameter values usable by the mempy.model classes and passes it to their negloglike function.
    nelder_mead_simplex()
        The Nelder-Mead-simplex fitting method powered by the lmfit-library.
    mcmc()
        Fitting via lmfit + emcee solver. Can either be used to only calucalte the uncertainties as the 2.5 and 97.5 percentiles of the flatchain or
        for parameter values as well (use with caution and see the emcee python package for details)
    simple_parameter_space_explorer()
        Fits a model to data using a simple random parameter explorer and the nelder_mead_simplex()-function
    
Functions
----------
deserialize()
    recover a serialized fit-object using pickle
deserialize_many()
    recover all fits in a given directory using pickle
'''
import lmfit
import pandas as pd
from tabulate import tabulate
import mempy.input_data as input_data
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pickle
import os
import emcee
import math
import corner
    
class Fit:

    def __init__(self):
        '''
        Initialising information about the performed fit.
        '''
        self.method = None
        self.params = None
        self.params_info = None
        self.residual = None
        self.uncertainties = None
        self.fit_info = None
        self.goodness = None
        self.hb_fix = None
        self.data = None
        self.data_info = None
        self.model = None
        self.flatchain = None
        self.uncertainties_method = None


    def _check_overwrite(self, overwrite):
        '''
        This method warns the user before they overwrite the information of an existing fit by performing a new fit.

        Parameters
        ----------
        overwrite: boolean
            Wheter or not the user allows overwriting the information in this fit.Fit instance.
        '''
        if self.method != None:
            if not overwrite:
                raise PermissionError("This fit-instance has already been used to perform a fit. Create a new mempy.fit.Fit-object or set overwrite to True.")


    def pretty_print(self):
        '''
        Prints all available information on the fit performed with this instance in a comprehensive way to the console.
        ''' 
        print(f'Model: {self.model.__class__.__name__}')
        print(f'Number of exposures: {self.model.num_expos}\n')

        print(' Best-Fit parameter values'.upper())
        keys = []
        values = []
        
        for key, value in self.params.items():
            keys.append(key)
            values.append(value)

        if self.uncertainties == None:
            list = [keys, values]
            print(tabulate(list, headers = 'firstrow', tablefmt="heavy_grid"))
            print('Uncertainties were not calculated.')
        else:
            upper = []
            lower = []
            #upper = []
            for key, value in self.params.items():
                if key in self.uncertainties:
                    lower.append(self.uncertainties[key]['lower'])
                    upper.append(self.uncertainties[key]['upper'])
                else:
                    lower.append['nAn']
                    upper.append['nAn']
            list = [keys, values, lower, upper]
            print(tabulate(list, headers = 'firstrow', tablefmt="heavy_grid", showindex=['Value', 'lower', 'upper']))
        
        print('\n', 'Fit-algorithm  Info'.upper())

        print(f'Method: {self.method}')
        hbf = {True: 'was', False: 'was not'}
        print(f'The background mortality {hbf[self.hb_fix]} priorly fitted to control-data.')

        keys = []
        values = []
        for key, value in self.fit_info.items():
            keys.append(key)
            values.append(value)
        list = [keys, values]
        print(tabulate(list, headers = 'firstrow', tablefmt="heavy_grid"))
        print(f'Value of the target function: {self.residual}')

        print('\n', 'Parameter ranges')
        keys = []
        min = []
        max = []
        initial = []
        for key, value in self.model.params_info.items():
            keys.append(key)
            min.append(value['min'])
            max.append(value['max'])
            initial.append(value['initial'])
        list = [keys, min, max, initial]
        print(tabulate(list, headers = 'firstrow', tablefmt='heavy_grid', showindex=['min','max','initial']))

        print('\n', 'Goodness of fit'.upper())
        keys = []
        values = []
        for key, value in self.goodness.items():
            keys.append(key)
            values.append(value)
        list = [keys, values]
        print(tabulate(list, headers = 'firstrow', tablefmt="heavy_grid"))

        print('\n', 'Data info'.upper())
        keys = []
        info = []
        for key, inf in self.data_info.items():
            keys.append(key)
            info.append(inf)

        list = [keys, info]
        print(tabulate(list, headers = 'firstrow', tablefmt="heavy_grid"))

    def serialize(self, dir, filename):
        '''
        Serializes this Fit instance using the pickle library to ensure future availability of the achieved results.

        Parameters
        ----------
        dir: string
            The directory in which the instance should be saved. Is created if it does not exist.
        filename: string
            The name of the .pickle-file in which this instance should be saved.
        '''
        if not os.path.exists(dir):
            os.makedirs(dir)
        
        with open(dir + filename + '.pickle', "wb") as file:
            pickle.dump(self, file)

    

    def visualize(self, share_axis = True, suptitle = 'Fit to training data'):
        '''
        Plots the model solutions with the fitted parameter values and the input-survival-data

        Parameters
        ----------
        share_axis: boolean
            Wheter or not the plots for each compartment should share their y-axis to achieve better visual comparability.
        suptitle: string
            The Title for the figure.
        '''
        self.model.plot(self.params, self.data['exposure'], observed_data = self.data['survival'], share_axis = share_axis, suptitle = suptitle)

    
    def non_lmfitize(self, params, datasets, model):
        '''
        Converts a lmfit.Parameters-object in to a dictionary of parameter values usable by the mempy.model classes and passes it to their negloglike function.

        This is to ensure, that the mempy.model classes can be entirely independant any specific library (lmfit) to allow the implementation
        of different fitting-methods that are not supported in lmfit.

        Parameters
        ----------
        params: lmfit.Parameters
            A lmfit.Parameters object to be evaluated with the model.
        datasets: dict
            The training data to compare the model results to.
        model: mempy.model.Model
            The bottom level mempy.model instance implementing the model ODEs

        Returns
        ----------
        result: float
            The resulting negative logarithmic likelihood as calculated by the negloglike-method of the passed model instance.
        '''
        params_dict = params.valuesdict()
        result = model.negloglike(params_dict, datasets)
        return result


    def nelder_mead_simplex(self, model, exposure_funcs, survival_data, hb_fix = False, maxiter = None, printres = True, visualize = True, overwrite = False):
        '''
        The Nelder-Mead-simplex fitting method powered by the lmfit-library.

        Parameters
        ----------
        model: mempy.model.Model
            The bottom level model instance to be fitted
        exposure_funcs: dict
            Dictionary of functions representing the time dependant external exposure
        survival_data: pandas.DataFrame
            The survival_data to which the model should be fitted
        hb_fix: boolean
            Wheter or not the background mortality should priorly be fitted solely to the control datasets and subsequently fixed to that value.
        printres: boolean
            Wheter or not the results of this fit should be printed to the console
        visualize: boolean
            Wheter or not the model should be plotted with the resulting parameter values
        overwrite: boolean
            Wheter or not the results saved in an instance can be overwritten by performing a second fit.
        '''
        self._check_overwrite(overwrite)

        datasets = input_data.create_datasets(exposure_funcs, survival_data)

        lmfit_params = lmfit.Parameters()
        for p in model.params_info:
            lmfit_params.add(model.params_info[p]['name'], 
                            min = model.params_info[p]['min'], 
                            max = model.params_info[p]['max'], 
                            value = model.params_info[p]['initial'], 
                            vary = model.params_info[p]['vary'])
            
        if hb_fix:

            control_datasets, datasets = input_data.split_control_treatment_dataset(datasets)

            for p in lmfit_params:
                lmfit_params[p].vary = False
            lmfit_params['hb'].vary = True

            minimizer = lmfit.Minimizer(self.non_lmfitize, lmfit_params, fcn_args = (control_datasets, model))
            result = minimizer.minimize(method='nelder', params=lmfit_params)

            lmfit_params = result.params

            for p in lmfit_params:
                lmfit_params[p].vary = True
            lmfit_params['hb'].vary = False
 
        minimizer = lmfit.Minimizer(self.non_lmfitize, lmfit_params, fcn_args = (datasets, model))
        result = minimizer.minimize(method='nelder', params=lmfit_params, options={'maxiter':maxiter})

        # Saving the results
        self.method = "Nelder-Mead-Simplex" 
        self.params = result.params.valuesdict() 
        self.params_info = model.params_info
        self.residual = result.residual
        self.uncertainties = None
        self.fit_info = {
            'success'   : result.success,
            'n_f_ev'    : result.nfev,
            'n_vary'    : result.nvarys
            }
        self.goodness = {
            'aic'       : result.aic,
            'bic'       : result.bic,
            'chi_sq'    : result.chisqr,
            'nrmse'     : model.nrmse(self.params, exposure_funcs, survival_data, with_akaike = False)
            }
        self.hb_fix = hb_fix
        self.model = model
        self.data = {
            'exposure': exposure_funcs,
            'survival': survival_data
        }
        self.data_info = {
            'num_expos': model.num_expos,
            'num_treatments': len(survival_data),
            'starttime' : survival_data.index[0],
            'endtime' : survival_data.index[-1],
            'num_individuals' : survival_data[survival_data.keys()[0]][0]
            }

        if printres:
            self.pretty_print()
        if visualize:
            self.visualize()

    
    def mcmc(self, model, exposure_funcs, survival_data, hb_fix=True, nsteps=10000, thin=1, nwalkers=None, uncertainties_only = True, progressbar=True, printres = True, visualize = True, overwrite = False):
        '''
        Fitting via lmfit + emcee solver. Can either be used to only calucalte the uncertainties as the 2.5 and 97.5 percentiles of the flatchain or
        for parameter values as well (see the emcee python package)

        Parameters
        ----------
        model: mempy.model.Model
            The bottom level model instance to be fitted
        exposure_funcs: dict
            Dictionary of functions representing the time dependant external exposure
        survival_data: pandas.DataFrame
            The survival_data to which the model should be fitted
        hb_fix: boolean
            Wheter or not the background mortality should priorly be fitted solely to the control datasets and subsequently fixed to that value.
        nsteps: int
            The amount of steps for each walker
        thin: int
            only accepts one in every *thin* samples (see the emcee python package)
        nwalkers: int
            Should be set so nwalkers >> nvarys, where nvarys are the number of parameters being varied during the fit. 
            'Walkers are the members of the ensemble. They are almost like separate Metropolis-Hastings chains but, of course, the proposal 
            distribution for a given walker depends on the positions of all the other walkers in the ensemble'. - from the emcee webpage.
        uncertainties_only: boolean
            Wheter or not only uncertainties should be calculated for already fitted parameters
        progressbar: boolean
            Wheter or not a progressbar should be shown
        printres: boolean
            Wheter or not the results of this fit should be printed to the console
        visualize: boolean
            Wheter or not the model should be plotted with the resulting parameter values
        overwrite: boolean
            Wheter or not the results saved in an instance can be overwritten by performing a second fit.        
        '''
        if not uncertainties_only:
            self._check_overwrite(overwrite)
        else:
            if self.method == None:
                raise PermissionError("Cannot calculate uncertainties only since best fit parameter values have not yet been calucalted.")


        datasets = input_data.create_datasets(exposure_funcs, survival_data)
        lmfit_params = lmfit.Parameters()

        if not uncertainties_only:

            for p in model.params_info:
                lmfit_params.add(model.params_info[p]['name'], 
                                min = model.params_info[p]['min'], 
                                max = model.params_info[p]['max'], 
                                value = model.params_info[p]['initial'], 
                                vary = model.params_info[p]['vary'])

            if hb_fix == True:
                control_datasets, datasets = input_data.split_control_treatment_dataset(datasets)

                for p in lmfit_params:
                    lmfit_params[p].vary = False
                lmfit_params['hb'].vary = True

                minimizer = lmfit.Minimizer(self.non_lmfitize, lmfit_params, fcn_args = (control_datasets, model))
                result = minimizer.minimize(method='nelder', params=lmfit_params)

                lmfit_params = result.params

                for p in lmfit_params:
                    lmfit_params[p].vary = True
                lmfit_params['hb'].vary = False
            
        else:
            lmfit_params = lmfit.Parameters()
            for p in model.params_info:
                lmfit_params.add(model.params_info[p]['name'], 
                                min = model.params_info[p]['min'], 
                                max = model.params_info[p]['max'], 
                                value = self.params[p], 
                                vary = model.params_info[p]['vary'])
                
        def objective(*args, **kwargs):
            return -model.negloglike(*args, **kwargs)

        if not nwalkers:
            nwalkers = 2*len([n for n, p in lmfit_params.items() if p.vary])

        print(f'Commencing MCMC with {nwalkers} walkers, {nsteps} steps')

        mini = lmfit.Minimizer(objective, lmfit_params, fcn_args=(datasets,))

        result = mini.emcee(burn=int(nsteps/2), steps=nsteps, thin=thin, nwalkers=nwalkers, 
                         ntemps=1, params=lmfit_params, progress=progressbar)
        
        unc = {}
        for p in lmfit_params:
            unc[p] = {'lower':1,'upper':1}
            unc[p]['lower'] = np.percentile(result.flatchain[p],2.5)
            unc[p]['upper'] = np.percentile(result.flatchain[p],97.5)

        if not uncertainties_only:
            # Saving the results
            self.method = "MCMC" 
            self.params = result.params.valuesdict() 
            self.params_info = model.params_info
            self.residual = result.residual
            self.uncertainties = unc
            self.flatchain = result.flatchain
            self.fit_info = {
                'success'   : result.success,
                'n_f_ev'    : result.nfev,
                'n_vary'    : result.nvarys
                }
            self.goodness = {
                'aic'       : result.aic,
                'bic'       : result.bic,
                'chi_sq'    : result.chisqr,
                'nrmse'     : model.nrmse(self.params, exposure_funcs, survival_data, with_akaike = False)
                }
            self.hb_fix = hb_fix
            self.model = model
            self.data = {
                'exposure': exposure_funcs,
                'survival': survival_data
            }
            self.data_info = {
                'num_expos': model.num_expos
                }
        else:
            self.uncertainties_method = 'mcmc'
            self.uncertainties = unc
            self.flatchain = result.flatchain

        def plot_mcmc(flatchain, res, quantiles=[0.025, 0.5, 0.975]):
            labels = flatchain.columns 
            c = corner.corner(flatchain, labels=labels,
                truths=[res[par] for par in res if par in flatchain.columns], title_fmt=".2E", 
                        verbose=True, show_titles=True, quantiles=quantiles)

        if printres:
            self.pretty_print()
        if visualize:
            self.visualize()
            plot_mcmc(self.flatchain, self.params)

    
    def simple_parameter_space_explorer(self, model, exposure_funcs, survival_data, hb_fix = False, combinations=100, pre_maxiter = 60, final_maxiter = None, printres = True, visualize = True, overwrite = False):
        '''
        Fits a model to data using a simple random parameter explorer and the nelder_mead_simplex()-function
        
        Parameters
        ----------
        model: mempy.model.Model
            The bottom level model instance to be fitted
        exposure_funcs: dict 
            dict containing the exposure functions (see mempy.input)
        survival_data: pandas.DataFrame
            DataFrame containing the treatments as columns and times as index (see mempy.input)
        hb_fix: boolean
            wheter or not the background mortality should priorly be fitted solely to the control datasets and subsequently fixed to that value.
        combinatinos: int
            the amount of initial parameter sets to be tested
        pre_maxiter: int
            the amount of steps in the minimization-process for the initial parameter sets
        final_maxiter: int
            the amount of steps in the minimization-process for the best of the initial parameter sets
        printres: boolean
            Wheter or not the results of this fit should be printed to the console
        visualize: boolean
            Wheter or not the model should be plotted with the resulting parameter values
        overwrite: boolean
            Wheter or not the results saved in an instance can be overwritten by performing a second fit.
        '''
        self._check_overwrite(overwrite)

        def random_combinations(params_info, combinations, hb_fix):
            #Logarithmically draws N combinations of values for the parameters
            param_combinations = []
            for _ in range(combinations):
                comb = {}
                for param in params_info:
                    if param == "hb" and hb_fix:
                        continue

                    log_max = np.log10(params_info[param]['max'])
                    log_min = np.log10(params_info[param]['min'])

                    rand = np.random.random()
                    rand_val = 10 ** (rand * (log_max - log_min) + log_min)
                    comb[param] = rand_val
                param_combinations.append(comb)
            return param_combinations 
        
        if combinations > 0:    
            param_combinations = random_combinations(model.params_info, combinations, hb_fix)
            param_exp_list = []
            for i, param_combi in enumerate(param_combinations):
                print(f'Starting parameter combination: {i}', end = '\r')
                for key in model.params_info:
                    if key in param_combi:
                        model.params_info[key]['initial'] = param_combi[key]

                self.nelder_mead_simplex(model, exposure_funcs, survival_data, hb_fix = hb_fix, maxiter = pre_maxiter, printres = False, visualize= False, overwrite = True)
                param_exp_list.append((self.residual, self.params))
            
            sort_params = sorted(param_exp_list, key=lambda tup: tup[0])
            
            for k in model.params_info:
                model.params_info[k]['initial'] = sort_params[0][1][k]
            
            print(f'\nStarting final minimization with optimal initial parameter set {sort_params[0][1]} with residual {sort_params[0][0]}.')
        self.nelder_mead_simplex(model, exposure_funcs, survival_data, hb_fix = hb_fix, maxiter = final_maxiter, printres = printres, visualize= visualize, overwrite = True)

        self.method = 'simple_parameter_space_explorer'



def deserialize(dir, filename):
    '''
    Recover a serialized fit-object using pickle

    Parameters
    ----------
    dir: string
        The directory containing the serialized fit-object to be recovered.
    filename: string
        The .pickle-file containg the fit-object to be recovered.

    Returns
    ----------
    ret: mempy.fit.Fit
        The deserialized fit-instance
    '''
    with open(dir + filename, "rb") as file:
        ret = pickle.load(file)
    return ret

def deserialize_many(dir):
    '''
    Recover all serialized fit-objects in a given directory using pickle

    Parameters
    ----------
    dir: string
        The directory containing the serialized fit-objects to be recovered.

    Returns
    ----------
    fits: list
        A list containing all the deserialized fit-objects
    '''
    fits = []
    for filename in os.listdir(dir):
        with open(dir+filename, "rb") as file:
            if ".pickle" in filename:
                fits.append(pickle.load(file))
    return fits