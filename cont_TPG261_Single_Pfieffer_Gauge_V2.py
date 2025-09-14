'''
Author: Kenneth Shepherd Jr
Purpose: Interface with the TPG261 Single Pfieffer Gauge
Version: 2
changelog: 
    2025_01_15 added code to sync the time clocks
Date Created: 2024/12/19
'''

import numpy as np
import time
import datetime
import tkinter as tk
import matplotlib.pyplot as plt
import os

# import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# import equipment modules
import pack_Pfieffer_TPG261


# plot config
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['lines.linewidth'] = 1
plt.rcParams['axes.labelsize'] = 10 
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 8
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=['black'])
plt.rcParams['lines.markersize'] = 2

figsize_x = 5
figsize_y = 3


################################################################################################
################################################################################################
            
        
class TPG261_GUI(tk.Frame):
    """ Class for pfieffer TGP261 Single Gauge pressure controller interfacing"""
    
    def __init__(self, master, name, Data):
        tk.Frame.__init__(self, master)
        self.master = master
        self.name = name
        self.Data = Data
        
        self.keys = ['pressure', 'state', 'sensor1',  'sensor2', 'cal_g1', 'cal_g2']
        self.label_names = ['Pressure (Torr)', 'State', 'Sensor 1', 'Sensor 2', 'Calibration (Sen1)', 'Calibration (Sen2)']

        #################
        ### Variables ###
        #################

        self.plot_limits = tk.StringVar(master, 'full')  # for radio buttons in plot window
        self.plot_dt = tk.IntVar(master, 10) # plot delta time for scroll option
                
        ####################
        ### Plot Display ###
        ####################
        self.frame = {}
        
        self.frame['Plot'] = tk.Frame(master)
        self.frame['Plot'].grid(row=0, column=0, padx=10, pady=10)
        
        self.f = Figure(figsize=(figsize_x, figsize_y))
        self.ax = self.f.add_subplot(111)

        self.ax.set_xlabel('Time (minutes)')
        self.ax.set_ylabel('Pressure (Torr)')
#        self.ax.set_yscale('log')
        
        self.pressure_plot, = self.ax.plot(self.Data.time_list, self.Data.P_list, 'o-', label='Pressure')
        self.canvas = FigureCanvasTkAgg(self.f, self.frame['Plot'])
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=4, padx=10, pady=5)
        
        self.Radio_Full = tk.Radiobutton(self.frame['Plot'], text='Full Time', variable=self.plot_limits, value='full')
        self.Radio_Full.grid(row=1 ,column=0)
        
        self.Radio_dt = tk.Radiobutton(self.frame['Plot'], text='Delta T', variable=self.plot_limits, value='dt')
        self.Radio_dt.grid(row=1, column=1)
        self.Radio_Combo = tk.OptionMenu(self.frame['Plot'], self.plot_dt, 1, 5, 10, 20, 30, 40, 50, 60)
        self.Radio_Combo.grid(row=1, column=2)
        self.Radio_Label = tk.Label(self.frame['Plot'], text='minutes').grid(row=1, column=3)
        
        self.Radio_log10 = tk.Radiobutton(self.frame['Plot'], text='Log10     ', variable=self.plot_limits, value='log10')
        self.Radio_log10.grid(row=2 ,column=0) 
        
        
        ############################
        ### Pressure Display (PD) ##
        ############################
        self.frame['PD'] = tk.LabelFrame(master,text='Current State', labelanchor='nw')
        self.frame['PD'].grid(row=1, column=0, sticky=tk.W+tk.E, padx=10, pady=10)
        
        self.PD_RO = {}
        self.labels = {}
        
        for i, key in enumerate(self.keys, 0):
            if i < 2:
                self.labels[key] = tk.Label(self.frame['PD'], text=self.label_names[i]).grid(row=i, column=0)
                self.PD_RO[key] = tk.Entry(self.frame['PD'], textvariable=self.Data.read_only[key])
                self.PD_RO[key].config(state='readonly')
                self.PD_RO[key].grid(row=i, column=1, padx=10, pady=5)

            else:
                self.labels[key] = tk.Label(self.frame['PD'], text=self.label_names[i]).grid(row=i-2, column=3)
                self.PD_RO[key] = tk.Entry(self.frame['PD'], textvariable=self.Data.read_only[key])
                self.PD_RO[key].config(state='readonly')
                self.PD_RO[key].grid(row=i-2, column=4, padx=10, pady=5)
                      
        self.PD_UI = {}
        self.entry = {}
        
        # creates entry boxes for the calibration 1 and calibration 2
        for i, key in enumerate(self.keys[4:], 4):
            self.entry[key] = tk.DoubleVar(master, Data.input_var[key].get())
            
            self.PD_UI[key] = tk.Label(self.frame['PD'], text=self.label_names[-2]).grid(row=i-2, column=0)
            self.PD_UI[key] = tk.Entry(self.frame['PD'], textvariable=self.Data.read_only[key])
            self.PD_UI[key].grid(row=i-2, column=1, padx=10, pady=5)
    
            self.PD_UI[key] = tk.Entry(self.frame['PD'], textvariable=self.entry[key])
            self.PD_UI[key].bind('<Return>', lambda event, key=key: self.callback(self.entry[key], self.Data.input_var[key]))
            self.PD_UI[key].bind('<FocusOut>', lambda event, key=key: self.off_click(self.entry[key], self.Data.input_var[key]))
            self.PD_UI[key].grid(row=i-2, column=1, padx=5, pady=5)
    
    def callback(self, a, b):
        """ Sets the set-point variable when entry-box is change after pressing enter """
        b.set(a.get())
        
    def off_click(self, a, b):
        """ Reset Entry Box to correct value when clicking off the entry box. This prevent the box from displaying a not current value"""
        a.set(b.get())
        
    def _update(self, plotdata='pressure'):
        """ Update Plots """
        # This is the lower limit of the pfieffer gauge
        ylim_low = 7.5e-10 + 0.3 * 7.5e-10  # the 0.3 is the STD
        ylim_low = 0.9*np.nanmin(self.Data.P_list)
        
        # Update Plot Data
        if plotdata == 'pressure':
            self.pressure_plot.set_xdata(self.Data.time_list) 
            self.pressure_plot.set_ydata(self.Data.P_list)
    
            # Update Plot Limits
            x_min = 0.9 * min(self.Data.time_list)
            x_max = 1.1 * max(self.Data.time_list)
            self.ax.set_xlim(x_min, x_max)
    
            if self.plot_limits.get() == 'full':
                self.ax.set_yscale('linear')
                self.ax.set_xlim(0.9*np.nanmin(self.Data.time_list), 1.1*np.nanmax(self.Data.time_list))
                self.ax.set_ylim(ylim_low, 1.1 * np.nanmax(self.Data.P_list))
            
            elif self.plot_limits.get() == 'dt':
                a = self.plot_dt.get()  # how many data points back in time
                self.ax.set_xlim(max(self.Data.time_list) - a, x_max)
                self.ax.set_ylim(ylim_low, 1.1 * np.nanmax(self.Data.P_list[-60 * a:]))
            
            elif self.plot_limits.get() == 'log10':
                self.ax.set_yscale('log')
                self.ax.set_ylim(ylim_low, 1000 * np.nanmax(self.Data.P_list))
    
            self.f.tight_layout()
            self.canvas.draw()
                
            
class Data_Structure_TPG261:
    """ Class to store global data used in GUI and to save logged data"""    
    
    def __init__(self, name, dt, start_time):
        # Meta Data
        self.name = name
        self.dt = dt
        self.start_time = start_time
        self.keys = ['pressure', 'state', 'sensor1',  'sensor2', 'cal_g1', 'cal_g2']
        
        self.read_only = {}
        self.input_var = {}
        
        # global variables
        for key in self.keys:
            if key in ['state', 'sensor1', 'sensor2']:
                self.read_only[key] = tk.StringVar()
            else:
                self.read_only[key] = tk.DoubleVar()
                self.input_var[key] = tk.DoubleVar()
                
        # plot arrays and data storage
        self.abs_time_list = [] # date time stamp
        self.time_list = []
        self.P_list = []
        self.state_list = []

        
    def data_update(self):
        """ Append Data to Lists"""
        
        self.abs_time_list.append(datetime.datetime.now())
        self.time_list.append((time.time()-self.start_time)/60)
        self.P_list.append(self.read_only['pressure'].get())
        self.state_list.append(self.read_only['state'].get())
        
    def save_prep(self):
        """ Prepare Data for Saving """
        SaveData = np.vstack((self.abs_time_list, self.time_list, self.state_list, self.P_list))
        SaveData = np.transpose(SaveData)
        
        return SaveData         
    
#--------------------------------------------------------------------------------------------------------      

####################
### Main Program ###
####################
        
if __name__=='__main__':    
    root = tk.Tk()
    root.title('TPG261 Pfeiffer Vacuum Single Gauge')
    
    SaveName = tk.StringVar(root)
    Clock = tk.StringVar(root,'0')
    Data_Num = tk.IntVar(root, 0)
    
    # save function
    def save_data(Data):
        tmp = datetime.datetime.now()
        date_time_stamp =f'{tmp.year}_{tmp.month:02d}_{tmp.day:02d}-{tmp.hour:02d}_{tmp.minute:02d}_{tmp.second:02d}_'
        SaveName = date_time_stamp + 'TPG261_pressure_controller'

        if len(Data) > 1:
            SaveData = np.hstack([Data[i] for i in range(len(Data))])
        else:
            SaveData = Data[0]
        print(SaveName)
        print(SaveData.shape)
        np.save(SaveName, SaveData)
        
    # quit function
    def _quit():
        # close serial connections
        TPG261.close()
        
        TPG261_save_data = TPG261_data.save_prep()
        # save data
        save_data([TPG261_save_data])
        
        # clear the signaling file after all controllers are ready
        with open('controller_ready.txt', 'w') as f:
            f.write('') # clear data
        
        # close application
        root.quit()
        root.destroy()  # prevent fatal error

    
    #############################################   
    ### Initialize Variables and Data Storage ###
    #############################################
    t0 = time.time()
    dt = 1000//10  # update time in milliseconds
    
    # initialize controller
    
    ports = {}
    ports['TPG261'] = 'COM23'
    TPG261_data = Data_Structure_TPG261('Pfieffer TPG261 Single Gauge', dt, t0)
    
    # TPG261 Pressure Controller
    TPG261 = pack_Pfieffer_TPG261.pfieffer_single_gauge_TPG261(ports['TPG261'])
    TPG261_data.read_only['pressure'].set(TPG261.get_pressure(gauge=1)[1])
    TPG261_data.read_only['state'].set(TPG261.get_pressure(gauge=1)[0])
    TPG261_data.read_only['sensor1'].set(TPG261.get_gauge_type()[0])
    TPG261_data.read_only['sensor2'].set(TPG261.get_gauge_type()[1])
    TPG261_data.read_only['cal_g1'].set(TPG261.get_calibration_factor()[0])
    TPG261_data.read_only['cal_g2'].set(TPG261.get_calibration_factor()[1])

#### NEW CODE 2025_01_15 Remove in a new version ####           
    
    with open('controller_ready.txt', 'a') as f:
        f.write('TPG261_Controller is ready\n')
        
    # waiting for all controllers to be ready
    expected_controllers = ['Substrate_Controller', 'TPG261_Controller', 'MKS_Pressure_Controller', 'BKP_Arb_Waveform_Controller']
    ready = False
    
    while not ready:
        with open('controller_ready.txt', 'r') as f:
            lines = f.readlines()
            
        ready = all(f'{controller} is ready\n' in lines for controller in expected_controllers)
        
        if not ready:
            print('Waiting for all controllers to be ready')
            time.sleep(0.01)
            
    
#### End new code ######      
    
    #########################   
    ### Create GUI Layout ###
    #########################   

    window = {}
    GUI = {}
    Width = 700
    Height = 700
    
    # TPG261 Single Gauge GUI
    window['TPG261 GUI'] = tk.LabelFrame(root, text='TPG261 Single Gauge Pressure Controller', font=('Helvetica', 15, 'bold'), labelanchor='n', width=Width, height=Height)
    window['TPG261 GUI'].grid(row=0, column=2, padx=10, pady=10, sticky=tk.N)
    
    GUI['TPG261'] = TPG261_GUI(window['TPG261 GUI'], 'Pressure', TPG261_data)
    GUI['TPG261'].grid(row=0, column=0)
    
    
    # Clock Display
    window['remaining widgets'] = tk.LabelFrame(window['TPG261 GUI'], text='Widgets', font=('Helvetica', 15, 'bold'), labelanchor='n')
    window['remaining widgets'].grid(row=3, column=0, sticky=tk.W, padx=10, pady=10)
    
    Clock_Label = tk.Label(window['remaining widgets'], text='Clock (min)').grid(row=3 ,column=0, pady=5)
    Clock_Display = tk.Entry(window['remaining widgets'], textvariable=Clock,font=('Helvetica', 13))
    Clock_Display.config('readonly')
    Clock_Display.grid(row=3, column=1, padx=5, pady=5)
    
    # Data Point Display
    Data_Point_Display = tk.Label(window['remaining widgets'], text='Data Point').grid(row=4, column=0, pady=5)
    Data_Point = tk.Entry(window['remaining widgets'], textvariable=Data_Num, font=('Helvetica', 13))
    Data_Point.config('readonly')
    Data_Point.grid(row=4, column=1, padx=5, pady=5)
        
    # Quit Button   
    Q_button = tk.Button(window['remaining widgets'], text='Quit',command=_quit, font=20, width=20)
    Q_button.grid(row=6, column=1, padx=5, pady=5)

    
    ########################
    ### Events and Loops ###
    ########################

    
    #################################
    ###### TPG 261 Cont  ############    
    ################################# 
    
    def set_Calibration_TPG261_gauge1(cont_TPG216, data):
        cont_TPG216.set_calibration_factor(1, data.input_var['cal_g1'].get())
        
    def set_Calibration_TPG261_gauge2(cont_TPG216, data):
        cont_TPG216.set_calibration_factor(2, data.input_var['cal_g2'].get())
        
        
    TPG261_data.input_var['cal_g1'].trace('w', lambda a, b, c: set_Calibration_TPG261_gauge1(TPG261, TPG261_data))
    TPG261_data.input_var['cal_g2'].trace('w', lambda a, b, c: set_Calibration_TPG261_gauge2(TPG261, TPG261_data))
    
    
    # Update Loop
    def update(t0):
        """ updates the data values after a pre-set time dt"""       
        
        # update the TPG261 Controller
        TPG261_data.read_only['pressure'].set(TPG261.get_pressure(gauge=1)[1])
        TPG261_data.read_only['state'].set(TPG261.get_pressure(gauge=1)[0])
        TPG261_data.read_only['cal_g1'].set(TPG261.get_calibration_factor()[0])
        TPG261_data.read_only['cal_g2'].set(TPG261.get_calibration_factor()[1])
        
        # Append to Data lists
        TPG261_data.data_update()
        
        # Update plots
        GUI['TPG261']._update()
        
        # Update Clock and Data Point Counter
        Clock.set(str((time.time()-t0)/60)[:-10])
        Data_Num.set(Data_Num.get() + 1)
        
        # Continue Loop
        root.after(dt, lambda: update(t0)) 
        
        
    root.after(0, lambda: update(t0))
    
    # Start main Loop
    
    root.protocol('WM_DELETE_WINDOW', _quit)
    root.mainloop()