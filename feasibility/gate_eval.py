import numpy as np

LIMIT = 0.94
COVERAGE = 0.90


def calibrate_qhat(pred_cal, y_cal, coverage=COVERAGE):
    over = np.asarray(pred_cal, dtype=np.float64) - np.asarray(y_cal, dtype=np.float64)
    over_sorted = np.sort(over)
    n = len(over_sorted)
    k = int(np.ceil((n + 1) * coverage))
    k = min(k, n)
    return float(over_sorted[k - 1])


def run_gate(pred_test, q_hat, limit=LIMIT):
    pred = np.asarray(pred_test, dtype=np.float64)
    lower = pred - q_hat
    certify = lower >= limit
    flag = pred < limit
    escalate = ~(certify | flag)
    return dict(pred=pred, lower=lower, certify=certify, flag=flag, escalate=escalate)


def score(gate_out, y_test, ms_surrogate, ms_solver, limit=LIMIT):
    y = np.asarray(y_test, dtype=np.float64)
    certify = gate_out["certify"]
    escalate = gate_out["escalate"]
    lower = gate_out["lower"]

    n = len(y)
    n_esc = int(escalate.sum())
    true_viol = y < limit
    missed = certify & true_viol

    escalation = float(escalate.mean())
    coverage = float((y >= lower).mean())
    missed_viol = float(missed.sum() / max(int(true_viol.sum()), 1))
    net_speedup = float(n * ms_solver / (n * ms_surrogate + n_esc * ms_solver))
    return dict(escalation=escalation, coverage=coverage, missed_viol=missed_viol,
                net_speedup=net_speedup, n=n, n_escalated=n_esc,
                n_true_viol=int(true_viol.sum()))
