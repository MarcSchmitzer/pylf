
import pyramid.testing as testing

from pytest import fixture


@fixture
def testconfig(request):
    config = testing.setUp()
    request.addfinalizer(testing.tearDown)
    return config
