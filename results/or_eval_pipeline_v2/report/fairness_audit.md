# OR-Eval Fairness Audit

- Overall status: pass

| check | status | value | detail |
| --- | --- | --- | --- |
| full_eval_rows | pass | 19928 | Full evaluation rows are available. |
| ablation_rows | pass | 12000 | Ablation rows are available for prompt-bias analysis. |
| prompt_hash_coverage | pass | 1.000 | Rows include prompt hashes for resume fairness. |
| config_hash_coverage | pass | 1.000 | Rows include config hashes for resume fairness. |
| solver_env_hash_coverage | pass | 1.000 | Rows include solver environment hashes. |
| schema_version_coverage | pass | 1.000 | Rows use current schema version or-eval-result-v2. |
| failed_prediction_suppression | pass | 0 | Non-executable rows must not contribute predicted values. |
| solver_environment_reported | pass | {"available_solvers": 5, "total_solvers": 15} | Solver availability matrix is reported. |
| failure_taxonomy_reported | pass | ["api_error", "correct", "exec_no_solve", "infeasible_unbounded_misclassification", "missing_module", "name_error", "no_code", "runtime_error", "syntax_error", "timeout", "wrong_numeric"] | Case-level failure taxonomy is available. |
| objective_evaluable_metric | pass | 0.689 | Objective-evaluable rate is tracked separately from solve rate. |
| variable_solution_evidence | pass | 0.648 | Variable values are tracked; legacy runs may have zero coverage until rerun with the updated prompt. |
| solver_specific_bias_detected | pass | {"solver_specific_coptpy": 1.0, "solver_specific_gurobipy": 0.9966666666666667, "solver_specific_pyscipopt": 0.9866666666666667} | Solver-specific prompts should expose forced solver concentration (≥60% of rows with max_share≥0.90). 25/30 pass. |
| neutral_prompt_bias_measured | pass | {"deepseek-v3": {"max_solver_share": 0.5633333333333334, "unavailable_solver_rate": 0.05}, "deepseek-v3.2": {"max_solver_share": 0.43, "unavailable_solver_rate": 0.02666666666666667}, "gemini-2.5-pro": {"max_solver_share": 0.43333333333333335, "unavailable_solver_rate": 0.07}, "gpt-4.1": {"max_solver_share": 0.6066666666666667, "unavailable_solver_rate": 0.21333333333333335}, "gpt-4.1-mini": {"max_solver_share": 0.8666666666666667, "unavailable_solver_rate": 0.11333333333333333}, "gpt-4o": {"max_solver_share": 0.7766666666666666, "unavailable_solver_rate": 0.11666666666666667}, "gpt-4o-mini": {"max_solver_share": 0.44, "unavailable_solver_rate": 0.2}, "o4-mini": {"max_solver_share": 0.8133333333333334, "unavailable_solver_rate": 0.03}, "qwen-max": {"max_solver_share": 0.57, "unavailable_solver_rate": 0.58}, "qwen3-235b-a22b": {"max_solver_share": 0.63, "unavailable_solver_rate": 0.15666666666666668}} | Neutral prompt concentration and unavailable-solver exposure are measured. |