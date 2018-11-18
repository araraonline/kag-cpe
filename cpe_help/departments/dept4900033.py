"""
Module for department 49-00033
"""

import pandas

from cpe_help import Department


class Department4900033(Department):
    """
    Class for department 49-00033

    Specified here is an example of how the preprocessing of specific
    department files will proceed.
    """
    @property
    def external_arrests_path(self):
        return self.external_dir / '49-00033_Arrests_2015.csv'
    
    @property
    def preprocessed_arrests_path(self):
        return self.preprocessed_dir / 'arrests_2015.pkl'

    def load_external_arrests(self):
        return pandas.read_csv(
            self.external_arrests_path,
            low_memory=False,
            skiprows=[1],
        )

    def load_preprocessed_arrests(self):
        return pandas.read_pickle(self.preprocessed_arrests_path)

    def save_preprocessed_arrests(self, df):
        df.to_pickle(self.preprocessed_arrests_path)
