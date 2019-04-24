class LoadCases:
	class lotsOnBulkhead:
		name = "lotsOnBulkhead"
		force = [100.000000, 100.000000, 100.000000, 0.000000, 0.000000, 0.000000]
		nodesForce = [0, force]
		nodeForceCases = [nodesForce]
		fixedNodes = [38, 39, 40, 41]
		objFuncNodes = [0, 1]
		objFuncWeight = 1.000000
	class downOnPyramid:
		name = "downOnPyramid"
		force = [0.000000, 0.000000, -200.000000, 0.000000, 0.000000, 0.000000]
		nodesForce = [52, force]
		nodeForceCases = [nodesForce]
		fixedNodes = [40, 41, 44, 45]
		objFuncNodes = [52]
		objFuncWeight = 1.200000
	listLoadCases = [downOnPyramid,lotsOnBulkhead]