""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load example3 class from file example3.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .example3 import Example3
    return Example3(iface)
