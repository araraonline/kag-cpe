"""
Task creators for doit
"""

from cpe_help import util


class TaskHelper(object):
    """
    I help with the creation of tasks
    """
    @staticmethod
    def download(url, out, overwrite=False, **kwargs):
        """
        Generate a task to download a file

        Note that, by default, downloads are never cleaned. You can
        change this behavior by sending clean=True along with the
        kwargs.

        Parameters
        ----------
        url : str
            The url to download from.
        out : str or Path
            The output filename.
        overwrite : bool, default False
            If True, overwrite existing files. Otherwise, do not perform
            the download when out exists.
        kwargs
            Keyword arguments are added as items of the resulting dict.

        Returns
        -------
        dict
            The task to be performed.
        """
        task = {
            'targets': [out],
            'actions': [(util.network.download, (url, out))],
            'uptodate': [not overwrite],
        }
        task.update(kwargs)
        return task

    @staticmethod
    def unzip(file, dir, **kwargs):
        """
        Generate a task to extract files from a ZIP archive

        Parameters
        ----------
        file : str or Path
            The input ZIP file.
        dir : str or Path
            The directory to extract the ZIP contents to.
        kwargs
            Keyword arguments are added as items of the resulting dict.

        Returns
        -------
        dict
            The task to be performed.

        Notes
        -----
        As we can't know the ZIP archive contents beforehand, this task
        will only be rerun when the whole output directory goes missing
        (not its contents).
        """
        task = {
            'file_dep': [file],
            'targets': [dir],
            'actions': [(util.compression.extract_zipfile, (file, dir))],
            'clean': [(util.file.maybe_rmtree, (dir,))],
        }
        task.update(kwargs)
        return task
