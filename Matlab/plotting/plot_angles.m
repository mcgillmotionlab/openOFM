function plot_angles(data,vicon_data,plot_title,gsettings)

if nargin == 2
    plot_title = "";
end 

if nargin == 3
    gsettingsWidth = 1.5;                                  % graph line width
    gsettings.FontSize = 16;                                    % heading font size
    gsettings.FontName = 'Arial';                               % heading font name
    gsettings.vcol = 'k';                                       % color for vicon OFM
    gsettings.zcol = 'r';                                       % color for openOFM
    gsettings.vstyle = '-';                                     % style for vicon OFM
    gsettings.zstyle = '--';                                    % style for openOFM
end

vcol = gsettings.vcol;                              % color for vicon OFM
zcol = gsettings.zcol;                              % color for openOFM

vstyle = gsettings.vstyle;                          % style for vicon OFM
zstyle = gsettings.zstyle;                          % style for openOFM

LineWidth = gsettingsWidth;
FontSize = gsettings.FontSize;
FontName = gsettings.FontName;
square = false;

fh = figure('name', ['multi-segment foot OFM for ', plot_title]);

first = 1;
% last = 100;
[last,~] = size(vicon_data.RTIBA);

sides = {'Right','Left'};
for i = 1:length(sides)
    side = sides{i};
    s = side(1);
    
    if strcmp(side,'Left')
        offset= 5;
    else
        offset = 0;
    end
    
    % sagittal plane
    subplot(3,10,offset+1);
    plot(vicon_data.([s,'TIBA'])(first:last,1),'Color',vcol,'LineStyle',vstyle,'LineWidth',LineWidth)
    hold on
    plot(data.([side,'TIBA_x'])(first:last),'Color',zcol,'LineStyle',zstyle,'LineWidth',LineWidth)
    title([s,'LabTibia'],'FontSize',FontSize,'FontName',FontName)
    if square
        axis('square')
    end
    
    if i==1
        ylabel({'Sagittal','Angles','(deg)'},'FontSize',FontSize,'FontName',FontName)
    end
    
    subplot(3,10,offset+2);
    plot(vicon_data.([s,'FFTBA'])(first:last,1),'Color',vcol,'LineStyle',vstyle,'LineWidth',LineWidth)
    hold on
    plot(data.([side,'FFTBA_x'])(first:last),'Color',zcol,'LineStyle',zstyle,'LineWidth',LineWidth)
    title([s,'FF/TIB'],'FontSize',FontSize,'FontName',FontName)
    if square
        axis('square')
    end
    
    subplot(3,10,offset+3);
    plot(vicon_data.([s,'HFTBA'])(first:last,1),'Color',vcol,'LineStyle',vstyle,'LineWidth',LineWidth)
    hold on
    plot(data.([side,'HFTBA_x'])(first:last),'Color',zcol,'LineStyle',zstyle,'LineWidth',LineWidth)
    title([s,'HF/TB'],'FontSize',FontSize,'FontName',FontName)
    if square
        axis('square')
    end
    
    subplot(3,10,offset+4);
    plot(vicon_data.([s,'FFHFA'])(first:last,1),'Color',vcol,'LineStyle',vstyle,'LineWidth',LineWidth)
    hold on
    plot(data.([side,'FFHFA_x'])(first:last),'Color',zcol,'LineStyle',zstyle,'LineWidth',LineWidth)
    title([s,'FF/HF'],'FontSize',FontSize,'FontName',FontName)
    if square
        axis('square')
    end
    
    subplot(3,10,offset+5);
    plot(vicon_data.([s,'HXFFA'])(first:last,1),'Color',vcol,'LineStyle',vstyle,'LineWidth',LineWidth)
    hold on
    plot(data.([side,'HXFFA_x'])(first:last),'Color',zcol,'LineStyle',zstyle,'LineWidth',LineWidth)
    title([s,'HX/FF'],'FontSize',FontSize,'FontName',FontName)
    if square
        axis('square')
    end
    
    % coronal plane
    subplot(3,10,offset+11);
    plot(vicon_data.([s,'TIBA'])(first:last,2),'Color',vcol,'LineStyle',vstyle,'LineWidth',LineWidth)
    hold on
    plot(data.([side,'TIBA_y'])(first:last),'Color',zcol,'LineStyle',zstyle,'LineWidth',LineWidth)
    if square
        axis('square')
    end
    
    if i==1
        ylabel({'Coronal','Angles','(deg)'},'FontSize',FontSize,'FontName',FontName)
    end
    
    subplot(3,10,offset+12);
    plot(vicon_data.([s,'FFTBA'])(first:last,3),'Color',vcol,'LineStyle',vstyle,'LineWidth',LineWidth)
    hold on
    plot(data.([side,'FFTBA_y'])(first:last),'Color',zcol,'LineStyle',zstyle,'LineWidth',LineWidth)
    if square
        axis('square')
    end
    
    subplot(3,10,offset+13);
    plot(vicon_data.([s,'HFTBA'])(first:last,3),'Color',vcol,'LineStyle',vstyle,'LineWidth',LineWidth)
    hold on
    plot(data.([side,'HFTBA_y'])(first:last),'Color',zcol,'LineStyle',zstyle,'LineWidth',LineWidth)
    if square
        axis('square')
    end
    
    subplot(3,10,offset+14);
    plot(vicon_data.([s,'FFHFA'])(first:last,3),'Color',vcol,'LineStyle',vstyle,'LineWidth',LineWidth)
    hold on
    plot(data.([side,'FFHFA_z'])(first:last),'Color',zcol,'LineStyle',zstyle,'LineWidth',LineWidth)
    if square
        axis('square')
    end

    
    % transverse plane
   
    subplot(3,10,offset+21);
    plot(vicon_data.([s,'TIBA'])(first:last,3),'Color',vcol,'LineStyle',vstyle,'LineWidth',LineWidth)
    hold on
    plot(data.([side,'TIBA_z'])(first:last),'Color',zcol,'LineStyle',zstyle,'LineWidth',LineWidth)
    if square
        axis('square')
    end
 
    if i==1
        ylabel({'Transverse','Angles','(deg)'},'FontSize',FontSize,'FontName',FontName)
    end
    
    subplot(3,10,offset+22);
    plot(vicon_data.([s,'FFTBA'])(first:last,2),'Color',vcol,'LineStyle',vstyle,'LineWidth',LineWidth)
    hold on
    plot(data.([side,'FFTBA_z'])(first:last),'Color',zcol,'LineStyle',zstyle,'LineWidth',LineWidth)
    if square
        axis('square')
    end
    
    subplot(3,10,offset+23);
    plot(vicon_data.([s,'HFTBA'])(first:last,2),'Color',vcol,'LineStyle',vstyle,'LineWidth',LineWidth)
    hold on
    plot(data.([side,'HFTBA_z'])(first:last),'Color',zcol,'LineStyle',zstyle,'LineWidth',LineWidth)
    if square
        axis('square')
    end
    
    subplot(3,10,offset+24);
    plot(vicon_data.([s,'FFHFA'])(first:last,2),'Color',vcol,'LineStyle',vstyle,'LineWidth',LineWidth)
    hold on
    plot(data.([side,'FFHFA_y'])(first:last),'Color',zcol,'LineStyle',zstyle,'LineWidth',LineWidth)
    if square
        axis('square')
    end

    subplot(3,10,offset+25);
    plot(vicon_data.([s,'HXFFA'])(first:last,2),'Color',vcol,'LineStyle',vstyle,'LineWidth',LineWidth)
    hold on
    plot(data.([side,'HXFFA_y'])(first:last),'Color',zcol,'LineStyle',zstyle,'LineWidth',LineWidth)
    if square
        axis('square')
    end
end

if i == 2
    ax = subplot(3,10,offset+15);
    axPos = ax.Position;
    delete(ax)
    lg = legend('Vicon OFM','openOFM');
    lg.Position(1:2) = axPos(1:2);
end

fh.WindowState = 'maximized';