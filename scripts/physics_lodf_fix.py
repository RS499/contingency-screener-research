"""Rebuild F3 correctly: fix the orientation, zero-fill non-finite, add a validity indicator.

Two defects in the PART B build are corrected here and reported, not overwritten silently:

D1 ORIENTATION. pypower makeLODF returns LODF[l, k] = H[l,k] / (1 - h[k]); the COLUMN index is
   the OUTAGED branch and the row is the MONITORED branch (see den = 1 - h.T, constant down
   each column). PART B extracted lodf[b, :], i.e. the row, which is the effect ON branch b of
   outaging everything else - the transpose of the intended "LODF row for the outaged branch".
   Corrected to lodf[:, b].

D2 NON-FINITE COUNT. PART B counted only NaN (663). The true count is 1302: 663 NaN plus 639
   +/-inf. Where the denominator is zero, H/0 gives inf when H != 0 and nan when H == 0. Both
   are undefined and both must be filled.
"""
import json, os, sys, time
import numpy as np, pandas as pd, networkx as nx
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(HERE,"..","feasibility")); sys.path.insert(0,HERE)
import generate_dataset as G, netstudy as V1
import pandapower as pp
from pandapower.pypower.makePTDF import makePTDF
from pandapower.pypower.makeLODF import makeLODF
from pandapower.pd2ppc import _pd2ppc

OUT="data/physics/lodf.parquet"

def main():
    net=G.build_net("case118"); pp.runpp(net,enforce_q_lims=True,init="dc",numba=True)
    ppc,_=_pd2ppc(net)
    slack=int(np.where(ppc["bus"][:,1]==3)[0][0])
    PT=makePTDF(ppc["baseMVA"],ppc["bus"],ppc["branch"],slack)
    L=makeLODF(ppc["branch"],PT)
    # h[k] = self-sensitivity; den = 1 - h[k] is zero exactly when the outage islands
    from pandapower.pypower.idx_brch import F_BUS,T_BUS
    from scipy.sparse import csr_matrix as sparse
    nl,nb=PT.shape
    f=np.real(ppc["branch"][:,F_BUS]).astype(int); t=np.real(ppc["branch"][:,T_BUS]).astype(int)
    Cft=sparse((np.r_[np.ones(nl),-np.ones(nl)],(np.r_[f,t],np.r_[np.arange(nl),np.arange(nl)])),(nb,nl))
    h=np.diag(np.asarray(PT*Cft))
    den=1.0-h
    branches=G.branch_list(net); lk=net["_pd2ppc_lookups"]["branch"]
    ppc_of=[int(lk[et][0])+int(ix) for et,ix in branches]

    M=np.array([L[:,k] for k in ppc_of])          # D1 FIX: column, not row
    nonfinite=~np.isfinite(M)
    # D3 TOLERANCE. Testing only for non-finite is too strict. Branches 121 and 185 have
    # den = 1.11e-16, i.e. h[k] = 1 to machine precision, which IS the islanding signature;
    # their entries are 0/0 that resolved to finite, plausible-looking values (max 1.75 and
    # 1.00). Plausible-looking noise is more dangerous than inf, because it survives a
    # finiteness check. Undefined is therefore |1 - h[k]| < DEN_TOL, not "non-finite".
    DEN_TOL=1e-9
    den_row=np.array([den[k] for k in ppc_of])
    undefined=(np.abs(den_row)<DEN_TOL)|nonfinite.any(axis=1)
    valid=(~undefined).astype(int)
    Mf=np.where(undefined[:,None],0.0,np.where(nonfinite,0.0,M))

    # simple-graph bridges, for the 9-vs-7 reconciliation
    g=nx.Graph()
    for i in net.line.index:
        if net.line.at[i,"in_service"]: g.add_edge(int(net.line.at[i,"from_bus"]),int(net.line.at[i,"to_bus"]))
    for i in net.trafo.index:
        if net.trafo.at[i,"in_service"]: g.add_edge(int(net.trafo.at[i,"hv_bus"]),int(net.trafo.at[i,"lv_bus"]))
    bset=set(tuple(sorted(b)) for b in nx.bridges(g))
    bridge_rows=[]
    for r,(et,ix) in enumerate(branches):
        a,b=(int(net.line.at[ix,"from_bus"]),int(net.line.at[ix,"to_bus"])) if et=="line" \
            else (int(net.trafo.at[ix,"hv_bus"]),int(net.trafo.at[ix,"lv_bus"]))
        if tuple(sorted((a,b))) in bset: bridge_rows.append(r)
    undef_rows=np.where(valid==0)[0].tolist()

    df=pd.DataFrame(Mf,columns=[f"lodf_{j}" for j in range(M.shape[1])])
    df.insert(0,"lodf_valid",valid)
    df.insert(0,"outaged_idx",[int(i) for _t,i in branches])
    df.insert(0,"outaged_type",[t for t,_i in branches])
    df.to_parquet(OUT,index=False)

    rep=dict(
        artifact=OUT, orientation_fix=dict(
            defect="PART B used lodf[b, :] (monitored-branch row); correct is lodf[:, b]",
            pypower_convention="LODF[l, k] = H[l,k] / (1 - h[k]); k = OUTAGED, l = MONITORED",
            evidence="makeLODF builds den = ones*h.T*-1 + 1, constant DOWN each column"),
        nonfinite=dict(n_nan=int(np.isnan(M).sum()), n_posinf=int(np.isposinf(M).sum()),
                       n_neginf=int(np.isneginf(M).sum()), n_total=int(nonfinite.sum()),
                       n_cells=int(M.size),
                       partB_undercount="PART B reported 663 (NaN only); +/-inf was missed",
                       rows_fully_nonfinite=int((nonfinite.all(axis=1)).sum())),
        fill_policy=dict(rule="row zero-filled when |1 - h[k]| < 1e-9 OR any cell non-finite",
                         den_tolerance=1e-9, indicator_column="lodf_valid",
                         indicator_semantics="1 = LODF row defined; 0 = outage islands the "
                                             "network and every entry was filled",
                         n_valid=int(valid.sum()), n_invalid=int((valid==0).sum())),
        undefined_branches=dict(
            rows=undef_rows,
            keys=[[branches[r][0],int(branches[r][1])] for r in undef_rows],
            den_1_minus_h=[float(den[ppc_of[r]]) for r in undef_rows]),
        reconciliation_9_vs_7=dict(
            instruction_said="zero-fill the 9 bridge columns",
            simple_graph_bridges=bridge_rows, n_simple_graph_bridges=len(bridge_rows),
            dc_undefined_rows=undef_rows, n_dc_undefined=len(undef_rows),
            in_bridges_not_undefined=sorted(set(bridge_rows)-set(undef_rows)),
            den_for_those=[float(den[ppc_of[r]]) for r in sorted(set(bridge_rows)-set(undef_rows))],
            verdict=("the count is 9 and the instruction was right. An earlier pass of this "
                     "script tested only for non-finite cells, found 7, and wrongly concluded "
                     "the other 2 held real values. They do not: den = 1.11e-16 for both, "
                     "i.e. h[k] = 1 to machine precision, the islanding signature. Their "
                     "entries are 0/0 that resolved to finite, plausible-looking numbers "
                     "(max |LODF| 1.75 and 1.00) which are numerically arbitrary. All 9 are "
                     "now zero-filled and flagged."),
            corrected_from="an earlier verdict in this same file that said 7, not 9"))
    print(json.dumps(rep,indent=1))
    return rep

if __name__=="__main__":
    rep=main()
    p="data/physics_features.json"
    d=json.load(open(p)); d["F3"]["CORRECTED"]=rep
    d["F3"]["n_cols"]=186; d["F3"]["extra_cols"]=["lodf_valid"]
    V1.write_json(p,d,dict(seed=None,input_file="data/dataset.parquet",
                           input_sha256=V1.sha256_of("data/dataset.parquet"),
                           run_settings=dict(part="B-corrected",network="case118")))
    print("\nupdated data/physics_features.json")
