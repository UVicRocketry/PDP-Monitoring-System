import numpy as np
import pandas as pd

class TestFeatureCompletion():
    def __init__(self, rho: list[int] | int, tau: list[int] | int, id: list[str] | str) -> None:
        self.__rhos: np.array[int] | int = np.array(rhos) if isinstance(rhos, list) else rho
        self.__taus: np.array[int] | int = np.array(taus) if isinstance(taus, list) else tau
        self.zetas: np.array[float] | float = None

        if self.__rhos.shape != self.__taus.shape:
            raise ValueError("The size of rhos and taus must be the same")

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
        print(T)
        return (((self.__rhos * self.__taus) / T)*100)
    
    @property
    def __is_equal_to_100(self) -> bool:
        zetas_sum: float = np.sum(self.zetas)
        return zetas_sum == 100

ids: list[str] = None
rhos: list[int] = None
taus: list[int] = None
zetas: list[float] = None


test_case_data = [
    pd.read_csv("test-case-completion-matrix-1.3.csv"),
    pd.read_csv("test-case-completion-matrix-1.6.csv")
]

test_case_numbers = [3, 6]

NUMBER_OF_TEST_CASES = len(test_case_data)

test_case_competition_matrix = None

if __name__ == '__main__':
    
    for i in range(NUMBER_OF_TEST_CASES):
        test_case_competition_matrix = test_case_data[i]
        
        ids = test_case_competition_matrix["Test Case ID"]
        rhos = test_case_competition_matrix["Priority type"]
        taus = test_case_competition_matrix["Priority importance"]

        completion = TestFeatureCompletion(rhos, taus, ids).compute_feature_completion()
        print(completion)
        updated_matrix = test_case_competition_matrix.assign(zeta=list(completion))

        print(updated_matrix)

        updated_matrix.to_csv(f"test-case-completion-matrix-1.{test_case_numbers[i]}.csv", index=False)

    
