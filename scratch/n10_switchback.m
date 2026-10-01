1;
% N10 Part A: the three MATPOWER solves for every exported case.
% Usage: octave --no-gui --quiet scratch/n10_switchback.m <case_dir>
% Reads <case_dir>/index.csv (row_id,file), writes <case_dir>/matpower_results.csv.
%   M0: runpf, no Q limits.
%   M1: runpf with pf.enforce_q_lims = 1 (MATPOWER's one-way PV->PQ conversion).
%   M2: M1 inside a switch-back outer loop (the N2 rule): a limited generator whose voltage contradicts its
%       limit (at Qmax with V > Vset, or at Qmin with V < Vset) returns to PV; consistent limited generators
%       are held as PQ at their limit (status off, injection moved into the bus load, as MATPOWER itself does).
%       Tolerances as N2 (1e-3 MVAr, 1e-3 pu); cap 30 outer iterations.
% Alignment with pandapower: the slack (ext_grid) generator has no Q limits in pandapower's enforce_q_lims,
% so its QMAX/QMIN are set to +/-Inf for M1 and M2.
% Min voltage = min VM over buses that are not isolated (BUS_TYPE ~= 4).

addpath(genpath('~/matpower'));
define_constants;

TOLQ = 1e-3;
TOLV = 1e-3;
MAX_OUTER = 30;

function v = min_vm(r)
  define_constants;
  ok = r.bus(:, BUS_TYPE) ~= 4;
  v = min(r.bus(ok, VM));
end

function mpc = unlimit_ref(mpc)
  define_constants;
  refbus = mpc.bus(mpc.bus(:, BUS_TYPE) == 3, BUS_I);
  gi = find(ismember(mpc.gen(:, GEN_BUS), refbus));
  mpc.gen(gi, QMAX) = Inf;
  mpc.gen(gi, QMIN) = -Inf;
end

function [status, vmin, nout, hist] = m2_solve(base, mo, tolq, tolv, maxo)
  define_constants;
  ng = size(base.gen, 1);
  fixed = zeros(ng, 1);
  refbus = base.bus(base.bus(:, BUS_TYPE) == 3, BUS_I);
  isref = ismember(base.gen(:, GEN_BUS), refbus);
  on = base.gen(:, GEN_STATUS) > 0;
  [~, gb] = ismember(base.gen(:, GEN_BUS), base.bus(:, BUS_I));
  vset = base.gen(:, VG);
  qmax = base.gen(:, QMAX);
  qmin = base.gen(:, QMIN);
  hist = [];
  status = 'iteration_cap';
  vmin = NaN;
  nout = maxo;
  for it = 1:maxo
    m = base;
    idx = find(fixed ~= 0);
    for k = 1:numel(idx)
      j = idx(k);
      if fixed(j) == 1
        q = qmax(j);
      else
        q = qmin(j);
      end
      m.bus(gb(j), PD) = m.bus(gb(j), PD) - m.gen(j, PG);
      m.bus(gb(j), QD) = m.bus(gb(j), QD) - q;
      m.gen(j, GEN_STATUS) = 0;
    end
    for k = 1:numel(idx)
      b = gb(idx(k));
      still_on = any(m.gen(:, GEN_BUS) == m.bus(b, BUS_I) & m.gen(:, GEN_STATUS) > 0);
      if m.bus(b, BUS_TYPE) == 2 && ~still_on
        m.bus(b, BUS_TYPE) = 1;
      end
    end
    r = runpf(m, mpoption(mo, 'pf.enforce_q_lims', 1));
    if ~r.success
      status = 'nonconverged';
      nout = it;
      return;
    end
    q = r.gen(:, QG);
    q(fixed == 1) = qmax(fixed == 1);
    q(fixed == -1) = qmin(fixed == -1);
    v = r.bus(gb, VM);
    atmax = on & ~isref & (q >= qmax - tolq);
    atmin = on & ~isref & (q <= qmin + tolq);
    badinj = atmax & (v > vset + tolv);
    badabs = atmin & (v < vset - tolv);
    bad = badinj | badabs;
    hist(end + 1) = sum(bad);
    vmin = min_vm(r);
    if sum(bad) == 0
      status = 'converged';
      nout = it;
      return;
    end
    newfixed = zeros(ng, 1);
    newfixed(atmin & ~bad) = -1;
    newfixed(atmax & ~bad & ~atmin) = 1;
    fixed = newfixed;
  end
end

args = argv();
casedir = args{1};
idx = csvread(fullfile(casedir, 'index.csv'), 1, 0);
mo = mpoption('verbose', 0, 'out.all', 0, 'pf.alg', 'NR', 'pf.tol', 1e-8, 'pf.nr.max_it', 30);
fid = fopen(fullfile(casedir, 'matpower_results.csv'), 'w');
fprintf(fid, 'row_id,m0_success,m0_min_vm,m1_success,m1_min_vm,m2_status,m2_min_vm,m2_n_outer,m2_history\n');
for i = 1:size(idx, 1)
  rid = idx(i, 1);
  s = load(fullfile(casedir, sprintf('row_%03d.mat', rid)));
  mpc = s.mpc;
  r0 = runpf(mpc, mpoption(mo, 'pf.enforce_q_lims', 0));
  v0 = NaN;
  if r0.success
    v0 = min_vm(r0);
  end
  m1 = unlimit_ref(mpc);
  r1 = runpf(m1, mpoption(mo, 'pf.enforce_q_lims', 1));
  v1 = NaN;
  if r1.success
    v1 = min_vm(r1);
  end
  [st, v2, no, hi] = m2_solve(m1, mo, TOLQ, TOLV, MAX_OUTER);
  hs = sprintf('%d;', hi);
  fprintf(fid, '%d,%d,%.15f,%d,%.15f,%s,%.15f,%d,%s\n', rid, r0.success, v0, r1.success, v1, st, v2, no, hs);
end
fclose(fid);
printf('done %d rows\n', size(idx, 1));
