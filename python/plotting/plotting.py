import matplotlib.pyplot as plt


def plot_angles(data, vicon_data=None, plot_title="", gsettings=None):
    """ helper function to compare vicon and OFM angles"""
    if gsettings is None:
        gsettings = {
            'LineWidth': 1.5,
            'FontSize': 15,
            'FontName': 'Arial',
            'vcol': 'k',
            'zcol': 'r',
            'vstyle': '-',
            'zstyle': '--',
            'square': False
        }

    vcol = gsettings['vcol']
    zcol = gsettings['zcol']
    vstyle = gsettings['vstyle']
    zstyle = gsettings['zstyle']
    LineWidth = gsettings['LineWidth']
    FontSize = gsettings['FontSize']
    FontName = gsettings['FontName']
    square = gsettings['square']

    plt.figure()
    plt.gcf().canvas.manager.set_window_title('multi-segment foot OFM for ' + plot_title)
    sides = ['Right', 'Left']
    for i, side in enumerate(sides):
        s = side[0]
        
        if side == 'Left':
            offset = 5
        else:
            offset = 0

        # sagittal plane
        ax = plt.subplot(3, 10, offset + 1)
        if vicon_data is not None:
            ax.plot(vicon_data[s + 'TIBA'][:, 0], color=vcol, linestyle=vstyle, linewidth=LineWidth)
            ax.set_title(s + 'LabTibia \n NRMSE = ' + data['nrmse' + side + 'TIBA_x'], fontsize=FontSize*0.8,
                         fontname=FontName)
        else:
            ax.set_title(s + 'LabTibia', fontsize=FontSize,fontname=FontName)
        ax.plot(data[side + 'TIBA_x'], color=zcol, linestyle=zstyle, linewidth=LineWidth)
        if square:
            ax.axis('square')

        if i == 0:
            ax.set_ylabel('Sagittal Angles (deg)', fontsize=FontSize, fontname=FontName)

        ax = plt.subplot(3, 10, offset + 2)
        if vicon_data is not None:
            ax.plot(vicon_data[s + 'FFTBA'][:, 0], color=vcol, linestyle=vstyle, linewidth=LineWidth)
            ax.set_title(s + 'FF/TIB \n NRMSE = ' + data['nrmse' + side + 'FFTBA_x'], fontsize=FontSize*0.8,
                         fontname=FontName)
        else:
            ax.set_title(s + 'FFTBA', fontsize=FontSize,fontname=FontName)
        ax.plot(data[side + 'FFTBA_x'], color=zcol, linestyle=zstyle, linewidth=LineWidth)

        if square:
            ax.axis('square')

        ax = plt.subplot(3, 10, offset + 3)
        if vicon_data is not None:
            ax.plot(vicon_data[s + 'HFTBA'][:, 0], color=vcol, linestyle=vstyle, linewidth=LineWidth)
            ax.set_title(s + 'HF/TB \n NRMSE = ' + data['nrmse' + side + 'HFTBA_x'], fontsize=FontSize*0.8,
                         fontname=FontName)
        else:
            ax.set_title(s + 'HFTBA', fontsize=FontSize,fontname=FontName)
        ax.plot(data[side + 'HFTBA_x'], color=zcol, linestyle=zstyle, linewidth=LineWidth)
        if square:
            ax.axis('square')

        ax = plt.subplot(3, 10, offset + 4)
        if vicon_data is not None:
            ax.plot(vicon_data[s + 'FFHFA'][:, 0], color=vcol, linestyle=vstyle, linewidth=LineWidth)
            ax.set_title(s + 'FF/HF \n NRMSE = ' + data['nrmse' + side + 'FFHFA_x'], fontsize=FontSize*0.8,
                         fontname=FontName)
        else:
            ax.set_title(s + 'FFHFA', fontsize=FontSize,fontname=FontName)
        ax.plot(data[side + 'FFHFA_x'], color=zcol, linestyle=zstyle, linewidth=LineWidth)
        if square:
            ax.axis('square')

        ax = plt.subplot(3, 10, offset + 5)
        if vicon_data is not None:
            ax.plot(vicon_data[s + 'HXFFA'][:, 0], color=vcol, linestyle=vstyle, linewidth=LineWidth)
            ax.set_title(s + 'HX/FF \n NRMSE = ' + data['nrmse' + side + 'HXFFA_x'], fontsize=FontSize*0.8,
                         fontname=FontName)
        else:
            ax.set_title(s + 'HXFFA', fontsize=FontSize,fontname=FontName)
        ax.plot(data[side + 'HXFFA_x'], color=zcol, linestyle=zstyle, linewidth=LineWidth)
        if square:
            ax.axis('square')

        # coronal plane
        ax = plt.subplot(3, 10, offset+11)
        if vicon_data is not None:
            ax.plot(vicon_data[s+'TIBA'][:, 1], color=vcol, linestyle=vstyle, linewidth=LineWidth)
            ax.set_title('NRMSE = ' + data['nrmse' + side + 'TIBA_y'], fontsize=FontSize*0.8,
                         fontname=FontName)
        ax.plot(data[side+'TIBA_y'], color=zcol, linestyle=zstyle, linewidth=LineWidth)
        if square:
            ax.axis('square')

        if i == 0:
            ax.set_ylabel('Coronal Angles (deg)', fontsize=FontSize, fontname=FontName)

        ax = plt.subplot(3, 10, offset+12)
        if vicon_data is not None:
            ax.plot(vicon_data[s+'FFTBA'][:, 2], color=vcol, linestyle=vstyle, linewidth=LineWidth)
            ax.set_title('NRMSE = ' + data['nrmse' + side + 'FFTBA_z'], fontsize=FontSize*0.8,
                         fontname=FontName)
        ax.plot(data[side+'FFTBA_z'], color=zcol, linestyle=zstyle, linewidth=LineWidth)
        if square:
            ax.axis('square')

        ax = plt.subplot(3, 10, offset+13)
        if vicon_data is not None:
            ax.plot(vicon_data[s+'HFTBA'][:, 2], color=vcol, linestyle=vstyle, linewidth=LineWidth)
            ax.set_title('NRMSE = ' + data['nrmse' + side + 'HFTBA_z'], fontsize=FontSize*0.8,
                         fontname=FontName)
        ax.plot(data[side+'HFTBA_z'], color=zcol, linestyle=zstyle, linewidth=LineWidth)
        if square:
            ax.axis('square')

        ax = plt.subplot(3, 10, offset+14)
        if vicon_data is not None:
            ax.plot(vicon_data[s+'FFHFA'][:, 2], color=vcol, linestyle=vstyle, linewidth=LineWidth)
            ax.set_title('NRMSE = ' + data['nrmse' + side + 'FFHFA_z'], fontsize=FontSize*0.8,
                         fontname=FontName)
        ax.plot(data[side+'FFHFA_z'], color=zcol, linestyle=zstyle, linewidth=LineWidth)
        if square:
            ax.axis('square')

        # ax = plt.subplot(3, 10, offset + 15)
        # if vicon_data is not None:
        #     ax.plot(vicon_data[s + 'ArchHeight'][:, 2], color=vcol, linestyle=vstyle, linewidth=LineWidth)
        #     ax.set_title(s + 'ArchHeight \n NRMSE = ' + data['nrmse' + side + 'ArchHeight'], fontsize=FontSize,
        #                  fontname=FontName)
        # ax.plot(data[s + 'ArchHeight_openOFM'][:, 2], color=zcol, linestyle=zstyle, linewidth=LineWidth)
        # if square:
        #     ax.axis('square')

        # transverse plane
        ax = plt.subplot(3, 10, offset+21)
        if vicon_data is not None:
            ax.plot(vicon_data[s+'TIBA'][:, 2], color=vcol, linestyle=vstyle, linewidth=LineWidth)
            ax.set_title('NRMSE = ' + data['nrmse' + side + 'TIBA_z'], fontsize=FontSize*0.8,
                         fontname=FontName)
        ax.plot(data[side+'TIBA_z'], color=zcol, linestyle=zstyle, linewidth=LineWidth)
        if square:
            ax.axis('square')

        if i == 0:
            ax.set_ylabel('Transverse Angles (deg)', fontsize=FontSize, fontname=FontName)

        ax = plt.subplot(3, 10, offset+22)
        if vicon_data is not None:
            ax.plot(vicon_data[s+'FFTBA'][:, 1], color=vcol, linestyle=vstyle, linewidth=LineWidth)
            ax.set_title('NRMSE = ' + data['nrmse' + side + 'FFTBA_y'], fontsize=FontSize*0.8,
                         fontname=FontName)
        ax.plot(data[side+'FFTBA_y'], color=zcol, linestyle=zstyle, linewidth=LineWidth)
        if square:
            ax.axis('square')

        ax = plt.subplot(3, 10, offset+23)
        if vicon_data is not None:
            ax.plot(vicon_data[s+'HFTBA'][:, 1], color=vcol, linestyle=vstyle, linewidth=LineWidth)
            ax.set_title('NRMSE = ' + data['nrmse' + side + 'HFTBA_y'], fontsize=FontSize*0.8,
                         fontname=FontName)
        ax.plot(data[side+'HFTBA_y'], color=zcol, linestyle=zstyle, linewidth=LineWidth)
        if square:
            ax.axis('square')

        ax = plt.subplot(3, 10, offset+24)
        if vicon_data is not None:
            ax.plot(vicon_data[s+'FFHFA'][:, 1], color=vcol, linestyle=vstyle, linewidth=LineWidth)
            ax.set_title('NRMSE = ' + data['nrmse' + side + 'FFHFA_y'], fontsize=FontSize*0.8,
                         fontname=FontName)
        ax.plot(data[side+'FFHFA_y'], color=zcol, linestyle=zstyle, linewidth=LineWidth)
        if square:
            ax.axis('square')

        ax = plt.subplot(3, 10, offset + 25)
        if vicon_data is not None:
            ax.plot(vicon_data[s + 'HXFFA'][:, 1], color=vcol, linestyle=vstyle, linewidth=LineWidth)
            ax.set_title('NRMSE = ' + data['nrmse' + side + 'HXFFA_y'], fontsize=FontSize*0.8,
                         fontname=FontName)
        ax.plot(data[side + 'HXFFA_y'], color=zcol, linestyle=zstyle, linewidth=LineWidth)
        if square:
            ax.axis('square')

        ax = plt.subplot(3, 10, offset + 15)
        axPos = ax.get_position()
        ax.remove()
        lg = ax.legend(['ViconOFM', 'openFoot'])
        lg.set_bbox_to_anchor(axPos)
        lg.get_frame().set_linewidth(0.0)

    plt.show()