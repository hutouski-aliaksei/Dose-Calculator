import numpy as np
from scipy import interpolate
from datetime import *
import sqlite3 as sq
import pandas as pd


class Source:
    def __init__(self, database, number, cur_date, distance):
        self._name = database.sources.Isotope[number]
        self._number = number
        self._serial = str(database.sources.SourceNumber[number])
        self._prod_date = database.sources.ProductionDate[number]
        self._cur_date = cur_date
        self._original_activity = round(database.sources.OriginalActivity_Bq[number])
        self._halflife = database.halflife.Half_life_d[database.halflife.Isotope == self._name].values[0]
        self._lines = database.read('Lines', self._name)
        self._distance = distance
        self._current_activity = 0
        self.decay()
        self._flux = []
        self._kerma_rate = []
        self._dose_rate = []

    @property
    def name(self):
        return self._name

    @property
    def number(self):
        return self._number

    @property
    def serial(self):
        return self._serial

    @property
    def prod_date(self):
        return self._prod_date

    @property
    def cur_date(self):
        return self._cur_date

    @property
    def original_activity(self):
        return self._original_activity

    @property
    def halflife(self):
        return self._halflife

    @property
    def lines(self):
        return self._lines

    @property
    def distance(self):
        return self._distance

    @property
    def kerma_rate(self):
        return self._kerma_rate

    @property
    def flux(self):
        return self._flux

    @property
    def dose_rate(self):
        return self._dose_rate

    @property
    def current_activity(self):
        return self._current_activity

    @name.setter
    def name(self, value):
        self._name = value

    @serial.setter
    def serial(self, value):
        self._serial = value

    @prod_date.setter
    def prod_date(self, value):
        self._prod_date = value

    @cur_date.setter
    def cur_date(self, value):
        self._cur_date = value

    @original_activity.setter
    def original_activity(self, value):
        self._original_activity = value

    @halflife.setter
    def halflife(self, value):
        self._halflife = value

    @lines.setter
    def lines(self, value):
        self._lines = value

    @distance.setter
    def distance(self, value):
        self._distance = value

    @current_activity.setter
    def current_activity(self, value):
        self._current_activity = value

    def decay(self):
        p_d = datetime.strptime(self._prod_date, '%m/%d/%Y')
        c_d = datetime.strptime(self._cur_date, '%m/%d/%Y')
        delta = c_d - p_d
        decay_time = delta.days
        current_activity = round(self._original_activity * np.exp(-(0.693 / self._halflife) * decay_time))
        self._current_activity = current_activity

    def line_kerma_rate(self, dose_type):
        kerma_interpolated = interpolate.interp1d(dose_type.kerma_coeffs[:, 0], dose_type.kerma_coeffs[:, 1], fill_value='extrapolate')
        kerma_value = kerma_interpolated(self._lines[:, 0]) * 3600
        kerma_rate = kerma_value * self._flux
        self._kerma_rate = kerma_rate

    def line_flux(self, shield, air_shield):
        s_a = np.arcsin(np.sin(0.5 / self._distance) ** 2) / np.pi
        flux = (self._lines[:, 1] / 100) * self._current_activity * s_a * shield.attenuation_values * air_shield.attenuation_values
        self._flux = flux
               # attenuation(att_coeff_air, energy, distance_cm - thickness_cm) * \
               # attenuation(att_coeff_material, energy, thickness_cm)

    def line_dose_rate(self, dose_type):
        h10_interpolated = interpolate.interp1d(dose_type.coefficients[:, 0], dose_type.coefficients[:, 1], fill_value='extrapolate')
        d_r = self._kerma_rate * h10_interpolated(self._lines[:, 0])
        self._dose_rate = d_r

class DoseType:
    def __init__(self, type, coefficients, kerma_coeffs):
        self._type = type
        self._coefficients = coefficients
        self._kerma_coeffs = kerma_coeffs

    @property
    def coefficients(self):
        return self._coefficients

    @property
    def type(self):
        return self._type

    @property
    def kerma_coeffs(self):
        return self._kerma_coeffs

    @coefficients.setter
    def coefficients(self, value):
        self._coefficients = value

    @type.setter
    def type(self, value):
        self._type = value


class Shield:
    def __init__(self, material, thickness, coefficients):
        self._material = material
        self._thickness = thickness
        self._coefficients = coefficients
        self._attenuation_values = []

    @property
    def coefficients(self):
        return self._coefficients

    @property
    def thickness(self):
        return self._thickness

    @property
    def material(self):
        return self._material

    @property
    def attenuation_values(self):
        return self._attenuation_values

    @coefficients.setter
    def coefficients(self, value):
        self._coefficients = value

    @thickness.setter
    def thickness(self, value):
        self._thickness = value

    @material.setter
    def material(self, value):
        self._material = value

    def attenuation(self, energy):
        attenuation_interpolated = interpolate.interp1d(self._coefficients[:, 0], self._coefficients[:, 1],
                                                        fill_value='extrapolate')
        attenuation_values = np.exp(-self._thickness * attenuation_interpolated(energy))
        self._attenuation_values = attenuation_values


class Database:
    def __init__(self, name):
        self._name = name
        con = sq.connect(self._name)
        self._cur = con.cursor()
        self._sources = self.read('Sources', '')
        self._halflife = self.read('Halflife', '')

    @property
    def sources(self):
        return self._sources

    @property
    def halflife(self):
        return self._halflife

    def read(self, table, name):
        data = np.zeros(5)
        if table in ['DoseConversionCoefficients', 'Materials']:
            res = self._cur.execute(f"select energy, {name} from {table} where {name} is not null order by energy asc")
            data = res.fetchall()
            data = np.array(data)
        elif table == 'Sources':
            res = self._cur.execute(f"select * from {table} order by id asc")
            data = res.fetchall()
            data = pd.DataFrame(data)
            data.columns = ['Number', 'Isotope', 'SourceNumber', 'ProductionDate', 'OriginalActivity_Bq']
        elif table == 'Halflife':
            res = self._cur.execute(f"select * from {table} order by Isotope asc")
            data = res.fetchall()
            data = pd.DataFrame(data)
            data.columns = ['Isotope', 'Half_life_d']
        elif table == 'Lines':
            res = self._cur.execute(f"select energy, yield from {table} where isotope = '{name}' order by energy asc")
            data = res.fetchall()
            data = np.array(data)
        return data
