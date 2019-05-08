# anycast_catchment_prediction
Algorithms to predict (deterministically, probabilistically or with the help of oracles) the catchment of anycasted IP prefixes

[1] Pavlos Sermpezis and Vasileios Kotronis. “Inferring Catchment in Internet Routing”, ACM SIGMETRICS, 2019.

This project implements the algorithms presented in [1], and includes some examples. Please cite [1] if you use this code for your research.


FILES:

Files for running a BGP simulation:
-- BGPnode.py
-- IXPNode.py
-- BGPtopology.py

Files for building the R-graph and implementing algorithms of [1]:
-- Rgraph.py
-- create_Rgraph_from_Topo.py
-- measurement_selection_methods.py

Files with examples (how to run the code):
-- example_catchment_inference.py
-- example_measurement_selection.py

Files with example datasets:
-- /CAIDA AS-graph/20190401.as-rel2.txt





