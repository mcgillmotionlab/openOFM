function foot_angles_comp_nrmse (data, data_val)

%nrsme HFTBA x axis
RightHFTBA_x = data.RightHFTBA_x.line;
RHFTBA = data_val.RHFTBA.line(:, 1);
NRMSE_RHFTBAX = nrmse(RHFTBA, RightHFTBA_x);

%nrsme HFTBA y axis
RightHFTBA_y = data.RightHFTBA_y.line;
RHFTBA = data_val.RHFTBA.line(:, 2);
NRMSE_RHFTBAY = nrmse(RHFTBA, RightHFTBA_y);

%nrsme HFTBA z axis
RightHFTBA_z = data.RightHFTBA_z.line;
RHFTBA = data_val.RHFTBA.line(:, 3);
NRMSE_RHFTBAZ = nrmse(RHFTBA, RightHFTBA_z);

%nrsme FFHFA x axis
RightFFHFA_x = data.RightFFHFA_x.line;
RFFHFA = data_val.RFFHFA.line(:, 1);
NRMSE_RFFHFAX = nrmse(RFFHFA, RightFFHFA_x);

%nrsme FFHFA y axis
RightFFHFA_y = data.RightFFHFA_y.line;
RFFHFA = data_val.RFFHFA.line(:, 2);
NRMSE_RFFHFAY = nrmse(RFFHFA, RightFFHFA_y);

%nrsme FFHFA z axis
RightFFHFA_z = data.RightFFHFA_z.line;
RFFHFA = data_val.RFFHFA.line(:, 3);
NRMSE_RFFHFAZ = nrmse(RFFHFA, RightFFHFA_z);

%nrsme HXFFA x axis
RightHXFFA_x = data.RightHXFFA_x.line;
RHXFFA = data_val.RHXFFA.line(:, 1);
NRMSE_RHXFFAX = nrmse(RHXFFA, RightHXFFA_x);

%nrsme FFHFA y axis
RightHXFFA_y = data.RightHXFFA_y.line;
RHXFFA = data_val.RHXFFA.line(:, 2);
NRMSE_RHXFFAY = nrmse (RHXFFA,RightHXFFA_y);

%add values on the figure
annotation('textbox', [0.15, 0.645, 0.1, 0.1], 'String', ['NRMSE = ', num2str(NRMSE_RHFTBAX)], 'linestyle', 'none')
annotation('textbox', [0.42, 0.645, 0.1, 0.1], 'String', ['NRMSE = ', num2str(NRMSE_RHFTBAY)], 'linestyle', 'none')
annotation('textbox', [0.71, 0.645, 0.1, 0.1], 'String', ['NRMSE = ', num2str(NRMSE_RHFTBAZ)], 'linestyle', 'none')
annotation('textbox', [0.15, 0.345, 0.1, 0.1], 'String', ['NRMSE = ', num2str(NRMSE_RFFHFAX)], 'linestyle', 'none')
annotation('textbox', [0.42, 0.345, 0.1, 0.1], 'String', ['NRMSE = ', num2str(NRMSE_RFFHFAY)], 'linestyle', 'none')
annotation('textbox', [0.71, 0.345, 0.1, 0.1], 'String', ['NRMSE = ', num2str(NRMSE_RFFHFAZ)], 'linestyle', 'none')
annotation('textbox', [0.15, 0.045, 0.1, 0.1], 'String', ['NRMSE = ', num2str(NRMSE_RHXFFAX)], 'linestyle', 'none')
annotation('textbox', [0.42, 0.045, 0.1, 0.1], 'String', ['NRMSE = ', num2str(NRMSE_RHXFFAY)], 'linestyle', 'none')



