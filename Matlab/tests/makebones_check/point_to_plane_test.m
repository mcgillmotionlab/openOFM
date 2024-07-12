% create a vector from a point on the plane that points to p1
p1=[1 1 1];
p2= [2 2 3];
p3= [2 3 2];
p4= [4 4 4];

w = p1 - p2;

% create vector normal to the plane
x = cross(p2-p4,p3-p4);

% make each row of n a unit vector and calculate t
t = zeros(size(x));
for i = 1:size(x,1)
    x(i,:) = x(i,:)/magnitude(x(i,:));
    t(i,:) = dot(w(i,:),x(i,:))*x(i,:);
end

% subtract t from w and add back p2 to get coordinates of projected point
proj_p1 = (w-t) + p2

% autre voir si même réponse
n = cross(p2-p4,p3-p4);
n = makeunit(n);
q_proj = p1 - dot(p1 - p2, n) * n

function r = makeunit(unt)

%   MAKEUNIT  makes all vectors unit vectors
%   unt ... N by 3 matrix of vectors.
%           rows are the number of vectors
%           columns are XYZ
%
% Created by JJ Loh ??
%
% updated November 2011 by Phil Dixon 
% - can normalize nx2 vectors

[~,c] = size(unt);


if c==3
    r = [];
    if iscell(unt)
        for i = 1:length(unt)
            plate = unt{i};
            mg = diag(sqrt(plate*plate'));
            plate = plate./[mg,mg,mg];
            r{i} = plate;
        end
    else
        mg = diag(sqrt(unt*unt'));
        plate = unt./[mg,mg,mg];
        r = plate;
    end
    
elseif c==2
    
    r = [];
    if iscell(unt)
        for i = 1:length(unt)
            plate = unt{i};
            mg = diag(sqrt(plate*plate'));
            plate = plate./[mg,mg];
            r{i} = plate;
        end
    else
        mg = diag(sqrt(unt*unt'));
        plate = unt./[mg,mg];
        r = plate;
    end
    
else
    
    if iscell(unt)
        for i = 1:length(unt)
            plate = unt{i};
            mg = diag(sqrt(plate*plate'));
            plate = plate./[mg,mg,mg];
            r{i} = plate;
        end
    else
        mg = diag(sqrt(unt*unt'));
        plate = unt./[mg,mg,mg];
        r = plate;
    end
    
    
    
    
    
    
end
end

