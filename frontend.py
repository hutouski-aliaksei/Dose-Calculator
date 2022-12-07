import datetime
import tkcalendar
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from beckend import *


class MainApp(ThemedTk):
    def __init__(self):
        super().__init__()

        self._now = datetime.now().strftime('%m/%d/%Y')
        self._db = Database('DoseCalculator_DB.db')
        self._source = Source(self._db, 0, self._now, 10)
        self._airshield = Shield('Air', self._source.distance, self._db.read('Materials', 'Air'))
        self._shield = Shield('Air', 0, self._db.read('Materials', 'Air'))
        self._dose_t = DoseType('Ambient', self._db.read('DoseConversionCoefficients', 'Ambient'), self._db.read('DoseConversionCoefficients', 'Kerma'))

        self.set_theme('ubuntu')
        self['bg'] = '#f6f4f2'
        self.title('Dose Calculator')
        self.geometry("800x600")
        self.resizable(False, False)

        small_font = ("Helvetica", 10)
        big_font = ("Helvetica", 14)
        standart_width = 18
        vertical_pad = 10

        parameters_frame = tk.Frame(self)
        parameters_frame['bg'] = '#f6f4f2'
        parameters_frame.grid(row=0, column=0, rowspan=2)

        results_frame = tk.Frame(self)
        results_frame['bg'] = '#f6f4f2'
        results_frame.grid(row=0, column=1, padx=vertical_pad*2)

        table_frame = tk.Frame(self)
        table_frame['bg'] = '#f6f4f2'
        table_frame.grid(row=1, column=1, padx=vertical_pad * 2)

        catalogue_label = ttk.Label(parameters_frame, text='Sources catalogue', font=small_font, width=standart_width)
        catalogue_label.grid(row=0, column=0, pady=vertical_pad)

        self._selected_source = tk.StringVar()
        source_cb = ttk.Combobox(parameters_frame, textvariable=self._selected_source, font=small_font, width=standart_width)
        source_cb['values'] = [str(self._db.sources.Number[m]) + '  ' + self._db.sources.Isotope[m] + ' ' +
                               self._db.sources.SourceNumber[m] for m in range(len(self._db.sources))]
        source_cb['state'] = 'readonly'
        source_cb.grid(row=0, column=1, pady=vertical_pad)
        source_cb.bind('<<ComboboxSelected>>', self.source_changed)

        source_parameters_label = ttk.Label(parameters_frame, text='Source parameters', font=small_font, width=standart_width)
        source_parameters_label.grid(row=1, column=0, columnspan=2, ipady=vertical_pad)

        isotope_label = ttk.Label(parameters_frame, text='Isotope', font=small_font, width=standart_width)
        isotope_label.grid(row=2, column=0, pady=vertical_pad-5)

        self._selected_isotope = tk.StringVar()
        isotope_cb = ttk.Combobox(parameters_frame, textvariable=self._selected_isotope, font=small_font, width=standart_width)
        isotope_cb['values'] = [self._db.halflife.Isotope[m] for m in range(len(self._db.halflife))]
        isotope_cb['state'] = 'readonly'
        isotope_cb.grid(row=2, column=1, pady=vertical_pad-5)
        isotope_cb.bind('<<ComboboxSelected>>', self.isotope_changed)

        halflife_label = ttk.Label(parameters_frame, text='Halflife, days', font=small_font, width=standart_width)
        halflife_label.grid(row=3, column=0, pady=vertical_pad-5)

        self._halflife = tk.StringVar()
        hl_box = ttk.Entry(parameters_frame, textvariable=self._halflife, width=standart_width + 2, font=small_font)
        hl_box.grid(row=3, column=1, pady=vertical_pad-5)
        hl_box['state'] = 'readonly'

        pdor_date_label = ttk.Label(parameters_frame, text='Production date', font=small_font, width=standart_width)
        pdor_date_label.grid(row=4, column=0, pady=vertical_pad-5)

        self._prod_date = tk.StringVar()
        prod_date_pick = tkcalendar.DateEntry(parameters_frame, selectmode='day', width=standart_width, textvariable=self._prod_date,
                                              date_pattern='m/d/Y', font=small_font)
        prod_date_pick.grid(row=4, column=1, pady=vertical_pad-5)
        prod_date_pick['state'] = 'readonly'
        prod_date_pick.bind('<<DateEntrySelected>>', self.prod_date_changed)

        original_activity_label = ttk.Label(parameters_frame, text='Original activity, Bq', font=small_font, width=standart_width)
        original_activity_label.grid(row=5, column=0, pady=vertical_pad-5)

        self._original_activity = tk.StringVar()
        original_activity_box = ttk.Entry(parameters_frame, textvariable=self._original_activity, width=standart_width + 2,
                                          font=small_font)
        original_activity_box.grid(row=5, column=1, pady=vertical_pad-5)
        self._original_activity.trace('w', self.original_activity_changed)

        cur_date_label = ttk.Label(parameters_frame, text='Current date', font=small_font, width=standart_width)
        cur_date_label.grid(row=6, column=0, pady=vertical_pad-5)

        self._cur_date = tk.StringVar()
        cur_date_pick = tkcalendar.DateEntry(parameters_frame, selectmode='day', width=standart_width, textvariable=self._cur_date,
                                             date_pattern='mm/dd/Y', font=small_font)
        cur_date_pick.grid(row=6, column=1, pady=vertical_pad-5)
        cur_date_pick['state'] = 'readonly'
        cur_date_pick.bind('<<DateEntrySelected>>', self.cur_date_changed)

        current_activity_label = ttk.Label(parameters_frame, text='Current activity, Bq', font=small_font, width=standart_width)
        current_activity_label.grid(row=7, column=0, pady=vertical_pad-5)

        self._current_activity = tk.StringVar()
        current_activity_box = ttk.Entry(parameters_frame, textvariable=self._current_activity, width=standart_width + 2, font=small_font)
        current_activity_box.grid(row=7, column=1, pady=vertical_pad-5)
        self._current_activity.trace('w', self.current_activity_changed)

        shield_parameters_label = ttk.Label(parameters_frame, text='Shield parameters', font=small_font, width=standart_width)
        shield_parameters_label.grid(row=8, column=0, columnspan=2, pady=vertical_pad)

        material_label = ttk.Label(parameters_frame, text='Material', font=small_font, width=standart_width)
        material_label.grid(row=9, column=0, pady=vertical_pad-5)

        self._selected_material = tk.StringVar()
        material_cb = ttk.Combobox(parameters_frame, textvariable=self._selected_material, font=small_font, width=standart_width)
        material_cb['values'] = ['Air', 'Iron', 'Lead', 'Aluminium', 'Copper', 'Tin', 'PMMA']
        material_cb['state'] = 'readonly'
        material_cb.grid(row=9, column=1, pady=vertical_pad-5)
        material_cb.bind('<<ComboboxSelected>>', self.material_changed)

        thickness_label = ttk.Label(parameters_frame, text='Thickness, cm', font=small_font, width=standart_width)
        thickness_label.grid(row=10, column=0, pady=vertical_pad-5)

        self._thickness = tk.StringVar()
        thickness_box = ttk.Entry(parameters_frame, textvariable=self._thickness, width=standart_width + 2, font=small_font)
        thickness_box.grid(row=10, column=1, pady=vertical_pad-5)
        self._thickness.trace('w', self.thickness_changed)

        distance_label = ttk.Label(parameters_frame, text='Distance, cm', font=small_font, width=standart_width)
        distance_label.grid(row=11, column=0, pady=vertical_pad-5)

        self._distance = tk.StringVar()
        distance_box = ttk.Entry(parameters_frame, textvariable=self._distance, width=standart_width + 2, font=small_font)
        distance_box.grid(row=11, column=1, pady=vertical_pad-5)
        self._distance.trace('w', self.distance_changed)

        dose_type_label = ttk.Label(parameters_frame, text='Dose type', font=small_font, width=standart_width)
        dose_type_label.grid(row=12, column=0, pady=vertical_pad)

        self._dose_type = tk.StringVar()
        dose_type_cb = ttk.Combobox(parameters_frame, textvariable=self._dose_type, font=small_font, width=standart_width)
        dose_type_cb['values'] = ['Ambient', 'Personal']
        dose_type_cb['state'] = 'readonly'
        dose_type_cb.grid(row=12, column=1, pady=vertical_pad-5)
        dose_type_cb.bind('<<ComboboxSelected>>', self.dose_type_changed)

        self._der_label = ttk.Label(results_frame, text='Dose equivalent rate, uSv/h', font=big_font)
        self._der_label.grid(row=0, column=0, pady=vertical_pad)

        self._der_result_label = ttk.Label(results_frame, text='0', font=big_font)
        self._der_result_label.grid(row=2, column=0, pady=vertical_pad, padx=vertical_pad)

        self._flux_label = ttk.Label(results_frame, text='Flux, p/cm\u00B2s', font=big_font)
        self._flux_label.grid(row=3, column=0, pady=vertical_pad)

        self._flux_result_label = ttk.Label(results_frame, text='0', font=big_font)
        self._flux_result_label.grid(row=4, column=0, pady=vertical_pad, padx=vertical_pad)

        columnwidth = 79
        style = ttk.Style()
        style.configure('mystyle.Treeview', font=small_font)
        style.configure('mystyle.Treeview.Heading', font=small_font)
        columns = ('Energy', 'Yield', 'KR', 'DER', 'Flux')
        self._table = ttk.Treeview(table_frame, columns=columns, show='headings', style='mystyle.Treeview', height=10)
        self._table.column('Energy', width=columnwidth + 2)
        self._table.column('Yield', width=columnwidth)
        self._table.column('KR', width=columnwidth)
        self._table.column('DER', width=columnwidth)
        self._table.column('Flux', width=columnwidth)
        self._table.heading('Energy', text='Energy, keV')
        self._table.heading('Yield', text='Yield, %')
        self._table.heading('KR', text='KR, uGy/h')
        self._table.heading('DER', text='DER, uSv/h')
        self._table.heading('Flux', text='Flux, p/cm\u00B2s')
        self._table.grid(row=0, column=0, columnspan=4)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self._table.yview)
        self._table.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=4, ipady=85)

        self.screen_update()

    def screen_update(self):
        self._selected_source.set(str(self._source.number + 1) + ' ' + self._source.name + ' ' + self._source.serial)
        self._selected_isotope.set(self._source.name)
        self._halflife.set(self._source.halflife)
        self._prod_date.set(self._source.prod_date)
        self._original_activity.set(self._source.original_activity)
        self._current_activity.set(self._source.current_activity)
        self._selected_material.set(self._shield.material)
        self._thickness.set(self._shield.thickness)
        self._distance.set(self._source.distance)
        self._dose_type.set(self._dose_t.type)
        self.results_update()

    def source_changed(self, event):
        source_index = int(self._selected_source.get().split(' ')[0]) - 1
        self._source = Source(self._db, source_index, self._cur_date.get(), float(self._distance.get()))
        self.screen_update()

    def isotope_changed(self, event):
        self._source.name = self._selected_isotope.get()
        self._source.halflife = self._db.halflife.Half_life_d[self._db.halflife.Isotope == self._source.name].values[0]
        self._source.prod_date = self._prod_date.get()
        self._source.original_activity = int(self._original_activity.get())
        self._source.lines = self._db.read('Lines', self._source.name)
        self._source.decay()
        self.screen_update()

    def original_activity_changed(self, *args):
        try:
            self._source.original_activity = int(self._original_activity.get())
            self._source.decay()
            self.screen_update()
        except ValueError:
            self._der_result_label['text'] = 'Wrong activity'

    def cur_date_changed(self, event):
        p_d = datetime.strptime(self._prod_date.get(), '%m/%d/%Y')
        c_d = datetime.strptime(self._cur_date.get(), '%m/%d/%Y')
        delta = c_d - p_d
        if delta.days >= 0:
            self._source.cur_date = self._cur_date.get()
            self._source.decay()
            self.screen_update()
        else:
            self._der_result_label['text'] = 'Wrong date'

    def prod_date_changed(self, event):
        p_d = datetime.strptime(self._prod_date.get(), '%m/%d/%Y')
        c_d = datetime.strptime(self._cur_date.get(), '%m/%d/%Y')
        delta = c_d - p_d
        if delta.days >= 0:
            self._source.prod_date = self._prod_date.get()
            self._source.decay()
            self.screen_update()
        else:
            self._der_result_label['text'] = 'Wrong date'

    def current_activity_changed(self, *args):
        try:
            self._source.current_activity = int(self._current_activity.get())
            self.results_update()
        except ValueError:
            self._der_result_label['text'] = 'Wrong activity'

    def material_changed(self, event):
        self._shield = Shield(self._selected_material.get(), float(self._thickness.get()), self._db.read('Materials', self._selected_material.get()))
        self._shield.attenuation(self._source.lines[:, 0])
        self.results_update()

    def thickness_changed(self, *args):
        try:
            self._shield = Shield(self._selected_material.get(), float(self._thickness.get()), self._db.read('Materials', self._selected_material.get()))
            self._shield.attenuation(self._source.lines[:, 0])
            self.results_update()
        except ValueError:
            self._der_result_label['text'] = 'Wrong thickness'

    def distance_changed(self, *args):
        try:
            self._source.distance = float(self._distance.get())
            self.results_update()
        except ValueError:
            self._der_result_label['text'] = 'Wrong distance'

    def dose_type_changed(self, event):
        self._dose_t.type = self._dose_type.get()
        self._dose_t.coefficients = self._db.read('DoseConversionCoefficients', self._dose_t.type)
        self.results_update()

    def results_update(self):
        self._shield.attenuation(self._source.lines[:, 0])
        self._airshield.attenuation(self._source.lines[:, 0])
        self._source.line_flux(self._shield, self._airshield)
        self._source.line_kerma_rate(self._dose_t)
        self._source.line_dose_rate(self._dose_t)
        for row in self._table.get_children():
            self._table.delete(row)
        for i in range(len(self._source.lines)):
            self._table.insert('', tk.END,
                         values=(np.round(self._source.lines[i, 0] * 1000, 3), np.round(self._source.lines[i, 1], 3),
                                 np.round(self._source.kerma_rate[i], 3), np.round(self._source.dose_rate[i], 3),
                                 np.round(self._source.flux[i], 3)))

        total_dose = np.sum(self._source.dose_rate)
        total_flux = np.round(np.sum(self._source.flux), 3)

        if total_dose > 1000000:
            total_dose = total_dose / 1000000
            self._der_label['text'] = 'Dose equivalent rate, Sv/h'
        elif total_dose > 1000:
            total_dose = total_dose / 1000
            self._der_label['text'] = 'Dose equivalent rate, mSv/h'
        else:
            self._der_label['text'] = 'Dose equivalent rate, \u03BCSv/h'

        if total_flux > 1000000:
            total_flux = total_flux / 1000000
            self._flux_label['text'] = 'Flux, p/cm\u00B2s x 10\u2076'
        elif total_flux > 1000:
            total_flux = total_flux / 1000
            self._flux_label['text'] = 'Flux, p/cm\u00B2s x 10\u00B3'
        else:
            self._flux_label['text'] = 'Flux, p/cm\u00B2s'

        self._der_result_label['text'] = np.round(total_dose, 3)
        self._flux_result_label['text'] = np.round(total_flux, 3)

        if self._selected_isotope.get() in ['Cf-252', 'Cm-244']:
            self._der_result_label['text'] = 'Only flux for neutrons'
