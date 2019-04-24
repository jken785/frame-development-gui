class LoadCases:
	class Test:
		name = "Test"
		force = [20.000000, 30.000000, 40.000000, 0.000000, 0.000000, 0.000000]
		nodesForce = [3,2,4, force]
		nodeForceCases = [nodesForce]
		fixedNodes = [6,7,8]
		objFuncNodes = [1,2]
		objFuncWeight = 0.065000
	class testingAgain:
		name = "testingAgain"
		force = [3.000000, 3.000000, 3.000000, 3.000000, 3.000000, 3.000000]
		nodesForce = [3,4,5,6,7, force]
		nodeForceCases = [nodesForce]
		fixedNodes = [8]
		objFuncNodes = [9]
		objFuncWeight = 0.700000
	listLoadCases = [testingAgain,Test]