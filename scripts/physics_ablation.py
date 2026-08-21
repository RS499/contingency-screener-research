"""PART C: ablate the physics feature families on case118.

Same seeds, same splits, same protocol as the committed run. For every configuration the M2
hyperparameter search is RE-RUN, because the optimal hyperparameters may differ once the
feature set changes. Results are also reported with the committed M2 tags HELD FIXED, so the
reader can separate "the features helped" from "the search found a different model".

Configurations: baseline | +F1 | +F1+F2 | +F1+F3 | +F1+F2+F3+F4

Written per configuration, so a crash costs one configuration rather than the run.
"""
import json, os, sys, time, gc
import numpy as np, pandas as pd

HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(HERE,"..","feasibility")); sys.path.insert(0,HERE)
import make_splits as ms, gate_eval as ge, manifest as mf, tune_surrogates as T
import netstudy as V1

DATASET="data/dataset.parquet"
PHYS="data/physics"
OUT="data/physics_ablation.json"
SEEDS=5; LIMIT=0.94; STRIP_HI=0.945
COVERAGE_LEVELS=[round(0.90+0.01*i,2) for i in range(9)]
OP_TARGET={"ridge":0.94,"histgb":0.97}
CONFIGS=[("baseline",[]),("+F1",["F1"]),("+F1+F2",["F1","F2"]),
         ("+F1+F3",["F1","F3"]),("+F1+F2+F3+F4",["F1","F2","F3","F4"])]


def load_base():
    df,feature_cols=ms.load_dataset(DATASET)
    X,y,groups,_b=ms.build_design_matrix(df,feature_cols)
    key=df[["scenario_id","outaged_type","outaged_idx"]].reset_index(drop=True)
    return df,X,y,groups,key


def feature_block(name,key):
    if name=="F1":
        fl=pd.read_parquet(os.path.join(PHYS,"base_flows.parquet"))
        m=key.merge(fl,on=["scenario_id","outaged_type","outaged_idx"],how="left")
        cols=["pre_p_mw","pre_q_mvar","pre_loading_percent","pre_i_ka"]
        return m[cols].astype(np.float32)
    if name=="F2":
        fl=pd.read_parquet(os.path.join(PHYS,"base_flows.parquet"))
        fl["bkey"]=fl.outaged_type.astype(str)+"_"+fl.outaged_idx.astype(str)
        piv=fl.pivot(index="scenario_id",columns="bkey",values="pre_loading_percent")
        piv.columns=[f"f2_load_{c}" for c in piv.columns]
        m=key[["scenario_id"]].merge(piv.reset_index(),on="scenario_id",how="left")
        return m.drop(columns=["scenario_id"]).astype(np.float32)
    if name=="F3":
        lo=pd.read_parquet(os.path.join(PHYS,"lodf.parquet"))
        m=key.merge(lo,on=["outaged_type","outaged_idx"],how="left")
        return m.drop(columns=["scenario_id","outaged_type","outaged_idx"]).astype(np.float32)
    if name=="F4":
        ed=pd.read_parquet(os.path.join(PHYS,"edistance.parquet"))
        m=key.merge(ed,on=["outaged_type","outaged_idx"],how="left")
        return m.drop(columns=["scenario_id","outaged_type","outaged_idx"]).astype(np.float32)
    raise ValueError(name)


def metrics_for(fitted,Xte,yte,pred_cal,yca,ms_solver):
    pte=T.predict(fitted,Xte)
    mae=float(np.abs(pte-yte).mean())
    ss=float(((yte-yte.mean())**2).sum()); r2=float(1.0-((yte-pte)**2).sum()/ss)
    out=dict(mae=mae,r2=r2)
    per={}
    for cov in COVERAGE_LEVELS:
        q=ge.calibrate_qhat(pred_cal,yca,cov)
        g=ge.run_gate(pte,q,LIMIT); s=ge.score(g,yte,1e-6,ms_solver,LIMIT)
        per[str(cov)]=dict(q_hat=q,escalation=s["escalation"],coverage_emp=s["coverage"],
                           missed_viol=s["missed_viol"],net_speedup=s["net_speedup"])
    out["by_target"]=per
    out["q_hat_90"]=per["0.9"]["q_hat"]
    return out


def run_config(label,fams,base,committed_tags,ms_solver):
    df,X,y,groups,key=base
    t0=time.time()
    parts=[X]+[feature_block(f,key) for f in fams]
    Xc=pd.concat(parts,axis=1) if len(parts)>1 else X
    print(f"[{label}] design matrix {Xc.shape[0]} x {Xc.shape[1]} "
          f"(added {Xc.shape[1]-X.shape[1]})",flush=True)
    r_c,h_c=T.ridge_candidates(),T.histgb_candidates()
    recs=[]
    for seed in range(SEEDS):
        sp=ms.make_splits(groups,seed)
        kept=ms.select_features(Xc,sp["train"]); Xk=Xc[kept]
        tr,cal,te=sp["train"],sp["cal"],sp["test"]
        g_tr=groups[tr]; inner=ms.make_splits(g_tr,T.INNER_SEED_OFFSET+seed)
        i_fit,i_cal,i_score=tr[inner["train"]],tr[inner["cal"]],tr[inner["test"]]
        Xfit=Xk.iloc[i_fit].to_numpy(np.float32); yfit=y[i_fit]
        Xic=Xk.iloc[i_cal].to_numpy(np.float32); yic=y[i_cal]
        Xis=Xk.iloc[i_score].to_numpy(np.float32); yis=y[i_score]
        Xtr=Xk.iloc[tr].to_numpy(np.float32); ytr=y[tr]
        Xca=Xk.iloc[cal].to_numpy(np.float32); yca=y[cal]
        Xte=Xk.iloc[te].to_numpy(np.float32); yte=y[te]
        for fam,cands in (("ridge",r_c),("histgb",h_c)):
            rows=T.search_one_family(fam,cands,Xfit,yfit,Xic,yic,Xis,yis,seed,ms_solver)
            _m1,m2=T.select_best(rows)
            for mode,tag in (("m2_searched",m2),("m2_fixed",committed_tags[str(seed)][fam]["m2"])):
                cfg=T.find_config(cands,tag)
                if cfg is None:
                    recs.append(dict(config=label,family=fam,seed=seed,mode=mode,tag=tag,
                                     status="TAG NOT IN CANDIDATE SET")); continue
                fitted=T.fit_one(fam,cfg,Xtr,ytr,seed)
                pc=T.predict(fitted,Xca)
                m=metrics_for(fitted,Xte,yte,pc,yca,ms_solver)
                recs.append(dict(config=label,family=fam,seed=seed,mode=mode,tag=tag,
                                 n_features=int(Xk.shape[1]),status="OK",**m))
                del fitted
            gc.collect()
        print(f"  [{label}] seed {seed} done [{time.time()-t0:.0f}s]",flush=True)
        del Xfit,Xic,Xis,Xtr,Xca,Xte,Xk; gc.collect()
    del Xc,parts; gc.collect()
    return recs,round(time.time()-t0,1)


def main():
    ms_solver=mf.load_solve_time()["ms_solver"]
    committed=json.load(open("data/tuned_metrics.json"))["selections"]
    base=load_base()
    all_recs=[]; timing={}
    for label,fams in CONFIGS:
        recs,el=run_config(label,fams,base,committed,ms_solver)
        all_recs+=recs; timing[label]=el
        doc=dict(part="C ablation",dataset=DATASET,seeds=SEEDS,limit=LIMIT,
                 coverage_levels=COVERAGE_LEVELS,operating_targets=OP_TARGET,
                 configs=[c[0] for c in CONFIGS],configs_done=list(timing),
                 comparison_uses=("m2_searched. m2_fixed is reported beside it so the reader "
                                  "can separate a feature effect from a search effect."),
                 ms_solver=ms_solver,elapsed_s=timing,records=all_recs)
        V1.write_json(OUT,doc,dict(seed=None,input_file=DATASET,
                                   input_sha256=V1.sha256_of(DATASET),
                                   run_settings=dict(part="C")))
        print(f"=== {label} complete in {el}s; artifact updated",flush=True)
    print("PART C DONE",flush=True)


if __name__=="__main__":
    main()
