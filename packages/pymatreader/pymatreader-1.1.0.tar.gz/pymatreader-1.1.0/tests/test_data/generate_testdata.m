% -*- coding: UTF-8 -*-
% Copyright (c) 2018, Dirk Gütlin & Thomas Hartmann
% All rights reserved.
%
% This file is part of the pymatreader Project, see: https://gitlab.com/obob/pymatreader
%
% Redistribution and use in source and binary forms, with or without
% modification, are permitted provided that the following conditions are met:
%
% * Redistributions of source code must retain the above copyright notice, this
%   list of conditions and the following disclaimer.
%
% * Redistributions in binary form must reproduce the above copyright notice,
%   this list of conditions and the following disclaimer in the documentation
%   and/or other materials provided with the distribution.
%
% THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
% AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
% IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
% DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
% FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
% DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
% SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
% CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
% OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
% OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

% This script generates the necessary test files for the unittests

restoredefaultpath

addpath('xml_io_tools');

clear all global

a_string = random_string(10);
a_second_string = random_string(20);

an_integer = randi(255, 1);
a_second_integer = randi(255, 1);

a_float = rand(1);
a_second_float = rand(1);

a_matrix = rand(100, 100);

a_complex_matrix = rand(10, 10) + i*rand(10, 10);

a_single_char = 'b';

an_empty_string = '';

a_unit64 = uint64(6273309986953);

a_complex_number = 2 + 3i;

a_cell_array = {};
for idx_cells = 1:100
  a_cell_array{idx_cells} = rand(2, 5);
end %for
clear idx_cells
a_second_cell_array = {};
for idx_cells = 1:100
  a_second_cell_array{idx_cells} = rand(2, 5);
end %for
clear idx_cells

a_heading_cell_array = cell(1,1);
a_heading_cell_array{1} = a_cell_array;
a_heading_cell_array{2} = a_second_cell_array;

a_struct = {};
a_struct.string = random_string(20);
a_struct.int = randi(255, 1);
a_struct.float = rand(1);
a_struct.matrix = rand(100, 100);
a_struct.a_cell_array = {};
for idx_cells = 1:100
  a_struct.a_cell_array{idx_cells} = rand(2, 5);
end %for
clear idx_cells
a_struct.a_cell_struct_array = {};
for idx_cells = 1:5
  a_struct.a_cell_struct_array{idx_cells}.int = randi(255, 1);
  a_struct.a_cell_struct_array{idx_cells}.float = rand(1);
  a_struct.a_cell_struct_array{idx_cells}.matrix = rand(100, 100);
  a_struct.a_cell_struct_array{idx_cells}.string = random_string(20);
end %for
clear idx_cells

a_struct.second_level.string = random_string(20);
a_struct.second_level.int = randi(255, 1);
a_struct.second_level.float = rand(1);
a_struct.second_level.matrix = rand(100, 100);
a_struct.second_level.a_cell_array = {};
for idx_cells = 1:100
  a_struct.second_level.a_cell_array{idx_cells} = rand(2, 5);
end %for
clear idx_cells

save('v6.mat', '-v6')
save('v7.mat', '-v7')
save('v73.mat', '-v7.3')
save('v4.mat', '-v4');

test_data.for_xml = load('v73.mat');
xml_write('xmldata.xml', test_data);

%% generate testdata for struct arrays vs. cell arrays...
clear all global

for idx = 1:5
  a_struct_array(idx).string = random_string(20);
  a_struct_array(idx).int = randi(255, 1);
  a_struct_array(idx).float = rand(1);
  a_struct_array(idx).matrix = rand(100, 100);
  
  a_cell_array{idx}.string = random_string(20);
  a_cell_array{idx}.int = randi(255, 1);
  a_cell_array{idx}.float = rand(1);
  a_cell_array{idx}.matrix = rand(100, 100);
end %for

clear idx

save('cell_struct_v6.mat', '-v6')
save('cell_struct_v7.mat', '-v7')
save('cell_struct_v73.mat', '-v7.3')

%% generate real string data...
clear all global
my_string = "hello world";
my_char = 'hello char';

save('string_v6.mat', '-v6');
save('string_v7.mat', '-v7');
save('string_v73.mat', '-v7.3');

%% Generatre Sparse Matrices...
clear all global

% Cases:
% * empty sparse matrix
% * sparse matrix with one element
% * column vector
% * row vector
% * 2D matrix
%   * M < N
%   * M == N
%   * M > N
% * full matrix
N = 10;

% empty sparse matrices of various sizes
A_empty        = sparse([], [], [], 0, 0);  % empty sparse matrix
A_empty_col    = sparse(N, 1);              % column vector
A_empty_row    = sparse(1, N);              % row vector
A_empty_square = sparse(N, N);              % M == N
A_empty_wide   = sparse(N, 2*N);            % M < N
A_empty_tall   = sparse(2*N, N);            % M > N

% Filled matrices
A_single = sparse([1]);                % sparse matrix with one element

% Create random values
Nel = N / 2;
rng(5656);  % seed the rng for reproducibility

i = randperm(N, Nel);  % row indices
j = randperm(N, Nel);  % column indices
v = rand(Nel, 1);      % values

A_col    = sparse(i, 1, v, N, 1);      % column vector
A_row    = sparse(1, j, v, 1, N);      % row vector
A_square = sparse(i, j, v, N, N);      % M == N
A_wide   = sparse(i, 2*j, v, N, 2*N);  % M < N
A_tall   = sparse(2*i, j, v, 2*N, N);  % M > N

% Write matrices to CSV files, since we need to load all values into scipy from
% a trusted filetype for the tests.
writematrix(full(A_empty), 'sparse_empty.csv');
writematrix(full(A_empty_col), 'sparse_empty_col.csv');
writematrix(full(A_empty_row), 'sparse_empty_row.csv');
writematrix(full(A_empty_square), 'sparse_empty_square.csv');
writematrix(full(A_empty_wide), 'sparse_empty_wide.csv');
writematrix(full(A_empty_tall), 'sparse_empty_tall.csv');

writematrix(full(A_single), 'sparse_single.csv');
writematrix(full(A_col), 'sparse_col.csv');
writematrix(full(A_row), 'sparse_row.csv');
writematrix(full(A_square), 'sparse_square.csv');
writematrix(full(A_wide), 'sparse_wide.csv');
writematrix(full(A_tall), 'sparse_tall.csv');

% Save the mat files in different versions
save('sparse_v4.mat',  '-v4');
save('sparse_v6.mat',  '-v6');
save('sparse_v7.mat',  '-v7');
save('sparse_v73.mat', '-v7.3');
