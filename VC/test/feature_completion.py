__author__ = "Kris Lemieux"
__version__ = "1.0.0"
__maintainer__ = "Kris Lemieux"
__username__ = "klemie"

'''
This file is meant to be ran as a script. It is used to compute the feature completion of a test case or suite of tests. To run the script, you must have the following files in the same directory as this file:

You must have a file named test-case-completion-matrix-1.{num}.csv where num is the number of the test case. This file must have the following columns:

- Test Case ID
- Priority type
- Priority importance

```bash

```

'''

import sys 
import numpy as np
import pandas as pd

class TestFeatureCompletion():
    '''
    
    Name:
        TestFeatureCompletion
    Desc:
        This class is used to compute the feature completion of a test case. It does this by computing the zeta index of the test case. The zeta index is computed by the formula:
        
        $\zeta$ = ($\rho$ * $\tau$) / T * 100
       
        where rho is the priority type of the test case, tau is the priority importance of the test case and T is the sum of the product of rho and tau. $\zeta$ then equates to a weighted sum of actual how much a test completes a feature. 
    '''
    def __init__(self, rho: list[int] | int, tau: list[int] | int, id: list[str] | str) -> None:
        self.__rhos: np.array[int] | int = np.array(rhos) if isinstance(rhos, list) else rho
        self.__taus: np.array[int] | int = np.array(taus) if isinstance(taus, list) else tau
        self.zetas: np.array[float] | float = None

        if self.__rhos.shape != self.__taus.shape:
            raise ValueError("The size of rhos and taus must be the same column size")
        
        if np.logical_and(self.__rhos > 0, self.__rhos < 4).any():
            raise ValueError("\nThe Test Importance (rho) must be range 0-4. See test legend for more information.")
        
        if np.logical_and(self.__taus > 1, self.__taus < 2).any():
            raise ValueError("\nThe Test Type (tau) must be range 1-2. See test legend for more information.")

        if not all(isinstance(rho, int) for rho in self.__rhos):
            raise ValueError("The elements of rhos must be integers")
        
        if not all(isinstance(tau, int) for tau in self.__taus):
            raise ValueError("The elements of taus must be integers")

    def compute_feature_completion(self) -> float:
        '''
        Name:
            TestFeatureCompletion.compute_feature_completion() -> float
        Desc:
            Computes the feature completion
        '''
        self.zetas = self.__zeta_index()
        if not self.__is_equal_to_100:
            raise ValueError("The sum of zetas must be equal to 100")
        return self.zetas

    def __zeta_index(self) -> float:
        '''
        Name:
            TestFeatureCompletion.__zeta_index() -> float
        Desc:
            Computes the zeta index
        '''
        T = np.sum(self.__rhos * self.__taus)
        return round((((self.__rhos * self.__taus) / T)*100), 2)
    
    @property
    def __is_equal_to_100(self) -> bool:
        zetas_sum: float = np.sum(self.zetas)
        return zetas_sum == 100

test_case_numbers = []

if len(sys.argv) > 1:
    flag = False
    for i, arg in enumerate(sys.argv):
        if flag:
            test_case_numbers.append(int(arg))
        if arg == "--filenumber" or arg == "-f":
            flag = True
        
else:
    raise ValueError("You must provide the input file numbers after a --filenumber or -f flag")

ids: list[str] = None
rhos: list[int] = None
taus: list[int] = None
zetas: list[float] = None

test_case_data = []

try:
    test_case_data = [pd.read_csv(f"test-case-completion-matrix-{num}.csv") for num in test_case_numbers]
except FileNotFoundError:
    raise FileNotFoundError("\n\n--> Either the file does not exist or the file is not in the correct directory or you inputting the incorrect file number as a command line argument. Please check the file and try again. <--\n\nexample input: `python feature_completion.py -f 1 2` where test-case-completion-matrix-1.csv and test-case-completion-matrix-2.csv exist in the same directory as this script.")

NUMBER_OF_TEST_CASES = len(test_case_data)

test_case_competition_matrix = None

if __name__ == '__main__':
    
    for i in range(NUMBER_OF_TEST_CASES):
        test_case_competition_matrix = test_case_data[i]
        
        ids = test_case_competition_matrix["Test Case ID"]
        rhos = test_case_competition_matrix["Priority type"]
        taus = test_case_competition_matrix["Priority importance"]

        completion = TestFeatureCompletion(rhos, taus, ids).compute_feature_completion()
        updated_matrix = test_case_competition_matrix.assign(zeta=list(completion))

        print("\n")
        print(updated_matrix)

        updated_matrix.to_csv(f"test-case-completion-matrix-{test_case_numbers[i]}.csv", index=False)

    
