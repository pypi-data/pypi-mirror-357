'''
This file contains the actual model equations and function to solve them and calculate the likelihood of given parametersets.
Models are strucuted in the following way:

                        
Top level:              shared parent class
                            | (inherits)
Intermediate level:     model-group specific derived class
                            | (inherits)
Bottom level:           model specific derived class


Important functions
-------------------
__init__ (Top level and Bottom level)
    Defines the variables of the specific model equations in a dict, containg starting values for fitting, ranges, names etc.
lp_X() (Top level)
    Calculates the LP_X for a given treatment and parameter set
_rhs (Bottom level)
    "right hand side" of the model specific ODEs to be integrated.
_solve (Top level and Bottom level)
    Solver for the model ODEs. For most SD model variants this is implemented in the Top level class. In case of particularities like the 
    dependance on the maximum damage up to this point in time in IT model variants this must be overwritten in the Bottom level class. This
    is because the scipy.integrate functions cannot handle anything but clean model ODEs in the _rhs()-methods.
plot (Intermediate level)
    Plots the model solutions with the fitted parameter values and, if given, the input-survival-data.
nrmse (Intermediate level)
    Calculates the Normalized Root Mean Square Error
negloglike (Intermediate level)
    Calculation of the negative logarithmic likelihood for parameter fitting.
mortality_loglogistic (Top level)
    Calculate mortality from cumulative log-logistic distribution

'''
import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as scipyInt
import pandas as pd
from scipy import interpolate

try:
    import jax
    import jax.numpy as jnp
    jax.config.update("jax_enable_x64", True)
except ModuleNotFoundError:
    pass

import mempy.input_data as input_data
from mempy.survival_models import (
    conditional_survival_hazard_error_model,
    conditional_survival_error_model
)

'''
----------------------------------------------------------------------------------------------------------------------------------------------------
TOP LEVEL: 
One shared class for all guts model variants defining necessary function and initialising important parameters.
----------------------------------------------------------------------------------------------------------------------------------------------------
''' 
class Model:
    extra_dim = None

    def __init__(self):
        '''
        Initialises some important variables with standard values. In case of a more unusual guts variant these must be overwritten in
        the  __init__-method of the variant specific derived class.
        '''
        self.params_info = {}
        self._params_info_defaults = {
            "initial": 1.0, 
            "name": None,
            "min": None,
            "max": None,
            "prior": None,
            "dims": None,
            "vary": True,
        }
        self.comp_info = [
            'Scaled Damage',
            'Survival'
        ]
        self._numCLike = 1
        self._numSLike = 1
        self.num_expos = 1

        self.state_variables = {
            "survival": {"dimensions": ["id", "time"], "observed": True},
        }

        self._likelihood_func_jax = None

    def mortality_loglogistic(self, x, alpha, beta):
        '''Calculate mortality from cumulative log-logistic distribution for IT model variants

        Parameters
        ----------
        x
            the scaled damage
        alpha
            the median threshold value
        beta
            the shape parameter

        Returns
        ----------
            cumulative log-logistic mortality given the parameters
        '''
        if x > 0:
            return 1.0 / (1 + (x/alpha)**-beta)
        else:
            return 0.0
        
    def LP_X(self, params, exposure_funcs, treatment, accuracy = 0.001, X = 50, visualize = True):
        '''
        Calculates the LP_X for a given treatment and parameter set

        Parameters
        ----------
        params: dict
            dict containing parameter values suitable for this model
        exposure_funcs: dict
            dict containing the exposure (see mempy.input_data)
        treatment: string
            name of the treatment to be used/ key of this treatment in the exposure_funcs dict
        accuracy: float
            accuracy of the LP_X
        X: float
            the percentage of survival to be reached in the last timestep
        visualize: boolean
            wheter or not the result should be plotted

        '''
        left = 0
        right = 1000000
        mid = None
        lp = X/100
        exp_f = {}
        for sub in exposure_funcs:
            exp_f[sub] = {}
            exp_f[sub][treatment] = {}
            knots = exposure_funcs[sub][treatment].get_knots()
            coeffs = exposure_funcs[sub][treatment].get_coeffs()
            exp_f[sub][treatment]['knots'] = knots
            exp_f[sub][treatment]['coeffs'] = coeffs
        
        def multiply_exp(exp_or, treat, factor):
            exp_new = {}
            for sub in exp_or:
                exp_new[sub] = {}
                original_coeffs = exp_or[sub][treat]['coeffs']
                knots = exp_or[sub][treat]['knots']
                end = knots[-1]
                exp_new[sub][treat] = exposure_funcs[sub][treat]
                exp_new[sub][treat + '_lp'] = interpolate.InterpolatedUnivariateSpline(knots, original_coeffs*factor, k=1)
            return end, exp_new
        
        while left <= right:
            mid = left + (right - left) / 2

            y0 = np.zeros(self._numCLike + self._numSLike, dtype=np.double)
            for j in range(self._numSLike):
                y0[-(j+1)]=1
        
            end, exp = multiply_exp(exp_f, treatment, mid)
            res = self._solve(params,y0,[0,end],input_data.get_xc(treatment + '_lp', exp))[-1][-1]
            if res + accuracy > lp and res - accuracy < lp:
                if visualize:
                    print(f'The LP_{X} is {mid}, leading to a final survival of {res}')
                    self.plot(params, exp, share_axis = True, suptitle = f'Model results with LP_{X}.')
                return mid
            if res > lp:
                left = mid
            else:
                right = mid
    
    def _rhs(self):
        '''
        Contains the model ODEs for a specific guts model variant. Must be overwritten in the model variant specific class.
        '''
        raise NotImplementedError('Must be implement in derived class (Bottom level)')
    
    def _rhs_jax(self):
        '''
        Contains the model ODEs for a specific guts model variant in jax syntax. Must be overwritten in the model variant specific class.
        '''
        raise NotImplementedError('Must be implement in derived class (Bottom level)')
    
    def negloglike(self):
        '''
        Calculates the negative logarithmic likelihood of a parameterset with respect to given training data. Must be implemented
        in a intermediate level derived class to specify the calculation depending on the specific model structure. For the standard 
        guts-reduced models this is the model.Reduced-class.
        '''
        raise NotImplementedError('negloglike()-function: must be implement in derived class (Intermediate level)')
    

    def nrmse(self):
        '''
        Calculates the negative logarithmic likelihood of a parameterset with respect to given training data. Must be implemented
        in a intermediate level derived class to specify the calculation depending on the specific model structure. For the standard 
        guts-reduced models this is the model.Reduced-class.
        '''
        raise NotImplementedError('nrmse().function: must be implement in derived class (Intermediate level)')
    

    def plot(self, params, exposure_funcs, observed_data = pd.DataFrame(), share_axis = True, suptitle = None):
        '''
        Plots the model solutions with the fitted parameter values and, if given, the input-survival-data.
        '''
        raise NotImplementedError('plot()-function: must be implement in derived class (Intermediate level)')


    def _solve(self, params, y0, times, xc):
        '''
        Solver for model ODEs. For most SD model variants this is implemented in the Top level class. In case of particularities like the 
        dependance on the maximum damage up to this point in time in IT model variants this must be overwritten in the Bottom level class. This
        is because the scipy.integrate functions cannot handle anything but clean model ODEs in the _rhs()-methods.

        Parameters
        ----------
        params
            A set of parameter values suitable for this model instance
        y0
            The initial conditions for the compartments
        times
            The timepoints at which the model should be evaluated
        xc
            A set of functions containing the time-dependant exposure profile
        
        Returns
        ----------
        result
            An array of lists containing the values for all model compartments at a specific timepoint.
        '''
        
        int_ode = scipyInt.ode(self._rhs).set_integrator('lsoda')
        int_ode.set_initial_value(y0)
        int_ode.set_f_params(params, xc)

        result = [y0]
        for t in times[1:]:
            int_ode.integrate(t)
            result.append(int_ode.y)

        return np.array(result)

    @staticmethod
    def _solver_post_processing(results, time, interpolation):
        return results

'''
----------------------------------------------------------------------------------------------------------------------------------------------------
INTERMEDIATE LEVEL: 
Different classes that implement likelihood calculation for different groups of guts models. 
All clases inherit from the model.Model-class and are used as parent for their model specific derived classes.
----------------------------------------------------------------------------------------------------------------------------------------------------
''' 
class Reduced(Model):
    extra_dim = "substance"
    '''
    This class contains the calculation of the negative logarithmic likelihood for all standard reduced guts models. The nll is
    calculated solely considering the survival.
    For different models, like e.g. the full guts model a class parallel to this is needed, implementing the likelihood calculation. This class
    is then used as parent for the specific model class.
    '''

    def negloglike(self, params, datasets):
        '''
        Calculates the negative logarithmic likelihood of a certain set of parameters and a number of treatments.

        This implements equation (3.41) from the guts paper (p. 57 f)

        Parameters
        ----------
        params: dict
            A suitable set of parameterset for the this model instance.
        datasets: dict
            The training data in the form of datasets (see input_data.create_datasets()).

        Returns
        ----------
        negloglikelihood: float
            The negative logarithmic likelihood of the given parameterset (params) with respect to the given training data.

        '''

        y0 = np.zeros(self._numCLike + self._numSLike)
        for i in range(self._numSLike):
            y0[-(i+1)] = 1.0

        negloglikelihood = 0
        for dataset in datasets:
            xc = tuple(dataset[:-1])

            expected_survival = dataset[-1]
            times = expected_survival.index.values
            expected_survival = np.array(expected_survival)

            y = self._solve(params, y0, times, xc)
            predicted_survival = np.array(y[:,-1], dtype = np.double)

            # Tail regularization parameter to avoid errors due to numercial precision limits
            eps = 1e-9
            predicted_survival[predicted_survival<eps] = eps

            data_diff = np.diff(expected_survival) * -1
            model_diff = np.diff(predicted_survival) * -1

            model_diff[model_diff<eps] = eps

            temp_ll = np.sum(data_diff * np.log(model_diff)) + expected_survival[-1] * np.log(predicted_survival[-1])

            if np.isnan(temp_ll):
                raise ValueError('Likelihood cannot be NaN')
            
            negloglikelihood -= temp_ll

        return negloglikelihood


    def nrmse(self, params, exposure_funcs, survival_data, with_akaike = False):
        '''
        Calculates the Normalized root mean square error of the model

        Parameters
        ----------
        params: dict
            the model parameter values to be used
        exposure_funcs: dict
            dictionary of function representing external concentrations
        survival_data: pandas.DataFrame
            the observed survival data to compare the model results to
        with_akaike: boolean
            wheter or not the Akaike information criterium is to be calucalted as well

        Returns
        ----------
        nrmse: float
            the nrmse of the model
        aic: float
            the aic of the model
        '''
        
        RMSE_top = 0
        RMSE_bot = 0
        all_observed = []
        treatments = survival_data.columns
        for i, treatment in enumerate(treatments):
            survival = survival_data[treatment].dropna()
            times = survival.index  
            xc = input_data.get_xc(treatment, exposure_funcs)
            
            #adding a 0 per damage compartment and the number of organisms per survival compartment to the initial values array
            s = survival.iloc[0]
            y0 = np.zeros(self._numCLike + self._numSLike, dtype=np.double)
            for i in range(self._numSLike):
                y0[-(i+1)]=s

            # Evaluate model at data time points with present parameter set
            y = self._solve(params, y0, times, xc)
            observed = survival.to_numpy()
            modelled = y[:,-1]
            RMSE_top += np.sum((modelled - observed)**2) 
            RMSE_bot += len(observed) 
            all_observed.extend(observed)
        RMSE = np.sqrt(RMSE_top/RMSE_bot) 
        NRMSE = RMSE/np.mean(np.array(all_observed)) 

        if not with_akaike:
            return NRMSE
        else:

            datasets = input_data.create_datasets(exposure_funcs, survival_data)
            neglog = self.negloglike(params, datasets)
            k = len(params)
            n = len(survival_data.columns)
            # different definitions of the AIC 
            aic = 2 * neglog + 2*k #+ (2*k**2+2*k)/(n-k-1)
            #aic = RMSE * np.log(RMSE_top / RMSE_bot) + 2*len(self.params)
            #aic =  n * np.log(RMSE_top/n) + 2*k + (2*k**2+2*k)/(n-k-1)
            return NRMSE, aic
        
    
    def plot(self, params, exposure_funcs, observed_data = pd.DataFrame(), share_axis = True, suptitle = None, return_data = False):
        '''
        Plots the model solutions with the fitted parameter values and, if given, the input-survival-data.

        Parameters
        ----------
        params: dict
            The parameter values appropriate for the used model
        exposure_funcs: dict
            Dict of exposures and treatments containing functions representing the external concentrations.
        observed_data: pandas.DataFrame
            Pandas.DataFrame containing the observed survival for the treatments and timepoints.
        share_axis: boolean
            Wheter or not the plots for each compartment should share their y-axis to achieve better visual comparability.
        suptitle: string
            The Title for the figure.
        return_data: boolean
            Wheter or not the simulated data should be returned for further use

        Returns
        ----------
        res_df: pd.DataFrame
            The simulated data for the given exposures and parameters for further use
        '''
        naming_expf = {}
        for expf in exposure_funcs:
            naming_expf = exposure_funcs[expf]
            break
        timing_expf = None
        for treat in naming_expf:
            timing_expf = naming_expf[treat]
            break
        starttime = timing_expf.get_knots()[0]
        endtime = timing_expf.get_knots()[-1]

        times = np.linspace(starttime, endtime, int((endtime-starttime)*100))
        # add the timepoints from the observed data into the timepoints to be simulated to ensure comparability
        if not observed_data.empty:
            times = np.insert(times, -1, np.array(observed_data.index))
            times = np.unique(times)

        if suptitle == None:
            headline = 'Model output'
        else:
            headline = suptitle
        numCLike = self._numCLike
        numSLike = self._numSLike

        num_expos = self.num_expos
        columns = 0
        for sub in exposure_funcs:
            columns = len(exposure_funcs[sub])
        rows = numCLike + numSLike + num_expos
        fig, axis = plt.subplots(rows, columns, figsize=(columns*5, rows*5))
        fig.tight_layout()

        res = {}
        for i, treat in enumerate(naming_expf.keys()):
            #adding a 0 per damage compartment and the number of organisms per survival compartment to the initial values array
            if not observed_data.empty:
                s = observed_data[treat].iloc[0]
            else:
                s = 1
            y0 = np.zeros(numCLike + numSLike, dtype=np.double)
            for j in range(numSLike):
                y0[-(j+1)]=s
            
            xc = input_data.get_xc(treat, exposure_funcs)
            y = self._solve(params, y0, times, xc)
            res[treat] = y

        if share_axis:
            max_y_ax = []
            for sub in exposure_funcs:
                max_exp_temp = 0
                for treat in exposure_funcs[sub]:
                    temp_max = max(exposure_funcs[sub][treat](times))
                    if max_exp_temp < temp_max:
                        max_exp_temp = temp_max
                max_y_ax.append(max_exp_temp)
            
            for n in np.arange(0,numCLike+numSLike):
                max_comp_n = 0
                for treat in res:
                    y = res[treat]
                    temp_max = max(y.transpose()[n])
                    if max_comp_n < temp_max:
                        max_comp_n = temp_max
                max_y_ax.append(max_comp_n)

        for i, treat in enumerate(naming_expf.keys()):
            y = res[treat]
            for k, sub in enumerate(exposure_funcs):
                ax = axis[k][i]
                ax.plot(times, exposure_funcs[sub][treat](times))
                if share_axis:
                    ax.set(title = f'Exposure {sub} {treat}', ylim = (-max_y_ax[k]/50, max_y_ax[k]+max_y_ax[k]/50))
                else:
                    ax.set(title = f'Exposure {sub} {treat}')
            for l, k in enumerate(np.arange(num_expos,num_expos+numCLike,1)):
                ax = axis[k][i]
                ax.plot(times, y.transpose()[l])
                if share_axis:
                    ax.set(title = f'{self.comp_info[l]} {treat}', ylim = (-max_y_ax[k]/50, max_y_ax[k]+max_y_ax[k]/50))
                else:
                    ax.set(title = f'{self.comp_info[l]} {treat}')
            for m, k in enumerate(np.arange(num_expos+numCLike, num_expos+numCLike+numSLike, 1)):
                ax = axis[k][i]
                ax.plot(times, y.transpose()[m+numCLike])
                if not observed_data.empty:
                    ax.scatter(observed_data[treat].index, observed_data[treat])
                if share_axis:
                    ax.set(title = f'{self.comp_info[m+numCLike]} {treat}', ylim = (-max_y_ax[k]/50, max_y_ax[k]+max_y_ax[k]/50))
                else:
                    ax.set(title = f'{self.comp_info[m+numCLike]} {treat}')
        fig.suptitle(headline, y=1.05, fontsize = 20)
        plt.show()

        if return_data:
            res_df = pd.DataFrame()
            res_df.insert(0, 'Time', times)
            res_df.set_index('Time', drop = True, inplace= True)

            for treat in res:
                assert len(res[treat].transpose()) == len(self.comp_info)
                for i, comp in enumerate(self.comp_info):
                    res_df.insert(len(res_df.columns), f'{comp}_{treat}', res[treat].transpose()[i])

            return res_df



'''
----------------------------------------------------------------------------------------------------------------------------------------------------
BOTTOM LEVEL: 
Classes that implement specific model ODEs (and if necessary solvers for them). They inherit from a suitable parent class from the
intermediate level to ensure proper likelihood calculation.
----------------------------------------------------------------------------------------------------------------------------------------------------
'''
class RED_SD(Reduced):
    '''
    the GUTS-RED-SD (Stoachastic Death) model
    '''
    def __init__(self):
        super().__init__()

        self.params_info['kd'] = {'name':'kd', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True, "prior": "lognorm(scale=1.0,s=3)"}
        self.params_info['b'] = {'name':'b', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True, "prior": "lognorm(scale=1.0,s=3)"}
        self.params_info['m'] = {'name':'m', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True, "prior": "lognorm(scale=1.0,s=3)"}
        self.params_info['hb'] = {'name':'hb', 'min':1.0e-8, 'max':1.0e3, 'initial':1.0, 'vary':True, "prior": "lognorm(scale=1.0,s=3)"}

        self.state_variables = {
            "D": {"dimensions": ["id", "time"], "observed": False, "y0": [0.0] * self._numCLike},
            "H": {"dimensions": ["id", "time"], "observed": False, "y0": 0.0},
            "survival": {"dimensions": ["id", "time"], "observed": True},
        }

        self._likelihood_func_jax = conditional_survival_hazard_error_model


    def _rhs(self, t, y, params, xc):
        '''
        Right-hand side DGLs 
        xc: list of functions (interpolation over time)
        y: actual model state
        '''
        xc = xc[0]
        dy = y.copy()

        # Damage
        dy[0] = params['kd'] * (xc(t) - y[0])

        # Hazard rate
        h_substance = params['b'] * max(0, y[0] - params['m'])
        h = h_substance + params['hb']

        # Survival
        dy[1] = -h * y[1]

        return dy

    @staticmethod
    def _rhs_jax(t, y, x_in, kd, b, m, hb):
        D, H = y
        dD_dt = kd * (x_in.evaluate(t) - D)

        # Hazard rate
        dH_dt = b * jnp.maximum(0.0, D - m) + hb

        return dD_dt, dH_dt

    @staticmethod
    def _solver_post_processing(results, time, interpolation):
        results["survival"] = jnp.exp(-results["H"])
        results["exposure"] = jax.vmap(interpolation.evaluate)(time)
        return results


class RED_IT(Reduced):
    '''
    the GUTS-RED-IT (Individual Tolerance) model
    '''

    def __init__(self):
        super().__init__()
        self.params_info['kd'] = {'name':'kd', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True, "prior": "lognorm(scale=1,s=3)"}
        self.params_info['m'] = {'name':'m', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True, "prior": "lognorm(scale=1,s=3)"}
        self.params_info['beta'] = {'name':'beta', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True, "prior": "lognorm(scale=1,s=3)"}
        self.params_info['hb'] = {'name':'hb', 'min':1.0e-8, 'max':1.0e3, 'initial':1.0, 'vary':True, "prior": "lognorm(scale=1,s=3)"}
        
        self.state_variables = {
            "D": {"dimensions": ["id", "time"], "observed": False, "y0": [0.0] * self._numCLike},
            "H": {"dimensions": ["id", "time"], "observed": False},
            "survival": {"dimensions": ["id", "time"], "observed": True},
        }

        self._likelihood_func_jax = conditional_survival_hazard_error_model

    def _rhs(self, t, y, params, xc):
        xc = xc[0]
        dy = y.copy()

        # Damage
        dy[0] = params['kd']*(xc(t) - y[0])

        dy[1] = -99

        return dy

    def _solve(self, params, y0, times, xc):        
        #Solve uptake equation
        y = super()._solve(params, y0,  times, xc)

        #Calculate individual tolerance survival
        for i, ystep in enumerate(y):
            if i == 0:
                continue

            t = times[i]

            #Maximum damage to this point
            D_wm = np.max(y[:i+1,0])

            #Calculate survival from ratio of max damage to tolerance threshold.
            F = self.mortality_loglogistic(D_wm, params['m'], params['beta'])
            surv = y[0, -1] * (1.0 - F) * np.exp(-params['hb']*t)
            y[i, -1] = surv

        return y

    @staticmethod
    def _rhs_jax(t, y, x_in, kd):
        D, = y
        C = x_in.evaluate(t)

        dD_dt = kd * (C - D)

        return (dD_dt, )
    
    @staticmethod
    def _solver_post_processing(results, t, interpolation, m, beta, hb, eps):
        """
        TODO: Try alternative formulation. This is computationally simpler and numerically
        more stable:
        log S = log 1.0 + log (1.0 - F) + log exp -hb * t = 0 + log (1.0 - F) - hb * t
        """

        d_max = jnp.squeeze(jnp.array([jnp.max(results["D"][:i+1])+eps for i in range(len(t))]))
        F = jnp.where(d_max > 0, 1.0 / (1.0 + (d_max / m) ** -beta), 0)
        S = 1.0 * (jnp.array([1.0], dtype=float) - F) * jnp.exp(-hb * t)
        results["H"] = - jnp.log(S)
        results["survival"] = S
        results["exposure"] = jax.vmap(interpolation.evaluate)(t)

        return results
    
class Mixture(Reduced):
    extra_dim = "substance"

class RED_SD_DA(Mixture):
    '''
    the GUTS-RED-SD-DA model. This is the SD option of the damage addition guts mixtures model.
    '''
    def __init__(self, num_expos = 1):
        super().__init__()  
        self.num_expos = num_expos
        self._numCLike = num_expos + 1
        self._numSLike = 1

        self._likelihood_func_jax = conditional_survival_hazard_error_model

        self.state_variables = {
            "D": {"dimensions": ["id", "time", "substance"], "observed": False, "y0": [0.0] * num_expos},
            "H": {"dimensions": ["id", "time"], "observed": False, "y0": 0.0},
            "survival": {"dimensions": ["id", "time"], "observed": True},
        }


        ###substance specific params
        for i in range(self.num_expos):
            #dominant rate constants
            self.params_info[f'kd{i+1}'] = {'name':f'kd{i+1}', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True, "dims": "substance"}
            if i == 0:
                #weight factors
                self.params_info[f'w{i+1}'] = {'name':f'w{i+1}', 'initial':1.0, 'vary':False, "dims": "substance"}
            else:
                self.params_info[f'w{i+1}'] = {'name':f'w{i+1}', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True, "dims": "substance"}
        ###shared params
        #killing rate
        self.params_info['b'] = {'name':'b', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True}
        #median of the threshold distribution 
        self.params_info['m'] = {'name':'m', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True}
        #background mortality rate
        self.params_info['hb'] = {'name':'hb', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True}
        #information about the compartments
        self.comp_info = []
        for i in range(self.num_expos):
            self.comp_info.append(f'Scaled damage {i+1}')
        self.comp_info.append('total scaled damage')
        self.comp_info.append('Survival')
    
    def _rhs(self, t, y, params, xc):
        
        dy = y.copy()
        
        # TODO: Paula/Leo: is this the same as before?
        #total damage from the last timestep
        # d_ges_last = y[0]

        # for i in range(self.num_expos):
        #     if i == 0:
        #         continue
        #     else:
        #         d_ges_last += y[i] * params[f'w{i+1}']
        
        d_ges_last = np.sum([params[f'w{i+1}'] * y[i] for i in range(self.num_expos)])

        #Damages
        for i in range(self.num_expos):
            dy[i] = params[f'kd{i+1}'] * (xc[i](t) - y[i])
        
        #Hazard rate; dependant of total damage
        hc = params['b'] * max(0, d_ges_last - params['m'])
        #Adding background mortality
        h = hc + params['hb']
        #survival
        dy[-1] = -h * y[-1]

        return dy
    
    @staticmethod
    def _rhs_jax(t, y, x_in, kd, w, b, m, hb):
        D, H = y
        dD_dt = kd * (x_in.evaluate(t) - D)

        # Hazard rate
        dH_dt = b * jnp.maximum(0.0, jnp.sum(w * D) - m) + hb

        return dD_dt, dH_dt

    @staticmethod
    def _solver_post_processing(results, time, interpolation):
        results["survival"] = jnp.exp(-results["H"])
        results["exposure"] = jax.vmap(interpolation.evaluate)(time)
        return results

    #solver for model ODEs, using scipy.integrate.ode.integrate with 'lsoda' integrator
    
    def _solve(self, params, y0, times, xc):
        
        #defining integrator, initial values and parameters
        int_ode = scipyInt.ode(self._rhs).set_integrator('lsoda')
        int_ode.set_initial_value(y0)
        int_ode.set_f_params(params, xc)
        
        #creating result data structures
        result = [y0]
        #actual integration; insertion of the total damage into the result-list
        for t in times[1:]:
            int_ode.integrate(t)
            res = int_ode.y

            #calculation of total damage for result array
            d_ges = res[0]
            for i in range(self.num_expos):
                if i == 0:
                    continue
                else:
                    d_ges += res[i] * params[f'w{i+1}']
            res[-2] = d_ges
            result.append(res)
        #returns sols; contains [damage1,...,damageN, damagesGES, survivalGES] as columns
        return np.array(result)   
    

class RED_IT_DA(Mixture):
    '''
    the GUTS-RED-IT-DA model. This is the IT option of the damage addition guts mixtures model.
    '''
    
    def __init__(self, num_expos = 1):
        super().__init__()   
        self.num_expos = num_expos
        self._numCLike = num_expos+1
        self._numSLike = 1

        # For the IT model this is equivalent to the hazard_error_model, because
        # IT calculates the hazard as -log(S)
        self._likelihood_func_jax = conditional_survival_error_model

        self.state_variables = {
            "D": {"dimensions": ["id", "time", "substance"], "observed": False, "y0": [0.0] * num_expos},
            "H": {"dimensions": ["id", "time"], "observed": False,},
            "survival": {"dimensions": ["id", "time"], "observed": True},
        }


        ### substance specific parameters
        for i in range(self.num_expos):
            #dominant rate constants
            self.params_info[f'kd{i+1}'] = {'name':f'kd{i+1}', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True, "dims": "substance"}
            if i == 0:
                #weight factors
                self.params_info[f'w{i+1}'] = {'name':f'w{i+1}', 'initial':1.0, 'vary':False, "dims": "substance"}
            else:
                self.params_info[f'w{i+1}'] = {'name':f'w{i+1}', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True, "dims": "substance"}
        ### shared parameters
        #median of the threshold distribution 
        self.params_info['m'] = {'name':'m', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True}
        #shape parameter
        self.params_info['beta'] = {'name':'beta', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True}
        #background mortality
        self.params_info['hb'] = {'name':'hb', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True}
        #information about the compartments
        self.comp_info = []
        for i in range(self.num_expos):
            self.comp_info.append(f'scaled damage {i+1}')
        self.comp_info.append('total scaled damage')
        self.comp_info.append('survival')
            
    def _rhs(self, t, y, params, xc):

        dy = y.copy()
        
        for i in range(self.num_expos):
            dy[i] = params[f'kd{i+1}'] * (xc[i](t) - y[i])
        
        return dy 
        
    
    def _solve(self, params, y0, times, xc):

        int_ode = scipyInt.ode(self._rhs).set_integrator('lsoda')
        int_ode.set_initial_value(y0)
        int_ode.set_f_params(params, xc)
        
        #creating result data structures
        result = [y0]
        #actual integration; insertion of the total damage (class attribute) into the result-list
        for t in times[1:]:
            int_ode.integrate(t)
            res = int_ode.y
            
            #calculation of total damage for result array
            d_ges = np.sum([params[f'w{i+1}'] * res[i] for i in range(self.num_expos)])

            res[-2] = d_ges
            result.append(res)
               
        y = np.array(result)

        #sols/y now contains the values for [damage1,...,damageN, damagesGES] and placeholders for 
        #the survival which are calculated in the following since the dependance of the 
        #maximum total damage cannot be realised within the integrator
        
        #determine the maximum total damage for every timestep and calculate the resulting survival
        for i, ystep in enumerate(y):
            if i == 0:
                continue
            
            t = times[i]

            #Maximum total damage to this point
            D_wm = np.max(y[:i+1,-2])
            
            #cumulative loglogistic distribution
            F = self.mortality_loglogistic(D_wm, params['m'], params['beta']) 
            
            #survival at time t/times[i]
            surv = y[0, -1] * (1.0 - F) * np.exp(-params['hb']*t)
            #replacement of the placeholder with the actual survival value
            y[i, -1] = surv
        return y
    
    @staticmethod
    def _rhs_jax(t, y, x_in, kd):
        D, = y
        C = x_in.evaluate(t)

        dD_dt = kd * (C - D)

        return (dD_dt, )

    @staticmethod
    def _solver_post_processing(results, t, interpolation, w, m, beta, hb, eps):
        # sum weighted damage
        D_sum = jnp.sum(results["D"] * w, axis=1)
        
        # calculate IT
        d_max = jnp.squeeze(jnp.array([jnp.max(D_sum[:i+1])+eps for i in range(len(t))]))
        F = jnp.where(d_max > 0, 1.0 / (1.0 + (d_max / m) ** -beta), 0)
        S = 1.0 * (jnp.array([1.0], dtype=float) - F) * jnp.exp(-hb * t)
        results["H"] = - jnp.log(S)
        results["survival"] = S
        results["exposure"] = jax.vmap(interpolation.evaluate)(t)

        return results

               
class RED_SD_IA(Mixture):
    '''
    the GUTS-RED-SD-IA model. This is the SD option of the independant action guts mixtures model.
    '''
    
    def __init__(self, num_expos = 1):
        super().__init__()     
        self.num_expos = num_expos
        self._numCLike = num_expos
        self._numSLike = num_expos + 2

        self._likelihood_func_jax = conditional_survival_hazard_error_model

        self.state_variables = {
            "D": {"dimensions": ["id", "time", "substance"], "observed": False, "y0": [0.0] * num_expos},
            "H_i": {"dimensions": ["id", "time", "substance"], "observed": False, "y0": [0.0] * num_expos},
            "H": {"dimensions": ["id", "time"], "observed": False},
            "survival": {"dimensions": ["id", "time"], "observed": True},
        }

        ###substance specific params
        for i in range(self.num_expos):
            #dominant rate constants
            self.params_info[f'kd{i+1}'] = {'name':f'kd{i+1}', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True, "dims": "substance",}
            #killing rates
            self.params_info[f'b{i+1}'] = {'name':f'b{i+1}', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True, "dims": "substance", }
            #medians of threshold distribution
            self.params_info[f'm{i+1}'] = {'name':f'm{i+1}', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True, "dims": "substance", }
        #background mortality rate
        self.params_info['hb'] = {'name':'hb', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True,}
        #information about the compartments
        self.comp_info = []
        for i in range(self.num_expos):
            self.comp_info.append(f'damage {i+1}')
        for i in range(self.num_expos):
            self.comp_info.append(f'survival {i+1}')
        self.comp_info.append('background survival')
        self.comp_info.append('total survival')
    
    def _rhs(self, t, y, params, xc):

        dy = y.copy()
        
        #damages
        for i in range(self.num_expos):
            dy[i] = params[f'kd{i+1}'] * (xc[i](t) - y[i])
        
        hzd_rates = []
        #Hazard rates
        for i in range(self.num_expos):
            hzd_temp = params[f'b{i+1}'] * max(0, y[i] - params[f'm{i+1}'])
            hzd_rates.append(hzd_temp)

        #substance induced mortality
        for i in range(self.num_expos):
            dy[self.num_expos + i] = -hzd_rates[i] * y[self.num_expos + i]
                    
        #background mortality
        dy[self.num_expos + self.num_expos] = -params['hb'] * y[self.num_expos + self.num_expos]
        
        #placeholder for mulitplied survival
        dy[-1] = -99

        return dy   
    
    @staticmethod
    def _rhs_jax(t, y, x_in, kd, b, m):
        """Calculates the hazard of each component in x_in separately.
        """
        D, H = y
        dD_dt = kd * (x_in.evaluate(t) - D)

        # Hazard rates chemicals
        dH_i_dt = b * jnp.maximum(0.0, D - m)

        return dD_dt, dH_i_dt

    @staticmethod
    def _solver_post_processing(results, time, interpolation, hb):
        """
        Derivation:

        $$
        S = \prod_i S_i  
        log(S) = \sum_i \log(S_i)
        S = \exp(-H)
        \log(S) = sum_i \log(\exp(-H_i)) = sum_i -H_i
        S = exp(\sum_i -H_i) = \exp(- \sum_i H_i)
        $$

        cumulative hazard from the background hazard $dH_bg/dt = h_b$  is added as the
        closed form solution  $H_bg = h_b * t$
        """
        results["H"] = jnp.sum(results["H_i"], axis=1) + hb * time
        results["survival"] = jnp.exp(-results["H"])
        results["exposure"] = jax.vmap(interpolation.evaluate)(time)

        return results


    def _solve(self, params, y0, times, xc):
        
        #defining integrator, initial values and parameters
        int_ode = scipyInt.ode(self._rhs).set_integrator('lsoda')
        int_ode.set_initial_value(y0)
        int_ode.set_f_params(params, xc)
            
        #creating result data structures
        sols = [y0]
        
        #integration + insertion of the total survival into the result-list
        for t in times[1:]:
            int_ode.integrate(t)
            res = int_ode.y
            
            #multiplikation of survivals
            surv_ges = 1
            for i in range(self.num_expos+1):
                surv_ges = surv_ges * (res[self.num_expos + i] / sols[0][self.num_expos + i])
        
            res[-1] = surv_ges * sols[0][self.num_expos + self.num_expos]
            
            sols.append(res)
        #returns sols; contains [damage1,..., damageN, survival1, ..., survivalN, survivalHB, survivalGES] as columns
        return np.array(sols)                    
                    

class RED_IT_IA(Mixture):
    '''
    the GUTS-RED-IT-IA model. This is the IT option of the independant action guts mixtures model.
    '''    
    
    def __init__(self, num_expos = 1):
        super().__init__()     
        self._numSLike = num_expos + 2
        self._numCLike = num_expos
        self.num_expos = num_expos

        self._likelihood_func_jax = conditional_survival_hazard_error_model

        self.state_variables = {
            "D": {"dimensions": ["id", "time", "substance"], "observed": False, "y0": [0.0] * num_expos},
            "H": {"dimensions": ["id", "time",], "observed": False, },
            "survival": {"dimensions": ["id", "time"], "observed": True},
        }

        #substance specific params
        for i in range(self.num_expos):
            #dominant rate constants
            self.params_info[f'kd{i+1}'] = {'name':f'kd{i+1}', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True, "dims": "substance",}
            #medians of threshold distribution
            self.params_info[f'm{i+1}'] = {'name':f'm{i+1}', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True, "dims": "substance",}
            #shape parameters for the distributions of thresholds
            self.params_info[f'beta{i+1}'] = {'name':f'beta{i+1}', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True, "dims": "substance",}
        #background mortality rate
        self.params_info['hb'] = {'name':'hb', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True}
        #information about the compartments
        self.comp_info = []
        for i in range(self.num_expos):
            self.comp_info.append(f'damage {i+1}')
        for i in range(self.num_expos):
            self.comp_info.append(f'survival {i+1}')
        self.comp_info.append('background survival')
        self.comp_info.append('total survival')
            
    def _rhs(self, t, y, params, xc):

        dy = y.copy()
        
        #damages
        for i in range(self.num_expos):
            dy[i] = params[f'kd{i+1}'] * (xc[i](t) - y[i])
        
        return dy 
        
    def _solve(self, params, y0, times, xc):
         
        #solve uptake equation
        y = super()._solve(params, y0,  times, xc)
        
        for i, ystep in enumerate(y):
            if i == 0:
                continue
            
            t = times[i]
            
            Ds_max = []
            #maximum damages to this point
            for j in range(self.num_expos):
                D_max_temp = np.max(y[:i+1, j])
                Ds_max.append(D_max_temp)
                
            Fs = []
            #probability distributions
            for j in range(self.num_expos):
                F_temp = self.mortality_loglogistic(Ds_max[j], params[f'm{j+1}'], params[f'beta{j+1}'])
                Fs.append(F_temp)
            
            #background mortality
            surv_bg = y[0,self.num_expos + self.num_expos] * np.exp(-params['hb']*t)
            y[i,self.num_expos + self.num_expos] = surv_bg
            
            #survivals
            for j in range(self.num_expos):
                y[i, self.num_expos + j] = y[0, self.num_expos + j] * (1.0 - Fs[j])
                
            #multiplikation of survivals
            surv_ges = 1
            for j in range(self.num_expos + 1):
                surv_ges = surv_ges * (y[i, self.num_expos + j] / y[0, self.num_expos + j])
            
            #if there are different numbers of organisms per substance/treatment it must be defined which number 
            #should be used for the overall survival, atm. it is the number from the control groups
            y[i, -1] = surv_ges * y[0, self.num_expos]

        return y  
    
    @staticmethod
    def _rhs_jax(t, y, x_in, kd):
        D, = y
        C = x_in.evaluate(t)

        dD_dt = kd * (C - D)

        return (dD_dt, )

    @staticmethod
    def _solver_post_processing(results, t, interpolation, m, beta, hb, eps):
        # calculate IT and take the maximum over the time dimension for each damage
        d_max = jnp.squeeze(jnp.array([jnp.max(results["D"][:i+1], axis=0)+eps for i in range(len(t))]))
        
        # This equation is equivalent to the inverse of S described in Bart et al. 2021 for IT models
        # S = 1 / (1+d_max/m) ** beta = 1 - F 
        # with F = 1 - 1 / (1+d_max / m) ** -beta
        # note the difference in the minus sign in the exponent (beta)
        F = jnp.where(d_max > 0, 1.0 / (1.0 + (d_max / m) ** -beta), 0)

        # take the product of the CDFs of the individual threshold functions then multiply
        # with the survival function of the background hazard
        S = 1.0 * jnp.prod(jnp.array([1.0], dtype=float) - F, axis=1) * jnp.exp(-hb * t)
        results["H"] = - jnp.log(S)
        results["survival"] = S
        results["exposure"] = jax.vmap(interpolation.evaluate)(t)
        
        return results
    
class BufferGUTS(Reduced):
    extra_dim = "exposure_path"

class BufferGUTS_SD(BufferGUTS):
    '''
    The BufferGUTS SD (Stochastic Death) model for event based, discretized exposures as experienced by above-ground terrestrial arthropods
    '''
    def __init__(self):
        super().__init__()
        self._numCLike = 2
        self.comp_info = [
            'Buffer',
            'Damage',
            'Survival']

        self.state_variables = {
            "B": {"dimensions": ["id", "time"], "observed": False, "y0": 0.0},
            "D": {"dimensions": ["id", "time"], "observed": False, "y0": 0.0},
            "H": {"dimensions": ["id", "time"], "observed": False, "y0": 0.0},
            "survival": {"dimensions": ["id", "time"], "observed": True},
        }

        self._likelihood_func_jax = conditional_survival_hazard_error_model


        self.params_info['kd'] = {'name':'kd', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True}
        self.params_info['b'] = {'name':'b', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True}
        self.params_info['m'] = {'name':'m', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True}
        self.params_info['hb'] = {'name':'hb', 'min':1.0e-10, 'max':1.0e3, 'initial':1e-3, 'vary':True}
        self.params_info['eta'] = {'name':'eta', 'min':0, 'max':1.0e6, 'initial':60*24, 'vary':False}

    def _rhs(self, t, y, params, xc):
        xc = xc[0]
        dy = y.copy()
        # buffer
        if xc(t) > y[0]:
            speed = params['eta']
        else:
            speed = params["kd"]
        dy[0] = speed*(xc(t) -y[0])

        # Damage
        dy[1] = params['kd'] * (y[0] - y[1])

        # Hazard rate
        h_substance = params['b'] * max(0, y[1] - params['m'])
        h = h_substance + params['hb']

        # Survival
        dy[2] = -h * y[2]

        return dy

    @staticmethod
    def _rhs_jax(t, y, x_in, eta, kd, b, m, hb):
        B, D, H = y

        C = x_in.evaluate(t)

        buffer_filling_rate = eta * (C - B)
        buffer_depletion_rate = kd * (C - B)

        dB_dt = jnp.where(C >= B, buffer_filling_rate, buffer_depletion_rate)

        dD_dt = kd * (B - D)

        dH_dt = (b * jnp.maximum((D - m),jnp.array([0.0], dtype=float)) + hb)
        
        return dB_dt, dD_dt, dH_dt
        
    @staticmethod
    def _solver_post_processing(results, time, interpolation):
        results["exposure"] = jax.vmap(interpolation.evaluate)(time)
        results["survival"] = jnp.exp(-results["H"])
        return results

class BufferGUTS_IT(BufferGUTS):
    '''
    The BufferGUTS IT (Individual Tolerance) model for event based, discretized exposures as experienced by above-ground terrestrial arthropods
    '''
    def __init__(self):
        super().__init__()
        self._numCLike = 2
        self.comp_info = [
            'Buffer',
            'Damage',
            'Survival']    


        self.state_variables = {
            "B": {"dimensions": ["id", "time"], "observed": False, "y0": 0.0},
            "D": {"dimensions": ["id", "time"], "observed": False, "y0": 0.0},
            "H": {"dimensions": ["id", "time"], "observed": False},
            "survival": {"dimensions": ["id", "time"], "observed": True},
        }

        self._likelihood_func_jax = conditional_survival_hazard_error_model

        self.params_info['kd'] = {'name':'kd', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True}
        self.params_info['m'] = {'name':'m', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True}
        self.params_info['beta'] = {'name':'beta', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True}
        self.params_info['hb'] = {'name':'hb', 'min':1.0e-10, 'max':1.0e3, 'initial':1e-3, 'vary':True}
        self.params_info['eta'] = {'name':'eta', 'min':0, 'max':1.0e6, 'initial':60*24, 'vary':False}

    def _rhs(self, t, y, params, xc):
        xc = xc[0]
        dy = y.copy()

        if xc(t) > y[0]:
            speed = params["eta"]
        else:
            speed = params["kd"]
        dy[0] = speed*(xc(t) -y[0])

        # Damage
        dy[1] = params['kd'] * (y[0] - y[1])

        dy[2] = -99

        return dy

    @staticmethod
    def _rhs_jax(t, y, x_in, eta, kd):
        B, D = y 

        C = x_in.evaluate(t)

        buffer_filling_rate = eta * (C - B)
        buffer_depletion_rate = kd * (C - B)

        dB_dt = jnp.where(C >= B, buffer_filling_rate, buffer_depletion_rate)

        dD_dt = kd * (B - D)

        return dB_dt, dD_dt


    def _solve(self, params, y0, times, xc):        
        #Solve uptake equation
        y = super()._solve(params, y0,  times, xc)

        #Calculate individual tolerance survival
        for i, ystep in enumerate(y):
            if i == 0:
                continue

            t = times[i]

            #Maximum damage to this point
            D_wm = np.max(y[:i+1,1])

            #Calculate survival from ratio of max damage to tolerance threshold.
            F = self.mortality_loglogistic(D_wm, params['m'], params['beta'])
            surv = y[0, -1] * (1.0 - F) * np.exp(-params['hb']*t)
            y[i, -1] = surv

        return y
    
    @staticmethod
    def _solver_post_processing(results, t, interpolation, m, beta, hb, eps):
        """
        TODO: Try alternative formulation. This is computationally simpler and numerically
        more stable:
        log S = log 1.0 + log (1.0 - F) + log exp -hb * t = 0 + log (1.0 - F) - hb * t
        """

        d_max = jnp.squeeze(jnp.array([jnp.max(results["D"][:i+1])+eps for i in range(len(t))]))
        F = jnp.where(d_max > 0, 1.0 / (1.0 + (d_max / m) ** -beta), 0)
        S = 1.0 * (jnp.array([1.0], dtype=float) - F) * jnp.exp(-hb * t)
        results["H"] = - jnp.log(S)
        results["survival"] = S
        return results


class BufferGUTS_SD_DA(BufferGUTS):
    '''
    The BufferGUTS SD (Stochastic Death) model for multiple exposure paths for event based, discretized exposures as experienced by above-ground terrestrial arthropods.
    The Damage Addition (DA) variant assumes individual uptake kinetics per exposure path.
    '''
    def __init__(self, num_expos = 1):
        super().__init__()  
        self.num_expos = num_expos
        self._numCLike = 2 * num_expos + 1
        self._numSLike = 1


        self.state_variables = {
            "B": {"dimensions": ["id", "time", self.extra_dim], "observed": False, "y0": [0.0] * self.num_expos},
            "D": {"dimensions": ["id", "time", self.extra_dim], "observed": False, "y0": [0.0] * self.num_expos},
            "H": {"dimensions": ["id", "time"], "observed": False, "y0": 0.0},
            "survival": {"dimensions": ["id", "time"], "observed": True},
        }

        self._likelihood_func_jax = conditional_survival_hazard_error_model


        ###substance specific params
        for i in range(self.num_expos):
            #dominant rate constants
            if i == 0:
                self.params_info[f'w{i+1}'] = {'name':f'w{i+1}', 'initial':1.0, 'vary':False, "dims": self.extra_dim}
            if i > 0:
                self.params_info[f'w{i+1}'] = {'name':f'w{i+1}', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True, "dims": self.extra_dim}
            
            self.params_info[f'kd{i+1}'] = {'name':f'kd{i+1}', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True, "dims": self.extra_dim}
                
        ###shared params
        #killing rate
        self.params_info['b'] = {'name':'b', 'min':1.0e-6, 'max':1.0e3, 'initial':1.0, 'vary':True}
        #median of the threshold distribution 
        self.params_info['m'] = {'name':'m', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True}
        #background mortality rate
        self.params_info['hb'] = {'name':'hb', 'min':1.0e-10, 'max':1.0e3, 'initial':1e-3, 'vary':True}
        self.params_info['eta'] = {'name':'eta', 'min':0, 'max':1.0e6, 'initial':60*24, 'vary':False}
        #information about the compartments
        self.comp_info = []
        for i in range(self.num_expos):
            self.comp_info.append(f'Buffer {i+1}')
        for i in range(self.num_expos):
            self.comp_info.append(f'Damage {i+1}')
        self.comp_info.append('Damage Sum')
        self.comp_info.append('Survival')
    
    def _rhs(self, t, y, params, xc):
        
        dy = y.copy()
        
        damage_sum = 0
        for i in range(self.num_expos):
            # Buffer
            if xc[i](t) > y[i]:
                speed = params["eta"]
            else:
                speed = params[f'kd{i+1}']
            dy[i] = speed*(xc[i](t) -y[i])

            # Damage
            new_damage = params[f'kd{i+1}'] * (y[i] - y[self.num_expos+i])
            dy[self.num_expos+i] = new_damage
            if i == 0:
                damage_sum += new_damage
            else:
                damage_sum += new_damage * params[f'w{i+1}']

        # Damagesum
        dy[-2] = damage_sum #np.sum(dy[self.num_expos:self.num_expos*2])
        
        #Hazard rate; dependant of total damage
        hc = params['b'] * max(0, y[-2] - params['m'])
        #Adding background mortality
        h = hc + params['hb']
        #survival
        dy[-1] = -h * y[-1]

        return dy

    @staticmethod
    def _rhs_jax(t, y, x_in, eta, kd, b, m, hb, w):

        B, D, H = y

        C = x_in.evaluate(t)

        buffer_filling_rate = eta * (C - B)
        buffer_depletion_rate = kd * (C - B)

        dB_dt = jnp.where(C >= B, buffer_filling_rate, buffer_depletion_rate)

        dD_dt = kd * (B - D)

        dH_dt = (b * jnp.maximum((jnp.sum(D * w) - m),jnp.array([0.0], dtype=float)) + hb)

        return dB_dt, dD_dt, dH_dt

    @staticmethod
    def _solver_post_processing(results, time, interpolation):
        results["exposure"] = jax.vmap(interpolation.evaluate)(time)
        results["survival"] = jnp.exp(-results["H"])
        return results

    
class BufferGUTS_SD_CA(BufferGUTS):
    '''
    The BufferGUTS SD (Stochastic Death) model for multiple exposure paths for event based, discretized exposures as experienced by above-ground terrestrial arthropods.
    The Concentration Addition (DA) variant assumes the same uptake kinetic for all exposure paths.
    '''
    def __init__(self, num_expos = 1):
        super().__init__()  
        self.num_expos = num_expos
        self._numCLike = num_expos + 2
        self._numSLike = 1

        self.state_variables = {
            "B": {"dimensions": ["id", "time", self.extra_dim], "observed": False, "y0": [0.0] * self.num_expos},
            "D": {"dimensions": ["id", "time"], "observed": False, "y0": 0.0},
            "H": {"dimensions": ["id", "time"], "observed": False, "y0": 0.0},
            "survival": {"dimensions": ["id", "time"], "observed": True},
        }

        self._likelihood_func_jax = conditional_survival_hazard_error_model


        ###substance specific params
        for i in range(self.num_expos):
            if i == 0:
                self.params_info[f'w{i+1}'] = {'name':f'w{i+1}', 'initial':1.0, 'vary':False, "dims": self.extra_dim}
            if i > 0:
                self.params_info[f'w{i+1}'] = {'name':f'w{i+1}', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True, "dims": self.extra_dim}
        ###shared params
        #dominant rate constants
        self.params_info['kd'] = {'name':'kd', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True}
        #killing rate
        self.params_info['b'] = {'name':'b', 'min':1.0e-6, 'max':1.0e3, 'initial':1.0, 'vary':True}
        #median of the threshold distribution 
        self.params_info['m'] = {'name':'m', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True}
        #background mortality rate
        self.params_info['hb'] = {'name':'hb', 'min':1.0e-10, 'max':1.0e3, 'initial':1e-3, 'vary':True}
        self.params_info['eta'] = {'name':'eta', 'min':0, 'max':1.0e6, 'initial':60*24, 'vary':False}
        #information about the compartments
        self.comp_info = []
        for i in range(self.num_expos):
            self.comp_info.append(f'Buffer {i+1}')
        self.comp_info.append('Buffer Sum')
        self.comp_info.append('Damage')
        self.comp_info.append('Survival')
    
    def _rhs(self, t, y, params, xc):
        
        dy = y.copy()
        
        buffer_sum = 0
        for i in range(self.num_expos):
            # Buffer
            if xc[i](t) > y[i]:
                speed = params["eta"]
            else:
                speed = params['kd']
            new_buffer = speed*(xc[i](t) -y[i])
            dy[i] = new_buffer

            if i == 0:
                buffer_sum += new_buffer
            else:
                buffer_sum += new_buffer * params[f'w{i+1}']

        # Buffer sum
        dy[-3] = buffer_sum

        dy[-2] = params['kd'] * (y[-3] - y[-2])
        #Hazard rate; dependant of total damage
        hc = params['b'] * max(0, y[-2] - params['m'])
        #Adding background mortality
        h = hc + params['hb']
        #survival
        dy[-1] = -h * y[-1]

        return dy

    @staticmethod
    def _rhs_jax(t, y, x_in, eta, kd, b, m, hb, w):
        """RHS accordint to Leo's buffer model"""

        B, D, H = y

        C = x_in.evaluate(t)

        buffer_filling_rate = eta * (C - B)
        buffer_depletion_rate = kd * (C - B)

        dB_dt = jnp.where(C >= B, buffer_filling_rate, buffer_depletion_rate)

        dD_dt = kd * (jnp.sum(B * w) - D)

        dH_dt = (b * jnp.maximum((D - m),jnp.array([0.0], dtype=float)) + hb)
        
        return dB_dt, dD_dt, dH_dt

    @staticmethod
    def _solver_post_processing(results, time, interpolation):
        results["exposure"] = jax.vmap(interpolation.evaluate)(time)
        results["survival"] = jnp.exp(-results["H"])
        return results

    
class BufferGUTS_IT_DA(BufferGUTS):
    '''
    The BufferGUTS IT (Individual Tolerance) model for multiple exposure paths for event based, discretized exposures as experienced by above-ground terrestrial arthropods.
    The Damage Addition (DA) variant assumes individual uptake kinetics per exposure path.
    '''
    
    def __init__(self, num_expos = 1):
        super().__init__()  
        self.num_expos = num_expos
        self._numCLike = 2 * num_expos + 1
        self._numSLike = 1

        self.state_variables = {
            "B": {"dimensions": ["id", "time", self.extra_dim], "observed": False, "y0": [0.0] * self.num_expos},
            "D": {"dimensions": ["id", "time"], "observed": False, "y0": 0.0},
            "H": {"dimensions": ["id", "time"], "observed": False},
            "survival": {"dimensions": ["id", "time"], "observed": True},
        }

        self._likelihood_func_jax = conditional_survival_hazard_error_model

        ### substance specific parameters
        for i in range(self.num_expos):
            #dominant rate constants
            if i == 0:
                self.params_info[f'w{i+1}'] = {'name':f'w{i+1}', 'initial':1.0, 'vary':False, "dims": self.extra_dim}
            if i > 0:
                self.params_info[f'w{i+1}'] = {'name':f'w{i+1}', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True, "dims": self.extra_dim}

            self.params_info[f'kd{i+1}'] = {'name':f'kd{i+1}', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True, "dims": self.extra_dim}

        ### shared parameters
        #median of the threshold distribution 
        self.params_info['m'] = {'name':'m', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True}
        #shape parameter
        self.params_info['beta'] = {'name':'beta', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True}
        #background mortality
        self.params_info['hb'] = {'name':'hb', 'min':1.0e-10, 'max':1.0e3, 'initial':1e-3, 'vary':True}
        self.params_info['eta'] = {'name':'eta', 'min':0, 'max':1.0e6, 'initial':60*24, 'vary':False}
        #information about the compartments
        self.comp_info = []
        for i in range(self.num_expos):
            self.comp_info.append(f'Buffer {i+1}')
        for i in range(self.num_expos):
            self.comp_info.append(f'Damage {i+1}')
        self.comp_info.append('Damage Sum')
        self.comp_info.append('Survival')
            
    def _rhs(self, t, y, params, xc):

        dy = y.copy()
        damage_sum = 0
        for i in range(self.num_expos):
            # Buffer
            if xc[i](t) > y[i]:
                speed = params["eta"]
            else:
                speed = params[f'kd{i+1}']
            dy[i] = speed*(xc[i](t) -y[i])
            # Damage
            new_damage = params[f'kd{i+1}'] * (y[i] - y[self.num_expos+i])
            dy[self.num_expos+i] = new_damage
            if i == 0:
                damage_sum += new_damage
            else:
                damage_sum += new_damage * params[f'w{i+1}']

        # Damagesum
        dy[-2] = damage_sum

        return dy

    @staticmethod
    def _rhs_jax(t, y, x_in, eta, kd, w):
        B, D = y 

        C = x_in.evaluate(t)

        buffer_filling_rate = eta * (C - B)
        buffer_depletion_rate = kd *(C - B)

        dB_dt = jnp.where(C >= B, buffer_filling_rate, buffer_depletion_rate)
        
        dD_dt = jnp.sum(kd * (B - D) * w)

        return dB_dt, dD_dt

    @staticmethod
    def _solver_post_processing(results, t, interpolation, m, beta, hb, eps):
        """
        TODO: Try alternative formulation. This is computationally simpler and numerically
        more stable:
        log S = log 1.0 + log (1.0 - F) + log exp -hb * t = 0 + log (1.0 - F) - hb * t
        """
        results["exposure"] = jax.vmap(interpolation.evaluate)(t)

        d_max = jnp.squeeze(jnp.array([jnp.max(results["D"][:i+1])+eps for i in range(len(t))]))
        F = jnp.where(d_max > 0, 1.0 / (1.0 + (d_max / m) ** -beta), 0)
        S = 1.0 * (jnp.array([1.0], dtype=float) - F) * jnp.exp(-hb * t)
        results["H"] = - jnp.log(S)
        results["survival"] = S
        return results
        

class BufferGUTS_IT_CA(BufferGUTS):
    '''
    The BufferGUTS IT (Individual Tolerance) model for multiple exposure paths for event based, discretized exposures as experienced by above-ground terrestrial arthropods.
    The Concentration Addition (DA) variant assumes the same uptake kinetic for all exposure paths.
    '''
    
    def __init__(self, num_expos = 1):
        super().__init__()  
        self.num_expos = num_expos
        self._numCLike = num_expos + 2
        self._numSLike = 1


        self.state_variables = {
            "B": {"dimensions": ["id", "time", self.extra_dim], "observed": False, "y0": [0.0] * self.num_expos},
            "D": {"dimensions": ["id", "time"], "observed": False, "y0": 0.0},
            "H": {"dimensions": ["id", "time"], "observed": False},
            "survival": {"dimensions": ["id", "time"], "observed": True},
        }

        self._likelihood_func_jax = conditional_survival_hazard_error_model


        ### substance specific parameters
        for i in range(self.num_expos):
            if i == 0:
                self.params_info[f'w{i+1}'] = {'name':f'w{i+1}', 'initial':1.0, 'vary':False, "dims": self.extra_dim}
            if i > 0:
                self.params_info[f'w{i+1}'] = {'name':f'w{i+1}', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True, "dims": self.extra_dim}

        ### shared parameters
        #dominant rate constants
        self.params_info['kd'] = {'name':'kd', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True}
        #median of the threshold distribution 
        self.params_info['m'] = {'name':'m', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True}
        #shape parameter
        self.params_info['beta'] = {'name':'beta', 'min':1.0e-3, 'max':1.0e3, 'initial':1.0, 'vary':True}
        #background mortality
        self.params_info['hb'] = {'name':'hb', 'min':1.0e-10, 'max':1.0e3, 'initial':1e-3, 'vary':True}
        self.params_info['eta'] = {'name':'eta', 'min':0, 'max':1.0e6, 'initial':60*24, 'vary':False}
        #information about the compartments
        self.comp_info = []
        for i in range(self.num_expos):
            self.comp_info.append(f'Buffer {i+1}')
        self.comp_info.append('Buffer Sum')
        self.comp_info.append('Damage')
        self.comp_info.append('Survival')
            
    def _rhs(self, t, y, params, xc):

        dy = y.copy()
        buffer_sum = 0
        for i in range(self.num_expos):
            # Buffer
            if xc[i](t) > y[i]:
                speed = params["eta"]
            else:
                speed = params['kd']
            new_buffer = speed*(xc[i](t) -y[i])
            dy[i] = new_buffer
            if i == 0:
                buffer_sum += new_buffer
            else:
                buffer_sum += new_buffer * params[f'w{i+1}']

        # Buffer sum
        dy[-3] = buffer_sum

        dy[-2] = params['kd'] * (y[-3] - y[-2])

        return dy
        
    @staticmethod
    def _rhs_jax(t, y, x_in, eta, kd, w):
        B, D = y 

        C = x_in.evaluate(t)

        buffer_filling_rate = eta * (C - B)
        buffer_depletion_rate = kd * (C - B)

        dB_dt = jnp.where(C >= B, buffer_filling_rate, buffer_depletion_rate)

        dD_dt = kd * (jnp.sum(B * w) - D)

        return dB_dt, dD_dt
    
    def _solve(self, params, y0, times, xc):

        #sols/y now contains the values for [damage1,...,damageN, damagesGES] and placeholders for 
        #the survival which are calculated in the following since the dependance of the 
        #maximum total damage cannot be realised within the integrator
        y = super()._solve(params, y0,  times, xc)
        #determine the maximum total damage for every timestep and calculate the resulting survival
        for i, ystep in enumerate(y):
            if i == 0:
                continue
            
            t = times[i]

            #Maximum total damage to this point
            D_wm = np.max(y[:i+1,-2])
            
            #cumulative loglogistic distribution
            F = self.mortality_loglogistic(D_wm, params['m'], params['beta']) 
            
            #survival at time t/times[i]
            surv = y[0, -1] * (1.0 - F) * np.exp(-params['hb']*t)
            #replacement of the placeholder with the actual survival value
            y[i, -1] = surv

        return y

    @staticmethod
    def _solver_post_processing(results, t, interpolation, m, beta, hb, eps):
        """
        TODO: Try alternative formulation. This is computationally simpler and numerically
        more stable:
        log S = log 1.0 + log (1.0 - F) + log exp -hb * t = 0 + log (1.0 - F) - hb * t
        """
        results["exposure"] = jax.vmap(interpolation.evaluate)(t)

        d_max = jnp.squeeze(jnp.array([jnp.max(results["D"][:i+1])+eps for i in range(len(t))]))
        F = jnp.where(d_max > 0, 1.0 / (1.0 + (d_max / m) ** -beta), 0)
        S = 1.0 * (jnp.array([1.0], dtype=float) - F) * jnp.exp(-hb * t)
        results["H"] = - jnp.log(S)
        results["survival"] = S
        return results
