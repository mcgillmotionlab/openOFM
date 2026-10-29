import os
from utils.utils import c3d_to_dict
from OFM2 import OFM2
from plotting_ofm2 import plot_ofm2_results

data_folder = os.path.join(os.getcwd(), 'Data_Sample', 'Sample')
static_path = r"C:\Users\avoce\PycharmProjects\openOFM\Data_Sample\Sample\static.c3d" # os.path.abspath(os.path.join(data_folder, 'static.c3d'))
dynamic_path = r"C:\Users\avoce\PycharmProjects\openOFM\Data_Sample\Sample\dynamic.c3d" # os.path.abspath(os.path.join(data_folder, 'dynamic.c3d'))
save_dir = r"C:\Users\avoce\PycharmProjects\openOFM\Data_Sample\OFM2"
def main():
    static_data = c3d_to_dict(static_path)
    dynamic_data = c3d_to_dict(dynamic_path)

    ofm = OFM2.from_dict(static_data)
    ofm.run_dict(static_data, static=True)
    results = ofm.run_dict(dynamic_data) 
    trial_plus = {**dynamic_data, **results}

    plots = plot_ofm2_results(results, save_dir=save_dir)

    return results, trial_plus, plots

'''
Missing markers:
R/LNAV, R/LP23M, R/LD4M

Causes no calculation for:
R/LMedForefootHindfootAngles2
R/LLatForefootHindfootAngles2
R/LIntForefootHindfootAngles2
R/LMedLongArchAngles2
'''

if __name__ == "__main__":
    results, trial_plus, plots = main()













