import matplotlib.pyplot as plt

def plot_angles(data, vicon_data=None, plot_title="", gsettings=None):
    """ helper function to compare vicon and OFM angles"""
    defaults = {'LineWidth': 1.5, 'FontSize': 15, 'FontName': 'Arial', 
                'vcol': 'k', 'zcol': 'r', 'vstyle': '-', 'zstyle': '--', 'square': False}
    if gsettings:
        defaults.update(gsettings)
    
    gs = defaults
    
    plt.figure()
    plt.gcf().canvas.manager.set_window_title('multi-segment foot OFM for ' + plot_title)
    
    sides = ['Right', 'Left']
    joints = ['TIBA', 'FFTBA', 'HFTBA', 'FFHFA', 'HXFFA']
    titles = ['LabTibia', 'FF/TIB', 'HF/TB', 'FF/HF', 'HX/FF']
    
    def _plot_pane(idx, joint, v_dim, d_char, title_base, y_label=None):
        ax = plt.subplot(3, 10, idx)
        
        if vicon_data is not None:
            ax.plot(vicon_data[s + joint][:, v_dim], color=gs['vcol'], linestyle=gs['vstyle'], linewidth=gs['LineWidth'])
            nrmse_key = 'nrmse' + side + joint + '_' + d_char
            title_str = f"{s}{title_base}\n NRMSE = {data[nrmse_key]}"
            font_s = gs['FontSize'] * 0.8
        else:
            title_str = s + title_base
            font_s = gs['FontSize']

        ax.set_title(title_str, fontsize=font_s, fontname=gs['FontName'])
        ax.plot(data[side + joint + '_' + d_char], color=gs['zcol'], linestyle=gs['zstyle'], linewidth=gs['LineWidth'])
        
        if gs['square']: ax.axis('square')
        if y_label: ax.set_ylabel(y_label, fontsize=gs['FontSize'], fontname=gs['FontName'])
        return ax

    for i, side in enumerate(sides):
        s = side[0]
        off = 5 if side == 'Left' else 0

        # All joints: Vicon col 0, Data suffix 'x'
        for j, (joint, title) in enumerate(zip(joints, titles)):
            _plot_pane(off + j + 1, joint, 0, 'x', title, 
                       'Sagittal Angles (deg)' if j == 0 and i == 0 else None)

        #nNote: HXFFA (index 4) is skipped in original code for this row
        for j, (joint, title) in enumerate(zip(joints[:4], titles[:4])):
            # Logic from original: TIBA uses index 1/'y', others use 2/'z'
            v_idx = 1 if joint == 'TIBA' else 2
            d_char = 'y' if joint == 'TIBA' else 'z'
            
            _plot_pane(off + j + 11, joint, v_idx, d_char, title if vicon_data is None else "", 
                       'Coronal Angles (deg)' if j == 0 and i == 0 else None)

        for j, (joint, title) in enumerate(zip(joints, titles)):
            # TIBA uses index 2/'z', others use 1/'y'
            v_idx = 2 if joint == 'TIBA' else 1
            d_char = 'z' if joint == 'TIBA' else 'y'
            
            _plot_pane(off + j + 21, joint, v_idx, d_char, title if vicon_data is None else "", 
                       'Transverse Angles (deg)' if j == 0 and i == 0 else None)

        ax = plt.subplot(3, 10, off + 15)
        axPos = ax.get_position()
        ax.remove()
        lg = plt.legend(['ViconOFM', 'openFoot'], bbox_to_anchor=axPos.p0, loc='lower left')
        lg.get_frame().set_linewidth(0.0)

    plt.show()