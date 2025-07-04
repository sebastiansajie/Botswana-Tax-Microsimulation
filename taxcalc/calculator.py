"""
PIT (personal income tax) Calculator class.
"""
# CODING-STYLE CHECKS:
# pycodestyle calculator.py
# pylint --disable=locally-disabled calculator.py
#
# pylint: disable=too-many-lines
# pylintx: disable=no-value-for-parameter,too-many-lines

import csv
import os
import json
import re
import copy
import numpy as np
import pandas as pd


import importlib

# Contrived example of generating a module named as a string
#full_module_name = "taxcalc.functions." + "net_salary_income"

# The file gets executed upon import, as expected.
#mymodule = importlib.import_module(full_module_name)

f = open('global_vars.json')
vars = json.load(f)

if vars['pit']:
    #pit_function_names_file = 'taxcalc'+'/'+vars['pit_function_names_filename']
    #f = open(pit_function_names_file)
    #self.pit_function_names = json.load(f)
    pit_oname = vars["pit_functions_filename"][:-3]
    pit_imp_statement = "from taxcalc." + pit_oname + " import *"
    exec(pit_imp_statement)

    """
    from taxcalc.functions import (net_salary_income, net_rental_income,
                                   income_business_profession,
                                   total_other_income, gross_total_income,
                                   itemized_deductions, deduction_10AA,
                                   taxable_total_income,
                                   tax_stcg_splrate, tax_ltcg_splrate,
                                   tax_specialrates, current_year_losses,
                                   brought_fwd_losses, agri_income, pit_liability)
    """
if vars['cit']:
    #CIT_VAR_INFO_FILENAME = 'taxcalc/'+vars['cit_records_variables_filename']
    #self.max_lag_years = vars['cit_max_lag_years']
    cit_function_names_file = 'taxcalc/'+vars['cit_function_names_filename']
    f = open(cit_function_names_file)
    cit_function_names = json.load(f)
    #print('self.cit_function_names ', self.cit_function_names)
    cit_oname = vars["cit_functions_filename"][:-3]
    cit_imp_statement = "from taxcalc." + cit_oname + " import *"
    exec(cit_imp_statement)         
    """
    from taxcalc.corpfunctions import (total_other_income_cit, depreciation_PM,
                                       corp_income_business_profession,
                                       corp_GTI_before_set_off, GTI_and_losses,
                                       cit_liability)
    """
if vars['vat']:
    #vat_function_names_file = 'taxcalc/'+vars['vat_function_names_filename']
    #f = open(vat_function_names_file)
    #self.vat_function_names = json.load(f)
    vat_oname = vars["vat_functions_filename"][:-3]
    vat_imp_statement = "from taxcalc." + vat_oname + " import *"
    exec(vat_imp_statement)

#print("global in calc ")                

from taxcalc.policy import Policy
from taxcalc.records import Records
from taxcalc.corprecords import CorpRecords
from taxcalc.gstrecords import GSTRecords
from taxcalc.growfactors import GrowFactors
# import pdb


class Calculator(object):
    """
    Constructor for the Calculator class.

    Parameters
    ----------
    policy: Policy class object
        this argument must be specified and object is copied for internal use

    records: Records class object
        this argument must be specified and object is copied for internal use

    corprecords: CorpRecords class object
        this argument must be specified and object is copied for internal use

    gstrecords: GSTRecords class object
        this argument must be specified and object is copied for internal use

    verbose: boolean
        specifies whether or not to write to stdout data-loaded and
        data-extrapolated progress reports; default value is true.

    sync_years: boolean
        specifies whether or not to synchronize policy year and records year;
        default value is true.

    Raises
    ------
    ValueError:
        if parameters are not the appropriate type.

    Returns
    -------
    class instance: Calculator

    Notes
    -----
    The most efficient way to specify current-law and reform Calculator
    objects is as follows:
         pol = Policy()
         rec = Records()
         grec = GSTRecords()
         crec = CorpRecords()
         # Current law
         calc1 = Calculator(policy=pol, records=rec, corprecords=crec,
                            gstrecords=grec)
         pol.implement_reform(...)
         # Reform
         calc2 = Calculator(policy=pol, records=rec, corprecords=crec,
                            gstrecords=grec)
    All calculations are done on the internal copies of the Policy and
    Records objects passed to each of the two Calculator constructors.
    """
    # pylint: disable=too-many-public-methods

    def __init__(self, policy=None, records=None, corprecords=None,
                 gstrecords=None, verbose=True, sync_years=True):
        # pylint: disable=too-many-arguments,too-many-branches
        #print("inside init of calc ")
        f = open('global_vars.json')
        vars = json.load(f)
        self.verbose = vars['verbose']
        verbose = self.verbose
        self.records = records
        self.corprecords = corprecords
        self.gstrecords = gstrecords

        if self.records is not None:
            PIT_VAR_INFO_FILENAME = 'taxcalc/'+vars['pit_records_variables_filename']
            pit_function_names_file = 'taxcalc'+'/'+vars['pit_function_names_filename']
            f = open(pit_function_names_file)
            self.pit_function_names = json.load(f)
            pit_oname = vars["pit_functions_filename"][:-3]
            pit_imp_statement = "import taxcalc." + pit_oname
            exec(pit_imp_statement)

            """
            from taxcalc.functions import (net_salary_income, net_rental_income,
                                           income_business_profession,
                                           total_other_income, gross_total_income,
                                           itemized_deductions, deduction_10AA,
                                           taxable_total_income,
                                           tax_stcg_splrate, tax_ltcg_splrate,
                                           tax_specialrates, current_year_losses,
                                           brought_fwd_losses, agri_income, pit_liability)
            """
        if self.corprecords is not None:
            CIT_VAR_INFO_FILENAME = 'taxcalc/'+vars['cit_records_variables_filename']
            self.max_lag_years = vars['cit_max_lag_years']
            cit_function_names_file = 'taxcalc/'+vars['cit_function_names_filename']
            f = open(cit_function_names_file)
            self.cit_function_names = json.load(f)
            cit_oname = vars["cit_functions_filename"][:-3]
            cit_imp_statement = "import taxcalc." + cit_oname
            exec(cit_imp_statement)
            """
            from taxcalc.corpfunctions import (total_other_income_cit, depreciation_PM,
                                               corp_income_business_profession,
                                               corp_GTI_before_set_off, GTI_and_losses,
                                               cit_liability)
            """
        if self.gstrecords is not None:
            VAT_VAR_INFO_FILENAME = 'taxcalc/'+vars['vat_records_variables_filename']
            vat_function_names_file = 'taxcalc/'+vars['vat_function_names_filename']
            f = open(vat_function_names_file)
            self.vat_function_names = json.load(f)
            vat_oname = vars["vat_functions_filename"][:-3]
            vat_imp_statement = "import taxcalc." + vat_oname
            exec(vat_imp_statement)           
            #from taxcalc.gstfunctions import (gst_liability_item)        
        gfactors=GrowFactors()
        self.gfactors = gfactors
        if isinstance(policy, Policy):
            self.__policy = copy.deepcopy(policy)
        else:
            raise ValueError('must specify policy as a Policy object')
        if self.records is not None:
            if isinstance(records, Records):
                self.__records = copy.deepcopy(records)
                with open(PIT_VAR_INFO_FILENAME) as vfile:
                    self.vardict = json.load(vfile)                
                self.ATTRIBUTE_READ_VARS_PIT = list(k for k,
                          v in self.vardict['read'].items()
                          if v['attribute'] == 'Yes')
                
            else:
                raise ValueError('must specify records as a Records object')
        if self.gstrecords is not None:
            if isinstance(gstrecords, GSTRecords):
                self.__gstrecords = copy.deepcopy(gstrecords)
                with open(VAT_VAR_INFO_FILENAME) as vfile:
                    self.vardict = json.load(vfile)                
                self.ATTRIBUTE_READ_VARS_VAT = list(k for k,
                          v in self.vardict['read'].items()
                          if v['attribute'] == 'Yes')                
            else:
                raise ValueError('must specify records as a GSTRecords object')
        if self.corprecords is not None:            
            if isinstance(corprecords, CorpRecords):
                self.__corprecords = copy.deepcopy(corprecords)
                #self.max_lag_years
                self.CROSS_YEAR_VARS = []
                with open(CIT_VAR_INFO_FILENAME) as vfile:
                    self.vardict = json.load(vfile)
                    vfile.close()
                for k, v in self.vardict["read"].items():
                  #print("key: ", x, "value: ", y)
                  if self.vardict["read"][k]["cross_year"]=='Yes':
                      self.CROSS_YEAR_VARS = self.CROSS_YEAR_VARS + [k]
                self.ATTRIBUTE_READ_VARS_CIT = list(k for k,
                          v in self.vardict['read'].items()
                          if v['attribute'] == 'Yes')                     
            else:
                raise ValueError('must specify records as a CorpRecords object')
        if self.records is not None:
            #print('self.__policy.current_year ', self.__policy.current_year)
            #print('self.__records.data_year ', self.__records.data_year)
            #print('self.__records.current_year ', self.__records.current_year)
            if self.__policy.current_year < self.__records.data_year:
                self.__policy.set_year(self.__records.data_year)        
            current_year_is_data_year = (
                    self.__records.current_year == self.__records.data_year)
            if sync_years and current_year_is_data_year:
                if verbose:
                    print('You loaded data for ' +
                          str(self.__records.data_year) + '.')
                    if self.__records.IGNORED_VARS:
                        print('Your data include the following unused ' +
                              'variables that will be ignored:')
                        for var in self.__records.IGNORED_VARS:
                            print('  ' +
                                  var)
                while self.__records.current_year < self.__policy.current_year:
                    self.__records.increment_year()
                if verbose:
                    print('Tax-Calculator startup automatically ' +
                          'extrapolated your data to ' +
                          str(self.__records.current_year) + '.')
        if self.gstrecords is not None:        
            if self.__policy.current_year < self.__gstrecords.data_year:
                self.__policy.set_year(self.__gstrecords.data_year)        
            current_year_is_data_year = (
                    self.__gstrecords.current_year == self.__gstrecords.data_year)
            if sync_years and current_year_is_data_year:
                if verbose:
                    print('You loaded data for ' +
                          str(self.__gstrecords.data_year) + '.')
                    if self.__gstrecords.IGNORED_VARS:
                        print('Your data include the following unused ' +
                              'variables that will be ignored:')
                        for var in self.__gstrecords.IGNORED_VARS:
                            print('  ' +
                                  var)
                while self.__gstrecords.current_year < self.__policy.current_year:
                    self.__gstrecords.increment_year()
                if verbose:
                    print('Tax-Calculator startup automatically ' +
                          'extrapolated your data to ' +
                          str(self.__gstrecords.current_year) + '.')
        if self.corprecords is not None:        
            if self.__policy.current_year < self.__corprecords.data_year:
                self.__policy.set_year(self.__corprecords.data_year)        
            current_year_is_data_year = (
                    self.__corprecords.current_year == self.__corprecords.data_year)
            if sync_years and current_year_is_data_year:
                if verbose:
                    print('You loaded data for ' +
                          str(self.__corprecords.data_year) + '.')
                    if self.__corprecords.IGNORED_VARS:
                        print('Your data include the following unused ' +
                              'variables that will be ignored:')
                        for var in self.__corprecords.IGNORED_VARS:
                            print('  ' +
                                  var)
                while self.__corprecords.current_year < self.__policy.current_year:
                    self.__corprecords.increment_year()
                if verbose:
                    print('Tax-Calculator startup automatically ' +
                          'extrapolated your data to ' +
                          str(self.__corprecords.current_year) + '.')                    
        if self.records is not None:
            assert self.__policy.current_year == self.__records.current_year
        if self.gstrecords is not None:   
            assert self.__policy.current_year == self.__gstrecords.current_year
        if self.corprecords is not None:            
            assert self.__policy.current_year == self.__corprecords.current_year
        self.__stored_records = None
        
    def set_current_year(self, year):
        self.current_year = year
        if self.records is not None:             
            self.__records.set_current_year(year)
        if self.corprecords is not None:             
            self.__corprecords.set_current_year(year)
        if self.gstrecords is not None:      
            self.__gstrecords.set_current_year(year)

        
    def increment_year(self):
        """
        Advance all embedded objects to next year.
        """
        # store the current year values of loss and closing balance of
        # fixed assets to be moved to next year
        if self.corprecords is not None:
            bf_loss={}
            for i in range(1, self.max_lag_years):
                bf_loss[i] = getattr(self.__corprecords, 'newloss'+str(i))           
            #bf_loss1 = self.__records.newloss1
            
            #print(bf_loss)
            cl_wdv = {}
            for var in self.CROSS_YEAR_VARS:
                cl_wdv[var] = getattr(self.__corprecords, 'Cl'+var[2:])
        #cl_wdv_bld = self.__records.Cl_WDV_Bld

        next_year = self.__policy.current_year + 1
        self.__policy.set_year(next_year)
         
        if self.records is not None:     
            self.__records.increment_year()        
        if self.gstrecords is not None:            
            self.__gstrecords.increment_year()
        if self.corprecords is not None:            
            self.__corprecords.increment_year()
            
        # populate the opening values of loss and opening balance of
        # fixed assets from the previous year      
        if self.corprecords is not None:         
            for i in range(1, self.max_lag_years):
                setattr(self.__corprecords, 'Loss_lag'+str(i), bf_loss[i])                 
            #self.__records.Loss_lag1 = bf_loss1
            for var in self.CROSS_YEAR_VARS:
                setattr(self.__corprecords, var, cl_wdv[var])
        
        #self.__records.Op_WDV_Bld = cl_wdv_bld   
        #self.__records.increment_year()
        #self.__gstrecords.increment_year()
        #self.__corprecords.increment_year()

    def advance_to_year(self, year):
        """
        The advance_to_year function gives an optional way of implementing
        increment year functionality by immediately specifying the year
        as input.  New year must be at least the current year.
        """
        #print("self.current_year ", self.current_year)
        iteration = year - self.current_year
        if iteration < 0:
            raise ValueError('New current year must be ' +
                             'greater than current year!')
        for _ in range(iteration):
            self.increment_year()
        assert self.current_year == year

    def calc_all(self):
        """
        Call all tax-calculation functions for the current_year.
        """
        # pylint: disable=too-many-function-args,no-value-for-parameter
        # conducts static analysis of Calculator object for current_year
        if self.records is not None:
            assert self.__records.current_year == self.__policy.current_year
        if self.gstrecords is not None:
            assert self.__gstrecords.current_year == self.__policy.current_year
        if self.corprecords is not None:
            assert self.__corprecords.current_year == self.__policy.current_year
        if self.records is not None:        
            self.__records.zero_out_changing_calculated_vars()
        if self.gstrecords is not None:        
            self.__gstrecords.zero_out_changing_calculated_vars()
        if self.corprecords is not None:        
            self.__corprecords.zero_out_changing_calculated_vars()            
        # For now, don't zero out for corporate
        # pdb.set_trace()
        # Note that the order of calling these functions is important
        # as some functions require values calculated by those before
        # Corporate calculations
        if self.corprecords is not None:
            for i in range(len(cit_function_names)):
                func_name = globals()[cit_function_names[str(i)]]
                #print(self.cit_function_names[str(i)])
                func_name(self.__policy, self.__corprecords)
        
        # Individual calculations
        # Note that the order of calling these functions is important
        # as some functions require values calculated by those before
        #f='net_salary_income("self.__policy", "self.__records")'       
        if self.records is not None:
            for i in range(len(self.pit_function_names)):
                #print('function name ', self.pit_function_names[str(i)])
                func_name = globals()[self.pit_function_names[str(i)]]
                #print(function_names[str(i)])
                func_name(self.__policy, self.__records)
        # GST calculations
        if self.gstrecords is not None:
            for i in range(len(self.vat_function_names)):
                print('function name ', self.vat_function_names[str(i)])
                func_name = globals()[self.vat_function_names[str(i)]]
                #print(function_names[str(i)])
                func_name(self.__policy, self.__gstrecords)
        """        
        if self.gstrecords is not None:         
            # agg_consumption(self.__policy, self.__gstrecords)
            # gst_liability_cereal(self.__policy, self.__gstrecords)
            # gst_liability_other(self.__policy, self.__gstrecords)
            gst_liability_item(self)
            # gst_liability_item(self.__policy, self.__gstrecords)
            # TODO: ADD: expanded_income(self.__policy, self.__records)
            # TODO: ADD: aftertax_income(self.__policy, self.__records)
        """
        
    def weighted_total_pit(self, variable_name):
        """
        Return all-filing-unit weighted total of named Records variable.
        """
        if self.records is not None:
            return (self.array(variable_name) * self.array('weight')).sum()

    def weighted_gst(self, variable_name):
        """
        Return all-filing-unit weighted total of named GST Records variable.
        """
        if self.gstrecords is not None:
            return (self.garray(variable_name) * self.garray('weight'))

    def weighted_total_gst(self, variable_name):
        """
        Return all-filing-unit weighted total of named GST Records variable.
        """
        if self.gstrecords is not None:        
            return (self.garray(variable_name) * self.garray('weight')).sum()

    def weighted_cit(self, variable_name):
        """
        Return all-filing-unit weighted total of named Corp Records variable.
        """
        if self.corprecords is not None:         
            return (self.carray(variable_name) * self.carray('weight'))

    def get_attribute_types(self, tax_type, attribute_index):
        """
        Parameters
        ----------
        tax_type : string
            tax_type is either 'pit' or 'cit' or 'vat'.
        attribute_index : int
            This gives the index of the attribute variables to be extracted.
            There may be multiple attribute variables and we only select 
            one of them. For example attributes variables could be 'Sector', 
            'Region', etc.

        Raises
        ------
        ValueError
            if the record is not created.

        Returns
        -------
        attribute type list. For example if attribute variable is 'Sector', the 
        attribute types in the dataset would be 'Banks', 'Oil &Gas', 'Hotels', 
        etc.
        Note that 'All' will always be there as an attribute type if 
        even if there are no attribute variables
        """

        attribute_data = []
        if tax_type == 'pit':
            if self.records is not None:
                if len(self.ATTRIBUTE_READ_VARS_PIT) > 0:
                    attribute_data = list(getattr(self.__records, 
                                                  self.ATTRIBUTE_READ_VARS_PIT[attribute_index]))
                    #print('attribute_data', attribute_data)
                    attribute_types = list(set(attribute_data))
                    #print('attribute_types', attribute_types) 
                else:
                    attribute_types = []          
            else:
                msg = 'tax type record ="{}" is not initialized'
                raise ValueError(msg.format(tax_type))
        elif tax_type == 'cit':
            if self.corprecords is not None:            
                if len(self.ATTRIBUTE_READ_VARS_CIT) > 0:
                    attribute_data = list(getattr(self.__corprecords, 
                                                  self.ATTRIBUTE_READ_VARS_CIT[attribute_index]))
                    attribute_types = list(set(attribute_data))
                else:
                    attribute_types = []                    
            else:
                msg = 'tax type record ="{}" is not initialized'
                raise ValueError(msg.format(tax_type))            
        elif tax_type == 'vat':
            if self.gstrecords is not None:            
                if len(self.ATTRIBUTE_READ_VARS_VAT) > 0:
                    attribute_data = list(getattr(self.__gstrecords, 
                                                  self.ATTRIBUTE_READ_VARS_VAT[attribute_index]))
                    attribute_types = list(set(attribute_data))
                else:
                    attribute_types = []                    
            else:
                msg = 'tax type record ="{}" is not initialized'
                raise ValueError(msg.format(tax_type))                
        else:
            msg = 'tax type ="{}" is not valid'
            raise ValueError(msg.format(tax_type))

        return (['All']+attribute_types, attribute_data)
        

    def weighted_total_tax_dict(self, tax_type, variable_name):
        """
        Return all-filing-unit weighted total of named tax variable.
        """
        if tax_type == 'pit':
            if self.records is not None:
                tax_data = self.array(variable_name)
                attribute_var = self.ATTRIBUTE_READ_VARS_PIT
                              
                (attribute_types, attribute_data)  = self.get_attribute_types(tax_type, 0)             
            else:
                msg = 'tax type record ="{}" is not initialized'
                raise ValueError(msg.format(tax_type))
        elif tax_type == 'cit':
            if self.corprecords is not None:            
                tax_data = self.carray(variable_name)
                attribute_var = self.ATTRIBUTE_READ_VARS_CIT               
                (attribute_types, attribute_data) = self.get_attribute_types(tax_type, 0)                 
            else:
                msg = 'tax type record ="{}" is not initialized'
                raise ValueError(msg.format(tax_type))            
        elif tax_type == 'vat':
            if self.gstrecords is not None:            
                tax_data = self.garray(variable_name)
                attribute_var = self.ATTRIBUTE_READ_VARS_VAT                 
                (attribute_types, attribute_data) = self.get_attribute_types(tax_type, 0)                   
            else:
                msg = 'tax type record ="{}" is not initialized'
                raise ValueError(msg.format(tax_type))              
        else:
            msg = 'tax type ="{}" is not valid'
            raise ValueError(msg.format(tax_type))
            return
        
        if tax_type == 'pit':
            wtd_total_tax = {}
            wtd_total_tax['All'] = (tax_data * self.array('weight')).sum()
        elif tax_type == 'cit':
            wtd_total_tax = {}
            wtd_total_tax['All'] = (tax_data * self.carray('weight')).sum()
        elif tax_type == 'vat':
            wtd_total_tax = {}
            wtd_total_tax['All'] = (tax_data * self.garray('weight')).sum()
            
        # We have  calculated for 'All' so no need to calculate further
        attribute_types.remove('All')
        if len(attribute_var)>0:            
            for attribute_value in attribute_types:
                attribute_bool = [1 if i==attribute_value else 0 for i in attribute_data]
                if tax_type == 'pit':
                    wtd_total_tax[attribute_value] = (tax_data * self.array('weight') * attribute_bool).sum()
                elif tax_type == 'cit':
                    wtd_total_tax[attribute_value] = (tax_data * self.carray('weight') * attribute_bool).sum()     
                elif tax_type == 'vat':
                    wtd_total_tax[attribute_value] = (tax_data * self.garray('weight') * attribute_bool).sum()
        #print(wtd_total_cit)
        return wtd_total_tax
            
    def weighted_total_cit(self, variable_name, attribute_var=None):
        """
        Return all-filing-unit weighted total of named Corp Records variable.
        """
        if self.corprecords is not None:
            if attribute_var is None:
                return (self.carray(variable_name) * self.carray('weight')).sum()  
            else:
                attribute_data = list(getattr(self.__corprecords, attribute_var))
                attribute_types = set(attribute_data)
                wtd_total_cit = {}
                for attribute_value in attribute_types:
                    attribute_bool = [1 if i==attribute_value else 0 for i in attribute_data]
                    wtd_total_cit['attribute_value'] = (self.carray(variable_name) * self.carray('weight') *
                                                      attribute_bool).sum()
                return wtd_total_cit
    
    def total_weight_pit(self):
        """
        Return all-filing-unit total of sampling weights.
        NOTE: var_weighted_mean = calc.weighted_total(var)/calc.total_weight()
        """
        if self.records is not None:         
            return self.array('weight').sum()

    def total_weight_gst(self):
        """
        Return all-filing-unit total of sampling weights.
        NOTE: var_weighted_mean = calc.weighted_total(var)/calc.total_weight()
        """
        if self.gstrecords is not None:         
            return self.garray('weight').sum()
    
    def total_weight_cit(self):
        """
        Return all-filing-unit total of sampling weights.
        NOTE: var_weighted_mean = calc.weighted_total(var)/calc.total_weight()
        """
        if self.corprecords is not None:         
            return self.carray('weight').sum()
    
    def dataframe(self, variable_list):
        """
        Return pandas DataFrame containing the listed variables from embedded
        Records object.
        """
        assert isinstance(variable_list, list)
        arys = [self.array(vname) for vname in variable_list]
        #print(arys)
        pdf = pd.DataFrame(data=np.column_stack(arys), columns=variable_list)
        del arys
        return pdf

    def dataframe_cit(self, variable_list, attribute_value=None, attribute_var=None):
        """
        Return pandas DataFrame containing the listed variables from embedded
        Records object.
        """
        if attribute_var is not None:
            variable_list = variable_list + [attribute_var]
        #print('variable_list ', variable_list)
        assert isinstance(variable_list, list)
        arys = [self.carray(vname) for vname in variable_list]
        #print(arys)
        #print('attribute_value ', attribute_value)
        #print('attribute_var ', attribute_var)
        pdf = pd.DataFrame(data=np.column_stack(arys), columns=variable_list)
        #print('pdf \n', pdf)
        if attribute_var is not None:
            if attribute_value != 'All':
                pdf = pdf[pdf[attribute_var]==attribute_value]
        del arys
        return pdf

    def dataframe_vat(self, variable_list):
        """
        Return pandas DataFrame containing the listed variables from embedded
        Records object.
        """
        assert isinstance(variable_list, list)
        arys = [self.garray(vname) for vname in variable_list]
        #print(arys)
        pdf = pd.DataFrame(data=np.column_stack(arys), columns=variable_list)
        del arys
        return pdf
    
    def distribution_table_dataframe(self, tax_type, DIST_VARIABLES, attribute_value=None, attribute_var=None):
        """
        Return pandas DataFrame containing the DIST_TABLE_COLUMNS variables
        from embedded Records object.
        """
        if tax_type == 'pit':        
            if self.records is not None:
                if attribute_var is not None:
                    if attribute_value == 'All':
                        return self.dataframe(DIST_VARIABLES)
                    else:
                        return self.dataframe(DIST_VARIABLES, attribute_value, attribute_var)
                else:
                        return self.dataframe(DIST_VARIABLES)            
        elif tax_type == 'cit':
            if self.corprecords is not None:
                if attribute_var is not None:
                    if attribute_value == 'All':
                        return self.dataframe_cit(DIST_VARIABLES)
                    else:
                        return self.dataframe_cit(DIST_VARIABLES, attribute_value, attribute_var)
                else:
                        return self.dataframe_cit(DIST_VARIABLES)
        elif tax_type == 'vat':        
            if self.gstrecords is not None:
                if attribute_var is not None:
                    if attribute_value == 'All':
                        return self.dataframe_vat(DIST_VARIABLES)
                    else:
                        return self.dataframe_vat(DIST_VARIABLES, attribute_value, attribute_var)
                else:
                        return self.dataframe_vat(DIST_VARIABLES)            
        else:
            msg = 'tax type ="{}" is not valid'
            raise ValueError(msg.format(tax_type))
            return            

    def array(self, variable_name, variable_value=None):
        """
        If variable_value is None, return numpy ndarray containing the
         named variable in embedded Records object.
        If variable_value is not None, set named variable in embedded Records
         object to specified variable_value and return None (which can be
         ignored).
        """
        if self.records is not None:         
            if variable_value is None:
                return getattr(self.__records, variable_name)
            assert isinstance(variable_value, np.ndarray)
            setattr(self.__records, variable_name, variable_value)
        return None

    def carray(self, variable_name, variable_value=None):
        """
        Corporate record version of array() function.
        If variable_value is None, return numpy ndarray containing the
         named variable in embedded Records object.
        If variable_value is not None, set named variable in embedded Records
         object to specified variable_value and return None (which can be
         ignored).
        """
        if self.corprecords is not None:       
            if variable_value is None:
                return getattr(self.__corprecords, variable_name)
            assert isinstance(variable_value, np.ndarray)
            setattr(self.__corprecords, variable_name, variable_value)
        return None

    def garray(self, variable_name, variable_value=None):
        """
        GST record version of array() function.
        If variable_value is None, return numpy ndarray containing the
         named variable in embedded Records object.
        If variable_value is not None, set named variable in embedded Records
         object to specified variable_value and return None (which can be
         ignored).
        """
        if self.gstrecords is not None:        
            if variable_value is None:
                return getattr(self.__gstrecords, variable_name)
            assert isinstance(variable_value, np.ndarray)
            setattr(self.__gstrecords, variable_name, variable_value)
        return None

    def n65(self):
        """
        Return numpy ndarray containing the number of
        individuals age 65+ in each filing unit.
        """
        vdf = self.dataframe(['age_head', 'age_spouse', 'elderly_dependents'])
        return ((vdf['age_head'] >= 65).astype(int) +
                (vdf['age_spouse'] >= 65).astype(int) +
                vdf['elderly_dependents'])

    def incarray(self, variable_name, variable_add):
        """
        Add variable_add to named variable in embedded Records object.
        """
        assert isinstance(variable_add, np.ndarray)
        setattr(self.__records, variable_name,
                self.array(variable_name) + variable_add)

    def zeroarray(self, variable_name):
        """
        Set named variable in embedded Records object to zeros.
        """
        setattr(self.__records, variable_name, np.zeros(self.array_len))

    def store_records(self):
        """
        Make internal copy of embedded Records object that can then be
        restored after interim calculations that make temporary changes
        to the embedded Records object.
        """
        assert self.__stored_records is None
        self.__stored_records = copy.deepcopy(self.__records)

    def restore_records(self):
        """
        Set the embedded Records object to the stored Records object
        that was saved in the last call to the store_records() method.
        """
        assert isinstance(self.__stored_records, Records)
        self.__records = copy.deepcopy(self.__stored_records)
        del self.__stored_records
        self.__stored_records = None

    def records_current_year(self, year=None):
        """
        If year is None, return current_year of embedded Records object.
        If year is not None, set embedded Records current_year to year and
         return None (which can be ignored).
        """
        if year is None:
            return self.__records.current_year
        assert isinstance(year, int)
        self.__records.set_current_year(year)
        return None

    @property
    def array_len(self):
        """
        Length of arrays in embedded Records object.
        """
        if self.records is not None:
            return self.__records.array_length
        if self.corprecords is not None:
            return self.__corprecords.array_length
        if self.gstrecords is not None:
            return self.__gstrecords.array_length         


    def policy_param(self, param_name, param_value=None):
        """
        If param_value is None, return named parameter in
         embedded Policy object.
        If param_value is not None, set named parameter in
         embedded Policy object to specified param_value and
         return None (which can be ignored).
        """
        if param_value is None:
            #from pprint import pprint
            #pprint(vars(self.__policy))
            return getattr(self.__policy, param_name)
        setattr(self.__policy, param_name, param_value)
        return None

    @property
    def reform_warnings(self):
        """
        Calculator class embedded Policy object's reform_warnings.
        """
        return self.__policy.parameter_warnings

    def policy_current_year(self, year=None):
        """
        If year is None, return current_year of embedded Policy object.
        If year is not None, set embedded Policy current_year to year and
         return None (which can be ignored).
        """
        if year is None:
            return self.__policy.current_year
        assert isinstance(year, int)
        self.__policy.set_year(year)
        return None

    @property
    def current_year(self):
        """
        Calculator class current assessment year property.
        """
        return self.__policy.current_year

    @property
    def data_year(self):
        """
        Calculator class initial (i.e., first) records data year property.
        """
        return self.__records.data_year

    def diagnostic_table(self, num_years):
        """
        Generate multi-year diagnostic table containing aggregate statistics;
        this method leaves the Calculator object unchanged.

        Parameters
        ----------
        num_years : Integer
            number of years to include in diagnostic table starting
            with the Calculator object's current_year (must be at least
            one and no more than what would exceed Policy end_year)

        Returns
        -------
        Pandas DataFrame object containing the multi-year diagnostic table
        """
        assert num_years >= 1
        max_num_years = self.__policy.end_year - self.__policy.current_year + 1
        assert num_years <= max_num_years
        diag_variables = DIST_VARIABLES + ['surtax']
        calc = copy.deepcopy(self)
        tlist = list()
        for iyr in range(1, num_years + 1):
            calc.calc_all()
            diag = create_diagnostic_table(calc.dataframe(diag_variables),
                                           calc.current_year)
            tlist.append(diag)
            if iyr < num_years:
                calc.increment_year()
        del diag_variables
        del calc
        del diag
        return pd.concat(tlist, axis=1)

    def distribution_tables_dict(self, tax_type, calc, groupby, distribution_vardict, 
                            income_measure=None,
                            averages=False, scaling=True,
                            attribute_var=None):
        """
        Get results from self and calc, sort them by GTI into table
        rows defined by groupby, compute grouped statistics, and
        return tables as a pair of Pandas dataframes.
        This method leaves the Calculator object(s) unchanged.
        Note that the returned tables have consistent income groups (based
        on the self GTI) even though the baseline GTI in self and
        the reform GTI in calc are different.

        Parameters
        ----------
        calc : Calculator object or None
            typically represents the reform while self represents the baseline;
            if calc is None, the second returned table is None

        groupby : String object
            options for input: 'weighted_deciles', 'standard_income_bins'
            determines how the columns in resulting Pandas DataFrame are sorted

        averages : boolean
            specifies whether or not monetary table entries are aggregates or
            averages (default value of False implies entries are aggregates)

        scaling : boolean
            specifies whether or not monetary table entries are scaled to
            billions and rounded to three decimal places when averages=False,
            or when averages=True, to thousands and rounded to three decimal
            places.  Regardless of the value of averages, non-monetary table
            entries are scaled to millions and rounded to three decimal places
            (default value of False implies entries are scaled and rounded)

        Return and typical usage
        ------------------------
        dist1, dist2 = calc1.distribution_tables(calc2, 'weighted_deciles')
        OR
        dist1, _ = calc1.distribution_tables(None, 'weighted_deciles')
        (where calc1 is a baseline Calculator object
        and calc2 is a reform Calculator object).
        Each of the dist1 and optional dist2 is a distribution table as a
        Pandas DataFrame with DIST_TABLE_COLUMNS and groupby rows.
        NOTE: when groupby is 'weighted_deciles', the returned tables have 3
              extra rows containing top-decile detail consisting of statistics
              for the 0.90-0.95 quantile range (bottom half of top decile),
              for the 0.95-0.99 quantile range, and
              for the 0.99-1.00 quantile range (top one percent); and the
              returned table splits the bottom decile into filing units with
              negative (denoted by a 0-10n row label),
              zero (denoted by a 0-10z row label), and
              positive (denoted by a 0-10p row label) values of the
              specified income_measure.
        """
        # nested function used only by this method
        def have_same_income_measure(calc1, calc2, imeasure):
            """
            Return true if calc1 and calc2 contain the same GTI;
            otherwise, return false.  (Note that "same" means nobody's
            GTI differs by more than one cent.)
            """
            if self.records is not None:
                im1 = calc1.array(imeasure)
                im2 = calc2.array(imeasure)
            if self.corprecords is not None:
                im1 = calc1.carray(imeasure)
                im2 = calc2.carray(imeasure)
            if self.gstrecords is not None:
                im1 = calc1.garray(imeasure)
                im2 = calc2.garray(imeasure)                
            return np.allclose(im1, im2, rtol=0.0, atol=0.01)
        
        # main logic of method
        from taxcalc.utils import create_distribution_table
        """
        (DIST_VARIABLES, DIST_TABLE_COLUMNS, DIST_TABLE_LABELS, 
        DECILE_ROW_NAMES,STANDARD_ROW_NAMES,STANDARD_INCOME_BINS)=dist_variables()
        """
        assert calc is None or isinstance(calc, Calculator)
        assert (groupby == 'weighted_deciles' or
                groupby == 'weighted_percentiles' or
                groupby == 'standard_income_bins')

        attribute_types = ['All']
        if calc is not None:
            if self.records is not None:
                assert np.allclose(self.array('weight'),
                                   calc.array('weight'))  # rows in same order
                if attribute_var is not None:
                    (attribute_types, attribute_data) = self.get_attribute_types(tax_type, 0)
            if self.corprecords is not None:
                assert np.allclose(self.carray('weight'),
                                   calc.carray('weight'))
                if attribute_var is not None:                
                    (attribute_types, attribute_data) = self.get_attribute_types(tax_type, 0)
            if self.gstrecords is not None:
                assert np.allclose(self.garray('weight'),
                                   calc.garray('weight'))
                if attribute_var is not None:                
                    (attribute_types, attribute_data) = self.get_attribute_types(tax_type, 0)
        #print('attribute_types ', attribute_types)
        dt1 = {}
        for attribute_value in attribute_types:                   
            var_dataframe = self.distribution_table_dataframe(tax_type, distribution_vardict['DIST_VARIABLES'], attribute_value, attribute_var)
            #print('var_dataframe \n', var_dataframe)
            if income_measure is None:
                imeasure = 'GTI'
            else:
                imeasure = income_measure

            dt1[attribute_value] = create_distribution_table(var_dataframe, groupby, distribution_vardict,
                                            imeasure, averages, scaling)
            del var_dataframe
        if calc is None:
            dt2 = None
        else:
            assert calc.current_year == self.current_year
            assert calc.array_len == self.array_len
            dt2 = {}
            for attribute_value in attribute_types:  
                var_dataframe = calc.distribution_table_dataframe(tax_type, distribution_vardict['DIST_VARIABLES'], attribute_value, attribute_var)
                if have_same_income_measure(self, calc, imeasure):
                    if income_measure is None:
                        imeasure = 'GTI'
                    else:
                        imeasure = income_measure
                else:
                    imeasure = 'GTI'
                    #imeasure = 'GTI_baseline'
                    var_dataframe[attribute_value][imeasure] = self.array(imeasure)
                dt2[attribute_value] = create_distribution_table(var_dataframe, groupby, 
                                                distribution_vardict,
                                                imeasure, averages, scaling)
                del var_dataframe
        return (dt1, dt2)
                    
    def distribution_tables(self, calc, groupby, distribution_vardict, 
                            income_measure=None,
                            averages=False, scaling=True,
                            attribute_value=None, attribute_var=None):
        """
        Get results from self and calc, sort them by GTI into table
        rows defined by groupby, compute grouped statistics, and
        return tables as a pair of Pandas dataframes.
        This method leaves the Calculator object(s) unchanged.
        Note that the returned tables have consistent income groups (based
        on the self GTI) even though the baseline GTI in self and
        the reform GTI in calc are different.

        Parameters
        ----------
        calc : Calculator object or None
            typically represents the reform while self represents the baseline;
            if calc is None, the second returned table is None

        groupby : String object
            options for input: 'weighted_deciles', 'standard_income_bins'
            determines how the columns in resulting Pandas DataFrame are sorted

        averages : boolean
            specifies whether or not monetary table entries are aggregates or
            averages (default value of False implies entries are aggregates)

        scaling : boolean
            specifies whether or not monetary table entries are scaled to
            billions and rounded to three decimal places when averages=False,
            or when averages=True, to thousands and rounded to three decimal
            places.  Regardless of the value of averages, non-monetary table
            entries are scaled to millions and rounded to three decimal places
            (default value of False implies entries are scaled and rounded)

        Return and typical usage
        ------------------------
        dist1, dist2 = calc1.distribution_tables(calc2, 'weighted_deciles')
        OR
        dist1, _ = calc1.distribution_tables(None, 'weighted_deciles')
        (where calc1 is a baseline Calculator object
        and calc2 is a reform Calculator object).
        Each of the dist1 and optional dist2 is a distribution table as a
        Pandas DataFrame with DIST_TABLE_COLUMNS and groupby rows.
        NOTE: when groupby is 'weighted_deciles', the returned tables have 3
              extra rows containing top-decile detail consisting of statistics
              for the 0.90-0.95 quantile range (bottom half of top decile),
              for the 0.95-0.99 quantile range, and
              for the 0.99-1.00 quantile range (top one percent); and the
              returned table splits the bottom decile into filing units with
              negative (denoted by a 0-10n row label),
              zero (denoted by a 0-10z row label), and
              positive (denoted by a 0-10p row label) values of the
              specified income_measure.
        """
        # nested function used only by this method
        def have_same_income_measure(calc1, calc2, imeasure):
            """
            Return true if calc1 and calc2 contain the same GTI;
            otherwise, return false.  (Note that "same" means nobody's
            GTI differs by more than one cent.)
            """
            if self.records is not None:
                im1 = calc1.array(imeasure)
                im2 = calc2.array(imeasure)
            if self.corprecords is not None:
                im1 = calc1.carray(imeasure)
                im2 = calc2.carray(imeasure)
            if self.gstrecords is not None:
                im1 = calc1.garray(imeasure)
                im2 = calc2.garray(imeasure)                
            return np.allclose(im1, im2, rtol=0.0, atol=0.01)
        
        # main logic of method
        from taxcalc.utils import create_distribution_table
        """
        (DIST_VARIABLES, DIST_TABLE_COLUMNS, DIST_TABLE_LABELS, 
        DECILE_ROW_NAMES,STANDARD_ROW_NAMES,STANDARD_INCOME_BINS)=dist_variables()
        """
        assert calc is None or isinstance(calc, Calculator)
        assert (groupby == 'weighted_deciles' or
                groupby == 'weighted_percentiles' or
                groupby == 'standard_income_bins')
        if calc is not None:
            if self.records is not None:
                assert np.allclose(self.array('weight'),
                                   calc.array('weight'))  # rows in same order
            if self.corprecords is not None:
                assert np.allclose(self.carray('weight'),
                                   calc.carray('weight'))
            if self.gstrecords is not None:
                assert np.allclose(self.garray('weight'),
                                   calc.garray('weight'))
                
        var_dataframe = self.distribution_table_dataframe(distribution_vardict['DIST_VARIABLES'], attribute_value, attribute_var)
        #print('var_dataframe \n', var_dataframe)
        if income_measure is None:
            imeasure = 'GTI'
        else:
            imeasure = income_measure
        dt1 = create_distribution_table(var_dataframe, groupby, distribution_vardict,
                                        imeasure, averages, scaling)
        del var_dataframe
        if calc is None:
            dt2 = None
        else:
            assert calc.current_year == self.current_year
            assert calc.array_len == self.array_len
            var_dataframe = calc.distribution_table_dataframe(distribution_vardict['DIST_VARIABLES'], attribute_value=None, attribute_var=None)
            if have_same_income_measure(self, calc, imeasure):
                if income_measure is None:
                    imeasure = 'GTI'
                else:
                    imeasure = income_measure
            else:
                imeasure = 'GTI'
                #imeasure = 'GTI_baseline'
                var_dataframe[imeasure] = self.array(imeasure)
            dt2 = create_distribution_table(var_dataframe, groupby, 
                                            distribution_vardict,
                                            imeasure, averages, scaling)
            del var_dataframe
        return (dt1, dt2)

    def difference_table(self, calc, groupby, tax_to_diff):
        """
        Get results from self and calc, sort them by expanded_income into
        table rows defined by groupby, compute grouped statistics, and
        return tax-difference table as a Pandas dataframe.
        This method leaves the Calculator objects unchanged.
        Note that the returned tables have consistent income groups (based
        on the self expanded_income) even though the baseline expanded_income
        in self and the reform expanded_income in calc are different.

        Parameters
        ----------
        calc : Calculator object
            calc represents the reform while self represents the baseline

        groupby : String object
            options for input: 'weighted_deciles', 'standard_income_bins'
            determines how the columns in resulting Pandas DataFrame are sorted

        tax_to_diff : String object
            options for input: 'iitax', 'payrolltax', 'combined'
            specifies which tax to difference

        Returns and typical usage
        -------------------------
        diff = calc1.difference_table(calc2, 'weighted_deciles', 'iitax')
        (where calc1 is a baseline Calculator object
        and calc2 is a reform Calculator object).
        The returned diff is a difference table as a Pandas DataFrame
        with DIST_TABLE_COLUMNS and groupby rows.
        NOTE: when groupby is 'weighted_deciles', the returned table has three
              extra rows containing top-decile detail consisting of statistics
              for the 0.90-0.95 quantile range (bottom half of top decile),
              for the 0.95-0.99 quantile range, and
              for the 0.99-1.00 quantile range (top one percent); and the
              returned table splits the bottom decile into filing units with
              negative (denoted by a 0-10n row label),
              zero (denoted by a 0-10z row label), and
              positive (denoted by a 0-10p row label) values of the
              specified income_measure.
        """
        assert isinstance(calc, Calculator)
        assert calc.current_year == self.current_year
        assert calc.array_len == self.array_len
        self_var_dataframe = self.dataframe(DIFF_VARIABLES)
        calc_var_dataframe = calc.dataframe(DIFF_VARIABLES)
        diff = create_difference_table(self_var_dataframe,
                                       calc_var_dataframe,
                                       groupby, tax_to_diff)
        del self_var_dataframe
        del calc_var_dataframe
        return diff

    MTR_VALID_VARIABLES = ['e00200p', 'e00200s',
                           'e00900p', 'e00300',
                           'e00400', 'e00600',
                           'e00650', 'e01400',
                           'e01700', 'e02000',
                           'e02400', 'p22250',
                           'p23250', 'e18500',
                           'e19200', 'e26270',
                           'e19800', 'e20100']

    def mtr(self, variable_str='e00200p',
            negative_finite_diff=False,
            zero_out_calculated_vars=False,
            calc_all_already_called=False,
            wrt_full_compensation=True):
        """
        Calculates the marginal payroll, individual income, and combined
        tax rates for every tax filing unit, leaving the Calculator object
        in exactly the same state as it would be in after a calc_all() call.

        The marginal tax rates are approximated as the change in tax
        liability caused by a small increase (the finite_diff) in the variable
        specified by the variable_str divided by that small increase in the
        variable, when wrt_full_compensation is false.

        If wrt_full_compensation is true, then the marginal tax rates
        are computed as the change in tax liability divided by the change
        in total compensation caused by the small increase in the variable
        (where the change in total compensation is the sum of the small
        increase in the variable and any increase in the employer share of
        payroll taxes caused by the small increase in the variable).

        If using 'e00200s' as variable_str, the marginal tax rate for all
        records where MARS != 2 will be missing.  If you want to perform a
        function such as np.mean() on the returned arrays, you will need to
        account for this.

        Parameters
        ----------
        variable_str: string
            specifies type of income or expense that is increased to compute
            the marginal tax rates.  See Notes for list of valid variables.

        negative_finite_diff: boolean
            specifies whether or not marginal tax rates are computed by
            subtracting (rather than adding) a small finite_diff amount
            to the specified variable.

        zero_out_calculated_vars: boolean
            specifies value of zero_out_calc_vars parameter used in calls
            of Calculator.calc_all() method.

        calc_all_already_called: boolean
            specifies whether self has already had its Calculor.calc_all()
            method called, in which case this method will not do a final
            calc_all() call but use the incoming embedded Records object
            as the outgoing Records object embedding in self.

        wrt_full_compensation: boolean
            specifies whether or not marginal tax rates on earned income
            are computed with respect to (wrt) changes in total compensation
            that includes the employer share of OASDI and HI payroll taxes.

        Returns
        -------
        A tuple of numpy arrays in the following order:
        mtr_payrolltax: an array of marginal payroll tax rates.
        mtr_incometax: an array of marginal individual income tax rates.
        mtr_combined: an array of marginal combined tax rates, which is
                      the sum of mtr_payrolltax and mtr_incometax.

        Notes
        -----
        The arguments zero_out_calculated_vars and calc_all_already_called
        cannot both be true.

        Valid variable_str values are:
        'e00200p', taxpayer wage/salary earnings (also included in e00200);
        'e00200s', spouse wage/salary earnings (also included in e00200);
        'e00900p', taxpayer Schedule C self-employment income (also in e00900);
        'e00300',  taxable interest income;
        'e00400',  federally-tax-exempt interest income;
        'e00600',  all dividends included in AGI
        'e00650',  qualified dividends (also included in e00600)
        'e01400',  federally-taxable IRA distribution;
        'e01700',  federally-taxable pension benefits;
        'e02000',  Schedule E total net income/loss
        'e02400',  all social security (OASDI) benefits;
        'p22250',  short-term capital gains;
        'p23250',  long-term capital gains;
        'e18500',  Schedule A real-estate-tax paid;
        'e19200',  Schedule A interest paid;
        'e26270',  S-corporation/partnership income (also included in e02000);
        'e19800',  Charity cash contributions;
        'e20100',  Charity non-cash contributions.
        """
        # pylint: disable=too-many-arguments,too-many-statements
        # pylint: disable=too-many-locals,too-many-branches
        assert not zero_out_calculated_vars or not calc_all_already_called
        # check validity of variable_str parameter
        if variable_str not in Calculator.MTR_VALID_VARIABLES:
            msg = 'mtr variable_str="{}" is not valid'
            raise ValueError(msg.format(variable_str))
        # specify value for finite_diff parameter
        finite_diff = 0.01  # a one-cent difference
        if negative_finite_diff:
            finite_diff *= -1.0
        # remember records object in order to restore it after mtr computations
        self.store_records()
        # extract variable array(s) from embedded records object
        variable = self.array(variable_str)
        if variable_str == 'e00200p':
            earnings_var = self.array('e00200')
        elif variable_str == 'e00200s':
            earnings_var = self.array('e00200')
        elif variable_str == 'e00900p':
            seincome_var = self.array('e00900')
        elif variable_str == 'e00650':
            divincome_var = self.array('e00600')
        elif variable_str == 'e26270':
            sche_income_var = self.array('e02000')
        # calculate level of taxes after a marginal increase in income
        self.array(variable_str, variable + finite_diff)
        if variable_str == 'e00200p':
            self.array('e00200', earnings_var + finite_diff)
        elif variable_str == 'e00200s':
            self.array('e00200', earnings_var + finite_diff)
        elif variable_str == 'e00900p':
            self.array('e00900', seincome_var + finite_diff)
        elif variable_str == 'e00650':
            self.array('e00600', divincome_var + finite_diff)
        elif variable_str == 'e26270':
            self.array('e02000', sche_income_var + finite_diff)
        self.calc_all(zero_out_calc_vars=zero_out_calculated_vars)
        payrolltax_chng = self.array('payrolltax')
        incometax_chng = self.array('iitax')
        combined_taxes_chng = incometax_chng + payrolltax_chng
        # calculate base level of taxes after restoring records object
        self.restore_records()
        if not calc_all_already_called or zero_out_calculated_vars:
            self.calc_all(zero_out_calc_vars=zero_out_calculated_vars)
        payrolltax_base = self.array('payrolltax')
        incometax_base = self.array('iitax')
        combined_taxes_base = incometax_base + payrolltax_base
        # compute marginal changes in combined tax liability
        payrolltax_diff = payrolltax_chng - payrolltax_base
        incometax_diff = incometax_chng - incometax_base
        combined_diff = combined_taxes_chng - combined_taxes_base
        # specify optional adjustment for employer (er) OASDI+HI payroll taxes
        mtr_on_earnings = (variable_str == 'e00200p' or
                           variable_str == 'e00200s')
        if wrt_full_compensation and mtr_on_earnings:
            adj = np.where(variable < self.policy_param('SS_Earnings_c'),
                           0.5 * (self.policy_param('FICA_ss_trt') +
                                  self.policy_param('FICA_mc_trt')),
                           0.5 * self.policy_param('FICA_mc_trt'))
        else:
            adj = 0.0
        # compute marginal tax rates
        mtr_payrolltax = payrolltax_diff / (finite_diff * (1.0 + adj))
        mtr_incometax = incometax_diff / (finite_diff * (1.0 + adj))
        mtr_combined = combined_diff / (finite_diff * (1.0 + adj))
        # if variable_str is e00200s, set MTR to NaN for units without a spouse
        if variable_str == 'e00200s':
            mars = self.array('MARS')
            mtr_payrolltax = np.where(mars == 2, mtr_payrolltax, np.nan)
            mtr_incometax = np.where(mars == 2, mtr_incometax, np.nan)
            mtr_combined = np.where(mars == 2, mtr_combined, np.nan)
        # delete intermediate variables
        del variable
        if variable_str == 'e00200p' or variable_str == 'e00200s':
            del earnings_var
        elif variable_str == 'e00900p':
            del seincome_var
        elif variable_str == 'e00650':
            del divincome_var
        elif variable_str == 'e26270':
            del sche_income_var
        del payrolltax_chng
        del incometax_chng
        del combined_taxes_chng
        del payrolltax_base
        del incometax_base
        del combined_taxes_base
        del payrolltax_diff
        del incometax_diff
        del combined_diff
        del adj
        # return the three marginal tax rate arrays
        return (mtr_payrolltax, mtr_incometax, mtr_combined)

    REQUIRED_REFORM_KEYS = set(['policy'])
    # THE REQUIRED_ASSUMP_KEYS ARE OBSOLETE BECAUSE NO ASSUMP FILES ARE USED
    REQUIRED_ASSUMP_KEYS = set(['consumption', 'behavior',
                                'growdiff_baseline', 'growdiff_response',
                                'growmodel'])

    @staticmethod
    def read_json_param_objects(reform, assump):
        """
        Read JSON reform object [and formerly assump object] and
        return a single dictionary containing 6 key:dict pairs:
        'policy':dict, 'consumption':dict, 'behavior':dict,
        'growdiff_baseline':dict, 'growdiff_response':dict, and
        'growmodel':dict.

        Note that either of the two function arguments can be None.
        If reform is None, the dict in the 'policy':dict pair is empty.
        If assump is None, the dict in the all the key:dict pairs is empty.

        Also note that either of the two function arguments can be strings
        containing a valid JSON string (rather than a filename),
        in which case the file reading is skipped and the appropriate
        read_json_*_text method is called.

        The reform file contents or JSON string must be like this:
        {"policy": {...}}
        and the assump file contents or JSON string must be like this:
        {"consumption": {...},
         "behavior": {...},
         "growdiff_baseline": {...},
         "growdiff_response": {...},
         "growmodel": {...}}
        The {...} should be empty like this {} if not specifying a policy
        reform or if not specifying any economic assumptions of that type.

        The returned dictionary contains parameter lists (not arrays).
        """
        # pylint: disable=too-many-branches
        # first process second assump parameter
        assert assump is None
        if assump is None:
            cons_dict = dict()
            behv_dict = dict()
            gdiff_base_dict = dict()
            gdiff_resp_dict = dict()
            growmodel_dict = dict()
        elif isinstance(assump, str):
            if os.path.isfile(assump):
                txt = open(assump, 'r').read()
            else:
                txt = assump
            (cons_dict,
             behv_dict,
             gdiff_base_dict,
             gdiff_resp_dict,
             growmodel_dict) = Calculator._read_json_econ_assump_text(txt)
        else:
            raise ValueError('assump is neither None nor string')
        # next process first reform parameter
        if reform is None:
            rpol_dict = dict()
        elif isinstance(reform, str):
            if os.path.isfile(reform):
                txt = open(reform, 'r').read()
            else:
                txt = reform
            rpol_dict = Calculator._read_json_policy_reform_text(txt)
        else:
            raise ValueError('reform is neither None nor string')
        # construct single composite dictionary
        param_dict = dict()
        param_dict['policy'] = rpol_dict
        param_dict['consumption'] = cons_dict
        param_dict['behavior'] = behv_dict
        param_dict['growdiff_baseline'] = gdiff_base_dict
        param_dict['growdiff_response'] = gdiff_resp_dict
        param_dict['growmodel'] = growmodel_dict
        # return the composite dictionary
        return param_dict

    @staticmethod
    def reform_documentation(params, policy_dicts=None):
        """
        Generate reform documentation.

        Parameters
        ----------
        params: dict
            dictionary is structured like dict returned from
            the static Calculator method read_json_param_objects()

        policy_dicts : list of dict or None
            each dictionary in list is a params['policy'] dictionary
            representing second and subsequent elements of a compound
            reform; None implies no compound reform with the simple
            reform characterized in the params['policy'] dictionary

        Returns
        -------
        doc: String
            the documentation for the policy reform specified in params
        """
        # pylint: disable=too-many-statements,too-many-branches

        # nested function used only in reform_documentation
        def param_doc(years, change, base):
            """
            Parameters
            ----------
            years: list of change years
            change: dictionary of parameter changes
            base: Policy object with baseline values
            syear: parameter start assessment year

            Returns
            -------
            doc: String
            """
            # pylint: disable=too-many-locals

            # nested function used only in param_doc
            def lines(text, num_indent_spaces, max_line_length=77):
                """
                Return list of text lines, each one of which is no longer
                than max_line_length, with the second and subsequent lines
                being indented by the number of specified num_indent_spaces;
                each line in the list ends with the '\n' character
                """
                if len(text) < max_line_length:
                    # all text fits on one line
                    line = text + '\n'
                    return [line]
                # all text does not fix on one line
                first_line = True
                line_list = list()
                words = text.split()
                while words:
                    if first_line:
                        line = ''
                        first_line = False
                    else:
                        line = ' ' * num_indent_spaces
                    while (words and
                           (len(words[0]) + len(line)) < max_line_length):
                        line += words.pop(0) + ' '
                    line = line[:-1] + '\n'
                    line_list.append(line)
                return line_list

            # begin main logic of param_doc
            # pylint: disable=too-many-nested-blocks
            assert len(years) == len(change.keys())
            assert isinstance(base, Policy)
            basex = copy.deepcopy(base)
            basevals = getattr(basex, '_vals', None)
            assert isinstance(basevals, dict)
            doc = ''
            for year in years:
                # write year
                basex.set_year(year)
                doc += '{}:\n'.format(year)
                # write info for each param in year
                for param in sorted(change[year].keys()):
                    # ... write param:value line
                    pval = change[year][param]
                    if isinstance(pval, list):
                        pval = pval[0]
                        if basevals[param]['boolean_value']:
                            if isinstance(pval, list):
                                pval = [True if item else
                                        False for item in pval]
                            else:
                                pval = bool(pval)
                    doc += ' {} : {}\n'.format(param, pval)
                    # ... write optional param-index line
                    if isinstance(pval, list):
                        pval = basevals[param]['col_label']
                        pval = [str(item) for item in pval]
                        doc += ' ' * (4 + len(param)) + '{}\n'.format(pval)
                    # ... write name line
                    if param.endswith('_cpi'):
                        rootparam = param[:-4]
                        name = '{} inflation indexing status'.format(rootparam)
                    else:
                        name = basevals[param]['long_name']
                    for line in lines('name: ' + name, 6):
                        doc += '  ' + line
                    # ... write optional desc line
                    if not param.endswith('_cpi'):
                        desc = basevals[param]['description']
                        for line in lines('desc: ' + desc, 6):
                            doc += '  ' + line
                    # ... write baseline_value line
                    if param.endswith('_cpi'):
                        rootparam = param[:-4]
                        bval = basevals[rootparam].get('cpi_inflated',
                                                       False)
                    else:
                        bval = getattr(basex, param[1:], None)
                        if isinstance(bval, np.ndarray):
                            bval = bval.tolist()
                            if basevals[param]['boolean_value']:
                                bval = [True if item else
                                        False for item in bval]
                        elif basevals[param]['boolean_value']:
                            bval = bool(bval)
                    doc += '  baseline_value: {}\n'.format(bval)
            return doc

        # begin main logic of reform_documentation
        # create Policy object with pre-reform (i.e., baseline) values
        clp = Policy()
        # generate documentation text
        doc = 'REFORM DOCUMENTATION\n'
        doc += 'Policy Reform Parameter Values by Year:\n'
        years = sorted(params['policy'].keys())
        if years:
            doc += param_doc(years, params['policy'], clp)
        else:
            doc += 'none: using current-law policy parameters\n'
        if policy_dicts is not None:
            assert isinstance(policy_dicts, list)
            base = clp
            base.implement_reform(params['policy'])
            assert not base.parameter_errors
            for policy_dict in policy_dicts:
                assert isinstance(policy_dict, dict)
                doc += 'Policy Reform Parameter Values by Year:\n'
                years = sorted(policy_dict.keys())
                doc += param_doc(years, policy_dict, base)
                base.implement_reform(policy_dict)
                assert not base.parameter_errors
        return doc

    # ----- begin private methods of Calculator class -----

    @staticmethod
    def _read_json_policy_reform_text(text_string):
        """
        Strip //-comments from text_string and return 1 dict based on the JSON.

        Specified text is JSON with at least 1 high-level key:object pair:
        a "policy": {...} pair.  Other keys will raise a ValueError.

        The {...}  object may be empty (that is, be {}), or
        may contain one or more pairs with parameter string primary keys
        and string years as secondary keys.  See tests/test_calculator.py for
        an extended example of a commented JSON policy reform text
        that can be read by this method.

        Returned dictionary prdict has integer years as primary keys and
        string parameters as secondary keys.  This returned dictionary is
        suitable as the argument to the Policy implement_reform(prdict) method.
        """
        # pylint: disable=too-many-locals
        # strip out //-comments without changing line numbers
        json_str = re.sub('//.*', ' ', text_string)
        # convert JSON text into a Python dictionary
        try:
            raw_dict = json.loads(json_str)
        except ValueError as valerr:
            msg = 'Policy reform text below contains invalid JSON:\n'
            msg += str(valerr) + '\n'
            msg += 'Above location of the first error may be approximate.\n'
            msg += 'The invalid JSON reform text is between the lines:\n'
            bline = 'XX----.----1----.----2----.----3----.----4'
            bline += '----.----5----.----6----.----7'
            msg += bline + '\n'
            linenum = 0
            for line in json_str.split('\n'):
                linenum += 1
                msg += '{:02d}{}'.format(linenum, line) + '\n'
            msg += bline + '\n'
            raise ValueError(msg)
        # check key contents of dictionary
        actual_keys = set(raw_dict.keys())
        missing_keys = Calculator.REQUIRED_REFORM_KEYS - actual_keys
        if missing_keys:
            msg = 'required key(s) "{}" missing from policy reform file'
            raise ValueError(msg.format(missing_keys))
        illegal_keys = actual_keys - Calculator.REQUIRED_REFORM_KEYS
        if illegal_keys:
            msg = 'illegal key(s) "{}" in policy reform file'
            raise ValueError(msg.format(illegal_keys))
        # convert raw_dict['policy'] dictionary into prdict
        raw_dict_policy = raw_dict['policy']
        tdict = Policy.translate_json_reform_suffixes(raw_dict['policy'])
        prdict = Calculator._convert_parameter_dict(tdict)
        return prdict

    @staticmethod
    def _read_json_econ_assump_text(text_string):
        """
        Strip //-comments from text_string and return 5 dict based on the JSON.
        Specified text is JSON with at least 5 high-level key:value pairs:
        a "consumption": {...} pair,
        a "behavior": {...} pair,
        a "growdiff_baseline": {...} pair,
        a "growdiff_response": {...} pair, and
        a "growmodel": {...} pair.
        Other keys such as "policy" will raise a ValueError.
        The {...}  object may be empty (that is, be {}), or
        may contain one or more pairs with parameter string primary keys
        and string years as secondary keys.  See tests/test_calculator.py for
        an extended example of a commented JSON economic assumption text
        that can be read by this method.
        Note that an example is shown in the ASSUMP_CONTENTS string in
        the tests/test_calculator.py file.
        Returned dictionaries (cons_dict, behv_dict, gdiff_baseline_dict,
        gdiff_respose_dict, growmodel_dict) have integer years as primary
        keys and string parameters as secondary keys.
        These returned dictionaries are suitable as the arguments to
        the Consumption.update_consumption(cons_dict) method, or
        the Behavior.update_behavior(behv_dict) method, or
        the GrowDiff.update_growdiff(gdiff_dict) method, or
        the GrowModel.update_growmodel(growmodel_dict) method.
        """
        # pylint: disable=too-many-locals
        # strip out //-comments without changing line numbers
        json_str = re.sub('//.*', ' ', text_string)
        # convert JSON text into a Python dictionary
        try:
            raw_dict = json.loads(json_str)
        except ValueError as valerr:
            msg = 'Economic assumption text below contains invalid JSON:\n'
            msg += str(valerr) + '\n'
            msg += 'Above location of the first error may be approximate.\n'
            msg += 'The invalid JSON asssump text is between the lines:\n'
            bline = 'XX----.----1----.----2----.----3----.----4'
            bline += '----.----5----.----6----.----7'
            msg += bline + '\n'
            linenum = 0
            for line in json_str.split('\n'):
                linenum += 1
                msg += '{:02d}{}'.format(linenum, line) + '\n'
            msg += bline + '\n'
            raise ValueError(msg)
        # check key contents of dictionary
        actual_keys = set(raw_dict.keys())
        missing_keys = Calculator.REQUIRED_ASSUMP_KEYS - actual_keys
        if missing_keys:
            msg = 'required key(s) "{}" missing from economic assumption file'
            raise ValueError(msg.format(missing_keys))
        illegal_keys = actual_keys - Calculator.REQUIRED_ASSUMP_KEYS
        if illegal_keys:
            msg = 'illegal key(s) "{}" in economic assumption file'
            raise ValueError(msg.format(illegal_keys))
        # convert the assumption dictionaries in raw_dict
        key = 'consumption'
        cons_dict = Calculator._convert_parameter_dict(raw_dict[key])
        key = 'behavior'
        behv_dict = Calculator._convert_parameter_dict(raw_dict[key])
        key = 'growdiff_baseline'
        gdiff_base_dict = Calculator._convert_parameter_dict(raw_dict[key])
        key = 'growdiff_response'
        gdiff_resp_dict = Calculator._convert_parameter_dict(raw_dict[key])
        key = 'growmodel'
        growmodel_dict = Calculator._convert_parameter_dict(raw_dict[key])
        return (cons_dict, behv_dict, gdiff_base_dict, gdiff_resp_dict,
                growmodel_dict)

    @staticmethod
    def _convert_parameter_dict(param_key_dict):
        """
        Converts specified param_key_dict into a dictionary whose primary
        keys are assessment years, and hence, is suitable as the argument
        to the Policy.implement_reform() method.

        Specified input dictionary has string parameter primary keys and
        string years as secondary keys.

        Returned dictionary has integer years as primary keys and
        string parameters as secondary keys.
        """
        # convert year skey strings into integers and
        # optionally convert lists into np.arrays
        year_param = dict()
        for pkey, sdict in param_key_dict.items():
            if not isinstance(pkey, str):
                msg = 'pkey {} in reform is not a string'
                raise ValueError(msg.format(pkey))
            rdict = dict()
            if not isinstance(sdict, dict):
                msg = 'pkey {} in reform is not paired with a dict'
                raise ValueError(msg.format(pkey))
            for skey, val in sdict.items():
                if not isinstance(skey, str):
                    msg = 'skey {} in reform is not a string'
                    raise ValueError(msg.format(skey))
                else:
                    year = int(skey)
                rdict[year] = val
            year_param[pkey] = rdict
        # convert year_param dictionary to year_key_dict dictionary
        year_key_dict = dict()
        years = set()
        for param, sdict in year_param.items():
            for year, val in sdict.items():
                if year not in years:
                    years.add(year)
                    year_key_dict[year] = dict()
                year_key_dict[year][param] = val
        return year_key_dict
