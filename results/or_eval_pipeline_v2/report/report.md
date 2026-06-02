# OR-Eval Report

- Problems evaluated: 10606
- Accuracy @5%: 0.573
- Accuracy @1%: 0.550
- Accuracy @1e-4: 0.514
- Executable rate: 0.726
- Solve rate: 0.681
- Objective-evaluable rate: 0.725
- Variable-output rate: 0.673

## Solver Availability

| solver | available | packages |
| --- | --- | --- |
| amplpy | False | amplpy:no |
| coptpy | False | coptpy:no |
| cvxpy | False | cvxpy:no |
| docplex | False | docplex:no, docplex.mp.model:no |
| gurobipy | True | gurobipy:yes@12.0.3 |
| highspy | False | highspy:no |
| linopy | False | linopy:no |
| mip | False | mip:no |
| mosek | False | mosek:no |
| ortools | True | ortools:yes@9.15.6755 |
| pulp | True | pulp:yes@3.3.1 |
| pyomo | False | pyomo:no, pyomo.environ:no |
| pyscipopt | True | pyscipopt:yes@6.2.1 |
| scipy.optimize | True | scipy.optimize:yes@1.13.1 |
| xpress | False | xpress:no |

## Dataset x Model x Solver

| dataset | model | solver | n | accuracy | executable_rate | solve_rate | objective_evaluable_rate | variable_output_rate | avg_tokens | avg_latency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IndustryOR | deepseek-v3 | coptpy | 3 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1386.000 | 23.905 |
| IndustryOR | deepseek-v3 | ortools | 3 | 0.000 | 1.000 | 0.667 | 1.000 | 0.667 | 2037.333 | 34.024 |
| IndustryOR | deepseek-v3 | pulp | 85 | 0.553 | 0.859 | 0.824 | 0.859 | 0.824 | 1210.635 | 21.832 |
| IndustryOR | deepseek-v3 | scipy.optimize | 8 | 0.750 | 1.000 | 0.875 | 1.000 | 0.875 | 1092.500 | 20.461 |
| IndustryOR | deepseek-v3 | unknown | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 853.000 | 14.679 |
| IndustryOR | deepseek-v3.2 | coptpy | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1046.000 | 21.906 |
| IndustryOR | deepseek-v3.2 | ortools | 6 | 0.333 | 0.667 | 0.500 | 0.667 | 0.500 | 2020.500 | 40.216 |
| IndustryOR | deepseek-v3.2 | pulp | 60 | 0.417 | 0.567 | 0.533 | 0.567 | 0.533 | 1371.417 | 30.658 |
| IndustryOR | deepseek-v3.2 | pulp+scipy.optimize | 2 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1613.000 | 33.089 |
| IndustryOR | deepseek-v3.2 | scipy.optimize | 27 | 0.296 | 0.519 | 0.519 | 0.519 | 0.519 | 1715.148 | 38.270 |
| IndustryOR | deepseek-v3.2 | unknown | 4 | 0.500 | 0.500 | 0.500 | 0.500 | 0.500 | 1098.000 | 22.481 |
| IndustryOR | gpt-4.1-mini | coptpy | 3 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1518.333 | 12.557 |
| IndustryOR | gpt-4.1-mini | cvxpy | 4 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1808.000 | 19.871 |
| IndustryOR | gpt-4.1-mini | cvxpy+mip | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1782.000 | 19.562 |
| IndustryOR | gpt-4.1-mini | ortools | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 4112.000 | 31.649 |
| IndustryOR | gpt-4.1-mini | pulp | 89 | 0.607 | 0.944 | 0.865 | 0.944 | 0.854 | 1413.562 | 14.683 |
| IndustryOR | gpt-4.1-mini | scipy.optimize | 1 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 | 2342.000 | 25.051 |
| IndustryOR | gpt-4.1-mini | unknown | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 847.000 | 7.062 |
| IndustryOR | gpt-4o | coptpy | 3 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1403.333 | 13.665 |
| IndustryOR | gpt-4o | cvxpy | 60 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1088.150 | 9.283 |
| IndustryOR | gpt-4o | ortools | 5 | 0.200 | 0.600 | 0.400 | 0.400 | 0.400 | 1587.400 | 19.817 |
| IndustryOR | gpt-4o | pulp | 21 | 0.667 | 0.952 | 0.810 | 0.952 | 0.810 | 905.810 | 10.070 |
| IndustryOR | gpt-4o | scipy.optimize | 11 | 0.273 | 0.818 | 0.727 | 0.818 | 0.455 | 1144.545 | 9.898 |
| IndustryOR | gpt-4o-mini | coptpy | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1390.000 | 8.253 |
| IndustryOR | gpt-4o-mini | cvxpy | 18 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1165.500 | 6.874 |
| IndustryOR | gpt-4o-mini | pulp | 41 | 0.488 | 0.780 | 0.732 | 0.780 | 0.732 | 962.049 | 6.346 |
| IndustryOR | gpt-4o-mini | scipy.optimize | 39 | 0.103 | 0.821 | 0.718 | 0.821 | 0.462 | 1093.000 | 8.324 |
| MAMO_ComplexLP | deepseek-v3 | ortools | 13 | 0.462 | 0.538 | 0.538 | 0.538 | 0.538 | 1326.846 | 20.167 |
| MAMO_ComplexLP | deepseek-v3 | pulp | 124 | 0.677 | 0.984 | 0.944 | 0.984 | 0.944 | 1473.815 | 22.952 |
| MAMO_ComplexLP | deepseek-v3 | scipy.optimize | 21 | 0.714 | 0.857 | 0.810 | 0.857 | 0.714 | 1324.667 | 22.692 |
| MAMO_ComplexLP | deepseek-v3 | unknown | 45 | 0.622 | 0.644 | 0.622 | 0.644 | 0.622 | 1111.956 | 15.213 |
| MAMO_ComplexLP | deepseek-v3.2 | mip+scipy.optimize | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 2265.000 | 40.716 |
| MAMO_ComplexLP | deepseek-v3.2 | ortools | 15 | 0.733 | 0.733 | 0.733 | 0.733 | 0.733 | 1759.933 | 30.118 |
| MAMO_ComplexLP | deepseek-v3.2 | pulp | 78 | 0.487 | 0.577 | 0.577 | 0.577 | 0.577 | 1404.295 | 23.348 |
| MAMO_ComplexLP | deepseek-v3.2 | scipy.optimize | 81 | 0.309 | 0.593 | 0.506 | 0.593 | 0.457 | 1598.432 | 31.121 |
| MAMO_ComplexLP | deepseek-v3.2 | unknown | 28 | 0.643 | 0.643 | 0.643 | 0.643 | 0.607 | 994.321 | 16.685 |
| MAMO_ComplexLP | gpt-4.1-mini | cvxpy | 7 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1037.571 | 10.377 |
| MAMO_ComplexLP | gpt-4.1-mini | pulp | 194 | 0.753 | 0.995 | 0.933 | 0.995 | 0.933 | 1472.582 | 13.139 |
| MAMO_ComplexLP | gpt-4.1-mini | unknown | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1275.500 | 7.824 |
| MAMO_ComplexLP | gpt-4o | unknown | 203 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 6.642 |
| MAMO_ComplexLP | gpt-4o-mini | cvxpy | 6 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1004.333 | 6.769 |
| MAMO_ComplexLP | gpt-4o-mini | pulp | 46 | 0.826 | 1.000 | 0.935 | 1.000 | 0.935 | 1456.152 | 7.226 |
| MAMO_ComplexLP | gpt-4o-mini | scipy.optimize | 149 | 0.221 | 0.846 | 0.624 | 0.846 | 0.383 | 1157.148 | 7.932 |
| MAMO_ComplexLP | gpt-4o-mini | unknown | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 910.500 | 4.210 |
| MAMO_EasyLP | deepseek-v3 | cvxpy+mip+pulp+scipy.optimize | 1 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1254.000 | 23.915 |
| MAMO_EasyLP | deepseek-v3 | mip+pulp+scipy.optimize | 8 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1244.250 | 24.822 |
| MAMO_EasyLP | deepseek-v3 | mip+scipy.optimize | 2 | 0.500 | 1.000 | 1.000 | 1.000 | 1.000 | 1089.000 | 22.309 |
| MAMO_EasyLP | deepseek-v3 | pulp | 278 | 0.874 | 0.921 | 0.910 | 0.921 | 0.910 | 892.932 | 14.325 |
| MAMO_EasyLP | deepseek-v3 | pulp+pyomo+scipy.optimize | 5 | 0.400 | 0.800 | 0.600 | 0.800 | 0.600 | 1156.400 | 22.666 |
| MAMO_EasyLP | deepseek-v3 | pulp+scipy.optimize | 85 | 0.824 | 0.941 | 0.929 | 0.941 | 0.929 | 1230.765 | 24.042 |
| MAMO_EasyLP | deepseek-v3 | pyomo | 41 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 840.268 | 13.615 |
| MAMO_EasyLP | deepseek-v3 | scipy.optimize | 222 | 0.725 | 0.932 | 0.851 | 0.932 | 0.851 | 1042.023 | 19.052 |
| MAMO_EasyLP | deepseek-v3.2 | mip+pulp+scipy.optimize | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1573.000 | 53.785 |
| MAMO_EasyLP | deepseek-v3.2 | mip+scipy.optimize | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1266.000 | 31.184 |
| MAMO_EasyLP | deepseek-v3.2 | ortools | 63 | 0.730 | 0.825 | 0.825 | 0.825 | 0.841 | 961.206 | 18.854 |
| MAMO_EasyLP | deepseek-v3.2 | ortools+pulp+scipy.optimize | 2 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1298.500 | 27.276 |
| MAMO_EasyLP | deepseek-v3.2 | pulp | 133 | 0.714 | 0.767 | 0.744 | 0.759 | 0.744 | 925.090 | 15.686 |
| MAMO_EasyLP | deepseek-v3.2 | pulp+scipy.optimize | 13 | 0.692 | 0.769 | 0.769 | 0.769 | 0.769 | 1678.000 | 39.318 |
| MAMO_EasyLP | deepseek-v3.2 | pyomo | 3 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1084.333 | 20.171 |
| MAMO_EasyLP | deepseek-v3.2 | scipy.optimize | 409 | 0.614 | 0.709 | 0.670 | 0.709 | 0.670 | 1316.873 | 29.007 |
| MAMO_EasyLP | deepseek-v3.2 | unknown | 17 | 0.765 | 1.000 | 1.000 | 1.000 | 1.000 | 786.059 | 15.889 |
| MAMO_EasyLP | gemini-2.5-pro | ortools | 10 | 0.200 | 0.200 | 0.200 | 0.200 | 0.300 | 4259.600 | 33.097 |
| MAMO_EasyLP | gemini-2.5-pro | pulp | 154 | 0.448 | 0.461 | 0.461 | 0.461 | 0.461 | 4066.812 | 32.284 |
| MAMO_EasyLP | gemini-2.5-pro | unknown | 74 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 4496.581 | 35.131 |
| MAMO_EasyLP | gpt-4.1-mini | pulp | 642 | 0.925 | 0.995 | 0.983 | 0.995 | 0.983 | 897.140 | 7.742 |
| MAMO_EasyLP | gpt-4o | cvxpy | 7 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 867.857 | 7.251 |
| MAMO_EasyLP | gpt-4o | ortools | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1006.000 | 6.915 |
| MAMO_EasyLP | gpt-4o | pulp | 554 | 0.908 | 0.957 | 0.951 | 0.957 | 0.951 | 817.134 | 5.567 |
| MAMO_EasyLP | gpt-4o | scipy.optimize | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 884.000 | 6.775 |
| MAMO_EasyLP | gpt-4o | unknown | 79 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 6.496 |
| MAMO_EasyLP | gpt-4o-mini | cvxpy | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1028.000 | 5.869 |
| MAMO_EasyLP | gpt-4o-mini | mip+scipy.optimize | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1087.500 | 6.570 |
| MAMO_EasyLP | gpt-4o-mini | pulp | 103 | 0.883 | 0.961 | 0.932 | 0.961 | 0.932 | 783.417 | 4.989 |
| MAMO_EasyLP | gpt-4o-mini | pulp+scipy.optimize | 17 | 0.882 | 1.000 | 1.000 | 1.000 | 1.000 | 1009.529 | 6.550 |
| MAMO_EasyLP | gpt-4o-mini | scipy.optimize | 519 | 0.505 | 0.988 | 0.794 | 0.988 | 0.794 | 876.676 | 5.478 |
| MAMO_EasyLP | o3-mini | pulp | 42 | 0.929 | 0.976 | 0.976 | 0.976 | 0.976 | 1961.071 | 9.269 |
| MAMO_EasyLP | o3-mini | unknown | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 4432.000 | 23.891 |
| NL4OPT | deepseek-v3 | cvxpy | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 712.000 | 12.126 |
| NL4OPT | deepseek-v3 | pulp | 122 | 0.770 | 0.836 | 0.795 | 0.836 | 0.795 | 797.066 | 14.773 |
| NL4OPT | deepseek-v3 | pulp+scipy.optimize | 15 | 0.800 | 1.000 | 0.800 | 1.000 | 0.800 | 1162.333 | 25.747 |
| NL4OPT | deepseek-v3 | pyomo | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 757.000 | 13.851 |
| NL4OPT | deepseek-v3 | scipy.optimize | 136 | 0.647 | 0.949 | 0.787 | 0.949 | 0.787 | 912.647 | 18.126 |
| NL4OPT | deepseek-v3.2 | mip+pulp | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1074.000 | 22.480 |
| NL4OPT | deepseek-v3.2 | mip+scipy.optimize | 1 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 | 914.000 | 17.268 |
| NL4OPT | deepseek-v3.2 | ortools | 6 | 0.833 | 0.833 | 0.833 | 0.833 | 0.833 | 845.000 | 15.200 |
| NL4OPT | deepseek-v3.2 | ortools+pulp | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 2237.000 | 53.619 |
| NL4OPT | deepseek-v3.2 | pulp | 87 | 0.690 | 0.782 | 0.713 | 0.782 | 0.713 | 825.425 | 15.421 |
| NL4OPT | deepseek-v3.2 | pulp+scipy.optimize | 2 | 0.500 | 0.500 | 0.500 | 0.500 | 0.500 | 1640.500 | 34.177 |
| NL4OPT | deepseek-v3.2 | scipy.optimize | 146 | 0.671 | 0.815 | 0.747 | 0.815 | 0.747 | 1056.014 | 21.882 |
| NL4OPT | deepseek-v3.2 | unknown | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 911.000 | 18.719 |
| NL4OPT | gemini-2.5-pro | cvxpy | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 4444.000 | 32.270 |
| NL4OPT | gemini-2.5-pro | ortools | 6 | 0.167 | 0.167 | 0.167 | 0.167 | 0.167 | 4289.500 | 35.904 |
| NL4OPT | gemini-2.5-pro | pulp | 203 | 0.493 | 0.552 | 0.522 | 0.552 | 0.522 | 3865.350 | 29.395 |
| NL4OPT | gemini-2.5-pro | scipy.optimize | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 4425.000 | 34.008 |
| NL4OPT | gemini-2.5-pro | unknown | 34 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 4442.882 | 34.132 |
| NL4OPT | gpt-4.1-mini | cvxpy | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 850.500 | 11.301 |
| NL4OPT | gpt-4.1-mini | pulp | 236 | 0.852 | 0.936 | 0.881 | 0.936 | 0.881 | 766.818 | 7.440 |
| NL4OPT | gpt-4.1-mini | scipy.optimize | 7 | 0.714 | 1.000 | 1.000 | 1.000 | 1.000 | 871.714 | 8.075 |
| NL4OPT | gpt-4o | cvxpy | 129 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 740.713 | 5.775 |
| NL4OPT | gpt-4o | pulp | 116 | 0.914 | 0.948 | 0.922 | 0.948 | 0.922 | 719.776 | 5.864 |
| NL4OPT | gpt-4o-mini | cvxpy | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 722.000 | 5.033 |
| NL4OPT | gpt-4o-mini | pulp | 198 | 0.843 | 0.934 | 0.869 | 0.934 | 0.869 | 703.126 | 4.873 |
| NL4OPT | gpt-4o-mini | scipy.optimize | 45 | 0.422 | 0.933 | 0.622 | 0.933 | 0.556 | 808.311 | 6.100 |
| NL4OPT | o3-mini | cvxpy | 8 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 2038.625 | 9.490 |
| NL4OPT | o3-mini | pulp | 237 | 0.890 | 1.000 | 0.928 | 0.992 | 0.928 | 1951.599 | 9.789 |
| OptMATH_Bench | deepseek-v3 | cvxpy | 34 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 2918.088 | 39.812 |
| OptMATH_Bench | deepseek-v3 | mip+scipy.optimize | 1 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 | 2192.000 | 42.226 |
| OptMATH_Bench | deepseek-v3 | ortools | 25 | 0.200 | 0.880 | 0.880 | 0.880 | 0.880 | 1693.240 | 28.238 |
| OptMATH_Bench | deepseek-v3 | pulp | 100 | 0.450 | 0.850 | 0.740 | 0.850 | 0.730 | 2329.730 | 36.615 |
| OptMATH_Bench | deepseek-v3 | pyomo | 3 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1824.667 | 31.208 |
| OptMATH_Bench | deepseek-v3 | scipy.optimize | 3 | 0.667 | 0.667 | 0.667 | 0.667 | 0.667 | 1951.667 | 35.991 |
| OptMATH_Bench | deepseek-v3.2 | cvxpy | 12 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 3256.833 | 49.548 |
| OptMATH_Bench | deepseek-v3.2 | cvxpy+scipy.optimize | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 4875.000 | 225.506 |
| OptMATH_Bench | deepseek-v3.2 | mip+scipy.optimize | 1 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 | 3226.000 | 103.290 |
| OptMATH_Bench | deepseek-v3.2 | ortools | 26 | 0.308 | 0.692 | 0.615 | 0.692 | 0.500 | 1876.654 | 38.232 |
| OptMATH_Bench | deepseek-v3.2 | ortools+pulp+scipy.optimize | 1 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 | 2658.000 | 60.722 |
| OptMATH_Bench | deepseek-v3.2 | pulp | 78 | 0.192 | 0.474 | 0.449 | 0.474 | 0.449 | 2275.987 | 42.433 |
| OptMATH_Bench | deepseek-v3.2 | pulp+scipy.optimize | 2 | 0.000 | 0.500 | 0.000 | 0.500 | 0.000 | 2292.500 | 46.046 |
| OptMATH_Bench | deepseek-v3.2 | scipy.optimize | 41 | 0.268 | 0.829 | 0.634 | 0.780 | 0.488 | 3130.122 | 60.972 |
| OptMATH_Bench | deepseek-v3.2 | unknown | 4 | 0.250 | 0.500 | 0.500 | 0.500 | 0.500 | 1427.500 | 19.480 |
| OptMATH_Bench | gpt-4.1-mini | cvxpy | 42 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 3102.190 | 25.604 |
| OptMATH_Bench | gpt-4.1-mini | cvxpy+mip | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 2058.500 | 18.514 |
| OptMATH_Bench | gpt-4.1-mini | pulp | 122 | 0.475 | 0.910 | 0.844 | 0.910 | 0.844 | 2324.320 | 20.246 |
| OptMATH_Bench | gpt-4o | cvxpy | 122 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 2019.238 | 13.894 |
| OptMATH_Bench | gpt-4o | ortools | 10 | 0.700 | 0.900 | 0.800 | 0.900 | 0.800 | 1544.900 | 17.553 |
| OptMATH_Bench | gpt-4o | pulp | 3 | 0.333 | 0.333 | 0.333 | 0.333 | 0.333 | 3800.667 | 27.278 |
| OptMATH_Bench | gpt-4o | scipy.optimize | 5 | 0.000 | 0.800 | 0.600 | 0.600 | 0.400 | 1555.400 | 21.734 |
| OptMATH_Bench | gpt-4o | unknown | 26 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 7.486 |
| OptMATH_Bench | gpt-4o-mini | cvxpy | 133 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1822.301 | 10.168 |
| OptMATH_Bench | gpt-4o-mini | pulp | 20 | 0.150 | 0.650 | 0.600 | 0.650 | 0.600 | 2446.950 | 11.620 |
| OptMATH_Bench | gpt-4o-mini | scipy.optimize | 13 | 0.154 | 0.308 | 0.308 | 0.308 | 0.077 | 1988.154 | 10.431 |
| OptiBench | deepseek-v3 | mip+scipy.optimize | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1221.000 | 25.037 |
| OptiBench | deepseek-v3 | pulp | 304 | 0.684 | 0.845 | 0.829 | 0.845 | 0.826 | 927.003 | 16.207 |
| OptiBench | deepseek-v3 | pulp+scipy.optimize | 11 | 0.636 | 0.818 | 0.818 | 0.818 | 0.818 | 1185.636 | 24.486 |
| OptiBench | deepseek-v3 | scipy.optimize | 289 | 0.657 | 0.927 | 0.834 | 0.924 | 0.834 | 948.197 | 18.232 |
| OptiBench | deepseek-v3.2 | ortools | 4 | 0.750 | 0.750 | 0.750 | 0.750 | 0.750 | 882.250 | 17.204 |
| OptiBench | deepseek-v3.2 | pulp | 227 | 0.573 | 0.670 | 0.661 | 0.670 | 0.665 | 1048.379 | 21.896 |
| OptiBench | deepseek-v3.2 | pulp+scipy.optimize | 6 | 0.167 | 0.500 | 0.500 | 0.500 | 0.500 | 1915.167 | 39.191 |
| OptiBench | deepseek-v3.2 | scipy.optimize | 360 | 0.625 | 0.831 | 0.775 | 0.822 | 0.775 | 1086.261 | 25.003 |
| OptiBench | deepseek-v3.2 | unknown | 8 | 0.875 | 1.000 | 1.000 | 1.000 | 1.000 | 734.750 | 21.547 |
| OptiBench | gpt-4.1-mini | cvxpy | 80 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 882.263 | 8.892 |
| OptiBench | gpt-4.1-mini | cvxpy+mip | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1213.500 | 13.258 |
| OptiBench | gpt-4.1-mini | cvxpy+mip+pulp | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 2361.000 | 18.924 |
| OptiBench | gpt-4.1-mini | cvxpy+mip+pulp+scipy.optimize | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 2400.000 | 22.829 |
| OptiBench | gpt-4.1-mini | cvxpy+mosek | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1733.500 | 18.844 |
| OptiBench | gpt-4.1-mini | cvxpy+pulp | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 2422.000 | 26.333 |
| OptiBench | gpt-4.1-mini | cvxpy+pulp+scipy.optimize | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1653.000 | 17.926 |
| OptiBench | gpt-4.1-mini | cvxpy+pyomo+scipy.optimize | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 2058.000 | 24.586 |
| OptiBench | gpt-4.1-mini | cvxpy+scipy.optimize | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1235.000 | 13.981 |
| OptiBench | gpt-4.1-mini | mip+pulp+scipy.optimize | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 2103.000 | 24.888 |
| OptiBench | gpt-4.1-mini | pulp | 479 | 0.758 | 0.871 | 0.858 | 0.871 | 0.858 | 901.591 | 10.443 |
| OptiBench | gpt-4.1-mini | scipy.optimize | 34 | 0.794 | 0.941 | 0.912 | 0.941 | 0.912 | 786.588 | 8.174 |
| OptiBench | gpt-4o | cvxpy | 235 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 821.519 | 8.708 |
| OptiBench | gpt-4o | pulp | 154 | 0.851 | 0.922 | 0.916 | 0.916 | 0.916 | 794.474 | 6.819 |
| OptiBench | gpt-4o | scipy.optimize | 18 | 0.667 | 0.944 | 0.889 | 0.944 | 0.722 | 856.556 | 11.422 |
| OptiBench | gpt-4o | unknown | 198 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | - | 6.606 |
| OptiBench | gpt-4o-mini | cvxpy | 94 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 827.223 | 5.278 |
| OptiBench | gpt-4o-mini | pulp | 353 | 0.759 | 0.892 | 0.870 | 0.892 | 0.870 | 777.164 | 5.703 |
| OptiBench | gpt-4o-mini | scipy.optimize | 158 | 0.430 | 0.873 | 0.791 | 0.873 | 0.741 | 826.095 | 6.074 |

## Dataset x Model x Prompt

| dataset | model | prompt_id | n | accuracy | executable_rate | solve_rate | objective_evaluable_rate | variable_output_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IndustryOR | deepseek-v3 | neutral_best_v2 | 100 | 0.530 | 0.840 | 0.790 | 0.840 | 0.790 |
| IndustryOR | deepseek-v3.2 | neutral_best_v2 | 100 | 0.390 | 0.560 | 0.530 | 0.560 | 0.530 |
| IndustryOR | gpt-4.1-mini | neutral_best_v2 | 100 | 0.550 | 0.860 | 0.790 | 0.860 | 0.780 |
| IndustryOR | gpt-4o | neutral_best_v2 | 100 | 0.180 | 0.320 | 0.270 | 0.310 | 0.240 |
| IndustryOR | gpt-4o-mini | neutral_best_v2 | 100 | 0.240 | 0.640 | 0.580 | 0.640 | 0.480 |
| MAMO_ComplexLP | deepseek-v3 | neutral_best_v2 | 203 | 0.655 | 0.867 | 0.833 | 0.867 | 0.823 |
| MAMO_ComplexLP | deepseek-v3.2 | neutral_best_v2 | 203 | 0.458 | 0.606 | 0.571 | 0.606 | 0.547 |
| MAMO_ComplexLP | gpt-4.1-mini | neutral_best_v2 | 203 | 0.719 | 0.951 | 0.892 | 0.951 | 0.892 |
| MAMO_ComplexLP | gpt-4o | neutral_best_v2 | 203 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_ComplexLP | gpt-4o-mini | neutral_best_v2 | 203 | 0.350 | 0.847 | 0.670 | 0.847 | 0.493 |
| MAMO_EasyLP | deepseek-v3 | neutral_best_v2 | 642 | 0.755 | 0.869 | 0.833 | 0.869 | 0.833 |
| MAMO_EasyLP | deepseek-v3.2 | neutral_best_v2 | 642 | 0.651 | 0.740 | 0.710 | 0.738 | 0.712 |
| MAMO_EasyLP | gemini-2.5-pro | neutral_best_v2 | 238 | 0.298 | 0.307 | 0.307 | 0.307 | 0.311 |
| MAMO_EasyLP | gpt-4.1-mini | neutral_best_v2 | 642 | 0.925 | 0.995 | 0.983 | 0.995 | 0.983 |
| MAMO_EasyLP | gpt-4o | neutral_best_v2 | 642 | 0.787 | 0.829 | 0.824 | 0.829 | 0.824 |
| MAMO_EasyLP | gpt-4o-mini | neutral_best_v2 | 642 | 0.573 | 0.980 | 0.818 | 0.980 | 0.818 |
| MAMO_EasyLP | o3-mini | neutral_best_v2 | 43 | 0.907 | 0.953 | 0.953 | 0.953 | 0.953 |
| NL4OPT | deepseek-v3 | neutral_best | 30 | 0.633 | 0.800 | 0.667 | 0.800 | 0.667 |
| NL4OPT | deepseek-v3 | neutral_best_v2 | 245 | 0.714 | 0.906 | 0.800 | 0.906 | 0.800 |
| NL4OPT | deepseek-v3.2 | neutral_best_v2 | 245 | 0.673 | 0.796 | 0.731 | 0.796 | 0.731 |
| NL4OPT | gemini-2.5-pro | neutral_best_v2 | 245 | 0.412 | 0.461 | 0.437 | 0.461 | 0.437 |
| NL4OPT | gpt-4.1-mini | neutral_best_v2 | 245 | 0.841 | 0.931 | 0.878 | 0.931 | 0.878 |
| NL4OPT | gpt-4o | neutral_best_v2 | 245 | 0.433 | 0.449 | 0.437 | 0.449 | 0.437 |
| NL4OPT | gpt-4o-mini | neutral_best_v2 | 245 | 0.759 | 0.927 | 0.816 | 0.927 | 0.804 |
| NL4OPT | o3-mini | neutral_best_v2 | 245 | 0.861 | 0.967 | 0.898 | 0.959 | 0.898 |
| OptMATH_Bench | deepseek-v3 | neutral_best_v2 | 166 | 0.313 | 0.663 | 0.596 | 0.663 | 0.590 |
| OptMATH_Bench | deepseek-v3.2 | neutral_best_v2 | 166 | 0.211 | 0.566 | 0.488 | 0.554 | 0.434 |
| OptMATH_Bench | gpt-4.1-mini | neutral_best_v2 | 166 | 0.349 | 0.669 | 0.620 | 0.669 | 0.620 |
| OptMATH_Bench | gpt-4o | neutral_best_v2 | 166 | 0.048 | 0.084 | 0.072 | 0.078 | 0.066 |
| OptMATH_Bench | gpt-4o-mini | neutral_best_v2 | 166 | 0.030 | 0.102 | 0.096 | 0.102 | 0.078 |
| OptiBench | deepseek-v3 | neutral_best_v2 | 605 | 0.671 | 0.884 | 0.831 | 0.883 | 0.830 |
| OptiBench | deepseek-v3.2 | neutral_best_v2 | 605 | 0.605 | 0.769 | 0.732 | 0.764 | 0.734 |
| OptiBench | gpt-4.1-mini | neutral_best_v2 | 605 | 0.646 | 0.744 | 0.732 | 0.744 | 0.732 |
| OptiBench | gpt-4o | neutral_best_v2 | 605 | 0.236 | 0.263 | 0.260 | 0.261 | 0.255 |
| OptiBench | gpt-4o-mini | neutral_best_v2 | 605 | 0.555 | 0.749 | 0.714 | 0.749 | 0.701 |

## Solver Availability Outcomes

| dataset | model | solver_availability_state | n | accuracy | executable_rate | solve_rate | objective_evaluable_rate | variable_output_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IndustryOR | deepseek-v3 | available | 96 | 0.552 | 0.875 | 0.823 | 0.875 | 0.823 |
| IndustryOR | deepseek-v3 | not_detected | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | deepseek-v3 | unavailable | 3 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | deepseek-v3.2 | available | 95 | 0.389 | 0.568 | 0.537 | 0.568 | 0.537 |
| IndustryOR | deepseek-v3.2 | not_detected | 4 | 0.500 | 0.500 | 0.500 | 0.500 | 0.500 |
| IndustryOR | deepseek-v3.2 | unavailable | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | gpt-4.1-mini | available | 91 | 0.593 | 0.934 | 0.857 | 0.934 | 0.846 |
| IndustryOR | gpt-4.1-mini | not_detected | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| IndustryOR | gpt-4.1-mini | unavailable | 8 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | gpt-4o | available | 37 | 0.486 | 0.865 | 0.730 | 0.838 | 0.649 |
| IndustryOR | gpt-4o | unavailable | 63 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | gpt-4o-mini | available | 80 | 0.300 | 0.800 | 0.725 | 0.800 | 0.600 |
| IndustryOR | gpt-4o-mini | unavailable | 20 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_ComplexLP | deepseek-v3 | available | 158 | 0.665 | 0.930 | 0.892 | 0.930 | 0.880 |
| MAMO_ComplexLP | deepseek-v3 | not_detected | 45 | 0.622 | 0.644 | 0.622 | 0.644 | 0.622 |
| MAMO_ComplexLP | deepseek-v3.2 | available | 174 | 0.425 | 0.598 | 0.557 | 0.598 | 0.534 |
| MAMO_ComplexLP | deepseek-v3.2 | not_detected | 28 | 0.643 | 0.643 | 0.643 | 0.643 | 0.607 |
| MAMO_ComplexLP | deepseek-v3.2 | unavailable | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_ComplexLP | gpt-4.1-mini | available | 194 | 0.753 | 0.995 | 0.933 | 0.995 | 0.933 |
| MAMO_ComplexLP | gpt-4.1-mini | not_detected | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_ComplexLP | gpt-4.1-mini | unavailable | 7 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_ComplexLP | gpt-4o | not_detected | 203 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_ComplexLP | gpt-4o-mini | available | 195 | 0.364 | 0.882 | 0.697 | 0.882 | 0.513 |
| MAMO_ComplexLP | gpt-4o-mini | not_detected | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_ComplexLP | gpt-4o-mini | unavailable | 6 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | deepseek-v3 | available | 585 | 0.810 | 0.928 | 0.891 | 0.928 | 0.891 |
| MAMO_EasyLP | deepseek-v3 | unavailable | 57 | 0.193 | 0.263 | 0.246 | 0.263 | 0.246 |
| MAMO_EasyLP | deepseek-v3.2 | available | 620 | 0.650 | 0.735 | 0.705 | 0.734 | 0.706 |
| MAMO_EasyLP | deepseek-v3.2 | not_detected | 17 | 0.765 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_EasyLP | deepseek-v3.2 | unavailable | 5 | 0.400 | 0.400 | 0.400 | 0.400 | 0.400 |
| MAMO_EasyLP | gemini-2.5-pro | available | 164 | 0.433 | 0.445 | 0.445 | 0.445 | 0.451 |
| MAMO_EasyLP | gemini-2.5-pro | not_detected | 74 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | gpt-4.1-mini | available | 642 | 0.925 | 0.995 | 0.983 | 0.995 | 0.983 |
| MAMO_EasyLP | gpt-4o | available | 556 | 0.908 | 0.957 | 0.951 | 0.957 | 0.951 |
| MAMO_EasyLP | gpt-4o | not_detected | 79 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | gpt-4o | unavailable | 7 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | gpt-4o-mini | available | 639 | 0.576 | 0.984 | 0.822 | 0.984 | 0.822 |
| MAMO_EasyLP | gpt-4o-mini | unavailable | 3 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | o3-mini | available | 42 | 0.929 | 0.976 | 0.976 | 0.976 | 0.976 |
| MAMO_EasyLP | o3-mini | not_detected | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | deepseek-v3 | available | 273 | 0.711 | 0.901 | 0.791 | 0.901 | 0.791 |
| NL4OPT | deepseek-v3 | unavailable | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | deepseek-v3.2 | available | 242 | 0.678 | 0.798 | 0.731 | 0.798 | 0.731 |
| NL4OPT | deepseek-v3.2 | not_detected | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NL4OPT | deepseek-v3.2 | unavailable | 2 | 0.000 | 0.500 | 0.500 | 0.500 | 0.500 |
| NL4OPT | gemini-2.5-pro | available | 210 | 0.481 | 0.538 | 0.510 | 0.538 | 0.510 |
| NL4OPT | gemini-2.5-pro | not_detected | 34 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | gemini-2.5-pro | unavailable | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | gpt-4.1-mini | available | 243 | 0.848 | 0.938 | 0.885 | 0.938 | 0.885 |
| NL4OPT | gpt-4.1-mini | unavailable | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | gpt-4o | available | 116 | 0.914 | 0.948 | 0.922 | 0.948 | 0.922 |
| NL4OPT | gpt-4o | unavailable | 129 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | gpt-4o-mini | available | 243 | 0.765 | 0.934 | 0.823 | 0.934 | 0.811 |
| NL4OPT | gpt-4o-mini | unavailable | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | o3-mini | available | 237 | 0.890 | 1.000 | 0.928 | 0.992 | 0.928 |
| NL4OPT | o3-mini | unavailable | 8 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | deepseek-v3 | available | 128 | 0.406 | 0.852 | 0.766 | 0.852 | 0.758 |
| OptMATH_Bench | deepseek-v3 | unavailable | 38 | 0.000 | 0.026 | 0.026 | 0.026 | 0.026 |
| OptMATH_Bench | deepseek-v3.2 | available | 148 | 0.230 | 0.615 | 0.527 | 0.601 | 0.466 |
| OptMATH_Bench | deepseek-v3.2 | not_detected | 4 | 0.250 | 0.500 | 0.500 | 0.500 | 0.500 |
| OptMATH_Bench | deepseek-v3.2 | unavailable | 14 | 0.000 | 0.071 | 0.071 | 0.071 | 0.071 |
| OptMATH_Bench | gpt-4.1-mini | available | 122 | 0.475 | 0.910 | 0.844 | 0.910 | 0.844 |
| OptMATH_Bench | gpt-4.1-mini | unavailable | 44 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | gpt-4o | available | 18 | 0.444 | 0.778 | 0.667 | 0.722 | 0.611 |
| OptMATH_Bench | gpt-4o | not_detected | 26 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | gpt-4o | unavailable | 122 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | gpt-4o-mini | available | 33 | 0.152 | 0.515 | 0.485 | 0.515 | 0.394 |
| OptMATH_Bench | gpt-4o-mini | unavailable | 133 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | deepseek-v3 | available | 604 | 0.671 | 0.884 | 0.831 | 0.882 | 0.829 |
| OptiBench | deepseek-v3 | unavailable | 1 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| OptiBench | deepseek-v3.2 | available | 597 | 0.601 | 0.765 | 0.729 | 0.760 | 0.730 |
| OptiBench | deepseek-v3.2 | not_detected | 8 | 0.875 | 1.000 | 1.000 | 1.000 | 1.000 |
| OptiBench | gpt-4.1-mini | available | 513 | 0.760 | 0.875 | 0.862 | 0.875 | 0.862 |
| OptiBench | gpt-4.1-mini | unavailable | 92 | 0.011 | 0.011 | 0.011 | 0.011 | 0.011 |
| OptiBench | gpt-4o | available | 172 | 0.831 | 0.924 | 0.913 | 0.919 | 0.895 |
| OptiBench | gpt-4o | not_detected | 198 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | gpt-4o | unavailable | 235 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | gpt-4o-mini | available | 511 | 0.658 | 0.886 | 0.845 | 0.886 | 0.830 |
| OptiBench | gpt-4o-mini | unavailable | 94 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

## Failure Taxonomy

| dataset | model | failure_type | n | accuracy | executable_rate | solve_rate | objective_evaluable_rate | variable_output_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IndustryOR | deepseek-v3 | correct | 53 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| IndustryOR | deepseek-v3 | infeasible_unbounded_misclassification | 5 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| IndustryOR | deepseek-v3 | missing_module | 4 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | deepseek-v3 | name_error | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | deepseek-v3 | runtime_error | 6 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | deepseek-v3 | syntax_error | 5 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | deepseek-v3 | wrong_numeric | 26 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| IndustryOR | deepseek-v3.2 | correct | 39 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| IndustryOR | deepseek-v3.2 | infeasible_unbounded_misclassification | 3 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| IndustryOR | deepseek-v3.2 | missing_module | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | deepseek-v3.2 | name_error | 7 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | deepseek-v3.2 | runtime_error | 23 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | deepseek-v3.2 | syntax_error | 13 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | deepseek-v3.2 | wrong_numeric | 14 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| IndustryOR | gpt-4.1-mini | correct | 55 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| IndustryOR | gpt-4.1-mini | infeasible_unbounded_misclassification | 7 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| IndustryOR | gpt-4.1-mini | missing_module | 8 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | gpt-4.1-mini | runtime_error | 4 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | gpt-4.1-mini | syntax_error | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | gpt-4.1-mini | wrong_numeric | 24 | 0.000 | 1.000 | 1.000 | 1.000 | 0.958 |
| IndustryOR | gpt-4o | correct | 18 | 1.000 | 1.000 | 1.000 | 1.000 | 0.944 |
| IndustryOR | gpt-4o | exec_no_solve | 1 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | gpt-4o | infeasible_unbounded_misclassification | 4 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| IndustryOR | gpt-4o | missing_module | 64 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | gpt-4o | runtime_error | 3 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | gpt-4o | syntax_error | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | gpt-4o | wrong_numeric | 9 | 0.000 | 1.000 | 1.000 | 1.000 | 0.778 |
| IndustryOR | gpt-4o-mini | correct | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| IndustryOR | gpt-4o-mini | infeasible_unbounded_misclassification | 6 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| IndustryOR | gpt-4o-mini | missing_module | 19 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | gpt-4o-mini | runtime_error | 15 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | gpt-4o-mini | syntax_error | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | gpt-4o-mini | wrong_numeric | 34 | 0.000 | 1.000 | 1.000 | 1.000 | 0.706 |
| MAMO_ComplexLP | deepseek-v3 | correct | 133 | 1.000 | 1.000 | 1.000 | 1.000 | 0.985 |
| MAMO_ComplexLP | deepseek-v3 | infeasible_unbounded_misclassification | 7 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| MAMO_ComplexLP | deepseek-v3 | missing_module | 17 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_ComplexLP | deepseek-v3 | runtime_error | 9 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_ComplexLP | deepseek-v3 | timeout | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_ComplexLP | deepseek-v3 | wrong_numeric | 36 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_ComplexLP | deepseek-v3.2 | correct | 93 | 1.000 | 1.000 | 1.000 | 1.000 | 0.978 |
| MAMO_ComplexLP | deepseek-v3.2 | infeasible_unbounded_misclassification | 7 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| MAMO_ComplexLP | deepseek-v3.2 | missing_module | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_ComplexLP | deepseek-v3.2 | name_error | 20 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_ComplexLP | deepseek-v3.2 | runtime_error | 40 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_ComplexLP | deepseek-v3.2 | syntax_error | 19 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_ComplexLP | deepseek-v3.2 | wrong_numeric | 23 | 0.000 | 1.000 | 1.000 | 1.000 | 0.870 |
| MAMO_ComplexLP | gpt-4.1-mini | correct | 146 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_ComplexLP | gpt-4.1-mini | infeasible_unbounded_misclassification | 12 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| MAMO_ComplexLP | gpt-4.1-mini | missing_module | 9 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_ComplexLP | gpt-4.1-mini | runtime_error | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_ComplexLP | gpt-4.1-mini | wrong_numeric | 35 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_ComplexLP | gpt-4o | api_error | 203 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_ComplexLP | gpt-4o-mini | correct | 71 | 1.000 | 1.000 | 1.000 | 1.000 | 0.944 |
| MAMO_ComplexLP | gpt-4o-mini | infeasible_unbounded_misclassification | 36 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| MAMO_ComplexLP | gpt-4o-mini | missing_module | 11 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_ComplexLP | gpt-4o-mini | runtime_error | 20 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_ComplexLP | gpt-4o-mini | wrong_numeric | 65 | 0.000 | 1.000 | 1.000 | 1.000 | 0.508 |
| MAMO_EasyLP | deepseek-v3 | correct | 485 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_EasyLP | deepseek-v3 | infeasible_unbounded_misclassification | 23 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| MAMO_EasyLP | deepseek-v3 | missing_module | 41 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | deepseek-v3 | name_error | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | deepseek-v3 | runtime_error | 29 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | deepseek-v3 | syntax_error | 13 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | deepseek-v3 | wrong_numeric | 50 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_EasyLP | deepseek-v3.2 | correct | 418 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_EasyLP | deepseek-v3.2 | exec_no_solve | 1 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | deepseek-v3.2 | infeasible_unbounded_misclassification | 18 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| MAMO_EasyLP | deepseek-v3.2 | missing_module | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | deepseek-v3.2 | name_error | 25 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | deepseek-v3.2 | runtime_error | 84 | 0.000 | 0.000 | 0.000 | 0.000 | 0.012 |
| MAMO_EasyLP | deepseek-v3.2 | syntax_error | 46 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | deepseek-v3.2 | timeout | 10 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | deepseek-v3.2 | wrong_numeric | 38 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_EasyLP | gemini-2.5-pro | correct | 71 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_EasyLP | gemini-2.5-pro | runtime_error | 5 | 0.000 | 0.000 | 0.000 | 0.000 | 0.200 |
| MAMO_EasyLP | gemini-2.5-pro | syntax_error | 160 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | gemini-2.5-pro | wrong_numeric | 2 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_EasyLP | gpt-4.1-mini | correct | 594 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_EasyLP | gpt-4.1-mini | infeasible_unbounded_misclassification | 8 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| MAMO_EasyLP | gpt-4.1-mini | runtime_error | 3 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | gpt-4.1-mini | wrong_numeric | 37 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_EasyLP | gpt-4o | api_error | 79 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | gpt-4o | correct | 505 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_EasyLP | gpt-4o | infeasible_unbounded_misclassification | 3 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| MAMO_EasyLP | gpt-4o | missing_module | 7 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | gpt-4o | runtime_error | 24 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | gpt-4o | wrong_numeric | 24 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_EasyLP | gpt-4o-mini | correct | 368 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_EasyLP | gpt-4o-mini | infeasible_unbounded_misclassification | 104 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| MAMO_EasyLP | gpt-4o-mini | missing_module | 3 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | gpt-4o-mini | runtime_error | 9 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | gpt-4o-mini | syntax_error | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | gpt-4o-mini | wrong_numeric | 157 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_EasyLP | o3-mini | correct | 39 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_EasyLP | o3-mini | no_code | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | o3-mini | syntax_error | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | o3-mini | wrong_numeric | 2 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NL4OPT | deepseek-v3 | correct | 194 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NL4OPT | deepseek-v3 | exec_no_solve | 17 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| NL4OPT | deepseek-v3 | infeasible_unbounded_misclassification | 13 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| NL4OPT | deepseek-v3 | missing_module | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | deepseek-v3 | name_error | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | deepseek-v3 | runtime_error | 8 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | deepseek-v3 | syntax_error | 18 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | deepseek-v3 | wrong_numeric | 22 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NL4OPT | deepseek-v3.2 | correct | 165 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NL4OPT | deepseek-v3.2 | exec_no_solve | 12 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| NL4OPT | deepseek-v3.2 | infeasible_unbounded_misclassification | 4 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| NL4OPT | deepseek-v3.2 | name_error | 5 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | deepseek-v3.2 | runtime_error | 31 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | deepseek-v3.2 | syntax_error | 14 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | deepseek-v3.2 | wrong_numeric | 14 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NL4OPT | gemini-2.5-pro | correct | 101 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NL4OPT | gemini-2.5-pro | exec_no_solve | 6 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| NL4OPT | gemini-2.5-pro | syntax_error | 132 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | gemini-2.5-pro | wrong_numeric | 6 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NL4OPT | gpt-4.1-mini | correct | 206 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NL4OPT | gpt-4.1-mini | exec_no_solve | 12 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| NL4OPT | gpt-4.1-mini | infeasible_unbounded_misclassification | 1 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| NL4OPT | gpt-4.1-mini | missing_module | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | gpt-4.1-mini | runtime_error | 15 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | gpt-4.1-mini | wrong_numeric | 9 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NL4OPT | gpt-4o | correct | 106 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NL4OPT | gpt-4o | exec_no_solve | 3 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| NL4OPT | gpt-4o | missing_module | 128 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | gpt-4o | runtime_error | 6 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | gpt-4o | syntax_error | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | gpt-4o | wrong_numeric | 1 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NL4OPT | gpt-4o-mini | correct | 186 | 1.000 | 1.000 | 1.000 | 1.000 | 0.984 |
| NL4OPT | gpt-4o-mini | exec_no_solve | 11 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| NL4OPT | gpt-4o-mini | infeasible_unbounded_misclassification | 16 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| NL4OPT | gpt-4o-mini | missing_module | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | gpt-4o-mini | runtime_error | 16 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | gpt-4o-mini | wrong_numeric | 14 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NL4OPT | o3-mini | correct | 211 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NL4OPT | o3-mini | exec_no_solve | 16 | 0.000 | 1.000 | 0.000 | 0.875 | 0.000 |
| NL4OPT | o3-mini | infeasible_unbounded_misclassification | 1 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| NL4OPT | o3-mini | missing_module | 8 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | o3-mini | wrong_numeric | 9 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| OptMATH_Bench | deepseek-v3 | correct | 52 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| OptMATH_Bench | deepseek-v3 | infeasible_unbounded_misclassification | 11 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| OptMATH_Bench | deepseek-v3 | missing_module | 37 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | deepseek-v3 | runtime_error | 14 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | deepseek-v3 | syntax_error | 4 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | deepseek-v3 | timeout | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | deepseek-v3 | wrong_numeric | 47 | 0.000 | 1.000 | 1.000 | 1.000 | 0.979 |
| OptMATH_Bench | deepseek-v3.2 | correct | 35 | 1.000 | 1.000 | 1.000 | 1.000 | 0.971 |
| OptMATH_Bench | deepseek-v3.2 | exec_no_solve | 2 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | deepseek-v3.2 | infeasible_unbounded_misclassification | 11 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| OptMATH_Bench | deepseek-v3.2 | missing_module | 12 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | deepseek-v3.2 | name_error | 13 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | deepseek-v3.2 | runtime_error | 22 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | deepseek-v3.2 | syntax_error | 24 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | deepseek-v3.2 | timeout | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | deepseek-v3.2 | wrong_numeric | 46 | 0.000 | 1.000 | 1.000 | 1.000 | 0.826 |
| OptMATH_Bench | gpt-4.1-mini | correct | 58 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| OptMATH_Bench | gpt-4.1-mini | infeasible_unbounded_misclassification | 8 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| OptMATH_Bench | gpt-4.1-mini | missing_module | 44 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | gpt-4.1-mini | runtime_error | 8 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | gpt-4.1-mini | syntax_error | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | gpt-4.1-mini | timeout | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | gpt-4.1-mini | wrong_numeric | 45 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| OptMATH_Bench | gpt-4o | api_error | 26 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | gpt-4o | correct | 8 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| OptMATH_Bench | gpt-4o | exec_no_solve | 1 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | gpt-4o | infeasible_unbounded_misclassification | 1 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| OptMATH_Bench | gpt-4o | missing_module | 120 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | gpt-4o | runtime_error | 3 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | gpt-4o | syntax_error | 3 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | gpt-4o | wrong_numeric | 4 | 0.000 | 1.000 | 1.000 | 1.000 | 0.750 |
| OptMATH_Bench | gpt-4o-mini | correct | 5 | 1.000 | 1.000 | 1.000 | 1.000 | 0.600 |
| OptMATH_Bench | gpt-4o-mini | infeasible_unbounded_misclassification | 1 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| OptMATH_Bench | gpt-4o-mini | missing_module | 133 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | gpt-4o-mini | runtime_error | 14 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | gpt-4o-mini | syntax_error | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | gpt-4o-mini | wrong_numeric | 11 | 0.000 | 1.000 | 1.000 | 1.000 | 0.909 |
| OptiBench | deepseek-v3 | correct | 406 | 1.000 | 1.000 | 1.000 | 1.000 | 0.998 |
| OptiBench | deepseek-v3 | exec_no_solve | 1 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | deepseek-v3 | infeasible_unbounded_misclassification | 31 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| OptiBench | deepseek-v3 | name_error | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | deepseek-v3 | runtime_error | 48 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | deepseek-v3 | syntax_error | 21 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | deepseek-v3 | wrong_numeric | 97 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| OptiBench | deepseek-v3.2 | correct | 366 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| OptiBench | deepseek-v3.2 | exec_no_solve | 3 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | deepseek-v3.2 | infeasible_unbounded_misclassification | 19 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| OptiBench | deepseek-v3.2 | name_error | 17 | 0.000 | 0.000 | 0.000 | 0.000 | 0.059 |
| OptiBench | deepseek-v3.2 | runtime_error | 71 | 0.000 | 0.000 | 0.000 | 0.000 | 0.014 |
| OptiBench | deepseek-v3.2 | syntax_error | 51 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | deepseek-v3.2 | timeout | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | deepseek-v3.2 | wrong_numeric | 77 | 0.000 | 1.000 | 1.000 | 1.000 | 0.987 |
| OptiBench | gpt-4.1-mini | correct | 391 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| OptiBench | gpt-4.1-mini | infeasible_unbounded_misclassification | 7 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| OptiBench | gpt-4.1-mini | missing_module | 90 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | gpt-4.1-mini | runtime_error | 64 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | gpt-4.1-mini | syntax_error | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | gpt-4.1-mini | wrong_numeric | 52 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| OptiBench | gpt-4o | api_error | 198 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | gpt-4o | correct | 143 | 1.000 | 1.000 | 1.000 | 1.000 | 0.986 |
| OptiBench | gpt-4o | exec_no_solve | 1 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | gpt-4o | infeasible_unbounded_misclassification | 1 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| OptiBench | gpt-4o | missing_module | 234 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | gpt-4o | runtime_error | 12 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | gpt-4o | syntax_error | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | gpt-4o | wrong_numeric | 14 | 0.000 | 1.000 | 1.000 | 1.000 | 0.929 |
| OptiBench | gpt-4o-mini | correct | 336 | 1.000 | 1.000 | 1.000 | 1.000 | 0.994 |
| OptiBench | gpt-4o-mini | infeasible_unbounded_misclassification | 21 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| OptiBench | gpt-4o-mini | missing_module | 93 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | gpt-4o-mini | name_error | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | gpt-4o-mini | runtime_error | 57 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | gpt-4o-mini | syntax_error | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | gpt-4o-mini | wrong_numeric | 96 | 0.000 | 1.000 | 1.000 | 1.000 | 0.938 |

## Verification Status

| dataset | model | verification_status | n | accuracy | executable_rate | solve_rate | objective_evaluable_rate | variable_output_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IndustryOR | deepseek-v3 | executed_no_verified_solution | 5 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| IndustryOR | deepseek-v3 | not_executable | 16 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | deepseek-v3 | objective_match | 53 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| IndustryOR | deepseek-v3 | objective_mismatch_with_variables | 26 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| IndustryOR | deepseek-v3.2 | executed_no_verified_solution | 3 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| IndustryOR | deepseek-v3.2 | not_executable | 44 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | deepseek-v3.2 | objective_match | 39 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| IndustryOR | deepseek-v3.2 | objective_mismatch_with_variables | 14 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| IndustryOR | gpt-4.1-mini | executed_no_verified_solution | 7 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| IndustryOR | gpt-4.1-mini | not_executable | 14 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | gpt-4.1-mini | objective_match | 55 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| IndustryOR | gpt-4.1-mini | objective_mismatch | 1 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| IndustryOR | gpt-4.1-mini | objective_mismatch_with_variables | 23 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| IndustryOR | gpt-4o | executed_no_verified_solution | 4 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| IndustryOR | gpt-4o | missing_objective | 1 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | gpt-4o | not_executable | 68 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | gpt-4o | objective_match | 18 | 1.000 | 1.000 | 1.000 | 1.000 | 0.944 |
| IndustryOR | gpt-4o | objective_mismatch | 2 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| IndustryOR | gpt-4o | objective_mismatch_with_variables | 7 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| IndustryOR | gpt-4o-mini | executed_no_verified_solution | 6 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| IndustryOR | gpt-4o-mini | not_executable | 36 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| IndustryOR | gpt-4o-mini | objective_match | 24 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| IndustryOR | gpt-4o-mini | objective_mismatch | 10 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| IndustryOR | gpt-4o-mini | objective_mismatch_with_variables | 24 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_ComplexLP | deepseek-v3 | executed_no_verified_solution | 7 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| MAMO_ComplexLP | deepseek-v3 | not_executable | 27 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_ComplexLP | deepseek-v3 | objective_match | 133 | 1.000 | 1.000 | 1.000 | 1.000 | 0.985 |
| MAMO_ComplexLP | deepseek-v3 | objective_mismatch_with_variables | 36 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_ComplexLP | deepseek-v3.2 | executed_no_verified_solution | 7 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| MAMO_ComplexLP | deepseek-v3.2 | not_executable | 80 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_ComplexLP | deepseek-v3.2 | objective_match | 93 | 1.000 | 1.000 | 1.000 | 1.000 | 0.978 |
| MAMO_ComplexLP | deepseek-v3.2 | objective_mismatch | 3 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| MAMO_ComplexLP | deepseek-v3.2 | objective_mismatch_with_variables | 20 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_ComplexLP | gpt-4.1-mini | executed_no_verified_solution | 12 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| MAMO_ComplexLP | gpt-4.1-mini | not_executable | 10 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_ComplexLP | gpt-4.1-mini | objective_match | 146 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_ComplexLP | gpt-4.1-mini | objective_mismatch_with_variables | 35 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_ComplexLP | gpt-4o | not_executable | 203 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_ComplexLP | gpt-4o-mini | executed_no_verified_solution | 36 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| MAMO_ComplexLP | gpt-4o-mini | not_executable | 31 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_ComplexLP | gpt-4o-mini | objective_match | 71 | 1.000 | 1.000 | 1.000 | 1.000 | 0.944 |
| MAMO_ComplexLP | gpt-4o-mini | objective_mismatch | 32 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| MAMO_ComplexLP | gpt-4o-mini | objective_mismatch_with_variables | 33 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_EasyLP | deepseek-v3 | executed_no_verified_solution | 23 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| MAMO_EasyLP | deepseek-v3 | not_executable | 84 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | deepseek-v3 | objective_match | 485 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_EasyLP | deepseek-v3 | objective_mismatch_with_variables | 50 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_EasyLP | deepseek-v3.2 | executed_no_verified_solution | 18 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| MAMO_EasyLP | deepseek-v3.2 | missing_objective | 1 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | deepseek-v3.2 | not_executable | 167 | 0.000 | 0.000 | 0.000 | 0.000 | 0.006 |
| MAMO_EasyLP | deepseek-v3.2 | objective_match | 418 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_EasyLP | deepseek-v3.2 | objective_mismatch_with_variables | 38 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_EasyLP | gemini-2.5-pro | not_executable | 165 | 0.000 | 0.000 | 0.000 | 0.000 | 0.006 |
| MAMO_EasyLP | gemini-2.5-pro | objective_match | 71 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_EasyLP | gemini-2.5-pro | objective_mismatch_with_variables | 2 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_EasyLP | gpt-4.1-mini | executed_no_verified_solution | 8 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| MAMO_EasyLP | gpt-4.1-mini | not_executable | 3 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | gpt-4.1-mini | objective_match | 594 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_EasyLP | gpt-4.1-mini | objective_mismatch_with_variables | 37 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_EasyLP | gpt-4o | executed_no_verified_solution | 3 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| MAMO_EasyLP | gpt-4o | not_executable | 110 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | gpt-4o | objective_match | 505 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_EasyLP | gpt-4o | objective_mismatch_with_variables | 24 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_EasyLP | gpt-4o-mini | executed_no_verified_solution | 104 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| MAMO_EasyLP | gpt-4o-mini | not_executable | 13 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | gpt-4o-mini | objective_match | 368 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_EasyLP | gpt-4o-mini | objective_mismatch_with_variables | 157 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_EasyLP | o3-mini | not_executable | 2 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| MAMO_EasyLP | o3-mini | objective_match | 39 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MAMO_EasyLP | o3-mini | objective_mismatch_with_variables | 2 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NL4OPT | deepseek-v3 | executed_no_verified_solution | 30 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| NL4OPT | deepseek-v3 | not_executable | 29 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | deepseek-v3 | objective_match | 194 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NL4OPT | deepseek-v3 | objective_mismatch_with_variables | 22 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NL4OPT | deepseek-v3.2 | executed_no_verified_solution | 16 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| NL4OPT | deepseek-v3.2 | not_executable | 50 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | deepseek-v3.2 | objective_match | 165 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NL4OPT | deepseek-v3.2 | objective_mismatch_with_variables | 14 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NL4OPT | gemini-2.5-pro | executed_no_verified_solution | 6 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| NL4OPT | gemini-2.5-pro | not_executable | 132 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | gemini-2.5-pro | objective_match | 101 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NL4OPT | gemini-2.5-pro | objective_mismatch_with_variables | 6 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NL4OPT | gpt-4.1-mini | executed_no_verified_solution | 13 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| NL4OPT | gpt-4.1-mini | not_executable | 17 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | gpt-4.1-mini | objective_match | 206 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NL4OPT | gpt-4.1-mini | objective_mismatch_with_variables | 9 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NL4OPT | gpt-4o | executed_no_verified_solution | 3 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| NL4OPT | gpt-4o | not_executable | 135 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | gpt-4o | objective_match | 106 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NL4OPT | gpt-4o | objective_mismatch_with_variables | 1 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NL4OPT | gpt-4o-mini | executed_no_verified_solution | 27 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| NL4OPT | gpt-4o-mini | not_executable | 18 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | gpt-4o-mini | objective_match | 186 | 1.000 | 1.000 | 1.000 | 1.000 | 0.984 |
| NL4OPT | gpt-4o-mini | objective_mismatch_with_variables | 14 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NL4OPT | o3-mini | executed_no_verified_solution | 15 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| NL4OPT | o3-mini | missing_objective | 2 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | o3-mini | not_executable | 8 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| NL4OPT | o3-mini | objective_match | 211 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NL4OPT | o3-mini | objective_mismatch_with_variables | 9 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| OptMATH_Bench | deepseek-v3 | executed_no_verified_solution | 11 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| OptMATH_Bench | deepseek-v3 | not_executable | 56 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | deepseek-v3 | objective_match | 52 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| OptMATH_Bench | deepseek-v3 | objective_mismatch | 1 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| OptMATH_Bench | deepseek-v3 | objective_mismatch_with_variables | 46 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| OptMATH_Bench | deepseek-v3.2 | executed_no_verified_solution | 11 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| OptMATH_Bench | deepseek-v3.2 | missing_objective | 2 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | deepseek-v3.2 | not_executable | 72 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | deepseek-v3.2 | objective_match | 35 | 1.000 | 1.000 | 1.000 | 1.000 | 0.971 |
| OptMATH_Bench | deepseek-v3.2 | objective_mismatch | 8 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| OptMATH_Bench | deepseek-v3.2 | objective_mismatch_with_variables | 38 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| OptMATH_Bench | gpt-4.1-mini | executed_no_verified_solution | 8 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| OptMATH_Bench | gpt-4.1-mini | not_executable | 55 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | gpt-4.1-mini | objective_match | 58 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| OptMATH_Bench | gpt-4.1-mini | objective_mismatch_with_variables | 45 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| OptMATH_Bench | gpt-4o | executed_no_verified_solution | 1 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| OptMATH_Bench | gpt-4o | missing_objective | 1 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | gpt-4o | not_executable | 152 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | gpt-4o | objective_match | 8 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| OptMATH_Bench | gpt-4o | objective_mismatch | 1 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| OptMATH_Bench | gpt-4o | objective_mismatch_with_variables | 3 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| OptMATH_Bench | gpt-4o-mini | executed_no_verified_solution | 1 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| OptMATH_Bench | gpt-4o-mini | not_executable | 149 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptMATH_Bench | gpt-4o-mini | objective_match | 5 | 1.000 | 1.000 | 1.000 | 1.000 | 0.600 |
| OptMATH_Bench | gpt-4o-mini | objective_mismatch | 1 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| OptMATH_Bench | gpt-4o-mini | objective_mismatch_with_variables | 10 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| OptiBench | deepseek-v3 | executed_no_verified_solution | 31 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| OptiBench | deepseek-v3 | missing_objective | 1 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | deepseek-v3 | not_executable | 70 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | deepseek-v3 | objective_match | 406 | 1.000 | 1.000 | 1.000 | 1.000 | 0.998 |
| OptiBench | deepseek-v3 | objective_mismatch_with_variables | 97 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| OptiBench | deepseek-v3.2 | executed_no_verified_solution | 19 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| OptiBench | deepseek-v3.2 | missing_objective | 3 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | deepseek-v3.2 | not_executable | 140 | 0.000 | 0.000 | 0.000 | 0.000 | 0.014 |
| OptiBench | deepseek-v3.2 | objective_match | 366 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| OptiBench | deepseek-v3.2 | objective_mismatch | 1 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| OptiBench | deepseek-v3.2 | objective_mismatch_with_variables | 76 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| OptiBench | gpt-4.1-mini | executed_no_verified_solution | 7 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| OptiBench | gpt-4.1-mini | not_executable | 155 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | gpt-4.1-mini | objective_match | 391 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| OptiBench | gpt-4.1-mini | objective_mismatch_with_variables | 52 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| OptiBench | gpt-4o | executed_no_verified_solution | 1 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| OptiBench | gpt-4o | missing_objective | 1 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | gpt-4o | not_executable | 446 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | gpt-4o | objective_match | 143 | 1.000 | 1.000 | 1.000 | 1.000 | 0.986 |
| OptiBench | gpt-4o | objective_mismatch | 1 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| OptiBench | gpt-4o | objective_mismatch_with_variables | 13 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| OptiBench | gpt-4o-mini | executed_no_verified_solution | 21 | 0.000 | 1.000 | 0.000 | 1.000 | 0.000 |
| OptiBench | gpt-4o-mini | not_executable | 152 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| OptiBench | gpt-4o-mini | objective_match | 336 | 1.000 | 1.000 | 1.000 | 1.000 | 0.994 |
| OptiBench | gpt-4o-mini | objective_mismatch | 6 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| OptiBench | gpt-4o-mini | objective_mismatch_with_variables | 90 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |

## Ablation Prompt Bias

| model | prompt_id | n | accuracy | executable_rate | solve_rate | objective_evaluable_rate | variable_output_rate | max_solver_share | top_solver | unavailable_solver_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepseek-v3 | neutral_best | 300 | 0.603 | 0.820 | 0.760 | 0.820 | 0.757 | 0.563 | pulp | 0.050 |
| deepseek-v3 | solver_specific_coptpy | 300 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | coptpy | 1.000 |
| deepseek-v3 | solver_specific_gurobipy | 300 | 0.690 | 0.850 | 0.843 | 0.850 | 0.000 | 1.000 | gurobipy | 0.000 |
| deepseek-v3 | solver_specific_pyscipopt | 300 | 0.727 | 0.837 | 0.820 | 0.833 | 0.000 | 1.000 | pyscipopt | 0.000 |
| deepseek-v3.2 | neutral_best | 300 | 0.533 | 0.697 | 0.660 | 0.693 | 0.653 | 0.430 | pulp | 0.027 |
| deepseek-v3.2 | solver_specific_coptpy | 300 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.997 | coptpy | 0.997 |
| deepseek-v3.2 | solver_specific_gurobipy | 300 | 0.593 | 0.733 | 0.727 | 0.733 | 0.000 | 1.000 | gurobipy | 0.000 |
| deepseek-v3.2 | solver_specific_pyscipopt | 300 | 0.627 | 0.770 | 0.763 | 0.767 | 0.000 | 0.997 | pyscipopt | 0.003 |
| gemini-2.5-pro | neutral_best | 11 | 0.273 | 0.364 | 0.273 | 0.364 | 0.273 | 0.818 | pulp | 0.000 |
| gpt-4.1-mini | neutral_best | 300 | 0.653 | 0.833 | 0.810 | 0.833 | 0.807 | 0.867 | pulp | 0.113 |
| gpt-4.1-mini | solver_specific_coptpy | 300 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.997 | coptpy | 1.000 |
| gpt-4.1-mini | solver_specific_gurobipy | 300 | 0.720 | 0.883 | 0.870 | 0.883 | 0.000 | 1.000 | gurobipy | 0.000 |
| gpt-4.1-mini | solver_specific_pyscipopt | 300 | 0.677 | 0.823 | 0.823 | 0.823 | 0.000 | 0.997 | pyscipopt | 0.003 |
| gpt-4o | neutral_best | 300 | 0.097 | 0.100 | 0.097 | 0.100 | 0.097 | 0.777 | unknown | 0.117 |
| gpt-4o | solver_specific_coptpy | 300 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.960 | unknown | 0.040 |
| gpt-4o | solver_specific_gurobipy | 300 | 0.037 | 0.053 | 0.050 | 0.053 | 0.000 | 0.937 | unknown | 0.000 |
| gpt-4o | solver_specific_pyscipopt | 300 | 0.020 | 0.033 | 0.033 | 0.033 | 0.000 | 0.957 | unknown | 0.000 |
| gpt-4o-mini | neutral_best | 300 | 0.413 | 0.697 | 0.640 | 0.697 | 0.573 | 0.440 | scipy.optimize | 0.200 |
| gpt-4o-mini | solver_specific_coptpy | 300 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.840 | coptpy | 0.840 |
| gpt-4o-mini | solver_specific_gurobipy | 300 | 0.490 | 0.540 | 0.540 | 0.540 | 0.000 | 0.647 | gurobipy | 0.000 |
| gpt-4o-mini | solver_specific_pyscipopt | 300 | 0.523 | 0.690 | 0.683 | 0.690 | 0.000 | 1.000 | pyscipopt | 0.000 |

## Ablation Solver Bias

| model | prompt_id | solver | n | accuracy | executable_rate | solve_rate |
| --- | --- | --- | --- | --- | --- | --- |
| deepseek-v3 | neutral_best | coptpy | 2 | 0.000 | 0.000 | 0.000 |
| deepseek-v3 | neutral_best | cvxpy | 10 | 0.000 | 0.000 | 0.000 |
| deepseek-v3 | neutral_best | docplex | 1 | 0.000 | 0.000 | 0.000 |
| deepseek-v3 | neutral_best | mip+pyomo | 1 | 0.000 | 0.000 | 0.000 |
| deepseek-v3 | neutral_best | ortools | 12 | 0.417 | 0.750 | 0.750 |
| deepseek-v3 | neutral_best | pulp | 169 | 0.680 | 0.864 | 0.822 |
| deepseek-v3 | neutral_best | pulp+scipy.optimize | 18 | 0.833 | 0.889 | 0.833 |
| deepseek-v3 | neutral_best | pyomo | 1 | 0.000 | 0.000 | 0.000 |
| deepseek-v3 | neutral_best | scipy.optimize | 80 | 0.537 | 0.900 | 0.775 |
| deepseek-v3 | neutral_best | unknown | 6 | 0.500 | 0.500 | 0.500 |
| deepseek-v3 | solver_specific_coptpy | coptpy | 300 | 0.000 | 0.000 | 0.000 |
| deepseek-v3 | solver_specific_gurobipy | gurobipy | 300 | 0.690 | 0.850 | 0.843 |
| deepseek-v3 | solver_specific_pyscipopt | pyscipopt | 300 | 0.727 | 0.837 | 0.820 |
| deepseek-v3.2 | neutral_best | coptpy | 2 | 0.000 | 0.000 | 0.000 |
| deepseek-v3.2 | neutral_best | cvxpy | 3 | 0.000 | 0.000 | 0.000 |
| deepseek-v3.2 | neutral_best | mip+pulp | 1 | 0.000 | 0.000 | 0.000 |
| deepseek-v3.2 | neutral_best | mip+pulp+scipy.optimize | 1 | 1.000 | 1.000 | 1.000 |
| deepseek-v3.2 | neutral_best | mip+scipy.optimize | 1 | 0.000 | 0.000 | 0.000 |
| deepseek-v3.2 | neutral_best | ortools | 22 | 0.500 | 0.727 | 0.727 |
| deepseek-v3.2 | neutral_best | pulp | 129 | 0.504 | 0.659 | 0.643 |
| deepseek-v3.2 | neutral_best | pulp+scipy.optimize | 4 | 0.750 | 1.000 | 1.000 |
| deepseek-v3.2 | neutral_best | scipy.optimize | 123 | 0.569 | 0.756 | 0.683 |
| deepseek-v3.2 | neutral_best | unknown | 14 | 0.714 | 0.714 | 0.714 |
| deepseek-v3.2 | solver_specific_coptpy | coptpy | 299 | 0.000 | 0.000 | 0.000 |
| deepseek-v3.2 | solver_specific_coptpy | pulp | 1 | 0.000 | 0.000 | 0.000 |
| deepseek-v3.2 | solver_specific_gurobipy | gurobipy | 300 | 0.593 | 0.733 | 0.727 |
| deepseek-v3.2 | solver_specific_pyscipopt | mip+pyscipopt | 1 | 0.000 | 0.000 | 0.000 |
| deepseek-v3.2 | solver_specific_pyscipopt | pyscipopt | 299 | 0.629 | 0.773 | 0.766 |
| gemini-2.5-pro | neutral_best | pulp | 9 | 0.333 | 0.444 | 0.333 |
| gemini-2.5-pro | neutral_best | unknown | 2 | 0.000 | 0.000 | 0.000 |
| gpt-4.1-mini | neutral_best | coptpy | 2 | 0.000 | 0.000 | 0.000 |
| gpt-4.1-mini | neutral_best | cvxpy | 29 | 0.000 | 0.000 | 0.000 |
| gpt-4.1-mini | neutral_best | cvxpy+mip | 1 | 0.000 | 0.000 | 0.000 |
| gpt-4.1-mini | neutral_best | cvxpy+pulp | 1 | 0.000 | 0.000 | 0.000 |
| gpt-4.1-mini | neutral_best | cvxpy+scipy.optimize | 1 | 0.000 | 0.000 | 0.000 |
| gpt-4.1-mini | neutral_best | ortools | 1 | 0.000 | 0.000 | 0.000 |
| gpt-4.1-mini | neutral_best | pulp | 260 | 0.746 | 0.942 | 0.915 |
| gpt-4.1-mini | neutral_best | pulp+scipy.optimize | 1 | 0.000 | 1.000 | 1.000 |
| gpt-4.1-mini | neutral_best | scipy.optimize | 4 | 0.500 | 1.000 | 1.000 |
| gpt-4.1-mini | solver_specific_coptpy | coptpy | 299 | 0.000 | 0.000 | 0.000 |
| gpt-4.1-mini | solver_specific_coptpy | coptpy+mip | 1 | 0.000 | 0.000 | 0.000 |
| gpt-4.1-mini | solver_specific_gurobipy | gurobipy | 300 | 0.720 | 0.883 | 0.870 |
| gpt-4.1-mini | solver_specific_pyscipopt | mip+pyscipopt | 1 | 0.000 | 0.000 | 0.000 |
| gpt-4.1-mini | solver_specific_pyscipopt | pyscipopt | 299 | 0.679 | 0.826 | 0.826 |
| gpt-4o | neutral_best | cvxpy | 35 | 0.000 | 0.000 | 0.000 |
| gpt-4o | neutral_best | ortools | 1 | 0.000 | 0.000 | 0.000 |
| gpt-4o | neutral_best | pulp | 31 | 0.935 | 0.968 | 0.935 |
| gpt-4o | neutral_best | unknown | 233 | 0.000 | 0.000 | 0.000 |
| gpt-4o | solver_specific_coptpy | coptpy | 12 | 0.000 | 0.000 | 0.000 |
| gpt-4o | solver_specific_coptpy | unknown | 288 | 0.000 | 0.000 | 0.000 |
| gpt-4o | solver_specific_gurobipy | gurobipy | 19 | 0.579 | 0.842 | 0.789 |
| gpt-4o | solver_specific_gurobipy | unknown | 281 | 0.000 | 0.000 | 0.000 |
| gpt-4o | solver_specific_pyscipopt | pyscipopt | 13 | 0.462 | 0.769 | 0.769 |
| gpt-4o | solver_specific_pyscipopt | unknown | 287 | 0.000 | 0.000 | 0.000 |
| gpt-4o-mini | neutral_best | coptpy | 2 | 0.000 | 0.000 | 0.000 |
| gpt-4o-mini | neutral_best | cvxpy | 58 | 0.000 | 0.000 | 0.000 |
| gpt-4o-mini | neutral_best | ortools | 1 | 0.000 | 0.000 | 0.000 |
| gpt-4o-mini | neutral_best | pulp | 106 | 0.726 | 0.887 | 0.849 |
| gpt-4o-mini | neutral_best | pulp+scipy.optimize | 1 | 1.000 | 1.000 | 1.000 |
| gpt-4o-mini | neutral_best | scipy.optimize | 132 | 0.348 | 0.864 | 0.765 |
| gpt-4o-mini | solver_specific_coptpy | coptpy | 252 | 0.000 | 0.000 | 0.000 |
| gpt-4o-mini | solver_specific_coptpy | unknown | 48 | 0.000 | 0.000 | 0.000 |
| gpt-4o-mini | solver_specific_gurobipy | gurobipy | 194 | 0.758 | 0.835 | 0.835 |
| gpt-4o-mini | solver_specific_gurobipy | unknown | 106 | 0.000 | 0.000 | 0.000 |
| gpt-4o-mini | solver_specific_pyscipopt | pyscipopt | 300 | 0.523 | 0.690 | 0.683 |