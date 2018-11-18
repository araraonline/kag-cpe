"""
Department file for Department 35-00103 (Charlotte, NC)
"""

from cpe_help import Department, util


class Department3500103(Department):
    def preprocess_shapefile(self):
        """
        This shapefile is composed of points. As a fallback method, convert
        those points into circular areas (radius).

        Also, remove Police Academy entry.
        """
        df = self.load_external_shapefile()
        df = df[df['NAME'] != 'Academy']

        # project into equal area
        proj = util.crs.equal_area_from_geodf(df)
        df = df.to_crs(proj)

        # calculate buffer (1.5km around each point)
        df.geometry = df.geometry.buffer(1500)

        # project into default
        df = df.to_crs(util.crs.DEFAULT)

        self.save_preprocessed_shapefile(df)
